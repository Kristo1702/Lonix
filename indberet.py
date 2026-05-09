from datetime import datetime, timedelta

import functions as ft
from colorama import init, Fore, Style

init()


def _parse_number(value):
    return float(value.replace(",", "."))


def _parse_clock_minutes(value):
    return ft.try_parse_clock_minutes(value)


def _calculate_hours_from_times(start_str, end_str):
    try:
        return ft.calculate_hours_from_times(start_str, end_str)
    except ValueError:
        return None


def _format_cli_number(value):
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)

def shift_entry_header(hours, rate, pause=0):
        if hours is None:
            hours = "-"
        if rate is None:
            rate = "-"
        else:
            rate = f"{rate} kr "

        if (len(str(hours)) + 11) > (len(str(rate)) + 11):
            longest_str = len(str(hours)) + 11
            rate_padding = (len(str(hours)) + 11) - (len(str(rate)) + 11)
            hours_padding = 0
        else:
            longest_str = len(str(rate)) + 11
            rate_padding = 0
            hours_padding = (len(str(rate)) + 11) - (len(str(hours)) + 11)

        print(Fore.LIGHTBLACK_EX + "    ┏" + "━"*longest_str + "┓")
        print("    ┃" + Fore.WHITE + f" Timer:   {hours} " + " "*hours_padding + Fore.LIGHTBLACK_EX + "┃")
        print("    ┃" + Fore.WHITE + f" Timeløn: {rate} " + Fore.LIGHTBLACK_EX + " "*rate_padding + "┃")
        print("    ┃" + Fore.WHITE + f" Pause:   {pause} min" + Fore.LIGHTBLACK_EX + " " * max(0, longest_str - len(str(pause)) - 14) + "┃")
        print("    ┗" + "━"*longest_str + "┛" + Style.RESET_ALL)

def _format_overwrite_entry(index, dato, løn_info):
    duration = ft.get_shift_duration_hours(løn_info)
    pause_hours = ft.get_shift_pause_hours(løn_info)
    rate = løn_info.get("timeløn", 0)
    time_text = ""
    if løn_info.get("start") and løn_info.get("slut"):
        time_text = f", {løn_info.get('start')}-{løn_info.get('slut')}"
    return (
        f"({index}) {dato}: {_format_cli_number(duration)} timer, "
        f"{_format_cli_number(rate)} kr/t, pause {_format_cli_number(pause_hours * 60)} min{time_text}"
    )


def _choose_entry_to_overwrite(dato, entries):
    if len(entries) == 1:
        return entries[0]

    print(Fore.YELLOW + f"\nDer findes {len(entries)} vagter på {dato}. Vælg hvilken vagt der skal overskrives:\n")
    for index, entry in enumerate(entries, start=1):
        _, løn_info = next(iter(entry.items()))
        print(Fore.WHITE + _format_overwrite_entry(index, dato, løn_info))
    print(Fore.RED + "\n(0) Annuller" + Style.RESET_ALL)

    valid_choices = {str(index) for index in range(1, len(entries) + 1)}
    while True:
        choice = input(Fore.WHITE + "\nVælg vagt: " + Style.RESET_ALL).strip()
        if choice == "0":
            return None
        if choice in valid_choices:
            return entries[int(choice) - 1]
        ft.error_message(
            sti="Hovedmenu > Vagter > Tilføj vagt > Gem",
            besked="Vælg en konkret vagt fra listen.",
            ugyldigt_valg=False,
            get_input=True,
        )


def save_shift(hours, rate, pause=0, start_time=None, end_time=None, entry_date=None):
    try:
        if entry_date is None:
            nu = datetime.now()
            entry_date = nu.date()
            if nu.time().hour < 4:
                entry_date = entry_date - timedelta(days=1)
        elif isinstance(entry_date, datetime):
            entry_date = entry_date.date()

        dato = entry_date.strftime("%d-%m-%Y")
        gemt_data = ft.load_data()
        eksisterende = [entry for entry in gemt_data if dato in entry]
        if any(ft.is_day_off(entry[dato]) for entry in eksisterende):
            ft.error_message(
                sti="Hovedmenu > Vagter > Tilføj vagt > Gem",
                besked=f"{dato} er markeret som fridag. Fjern fridagen før du indberetter en vagt på datoen.",
                ugyldigt_valg=False,
                get_input=True,
            )
            return False, None

        shift_info = {
            "timer": hours,
            "timeløn": rate
        }
        normalized_start = ft.normalize_clock_text(start_time)
        normalized_end = ft.normalize_clock_text(end_time)
        if normalized_start and normalized_end:
            shift_info["start"] = normalized_start
            shift_info["slut"] = normalized_end

        pause_hours = max(0, pause / 60)
        if pause_hours > 0:
            shift_info["pause"] = pause_hours

        data = {dato: shift_info}

        if eksisterende:
            ft.header("Hovedmenu > Vagter > Tilføj vagt > Gem")
            choice = input(
                Fore.YELLOW
                + f"{dato} findes allerede i databasen.\n"
                + "(o) Overskriv vagt\n"
                + "(t) Tilføj ny vagt\n"
                + "(a) Annuller\n\nVælg: "
                + Style.RESET_ALL
            ).strip().lower()

            if choice == "o":
                selected_entry = _choose_entry_to_overwrite(dato, eksisterende)
                if selected_entry is None:
                    return False, None

                _, selected_info = next(iter(selected_entry.items()))
                shift_info[ft.ENTRY_ID_KEY] = ft.get_entry_id(selected_info) or ft.new_entry_id()
                if isinstance(selected_info, dict) and selected_info.get(ft.ENTRY_CREATED_KEY):
                    shift_info[ft.ENTRY_CREATED_KEY] = selected_info.get(ft.ENTRY_CREATED_KEY)
                ft.save_data({dato: shift_info})
            elif choice == "t":
                ft.save_data(data)
            else:
                return False, None
        else:
            ft.save_data(data)
        return True, dato

    except Exception as e:
        ft.error_message(
            sti="Hovedmenu > Vagter > Tilføj vagt > Gem",
            besked=f"UKENDT FEJL:\n\n{e}",
            ugyldigt_valg=False,
            get_input=True
        )
        return False, None


def main():
    hours = None
    rate = None
    pause = 0
    start_time = None
    end_time = None
    while True:
        ft.header("Hovedmenu > Vagter > Tilføj vagt")
        shift_entry_header(hours, rate, pause)
        
        print(Fore.LIGHTBLACK_EX + "──────────────────────" + Fore.LIGHTBLUE_EX)
        print("(1) Timer")
        print("(2) Timeløn")
        print("(3) Pause" + Fore.GREEN)
        print("\n(4) Gem vagt" + Fore.YELLOW)
        print("\n(0) Tilbage")
        print(Fore.LIGHTBLACK_EX + "──────────────────────")
        choice_main = input(Fore.WHITE + "\n\nVælg: " + Style.RESET_ALL).strip().lower()

        if choice_main not in ["1", "2", "3", "4", "0"]:
            ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt", besked=None, ugyldigt_valg=True, sov=False, get_input=True)
            continue

        elif choice_main == "1":
            while True:
                ft.header("Hovedmenu > Vagter > Tilføj vagt > Timer")
                shift_entry_header(hours, rate, pause)
                hours_str = input(Fore.WHITE + "Timer eller starttid (fx 5.25 eller 14:00, 0 for at afslutte): ").strip().lower()

                if hours_str == "0":
                    break

                if ":" in hours_str:
                    start_minutes = _parse_clock_minutes(hours_str)
                    if start_minutes is None:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Starttidspunkt skal skrives som HH:MM, fx 14:00.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue

                    end_str = input(Fore.WHITE + "Sluttidspunkt (fx 19:15, 0 for at afslutte): ").strip().lower()
                    if end_str == "0":
                        break

                    calculated_hours = _calculate_hours_from_times(hours_str, end_str)
                    if calculated_hours is None:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Sluttidspunkt skal skrives som HH:MM, fx 19:15.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue
                    if calculated_hours <= 0:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Sluttidspunkt skal være efter starttidspunkt.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue

                    hours = calculated_hours
                    start_time = ft.normalize_clock_text(hours_str)
                    end_time = ft.normalize_clock_text(end_str)
                    break

                try:
                    parsed_hours = _parse_number(hours_str)
                    if parsed_hours <= 0:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Antal timer skal være over 0.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue
                    hours = parsed_hours
                    start_time = None
                    end_time = None
                    break
                except ValueError:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Antal timer skal være et tal eller et klokkeslæt.", ugyldigt_valg=False, sov=False, get_input=True)

        elif choice_main == "2":
            while True:
                ft.header("Hovedmenu > Vagter > Tilføj vagt > Timeløn")
                shift_entry_header(hours, rate, pause)
                rate_str = input(Fore.WHITE + "Timeløn (0 for at afslutte): ").strip().lower()

                if rate_str == "0":
                    break

                try:
                    parsed_rate = _parse_number(rate_str)
                    if parsed_rate <= 0:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timeløn", besked="Timeløn skal være over 0.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue
                    rate = parsed_rate
                    break
                except ValueError:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timeløn", besked="Timeløn skal være et tal.", ugyldigt_valg=False, sov=False, get_input=True)

        elif choice_main == "3":
            while True:
                ft.header("Hovedmenu > Vagter > Tilføj vagt > Pause")
                shift_entry_header(hours, rate, pause)
                pause_str = input(Fore.WHITE + "Pause i minutter (0 for ingen pause): ").strip().lower()

                try:
                    parsed_pause = _parse_number(pause_str)
                    if parsed_pause < 0:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Pause", besked="Pause må ikke være under 0.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue
                    pause = parsed_pause
                    break
                except ValueError:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Pause", besked="Pause skal være et tal.", ugyldigt_valg=False, sov=False, get_input=True)
        
        elif choice_main == "4":
            if hours is None or rate is None:
                ft.error_message(
                    sti="Hovedmenu > Vagter > Tilføj vagt > Gem",
                    besked="Venligst indstil antal timer og timeløn.",
                    ugyldigt_valg=False,
                    get_input=True
                )
                continue
            paid_hours = hours - (pause / 60)
            if paid_hours <= 0:
                ft.error_message(
                    sti="Hovedmenu > Vagter > Tilføj vagt > Gem",
                    besked="Pause må ikke være lige så lang som eller længere end vagten.",
                    ugyldigt_valg=False,
                    get_input=True
                )
                continue
            success, dato = save_shift(hours, rate, pause, start_time=start_time, end_time=end_time)
            if success:
                ft.header("Hovedmenu > Vagter > Tilføj vagt > Gem")
                brutto = paid_hours * rate
                netto = ft.calculate_netto_salary_from_brutto(brutto)
                print(Fore.GREEN + f"Data gemt:\n\n- Dato: {dato}\n- Timer før pause: {hours}\n- Pause: {pause} min\n- Betalte timer: {paid_hours}\n- Timeløn: {rate}\n\n= Brutto indtjening: {brutto:.1f} kr\n= Netto indtjening: {netto:.1f} kr")
                input(Fore.WHITE + "\n\nTryk enter for at fortsætte...")
                return
            
        elif choice_main == "0":
             return

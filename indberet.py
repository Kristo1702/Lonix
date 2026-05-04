import re
from datetime import datetime, timedelta

import functions as ft
from colorama import init, Fore, Style

init()


TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def _parse_number(value):
    return float(value.replace(",", "."))


def _parse_clock_minutes(value):
    match = TIME_PATTERN.fullmatch(value.strip())
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    return (hours * 60) + minutes


def _calculate_hours_from_times(start_str, end_str):
    start_minutes = _parse_clock_minutes(start_str)
    end_minutes = _parse_clock_minutes(end_str)
    if start_minutes is None or end_minutes is None:
        return None

    if end_minutes < start_minutes:
        end_minutes += 24 * 60

    return (end_minutes - start_minutes) / 60

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

def save_shift(hours, rate, pause=0):
    try:
        nu = datetime.now()

        dato = nu.date()
        tid = nu.time()

        if tid.hour < 4:
            dato = dato - timedelta(days=1)

        dato = dato.strftime("%d-%m-%Y")

        gemt_data = ft.load_data()
        findes_allerede = any(dato in entry for entry in gemt_data)

        if findes_allerede:
            ft.header("Hovedmenu > Vagter > Tilføj vagt > Gem")
            overwrite = input(
                Fore.YELLOW + f"Du har allerede data for denne dato: {dato}.\nØnsker du at overskrive dataen? (j/n): ").strip().lower()

            if overwrite != "j":
                return False, None

        shift_info = {
            "timer": hours,
            "timeløn": rate
        }
        pause_hours = max(0, pause / 60)
        if pause_hours > 0:
            shift_info["pause"] = pause_hours

        data = {dato: shift_info}

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
                    break

                try:
                    parsed_hours = _parse_number(hours_str)
                    if parsed_hours <= 0:
                        ft.error_message(sti="Hovedmenu > Vagter > Tilføj vagt > Timer", besked="Antal timer skal være over 0.", ugyldigt_valg=False, sov=False, get_input=True)
                        continue
                    hours = parsed_hours
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
            success, dato = save_shift(hours, rate, pause)
            if success:
                ft.header("Hovedmenu > Vagter > Tilføj vagt > Gem")
                brutto = paid_hours * rate
                netto = ft.calculate_netto_salary_from_brutto(brutto)
                print(Fore.GREEN + f"Data gemt:\n\n- Dato: {dato}\n- Timer før pause: {hours}\n- Pause: {pause} min\n- Betalte timer: {paid_hours}\n- Timeløn: {rate}\n\n= Brutto indtjening: {brutto:.1f} kr\n= Netto indtjening: {netto:.1f} kr")
                input(Fore.WHITE + "\n\nTryk enter for at fortsætte...")
                return
            
        elif choice_main == "0":
             return

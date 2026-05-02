import functions as ft
from colorama import init, Fore, Style
from datetime import datetime
init()

MONTH_NAMES = {
    1: "Januar",
    2: "Februar",
    3: "Marts",
    4: "April",
    5: "Maj",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "December",
}

def _format_timer(timer):
    return f"{timer:.2f}".rstrip("0").rstrip(".")

def _get_udbetaling_titel(udbetaling):
    periode_slut = udbetaling.get("periode_slut")
    måned = MONTH_NAMES.get(periode_slut.month, str(periode_slut.month))
    return f"{måned} {periode_slut.year}"

def build_menu(udbetalinger):
    print(Fore.LIGHTBLACK_EX + "─────────────────────────────────────────────" + Fore.LIGHTBLUE_EX)
    for index, udbetaling in enumerate(udbetalinger, start=1):
        titel = _get_udbetaling_titel(udbetaling)
        print(f"({index}) {titel}")
    print(Fore.RED + "\n(0) Tilbage")
    print(Fore.LIGHTBLACK_EX + "─────────────────────────────────────────────" + Style.RESET_ALL)

def build_udbetaling_overview(settings, udbetaling):
    periode_start = udbetaling.get("periode_start")
    periode_slut = udbetaling.get("periode_slut")
    timer = udbetaling.get("timer", 0)
    brutto = udbetaling.get("brutto", 0)
    netto_løn = udbetaling.get("netto", 0)
    su = settings.get("su", 0)
    boligstøtte = settings.get("boligstøtte", 0)
    total_udbetalt = netto_løn + su + boligstøtte
    titel = _get_udbetaling_titel(udbetaling)

    print(Fore.LIGHTBLACK_EX + "───────────────────────────────────────")
    print(Fore.WHITE + f"\n  {titel}")
    print(Fore.WHITE + "\n  ===== LØN =====")
    print(Fore.LIGHTBLACK_EX + f"  Periode: {periode_start.strftime('%d-%m-%Y')} - {periode_slut.strftime('%d-%m-%Y')}")
    if timer > 0:
        timeløn = brutto / timer
        print(Fore.BLUE + f"  Timer: {_format_timer(timer)} á {timeløn:.0f} kr.")
    else:
        print(Fore.YELLOW + "  Ingen timer registreret")
    print(Fore.BLUE + f"  Brutto løn: {brutto:.0f} kr.")
    print(Fore.LIGHTGREEN_EX + f"  • Netto løn: {netto_løn:.0f} kr.")

    print(Fore.WHITE + "\n  ===== ANDEN INDKOMST =====")
    print(Fore.LIGHTGREEN_EX + f"  • SU: {su:.0f} kr.")
    print(Fore.LIGHTGREEN_EX + f"  • Boligstøtte: {boligstøtte:.0f} kr.")

    print(Fore.WHITE + "\n  ===== TOTAL =====")
    print(Fore.GREEN + f"  • Total udbetalt: {total_udbetalt:.0f} kr.")
    print(Fore.LIGHTBLACK_EX + "\n───────────────────────────────────────" + Style.RESET_ALL)

def main():
    ft.header("Hovedmenu > udbetalinger")

    settings = ft.load_settings()
    data = ft.load_data()
    required_keys = ["skat", "fradrag", "am bidrag", "su", "boligstøtte", "løn start", "løn slut"]
    if not all(key in settings for key in required_keys):
        ft.error_message(
            sti="Hovedmenu > udbetalinger",
            besked="Forkerte indstillinger: nøgle(r) mangler",
            ugyldigt_valg=False,
            get_input=True
        )
        return None
    
    if not data:
        ft.error_message(
            sti="Hovedmenu > udbetalinger",
            besked="Din data er tom. Venligst indberet dagsløn først.",
            ugyldigt_valg=False,
            get_input=True
        )
        return None

    try:
        udbetalinger = ft.calculate_all_netto_salaries()
    except Exception as error:
        ft.error_message(
            sti="Hovedmenu > udbetalinger",
            besked=f"Kunne ikke beregne udbetalinger:\n\n{error}",
            ugyldigt_valg=False,
            get_input=True
        )
        return

    i_dag = datetime.now().date()
    igangværende_start, igangværende_slut = ft.get_salary_period_for_date(
        i_dag,
        settings.get("løn start"),
        settings.get("løn slut")
    )
    udbetalinger = [
        udbetaling for udbetaling in udbetalinger
        if not (
            udbetaling.get("periode_start") == igangværende_start
            and udbetaling.get("periode_slut") == igangværende_slut
        )
    ]

    if not udbetalinger:
        ft.error_message(
            sti="Hovedmenu > udbetalinger",
            besked="Ingen afsluttede udbetalinger fundet.",
            ugyldigt_valg=False,
            get_input=True
        )
        return

    while True:
        ft.header("Hovedmenu > udbetalinger")
        build_menu(udbetalinger)

        gyldige_valg = [str(i) for i in range(1, len(udbetalinger) + 1)] + ["0"]
        choice = input(Fore.WHITE + "\n\nVælg: " + Style.RESET_ALL).strip().lower()
        if choice not in gyldige_valg:
            ft.error_message(sti="Hovedmenu > udbetalinger", besked=None, ugyldigt_valg=True, get_input=True)
            continue

        if choice == "0":
            return

        valgt_udbetaling = udbetalinger[int(choice) - 1]
        titel = _get_udbetaling_titel(valgt_udbetaling)

        ft.header(f"Hovedmenu > udbetalinger > {titel}")
        build_udbetaling_overview(settings, valgt_udbetaling)
        input("\n\nTryk enter for at gå tilbage...")
    

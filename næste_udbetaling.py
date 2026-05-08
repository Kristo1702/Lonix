from colorama import Fore, Style, init

import functions as ft

init()


def _format_hours(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def build_overview(settings, netto_løn, brutto_løn, timer, forecast=None, rådighed=False):
    anden_indkomst = ft.get_other_income(settings)
    faste_udgifter = ft.calculate_budget_expenses(settings)
    lønperiode = ft.get_pay_period_description(settings)

    total_netto = anden_indkomst + netto_løn
    til_rådighed = ft.calculate_disposable_income(total_netto, settings)

    estimeret_total = None
    estimeret_til_rådighed = None
    if forecast and forecast.get("estimated_total_income") is not None:
        estimeret_total = forecast["estimated_total_income"]
        estimeret_til_rådighed = forecast.get("estimated_disposable_income")

    separator = ft.ui_line(42)
    print(Fore.LIGHTBLACK_EX + separator)

    print(Fore.WHITE + "\n  ===== ANDEN INDKOMST =====")
    print(Fore.LIGHTGREEN_EX + f"  - Anden indkomst (netto): {anden_indkomst:.0f} kr.")

    print(Fore.WHITE + "\n  ===== LØN =====")
    print(Fore.LIGHTBLACK_EX + f"  OBS: Lønperiode: {lønperiode}")
    if timer > 0:
        timeløn = brutto_løn / timer
        print(Fore.BLUE + f"  Registreret nu: {_format_hours(timer)} t. á {timeløn:.0f} kr.")
        print(Fore.BLUE + f"  Brutto løn nu: {brutto_løn:.0f} kr.")
        print(Fore.LIGHTGREEN_EX + f"  - Netto løn nu: {netto_løn:.0f} kr.")
    else:
        print(Fore.YELLOW + "  Ingen timer registreret endnu")

    print(Fore.WHITE + "\n  ===== ESTIMAT =====")
    if forecast and forecast.get("estimated_brutto") is not None and forecast.get("estimated_netto") is not None:
        print(Fore.LIGHTBLACK_EX + f"  Forløb: {forecast['elapsed_days']} / {forecast['total_days']} dage")
        print(Fore.BLUE + f"  Timer ved periodens slut: {_format_hours(forecast['estimated_hours'])}")
        print(Fore.BLUE + f"  Estimeret brutto løn: {forecast['estimated_brutto']:.0f} kr.")
        print(Fore.LIGHTGREEN_EX + f"  - Estimeret netto løn: {forecast['estimated_netto']:.0f} kr.")
    else:
        print(Fore.YELLOW + "  Ingen prognose endnu")

    print(Fore.WHITE + "\n  ===== TOTAL =====")
    print(Fore.GREEN + f"  - Total udbetalt nu: {total_netto:.0f} kr.")
    if estimeret_total is not None:
        print(Fore.GREEN + f"  - Estimeret total udbetalt: {estimeret_total:.0f} kr.")
    if rådighed:
        print(Fore.LIGHTBLACK_EX + f"  Budgetterede faste udgifter: {faste_udgifter:.0f} kr.")
        print(Fore.GREEN + f"  - Rådighedsbeløb nu: {til_rådighed:.0f} kr.")
        if estimeret_til_rådighed is not None:
            print(Fore.GREEN + f"  - Estimeret rådighedsbeløb: {estimeret_til_rådighed:.0f} kr.")
    print(Fore.LIGHTBLACK_EX + "\n" + separator + Style.RESET_ALL)


def main():
    ft.header("Hovedmenu > Næste udbetaling")

    settings = ft.load_settings()
    required_keys = ft.REQUIRED_SETTINGS_KEYS
    if not all(key in settings for key in required_keys):
        ft.error_message(
            sti="Hovedmenu > Næste udbetaling",
            besked="Forkerte indstillinger: nøgle(r) mangler",
            ugyldigt_valg=False,
            get_input=True,
        )
        return None

    try:
        brutto, netto, timer = ft.calculate_netto_salary()
        forecast = ft.calculate_salary_forecast(settings=settings)
    except Exception as error:
        ft.error_message(
            sti="Hovedmenu > Næste udbetaling",
            besked=f"Kunne ikke beregne netto løn:\n\n{error}",
            ugyldigt_valg=False,
            get_input=True,
        )
        return

    build_overview(settings, netto, brutto, timer, forecast, False)
    choice = input("\n\nTryk enter for at gå tilbage...")
    if choice == "full":
        ft.header("Hovedmenu > Næste udbetaling")
        build_overview(settings, netto, brutto, timer, forecast, True)
        input("\n\nTryk enter for at gå tilbage...")

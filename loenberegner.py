from colorama import Fore, Style, init

import functions as ft

init()

AM_BIDRAG = 0.08


def _format_number(value, decimals=2):
    if decimals <= 0:
        return f"{value:.0f}"
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def _format_money(value):
    return f"{_format_number(value)} kr"


def _parse_number(value):
    return float(value.replace(",", "."))


def _read_positive_number(path, label):
    while True:
        value_str = input(Fore.WHITE + f"{label} (0 for at gå tilbage): " + Style.RESET_ALL).strip()

        if value_str == "0":
            return None

        try:
            value = _parse_number(value_str)
        except ValueError:
            ft.error_message(
                sti=path,
                besked=f"{label} skal være et tal.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        if value <= 0:
            ft.error_message(
                sti=path,
                besked=f"{label} skal være over 0.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        return value


def _read_non_negative_number(path, label):
    while True:
        value_str = input(Fore.WHITE + f"{label}: " + Style.RESET_ALL).strip()

        try:
            value = _parse_number(value_str)
        except ValueError:
            ft.error_message(
                sti=path,
                besked=f"{label} skal være et tal.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        if value < 0:
            ft.error_message(
                sti=path,
                besked=f"{label} må ikke være under 0.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        return value


def _read_tax_rate(path):
    while True:
        value_str = input(Fore.WHITE + "Skatteprocent (fx 39 eller 0.39): " + Style.RESET_ALL).strip()

        try:
            value = _parse_number(value_str)
        except ValueError:
            ft.error_message(
                sti=path,
                besked="Skatteprocent skal være et tal.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        if value < 0:
            ft.error_message(
                sti=path,
                besked="Skatteprocent må ikke være under 0.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        tax_rate = value / 100 if value >= 1 else value
        if tax_rate > 1:
            ft.error_message(
                sti=path,
                besked="Skatteprocent må ikke være over 100.",
                ugyldigt_valg=False,
                get_input=True,
            )
            continue

        return tax_rate


def _print_result(path, breakdown, tax_rate, pension_rate=0, extra_lines=None):
    ft.header(path)
    separator = ft.ui_line(36)
    extra_lines = extra_lines or []

    print(Fore.LIGHTBLACK_EX + separator)
    for line in extra_lines:
        print(Fore.BLUE + f"  {line}")

    print(Fore.WHITE + "\n  ===== BEREGNING =====")
    print(Fore.BLUE + f"  Brutto løn: {_format_money(breakdown['brutto'])}")
    if pension_rate > 0:
        print(Fore.BLUE + f"  Pension ({_format_number(pension_rate * 100)}%): -{_format_money(breakdown['pension'])}")
    print(Fore.BLUE + f"  AM-bidrag ({_format_number(AM_BIDRAG * 100)}%): -{_format_money(breakdown['am_bidrag'])}")
    print(Fore.BLUE + f"  Efter AM-bidrag: {_format_money(breakdown['efter_am'])}")
    print(Fore.BLUE + f"  Fradrag: {_format_money(breakdown['fradrag'])}")
    print(Fore.BLUE + f"  Skattegrundlag: {_format_money(breakdown['skattegrundlag'])}")
    print(Fore.BLUE + f"  Skat ({_format_number(tax_rate * 100)}%): -{_format_money(breakdown['skat'])}")

    print(Fore.WHITE + "\n  ===== RESULTAT =====")
    print(Fore.GREEN + f"  Netto løn: {_format_money(breakdown['netto'])}")
    print(Fore.LIGHTBLACK_EX + "\n" + separator + Style.RESET_ALL)
    input(Fore.WHITE + "\n\nTryk enter for at gå tilbage..." + Style.RESET_ALL)


def _calculate_from_brutto():
    path = "Hovedmenu > Lønberegner > Bruttoløn"
    ft.header(path)

    brutto = _read_positive_number(path, "Bruttoløn i kr")
    if brutto is None:
        return

    _calculate_with_brutto(path, brutto)


def _calculate_from_hours():
    path = "Hovedmenu > Lønberegner > Timer"
    ft.header(path)

    hours = _read_positive_number(path, "Timer")
    if hours is None:
        return

    rate = _read_positive_number(path, "Timeløn i kr")
    if rate is None:
        return

    brutto = hours * rate
    _calculate_with_brutto(
        path,
        brutto,
        [
            f"Timer: {_format_number(hours)}",
            f"Timeløn: {_format_money(rate)}",
        ],
    )


def _calculate_with_brutto(path, brutto, extra_lines=None):
    fradrag = _read_non_negative_number(path, "Fradrag i kr")
    tax_rate = _read_tax_rate(path)
    pension = _read_non_negative_number(path, "Eget pensionsbidrag % (fx 5 eller 0)")
    pension_rate = pension / 100 if pension > 1 else pension
    breakdown = ft.calculate_salary_breakdown(
        brutto,
        tax_rate,
        fradrag,
        AM_BIDRAG,
        settings={ft.PENSION_CONTRIBUTION_KEY: pension_rate},
    )
    _print_result(path, breakdown, tax_rate, pension_rate, extra_lines)


def main():
    while True:
        ft.header("Hovedmenu > Lønberegner")

        separator = ft.ui_line(30)
        print(Fore.LIGHTBLACK_EX + separator + Fore.LIGHTBLUE_EX)
        print("(1) Bruttoløn")
        print("(2) Timer + timeløn" + Fore.RED)
        print("\n(0) Tilbage")
        print(Fore.LIGHTBLACK_EX + separator)

        choice = input(Fore.WHITE + "\n\nVælg: " + Style.RESET_ALL).strip().lower()

        if choice not in ["0", "1", "2"]:
            ft.error_message(sti="Hovedmenu > Lønberegner", besked=None, ugyldigt_valg=True, get_input=True)
            continue

        if choice == "0":
            return

        if choice == "1":
            _calculate_from_brutto()

        elif choice == "2":
            _calculate_from_hours()

import re
from datetime import date, datetime

from colorama import Fore, Style, init

import functions as ft

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

REQUIRED_KEYS = ft.REQUIRED_SETTINGS_KEYS
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def main():
    ft.header("Hovedmenu > Statistik")

    settings = ft.load_settings()
    data = ft.load_data()

    if not all(key in settings for key in REQUIRED_KEYS):
        ft.error_message(
            sti="Hovedmenu > Statistik",
            besked="Forkerte indstillinger: nøgle(r) mangler",
            ugyldigt_valg=False,
            get_input=True,
        )
        return

    if not data:
        ft.error_message(
            sti="Hovedmenu > Statistik",
            besked="Din data er tom. Tilføj en vagt først.",
            ugyldigt_valg=False,
            get_input=True,
        )
        return

    try:
        print_stats(data, settings)
    except Exception as error:
        ft.error_message(
            sti="Hovedmenu > Statistik",
            besked=f"Kunne ikke beregne statistik:\n\n{error}",
            ugyldigt_valg=False,
            get_input=True,
        )
        return

    input(Fore.WHITE + "\n\nTryk enter for at gå tilbage..." + Style.RESET_ALL)


def print_stats(data=None, settings=None):
    data = data if data is not None else ft.load_data()
    settings = settings if settings is not None else ft.load_settings()
    if not data:
        return

    statistics = _build_statistics(data, settings)

    hours_per_shift, hours_per_period, hours_per_year = calculate_average_hours(data)
    salary_per_shift, salary_per_period, salary_per_year = calculate_average_salary_before_tax(data)
    salary_after_shift, salary_after_period, salary_after_year = statistics["averages"]["salary_after_tax"]

    print(Fore.LIGHTBLACK_EX + "  Beløb vises som før skat / efter skat." + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "  Rød N/A betyder, at der ikke er nok data til en retvisende beregning." + Style.RESET_ALL)

    _print_table(
        "Gennemsnit",
        ["Måling", "Vagt", "Lønperiode", "År"],
        [
            [
                "Timer",
                _format_optional(hours_per_shift, _format_number),
                _format_optional(hours_per_period, _format_number),
                _format_optional(hours_per_year, _format_number),
            ],
            [
                "Løn før skat",
                _format_optional(salary_per_shift, _format_money),
                _format_optional(salary_per_period, _format_money),
                _format_optional(salary_per_year, _format_money),
            ],
            [
                "Løn efter skat",
                _format_optional(salary_after_shift, _format_money),
                _format_optional(salary_after_period, _format_money),
                _format_optional(salary_after_year, _format_money),
            ],
        ],
        right_align={1, 2, 3},
    )

    _print_table(
        "Vagter",
        ["Måling", "Værdi"],
        [
            ["Timer i alt", _format_number(statistics["totals"]["timer"])],
            ["Pause i alt", f"{_format_number(statistics['totals'].get('pause', 0) * 60)} min."],
            ["Fridage i alt", statistics["day_off_counts"]["total"]],
            ["Løn i alt", _format_money_pair(statistics["totals"]["brutto"], statistics["totals"]["netto"])],
        ],
        right_align={1},
    )

    _print_table(
        "Vagtantal",
        ["Måling", "Værdi"],
        [
            ["Vagter i alt", statistics["shift_counts"]["total"]],
            ["Vagter i år", statistics["shift_counts"]["year"]],
            ["Nuværende lønperiode", statistics["current_period_label"]],
            ["Vagter i nuværende lønperiode", statistics["shift_counts"]["current_period"]],
            ["Fridage i nuværende lønperiode", statistics["day_off_counts"]["current_period"]],
            ["Vagter pr. lønperiode i snit", _format_optional(statistics["shift_counts"]["per_period"], _format_number)],
            ["Fridage pr. lønperiode i snit", _format_optional(statistics["day_off_counts"]["per_period"], _format_number)],
        ],
        right_align={1},
    )

    _print_table(
        "Rekorder",
        ["Kategori", "Dato", "Timer", "Pause", "Før skat", "Efter skat"],
        [
            _shift_row("Længste vagt", statistics["records"]["longest"]),
            _shift_row("Korteste vagt", statistics["records"]["shortest"]),
            _shift_row("Mest indbringende / højeste dag", statistics["records"]["highest_paid"]),
        ],
        right_align={2, 3, 4, 5},
    )

    _print_table(
        "Bedste lønperioder",
        ["Måling", "Periode", "Timer", "Pause", "Før skat", "Efter skat"],
        [
            _period_row("Timer", statistics["periods"]["best_timer"]),
            _period_row("Brutto", statistics["periods"]["best_brutto"]),
            _period_row("Netto", statistics["periods"]["best_netto"]),
        ],
        right_align={2, 3, 4, 5},
    )

    _print_table(
        "Dårligste lønperioder",
        ["Måling", "Periode", "Timer", "Pause", "Før skat", "Efter skat"],
        [
            _period_row("Timer", statistics["periods"]["worst_timer"]),
            _period_row("Brutto", statistics["periods"]["worst_brutto"]),
            _period_row("Netto", statistics["periods"]["worst_netto"]),
        ],
        right_align={2, 3, 4, 5},
    )

    if statistics["development"] is None:
        _print_table(
            "Udvikling",
            ["Måling", "Seneste", "Forrige", "Ændring", "Pct."],
            [
                ["Timer", _na(), _na(), _na(), _na()],
                ["Løn før skat", _na(), _na(), _na(), _na()],
                ["Løn efter skat", _na(), _na(), _na(), _na()],
            ],
            right_align={1, 2, 3, 4},
        )
    else:
        development = statistics["development"]
        print(
            Fore.LIGHTBLACK_EX
            + f"\n  { _format_period_title(development['latest']) } mod { _format_period_title(development['previous']) }"
            + Style.RESET_ALL
        )
        _print_table(
            "Udvikling",
            ["Måling", "Seneste", "Forrige", "Ændring", "Pct."],
            [
                [
                    "Timer",
                    _format_number(development["latest"]["timer"]),
                    _format_number(development["previous"]["timer"]),
                    _format_signed_number(development["timer_delta"]),
                    _format_percent(development["timer_percent"]),
                ],
                [
                    "Løn før skat",
                    _format_money(development["latest"]["brutto"]),
                    _format_money(development["previous"]["brutto"]),
                    _format_signed_money(development["brutto_delta"]),
                    _format_percent(development["brutto_percent"]),
                ],
                [
                    "Løn efter skat",
                    _format_money(development["latest"]["netto"]),
                    _format_money(development["previous"]["netto"]),
                    _format_signed_money(development["netto_delta"]),
                    _format_percent(development["netto_percent"]),
                ],
            ],
            right_align={1, 2, 3, 4},
        )

    average_gap = statistics["patterns"]["average_gap"]
    streak = statistics["patterns"]["longest_streak"]
    _print_table(
        "Arbejdsmønster",
        ["Måling", "Værdi"],
        [
            ["Gennemsnitlige dage mellem vagter", _format_optional(average_gap, _format_number)],
            ["Længste streak", _format_streak(streak)],
        ],
    )

    _print_table(
        "Fradrag",
        ["Måling", "Beløb"],
        [
            ["Samlet AM-bidrag", _format_money(statistics["deductions"]["am_bidrag"])],
            ["Samlet skat", _format_money(statistics["deductions"]["skat"])],
            ["Samlet trukket i alt", _format_money(statistics["deductions"]["am_bidrag"] + statistics["deductions"]["skat"])],
        ],
        right_align={1},
    )

    _print_table(
        "Prognose",
        ["Måling", "Værdi"],
        [
            [
                "Forløb i nuværende lønperiode",
                f"{statistics['forecast']['elapsed_days']} / {statistics['forecast']['total_days']} dage",
            ],
            [
                "Registreret indtil nu",
                _format_money_pair(statistics["forecast"]["current_brutto"], statistics["forecast"]["current_netto"]),
            ],
            ["Registrerede timer indtil nu", _format_number(statistics["forecast"]["current_hours"])],
            ["Estimerede timer ved periodens slut", _format_optional(statistics["forecast"]["estimated_hours"], _format_number)],
            ["Estimeret løn ved periodens slut", _format_money_pair_optional(statistics["forecast"]["estimated_brutto"], statistics["forecast"]["estimated_netto"])],
            [
                "Estimeret total inkl. anden indkomst",
                _format_optional(statistics["forecast"]["estimated_total_income"], _format_money),
            ],
            [
                "Budgetterede faste udgifter",
                _format_money(statistics["forecast"]["budget_expenses"]),
            ],
            [
                "Estimeret rådighedsbeløb",
                _format_optional(statistics["forecast"]["estimated_disposable_income"], _format_money),
            ],
        ],
        right_align={1},
    )


def calculate_average_hours(data):
    settings = ft.load_settings()
    shifts, _, complete_periods, _, complete_years = _build_dataset_context(data, settings)
    work_shifts = _work_shifts(shifts)
    return _calculate_average_hours_from_groups(work_shifts, complete_periods, complete_years)


def calculate_average_salary_before_tax(data):
    settings = ft.load_settings()
    shifts, _, complete_periods, _, complete_years = _build_dataset_context(data, settings)
    work_shifts = _work_shifts(shifts)
    return _calculate_average_salary_before_tax_from_groups(work_shifts, complete_periods, complete_years)


def _build_statistics(data, settings):
    shifts, periods, complete_periods, _, complete_years = _build_dataset_context(data, settings)
    work_shifts = _work_shifts(shifts)
    day_offs = _day_offs(shifts)

    hours_average = _calculate_average_hours_from_groups(work_shifts, complete_periods, complete_years)
    salary_before_average = _calculate_average_salary_before_tax_from_groups(work_shifts, complete_periods, complete_years)
    salary_after_average = _calculate_average_salary_after_tax_from_groups(work_shifts, complete_periods, complete_years)

    current_period_start, current_period_end = ft.get_salary_period_for_date(
        datetime.now().date(),
        settings.get("løn start"),
        settings.get("løn slut"),
    )

    totals = {
        "timer": sum(shift["timer"] for shift in work_shifts),
        "pause": sum(shift["pause"] for shift in work_shifts),
        "brutto": sum(shift["brutto"] for shift in work_shifts),
        "netto": sum(period["netto"] for period in periods),
        "fridage": len(day_offs),
        "registreringer": len(shifts),
    }

    shift_counts = {
        "total": len(work_shifts),
        "year": sum(1 for shift in work_shifts if shift["dato"].year == datetime.now().year),
        "current_period": sum(1 for shift in work_shifts if current_period_start <= shift["dato"] <= current_period_end),
        "per_period": _average_or_none([period["vagter"] for period in complete_periods]),
    }

    day_off_counts = {
        "total": len(day_offs),
        "year": sum(1 for shift in day_offs if shift["dato"].year == datetime.now().year),
        "current_period": sum(1 for shift in day_offs if current_period_start <= shift["dato"] <= current_period_end),
        "per_period": _average_or_none([period.get("fridage", 0) for period in complete_periods]),
    }

    records = {
        "longest": max(work_shifts, key=lambda shift: (shift["timer"], shift["brutto"], shift["dato"])) if work_shifts else None,
        "shortest": min(work_shifts, key=lambda shift: (shift["timer"], shift["brutto"], shift["dato"])) if work_shifts else None,
        "highest_paid": max(work_shifts, key=lambda shift: (shift["brutto"], shift["timer"], shift["dato"])) if work_shifts else None,
    }

    periods_statistics = {
        "best_timer": None,
        "worst_timer": None,
        "best_brutto": None,
        "worst_brutto": None,
        "best_netto": None,
        "worst_netto": None,
    }
    if complete_periods:
        periods_statistics = {
            "best_timer": max(complete_periods, key=lambda period: (period["timer"], period["brutto"], period["periode_slut"])),
            "worst_timer": min(complete_periods, key=lambda period: (period["timer"], period["brutto"], period["periode_slut"])),
            "best_brutto": max(complete_periods, key=lambda period: (period["brutto"], period["netto"], period["periode_slut"])),
            "worst_brutto": min(complete_periods, key=lambda period: (period["brutto"], period["netto"], period["periode_slut"])),
            "best_netto": max(complete_periods, key=lambda period: (period["netto"], period["brutto"], period["periode_slut"])),
            "worst_netto": min(complete_periods, key=lambda period: (period["netto"], period["brutto"], period["periode_slut"])),
        }

    development = None
    if len(complete_periods) >= 2:
        latest = complete_periods[-1]
        previous = complete_periods[-2]
        development = {
            "latest": latest,
            "previous": previous,
            "timer_delta": latest["timer"] - previous["timer"],
            "timer_percent": _percentage_change(latest["timer"], previous["timer"]),
            "brutto_delta": latest["brutto"] - previous["brutto"],
            "brutto_percent": _percentage_change(latest["brutto"], previous["brutto"]),
            "netto_delta": latest["netto"] - previous["netto"],
            "netto_percent": _percentage_change(latest["netto"], previous["netto"]),
        }

    deductions = {
        "am_bidrag": sum(period["am_bidrag"] for period in periods),
        "skat": sum(period["skat"] for period in periods),
    }

    forecast = ft.calculate_salary_forecast(data, settings)

    return {
        "averages": {
            "hours": hours_average,
            "salary_before_tax": salary_before_average,
            "salary_after_tax": salary_after_average,
        },
        "totals": totals,
        "shift_counts": shift_counts,
        "day_off_counts": day_off_counts,
        "records": records,
        "periods": periods_statistics,
        "development": development,
        "patterns": {
            "average_gap": _calculate_average_gap(work_shifts),
            "longest_streak": _calculate_longest_streak(work_shifts),
        },
        "deductions": deductions,
        "forecast": forecast,
        "current_period_label": f"{current_period_start.strftime('%d-%m-%Y')} - {current_period_end.strftime('%d-%m-%Y')}",
    }


def _parse_shifts(data):
    shifts = []
    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato = datetime.strptime(dato_str, "%d-%m-%Y").date()
        is_day_off = ft.is_day_off(løn_info)
        varighed = ft.get_shift_duration_hours(løn_info)
        pause = ft.get_shift_pause_hours(løn_info)
        timer = ft.get_shift_paid_hours(løn_info)
        timeløn = float(løn_info.get("timeløn", 0))

        shifts.append(
            {
                "dato": dato,
                "varighed": varighed,
                "timer": timer,
                "pause": pause,
                "timeløn": timeløn,
                "brutto": timer * timeløn,
                "netto": 0.0,
                "am_bidrag": 0.0,
                "skat": 0.0,
                "is_day_off": is_day_off,
            }
        )

    return sorted(shifts, key=lambda shift: (shift["dato"], shift["brutto"], shift["timer"]))


def _work_shifts(shifts):
    return [shift for shift in shifts if not shift.get("is_day_off")]


def _day_offs(shifts):
    return [shift for shift in shifts if shift.get("is_day_off")]


def _build_dataset_context(data, settings):
    shifts = _parse_shifts(data)
    periods = _group_periods(shifts, settings)
    complete_periods = _get_complete_periods(periods, settings)
    years = _group_years(shifts)
    complete_years = _get_complete_years(years, shifts)
    return shifts, periods, complete_periods, years, complete_years


def _group_periods(shifts, settings):
    periods = {}

    for shift in shifts:
        periode_start, periode_slut = ft.get_salary_period_for_date(
            shift["dato"],
            settings.get("løn start"),
            settings.get("løn slut"),
        )
        period_key = (periode_start, periode_slut)

        if period_key not in periods:
            periods[period_key] = {
                "periode_start": periode_start,
                "periode_slut": periode_slut,
                "varighed": 0.0,
                "timer": 0.0,
                "pause": 0.0,
                "brutto": 0.0,
                "netto": 0.0,
                "am_bidrag": 0.0,
                "efter_am": 0.0,
                "fradrag": 0.0,
                "skattegrundlag": 0.0,
                "skat": 0.0,
                "vagter": 0,
                "fridage": 0,
                "registreringer": 0,
                "shifts": [],
            }

        period = periods[period_key]
        period["varighed"] += shift["varighed"]
        period["timer"] += shift["timer"]
        period["pause"] += shift["pause"]
        period["brutto"] += shift["brutto"]
        period["registreringer"] += 1
        if shift.get("is_day_off"):
            period["fridage"] += 1
        else:
            period["vagter"] += 1
        period["shifts"].append(shift)

    sorted_periods = sorted(periods.values(), key=lambda period: period["periode_start"])
    for period in sorted_periods:
        breakdown = ft.calculate_salary_breakdown_from_brutto(period["brutto"])
        period["netto"] = breakdown["netto"]
        period["am_bidrag"] = breakdown["am_bidrag"]
        period["efter_am"] = breakdown["efter_am"]
        period["fradrag"] = breakdown["fradrag"]
        period["skattegrundlag"] = breakdown["skattegrundlag"]
        period["skat"] = breakdown["skat"]

        if period["brutto"] == 0:
            continue

        for shift in period["shifts"]:
            share = shift["brutto"] / period["brutto"]
            shift["netto"] = period["netto"] * share
            shift["am_bidrag"] = period["am_bidrag"] * share
            shift["skat"] = period["skat"] * share

    return sorted_periods


def _group_years(shifts):
    years = {}

    for shift in shifts:
        year = shift["dato"].year
        if year not in years:
            years[year] = {
                "år": year,
                "varighed": 0.0,
                "timer": 0.0,
                "pause": 0.0,
                "brutto": 0.0,
                "netto": 0.0,
                "vagter": 0,
                "fridage": 0,
                "registreringer": 0,
            }

        years[year]["varighed"] += shift["varighed"]
        years[year]["timer"] += shift["timer"]
        years[year]["pause"] += shift["pause"]
        years[year]["brutto"] += shift["brutto"]
        years[year]["netto"] += shift["netto"]
        years[year]["registreringer"] += 1
        if shift.get("is_day_off"):
            years[year]["fridage"] += 1
        else:
            years[year]["vagter"] += 1

    return sorted(years.values(), key=lambda year: year["år"])


def _get_complete_periods(periods, settings):
    if not periods:
        return []

    current_period_start, _ = ft.get_salary_period_for_date(
        datetime.now().date(),
        settings.get("løn start"),
        settings.get("løn slut"),
    )

    return [
        period
        for period in periods
        if period["periode_slut"] < current_period_start
    ]


def _get_complete_years(years, shifts):
    if not shifts:
        return []

    first_date = shifts[0]["dato"]
    last_date = shifts[-1]["dato"]
    complete_years = []

    for year in years:
        year_number = year["år"]
        year_start = date(year_number, 1, 1)
        year_end = date(year_number, 12, 31)
        if first_date <= year_start and last_date >= year_end:
            complete_years.append(year)

    return complete_years


def _calculate_average_hours_from_groups(shifts, periods, years):
    return (
        _average_or_none([shift["timer"] for shift in shifts]),
        _average_or_none([period["timer"] for period in periods]),
        _average_or_none([year["timer"] for year in years]),
    )


def _calculate_average_salary_before_tax_from_groups(shifts, periods, years):
    return (
        _average_or_none([shift["brutto"] for shift in shifts]),
        _average_or_none([period["brutto"] for period in periods]),
        _average_or_none([year["brutto"] for year in years]),
    )


def _calculate_average_salary_after_tax_from_groups(shifts, periods, years):
    return (
        _average_or_none([shift["netto"] for shift in shifts]),
        _average_or_none([period["netto"] for period in periods]),
        _average_or_none([year["netto"] for year in years]),
    )


def _calculate_average_gap(shifts):
    work_dates = sorted({shift["dato"] for shift in shifts})
    if len(work_dates) < 2:
        return None

    gaps = [(work_dates[index] - work_dates[index - 1]).days for index in range(1, len(work_dates))]
    return _average_or_none(gaps)


def _calculate_longest_streak(shifts):
    work_dates = sorted({shift["dato"] for shift in shifts})
    if not work_dates:
        return {"start": None, "end": None, "length": 0}

    best = {"start": work_dates[0], "end": work_dates[0], "length": 1}
    current_start = work_dates[0]
    current_length = 1

    for index in range(1, len(work_dates)):
        previous_date = work_dates[index - 1]
        current_date = work_dates[index]

        if (current_date - previous_date).days == 1:
            current_length += 1
        else:
            if current_length > best["length"]:
                best = {"start": current_start, "end": previous_date, "length": current_length}
            current_start = current_date
            current_length = 1

    if current_length > best["length"]:
        best = {"start": current_start, "end": work_dates[-1], "length": current_length}

    return best


def _average_or_none(values):
    return (sum(values) / len(values)) if values else None


def _percentage_change(current, previous):
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def _format_number(value, decimals=2):
    if decimals <= 0:
        return f"{value:.0f}"
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def _format_money(value):
    return f"{_format_number(value)} kr"


def _format_money_pair(brutto, netto):
    return f"{_format_money(brutto)} / {_format_money(netto)}"


def _format_money_pair_optional(brutto, netto):
    if brutto is None or netto is None:
        return _na()
    return _format_money_pair(brutto, netto)


def _format_signed_money(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{_format_money(value)}"


def _format_signed_number(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{_format_number(value)}"


def _format_percent(value):
    if value is None:
        return _na()
    prefix = "+" if value > 0 else ""
    return f"{prefix}{_format_number(value)}%"


def _format_period_title(period):
    month_name = MONTH_NAMES.get(period["periode_slut"].month, str(period["periode_slut"].month))
    return f"{month_name} {period['periode_slut'].year}"


def _na():
    return Fore.RED + "N/A" + Fore.WHITE


def _format_optional(value, formatter):
    if value is None:
        return _na()
    return formatter(value)


def _period_label(period):
    start = period["periode_start"].strftime("%d-%m")
    end = period["periode_slut"].strftime("%d-%m")
    return f"{_format_period_title(period)} ({start} - {end})"


def _shift_row(label, shift):
    if shift is None:
        return [label, _na(), _na(), _na(), _na(), _na()]
    return [
        label,
        shift["dato"].strftime("%d-%m-%Y"),
        _format_number(shift["timer"]),
        f"{_format_number(shift.get('pause', 0) * 60)} min.",
        _format_money(shift["brutto"]),
        _format_money(shift["netto"]),
    ]


def _period_row(label, period):
    if period is None:
        return [label, _na(), _na(), _na(), _na(), _na()]
    return [
        label,
        _period_label(period),
        _format_number(period["timer"]),
        f"{_format_number(period.get('pause', 0) * 60)} min.",
        _format_money(period["brutto"]),
        _format_money(period["netto"]),
    ]


def _format_streak(streak):
    if not streak or streak.get("length", 0) <= 0 or streak.get("start") is None or streak.get("end") is None:
        return _na()
    return f"{streak['length']} dage ({streak['start'].strftime('%d-%m-%Y')} - {streak['end'].strftime('%d-%m-%Y')})"


def _table_border(widths):
    return "  +" + "+".join("-" * (width + 2) for width in widths) + "+"


def _table_row(cells, widths, right_align):
    padded_cells = []
    for index, cell in enumerate(cells):
        text = str(cell)
        padding = widths[index] - _visible_length(text)
        if index in right_align:
            padded_cells.append(" " * padding + text)
        else:
            padded_cells.append(text + " " * padding)
    return "  | " + " | ".join(padded_cells) + " |"


def _print_table(title, headers, rows, right_align=None):
    right_align = right_align or set()
    string_headers = [str(header) for header in headers]
    string_rows = [[str(cell) for cell in row] for row in rows]

    widths = [_visible_length(header) for header in string_headers]
    for row in string_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], _visible_length(cell))

    border = _table_border(widths)

    print(Fore.WHITE + f"\n  {title.upper()}" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + border + Style.RESET_ALL)
    print(Fore.WHITE + _table_row(string_headers, widths, set()) + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + border + Style.RESET_ALL)
    for row in string_rows:
        print(Fore.WHITE + _table_row(row, widths, right_align) + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + border + Style.RESET_ALL)


def _visible_length(text):
    return len(ANSI_ESCAPE_PATTERN.sub("", text))

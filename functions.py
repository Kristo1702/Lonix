import json
import os
import re
import sys
import time
from calendar import monthrange
from datetime import date, datetime

from colorama import Fore, Style, init

init()

OTHER_INCOME_KEY = "anden indkomst netto"
DEFAULT_HOURLY_RATE_KEY = "standard timeløn"
TUTORIAL_DONE_KEY = "tutorial gennemført"
ENTRY_TYPE_KEY = "type"
DAY_OFF_ENTRY_TYPE = "fridag"
REQUIRED_SETTINGS_KEYS = ["skat", "fradrag", "am bidrag", OTHER_INCOME_KEY, "løn start", "løn slut"]
DEFAULT_FIXED_EXPENSES = 0
DEFAULT_HOURLY_RATE = 150
LEGACY_DEFAULT_FIXED_EXPENSES = 8250
LEGACY_DEFAULT_OTHER_INCOME = 9539 + 1203


def _stdout_supports(text):
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


_USE_UNICODE_UI = _stdout_supports("╭╮╰╯│─⚠️")
_BOX_TOP_LEFT = "╭" if _USE_UNICODE_UI else "+"
_BOX_TOP_RIGHT = "╮" if _USE_UNICODE_UI else "+"
_BOX_BOTTOM_LEFT = "╰" if _USE_UNICODE_UI else "+"
_BOX_BOTTOM_RIGHT = "╯" if _USE_UNICODE_UI else "+"
_BOX_VERTICAL = "│" if _USE_UNICODE_UI else "|"
_BOX_HORIZONTAL = "─" if _USE_UNICODE_UI else "-"
_WARNING_ICON = "⚠️" if _USE_UNICODE_UI else "[!]"
_HEADER_LINES = (
    "     _     ____ _   _ _____  __",
    "    | |   / _//| \\ | |_ _\\ \\/ /",
    "    | |  | |// |  \\| || | \\  / ",
    "    | |__| //| | |\\  || | /  \\ ",
    "    |_____//__/|_| \\_|___/_/\\_\\",
)


def ui_line(length):
    return _BOX_HORIZONTAL * length


def clear_terminal():
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")
    else:
        print("\033c", end="")


def header(path: str = None, clear: bool = True, løn: list = None, invalid_choice: bool = False):
    if clear:
        clear_terminal()
    print(Fore.GREEN + "\n".join(_HEADER_LINES) + Style.RESET_ALL)
    if path is None:
        return

    path_length = len(path)
    border_length_minus_edges = path_length + 4
    print(Fore.GREEN + "    " + _BOX_TOP_LEFT + _BOX_HORIZONTAL * border_length_minus_edges + _BOX_TOP_RIGHT)
    print("    " + _BOX_VERTICAL + "  " + Fore.WHITE + path + Fore.GREEN + "  " + _BOX_VERTICAL)
    print(Fore.GREEN + "    " + _BOX_BOTTOM_LEFT + _BOX_HORIZONTAL * border_length_minus_edges + _BOX_BOTTOM_RIGHT + Style.RESET_ALL)
    if not invalid_choice:
        print("\n" * 2)


def error_message(
    sti: str = None,
    besked: str = None,
    ugyldigt_valg: bool = True,
    sov: float = 0.0,
    get_input: bool = True,
):
    header(sti, invalid_choice=True)
    print("\n")

    if ugyldigt_valg:
        besked = "Ugyldigt valg. Prøv igen!"

    if besked:
        sentences = besked.splitlines()
        if not sentences:
            sentences = [""]
        ansi_escape_pattern = re.compile(r"\x1b\[[0-9;]*m")
        visible_sentence_lengths = [len(ansi_escape_pattern.sub("", sentence)) for sentence in sentences]
        biggest_sentence_length = max(visible_sentence_lengths)
        print(_WARNING_ICON)
        print(_BOX_TOP_LEFT + _BOX_HORIZONTAL * (biggest_sentence_length + 2) + _BOX_TOP_RIGHT)
        for sentence, visible_sentence_length in zip(sentences, visible_sentence_lengths):
            difference_to_biggest = biggest_sentence_length - visible_sentence_length
            print(
                Fore.WHITE
                + _BOX_VERTICAL
                + Fore.RED
                + f" {sentence} "
                + Fore.WHITE
                + " " * difference_to_biggest
                + _BOX_VERTICAL
            )
        print(_BOX_BOTTOM_LEFT + _BOX_HORIZONTAL * (biggest_sentence_length + 2) + _BOX_BOTTOM_RIGHT + Style.RESET_ALL)

    if sov:
        time.sleep(sov)

    if get_input:
        input(Fore.LIGHTBLACK_EX + "\n\nTryk Enter for at gå tilbage..." + Style.RESET_ALL)


def load_data():
    if not os.path.exists("data"):
        os.mkdir("data")

    if not os.path.exists("data/løn.txt"):
        with open("data/løn.txt", "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        return []

    with open("data/løn.txt", "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(new_data):
    data = load_data()
    ny_dato = next(iter(new_data))

    for i, entry in enumerate(data):
        if ny_dato in entry:
            data[i] = new_data
            break
    else:
        data.append(new_data)

    data = sorted(data, key=lambda entry: datetime.strptime(next(iter(entry)), "%d-%m-%Y"))

    with open("data/løn.txt", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_settings():
    if not os.path.exists("data"):
        os.mkdir("data")

    if not os.path.exists("data/oplysninger.txt"):
        default_data = {
            "skat": 0.4,
            "fradrag": 0,
            "am bidrag": 0.08,
            OTHER_INCOME_KEY: 0,
            DEFAULT_HOURLY_RATE_KEY: DEFAULT_HOURLY_RATE,
            TUTORIAL_DONE_KEY: False,
            "udgifter": DEFAULT_FIXED_EXPENSES,
            "budget kategorier": [],
            "ønsket rådighedsbeløb": 1000,
            "løn start": 15,
            "løn slut": 14,
        }
        with open("data/oplysninger.txt", "w", encoding="utf-8") as file:
            json.dump(default_data, file, ensure_ascii=False, indent=4)
        return default_data

    with open("data/oplysninger.txt", "r", encoding="utf-8") as file:
        settings = json.load(file)

    return normalize_settings(settings)


def save_settings(new_settings):
    new_settings = normalize_settings(new_settings)
    if not all(key in new_settings for key in REQUIRED_SETTINGS_KEYS):
        raise ValueError("Kunne ikke gemme data: nøgle mangler")

    # Legacy compatibility only. New calculations use budget categories.
    new_settings["udgifter"] = calculate_budget_expenses(new_settings)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/oplysninger.txt", "w", encoding="utf-8") as file:
        json.dump(new_settings, file, ensure_ascii=False, indent=4)


def normalize_settings(settings):
    if not isinstance(settings, dict):
        settings = {}

    normalized = dict(settings)
    if "udgifter" not in normalized:
        normalized["udgifter"] = DEFAULT_FIXED_EXPENSES

    if "budget kategorier" not in normalized:
        legacy_expenses = float(normalized.get("udgifter", 0) or 0)
        if legacy_expenses > 0 and legacy_expenses != LEGACY_DEFAULT_FIXED_EXPENSES:
            normalized["budget kategorier"] = [
                {"navn": "Faste udgifter", "beløb": legacy_expenses}
            ]
        else:
            normalized["budget kategorier"] = []
    else:
        clean_categories = []
        for item in normalized.get("budget kategorier", []):
            if not isinstance(item, dict):
                continue
            try:
                amount = float(item.get("beløb", 0) or 0)
            except (TypeError, ValueError):
                continue
            clean_categories.append(
                {
                    "navn": str(item.get("navn", "Kategori")),
                    "beløb": max(0.0, amount),
                }
            )
        if (
            len(clean_categories) == 1
            and clean_categories[0]["navn"] == "Faste udgifter"
            and clean_categories[0]["beløb"] == LEGACY_DEFAULT_FIXED_EXPENSES
        ):
            clean_categories = []
        normalized["budget kategorier"] = clean_categories

    if OTHER_INCOME_KEY not in normalized:
        try:
            legacy_other_income = float(normalized.get("su", 0) or 0) + float(normalized.get("boligstøtte", 0) or 0)
        except (TypeError, ValueError):
            legacy_other_income = 0.0
        normalized[OTHER_INCOME_KEY] = 0.0 if legacy_other_income == LEGACY_DEFAULT_OTHER_INCOME else legacy_other_income
    else:
        try:
            normalized[OTHER_INCOME_KEY] = max(0.0, float(normalized.get(OTHER_INCOME_KEY, 0) or 0))
        except (TypeError, ValueError):
            normalized[OTHER_INCOME_KEY] = 0.0
    normalized.pop("su", None)
    normalized.pop("boligstøtte", None)

    if "ønsket rådighedsbeløb" not in normalized:
        normalized["ønsket rådighedsbeløb"] = float(normalized.get("rådighed advarsel", 1000) or 0)
    normalized.pop("rådighed advarsel", None)

    try:
        normalized[DEFAULT_HOURLY_RATE_KEY] = max(
            0.0,
            float(normalized.get(DEFAULT_HOURLY_RATE_KEY, DEFAULT_HOURLY_RATE) or DEFAULT_HOURLY_RATE),
        )
    except (TypeError, ValueError):
        normalized[DEFAULT_HOURLY_RATE_KEY] = float(DEFAULT_HOURLY_RATE)

    normalized[TUTORIAL_DONE_KEY] = bool(normalized.get(TUTORIAL_DONE_KEY, False))

    return normalized


def get_budget_categories(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    categories = []
    for item in settings.get("budget kategorier", []):
        if not isinstance(item, dict):
            continue
        try:
            amount = float(item.get("beløb", 0) or 0)
        except (TypeError, ValueError):
            continue
        categories.append(
            {
                "navn": str(item.get("navn", "Kategori")),
                "beløb": max(0.0, amount),
            }
        )
    return categories


def get_disposable_income_goal(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, float(settings.get("ønsket rådighedsbeløb", 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def get_other_income(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, float(settings.get(OTHER_INCOME_KEY, 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def get_default_hourly_rate(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, float(settings.get(DEFAULT_HOURLY_RATE_KEY, DEFAULT_HOURLY_RATE) or DEFAULT_HOURLY_RATE))
    except (TypeError, ValueError):
        return float(DEFAULT_HOURLY_RATE)


def is_tutorial_completed(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    return bool(settings.get(TUTORIAL_DONE_KEY, False))


def is_day_off(løn_info):
    if not isinstance(løn_info, dict):
        return False
    return løn_info.get(ENTRY_TYPE_KEY) == DAY_OFF_ENTRY_TYPE or løn_info.get("fridag") is True


def get_shift_duration_hours(løn_info):
    if is_day_off(løn_info):
        return 0.0
    try:
        return max(0.0, float(løn_info.get("timer", 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def get_shift_pause_hours(løn_info):
    if is_day_off(løn_info):
        return 0.0
    try:
        return max(0.0, float(løn_info.get("pause", 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def get_shift_paid_hours(løn_info):
    if is_day_off(løn_info):
        return 0.0
    return max(0.0, get_shift_duration_hours(løn_info) - get_shift_pause_hours(løn_info))


def calculate_budget_expenses(settings=None):
    return sum(category["beløb"] for category in get_budget_categories(settings))


def calculate_disposable_income(total_income, settings=None):
    return float(total_income) - calculate_budget_expenses(settings)


def _shift_month(year, month, months):
    month = month + months
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def _safe_date(year, month, day):
    day = int(day)
    if day < 1:
        day = 1

    max_day = monthrange(year, month)[1]
    if day > max_day:
        day = max_day

    return date(year, month, day)


def get_salary_period_for_date(dato_obj, løn_start, løn_slut):
    løn_start = int(løn_start)
    løn_slut = int(løn_slut)

    def make_period(year, month):
        start = _safe_date(year, month, løn_start)

        if løn_start > løn_slut:
            end_year, end_month = _shift_month(year, month, 1)
            end = _safe_date(end_year, end_month, løn_slut)
        else:
            end = _safe_date(year, month, løn_slut)

        return start, end

    current_start, current_end = make_period(dato_obj.year, dato_obj.month)

    if current_start <= dato_obj <= current_end:
        return current_start, current_end

    previous_year, previous_month = _shift_month(dato_obj.year, dato_obj.month, -1)
    previous_start, previous_end = make_period(previous_year, previous_month)

    if previous_start <= dato_obj <= previous_end:
        return previous_start, previous_end

    next_year, next_month = _shift_month(dato_obj.year, dato_obj.month, 1)
    next_start, next_end = make_period(next_year, next_month)

    if next_start <= dato_obj <= next_end:
        return next_start, next_end

    if dato_obj < current_start:
        return previous_start, previous_end
    return next_start, next_end


def calculate_netto_salary():
    settings = load_settings()
    data = load_data()
    if not all(key in settings for key in REQUIRED_SETTINGS_KEYS):
        error_message(
            sti=None,
            besked=Fore.RED + "Forkerte indstillinger: nøgle(r) mangler" + Style.RESET_ALL,
            ugyldigt_valg=False,
            get_input=True,
        )
        return None

    if not data:
        error_message(
            sti=None,
            besked=Fore.RED + "Din data er tom. Tilføj en vagt først." + Style.RESET_ALL,
            ugyldigt_valg=False,
            get_input=True,
        )
        return None

    i_dag = datetime.now().date()

    løn_start = settings.get("løn start")
    løn_slut = settings.get("løn slut")

    periode_start, periode_slut = get_salary_period_for_date(i_dag, løn_start, løn_slut)

    total_timer = 0
    total_brutto = 0
    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()

        if periode_start <= dato_obj <= periode_slut:
            timer = get_shift_paid_hours(løn_info)
            timeløn = løn_info.get("timeløn", 0)
            total_timer += timer
            total_brutto += timer * timeløn

    netto = calculate_netto_salary_from_brutto(total_brutto)
    return total_brutto, netto, total_timer


def calculate_all_netto_salaries():
    settings = load_settings()
    data = load_data()
    if not all(key in settings for key in REQUIRED_SETTINGS_KEYS):
        error_message(
            sti=None,
            besked=Fore.RED + "Forkerte indstillinger: nøgle(r) mangler" + Style.RESET_ALL,
            ugyldigt_valg=False,
            get_input=True,
        )
        return None

    if not data:
        error_message(
            sti=None,
            besked=Fore.RED + "Din data er tom. Tilføj en vagt først." + Style.RESET_ALL,
            ugyldigt_valg=False,
            get_input=True,
        )
        return None

    løn_start = settings.get("løn start")
    løn_slut = settings.get("løn slut")

    lønsedler = {}
    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()
        periode_start, periode_slut = get_salary_period_for_date(dato_obj, løn_start, løn_slut)

        lønseddel_nøgle = (periode_start, periode_slut)
        if lønseddel_nøgle not in lønsedler:
            lønsedler[lønseddel_nøgle] = {
                "periode_start": periode_start,
                "periode_slut": periode_slut,
                "timer": 0,
                "pause": 0,
                "brutto": 0,
                "vagter": 0,
                "fridage": 0,
                "registreringer": 0,
            }

        is_day_off_entry = is_day_off(løn_info)
        timer = get_shift_paid_hours(løn_info)
        pause = get_shift_pause_hours(løn_info)
        timeløn = løn_info.get("timeløn", 0)
        brutto = timer * timeløn

        lønsedler[lønseddel_nøgle]["timer"] += timer
        lønsedler[lønseddel_nøgle]["pause"] += pause
        lønsedler[lønseddel_nøgle]["brutto"] += brutto
        lønsedler[lønseddel_nøgle]["registreringer"] += 1
        if is_day_off_entry:
            lønsedler[lønseddel_nøgle]["fridage"] += 1
        else:
            lønsedler[lønseddel_nøgle]["vagter"] += 1

    sorterede_lønsedler = sorted(lønsedler.values(), key=lambda value: value["periode_start"], reverse=True)
    for lønseddel in sorterede_lønsedler:
        breakdown = calculate_salary_breakdown_from_brutto(lønseddel["brutto"])
        lønseddel["netto"] = breakdown["netto"]
        lønseddel["am_bidrag"] = breakdown["am_bidrag"]
        lønseddel["efter_am"] = breakdown["efter_am"]
        lønseddel["fradrag"] = breakdown["fradrag"]
        lønseddel["skattegrundlag"] = breakdown["skattegrundlag"]
        lønseddel["skat"] = breakdown["skat"]

    return sorterede_lønsedler


def calculate_salary_forecast(data=None, settings=None, today=None):
    settings = settings if settings is not None else load_settings()
    data = data if data is not None else load_data()

    if not all(key in settings for key in REQUIRED_SETTINGS_KEYS):
        return None

    if not data:
        return None

    if today is None:
        today = datetime.now().date()

    løn_start = settings.get("løn start")
    løn_slut = settings.get("løn slut")
    periode_start, periode_slut = get_salary_period_for_date(today, løn_start, løn_slut)

    total_days = (periode_slut - periode_start).days + 1
    elapsed_days = min(max((today - periode_start).days + 1, 1), total_days)
    remaining_days = max(total_days - elapsed_days, 0)
    progress_ratio = elapsed_days / total_days if total_days else 1

    current_hours = 0.0
    current_brutto = 0.0
    historical_periods = {}

    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()
        timer = get_shift_paid_hours(løn_info)
        timeløn = float(løn_info.get("timeløn", 0))
        brutto = timer * timeløn

        entry_periode_start, entry_periode_slut = get_salary_period_for_date(dato_obj, løn_start, løn_slut)
        period_key = (entry_periode_start, entry_periode_slut)
        if period_key not in historical_periods:
            historical_periods[period_key] = {
                "periode_start": entry_periode_start,
                "periode_slut": entry_periode_slut,
                "timer": 0.0,
                "brutto": 0.0,
                "total_days": (entry_periode_slut - entry_periode_start).days + 1,
            }

        historical_periods[period_key]["timer"] += timer
        historical_periods[period_key]["brutto"] += brutto

        if periode_start <= dato_obj <= today:
            current_hours += timer
            current_brutto += brutto

    afsluttede_perioder = [
        period
        for period in historical_periods.values()
        if period["periode_slut"] < periode_start
    ]

    historical_daily_hours = None
    historical_daily_brutto = None
    historical_average_hours = None
    historical_average_brutto = None
    if afsluttede_perioder:
        historical_total_days = sum(period["total_days"] for period in afsluttede_perioder)
        historical_total_hours = sum(period["timer"] for period in afsluttede_perioder)
        historical_total_brutto = sum(period["brutto"] for period in afsluttede_perioder)

        if historical_total_days > 0:
            historical_daily_hours = historical_total_hours / historical_total_days
            historical_daily_brutto = historical_total_brutto / historical_total_days

        historical_average_hours = historical_total_hours / len(afsluttede_perioder)
        historical_average_brutto = historical_total_brutto / len(afsluttede_perioder)

    current_daily_hours = current_hours / elapsed_days if elapsed_days > 0 else None
    current_daily_brutto = current_brutto / elapsed_days if elapsed_days > 0 else None

    estimated_remaining_daily_hours = _blend_forecast_rate(current_daily_hours, historical_daily_hours, progress_ratio)
    estimated_remaining_daily_brutto = _blend_forecast_rate(current_daily_brutto, historical_daily_brutto, progress_ratio)

    estimated_total_hours = None
    estimated_total_brutto = None
    if estimated_remaining_daily_hours is not None:
        estimated_total_hours = current_hours + (estimated_remaining_daily_hours * remaining_days)
    if estimated_remaining_daily_brutto is not None:
        estimated_total_brutto = current_brutto + (estimated_remaining_daily_brutto * remaining_days)

    estimated_total_netto = None
    estimated_total_income = None
    estimated_disposable_income = None
    other_income = get_other_income(settings)
    if estimated_total_brutto is not None:
        estimated_total_netto = calculate_netto_salary_from_brutto(estimated_total_brutto)
        estimated_total_income = estimated_total_netto + other_income
        estimated_disposable_income = calculate_disposable_income(estimated_total_income, settings)

    current_netto = calculate_netto_salary_from_brutto(current_brutto)
    current_total_income = current_netto + other_income
    current_disposable_income = calculate_disposable_income(current_total_income, settings)
    budget_expenses = calculate_budget_expenses(settings)

    return {
        "periode_start": periode_start,
        "periode_slut": periode_slut,
        "total_days": total_days,
        "elapsed_days": elapsed_days,
        "remaining_days": remaining_days,
        "progress_ratio": progress_ratio,
        "current_hours": current_hours,
        "current_brutto": current_brutto,
        "current_netto": current_netto,
        "other_income": other_income,
        "current_total_income": current_total_income,
        "current_total_with_support": current_total_income,
        "current_disposable_income": current_disposable_income,
        "budget_expenses": budget_expenses,
        "historical_periods_count": len(afsluttede_perioder),
        "historical_average_hours": historical_average_hours,
        "historical_average_brutto": historical_average_brutto,
        "estimated_hours": estimated_total_hours,
        "estimated_brutto": estimated_total_brutto,
        "estimated_netto": estimated_total_netto,
        "estimated_total_income": estimated_total_income,
        "estimated_total_with_support": estimated_total_income,
        "estimated_disposable_income": estimated_disposable_income,
    }


def _blend_forecast_rate(current_rate, historical_rate, progress_ratio):
    if current_rate is None and historical_rate is None:
        return None

    if current_rate is None:
        return historical_rate

    if historical_rate is None:
        return current_rate

    return (historical_rate * (1 - progress_ratio)) + (current_rate * progress_ratio)


def calculate_salary_breakdown(brutto, skat, fradrag, am_bidrag=0.08):
    brutto = float(brutto)
    skat = float(skat)
    fradrag = float(fradrag)
    am_bidrag = float(am_bidrag)

    am_beløb = brutto * am_bidrag
    efter_am = brutto - am_beløb
    skattegrundlag = max(0, efter_am - fradrag)
    skat_beløb = skattegrundlag * skat
    netto = efter_am - skat_beløb

    return {
        "brutto": brutto,
        "am_bidrag": am_beløb,
        "efter_am": efter_am,
        "fradrag": fradrag,
        "skattegrundlag": skattegrundlag,
        "skat": skat_beløb,
        "netto": netto,
    }


def calculate_salary_breakdown_from_brutto(brutto):
    settings = load_settings()

    return calculate_salary_breakdown(
        brutto,
        settings.get("skat", 1),
        settings.get("fradrag", 0),
        settings.get("am bidrag", 1),
    )


def calculate_netto_salary_from_brutto(brutto):
    return calculate_salary_breakdown_from_brutto(brutto)["netto"]

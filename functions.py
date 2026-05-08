import json
import os
import re
import sys
import time
from calendar import monthrange
from copy import deepcopy
from datetime import date, datetime, timedelta
from uuid import uuid4

from colorama import Fore, Style, init

init()

OTHER_INCOME_KEY = "anden indkomst netto"
DEFAULT_HOURLY_RATE_KEY = "standard timeløn"
INTRODUCTION_DONE_KEY = "introduktion gennemført"
PENSION_CONTRIBUTION_KEY = "eget pensionsbidrag"
PAY_PERIOD_TYPE_KEY = "lønperiode type"
PAY_PERIOD_TYPE_MONTH = "måned"
PAY_PERIOD_TYPE_WEEKS = "uger"
PAY_PERIOD_WEEKS_KEY = "lønperiode uger"
PAY_PERIOD_ANCHOR_KEY = "lønperiode ankerdato"
ENTRY_TYPE_KEY = "type"
DAY_OFF_ENTRY_TYPE = "fridag"
ENTRY_ID_KEY = "id"
ENTRY_SETTINGS_KEY = "indstillinger"
ENTRY_CREATED_KEY = "registreret"
REQUIRED_SETTINGS_KEYS = ["skat", "fradrag", "am bidrag", OTHER_INCOME_KEY, "løn start", "løn slut"]
DEFAULT_FIXED_EXPENSES = 0
DEFAULT_HOURLY_RATE = 150
DEFAULT_PAY_PERIOD_WEEKS = 2
DEFAULT_PAY_PERIOD_ANCHOR = "01-01-2024"
LEGACY_DEFAULT_FIXED_EXPENSES = 8250
LEGACY_DEFAULT_OTHER_INCOME = 9539 + 1203
AVERAGE_DAYS_PER_MONTH = 365.2425 / 12
ENTRY_SETTINGS_SNAPSHOT_KEYS = (
    "skat",
    "fradrag",
    "am bidrag",
    PENSION_CONTRIBUTION_KEY,
    OTHER_INCOME_KEY,
    DEFAULT_HOURLY_RATE_KEY,
    "udgifter",
    "budget kategorier",
    "ønsket rådighedsbeløb",
    "løn start",
    "løn slut",
    PAY_PERIOD_TYPE_KEY,
    PAY_PERIOD_WEEKS_KEY,
    PAY_PERIOD_ANCHOR_KEY,
)


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
    ny_dato, løn_info = next(iter(new_data.items()))
    løn_info = normalize_entry_info(løn_info, date_key=ny_dato)
    ny_id = løn_info.get(ENTRY_ID_KEY)

    for i, entry in enumerate(data):
        _, existing_info = next(iter(entry.items()))
        if isinstance(existing_info, dict) and existing_info.get(ENTRY_ID_KEY) == ny_id:
            data[i] = {ny_dato: løn_info}
            break
    else:
        data.append({ny_dato: løn_info})

    data = sorted(
        data,
        key=lambda entry: (
            datetime.strptime(next(iter(entry)), "%d-%m-%Y"),
            str(next(iter(entry.values())).get(ENTRY_ID_KEY, "")),
        ),
    )

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
            PENSION_CONTRIBUTION_KEY: 0,
            OTHER_INCOME_KEY: 0,
            DEFAULT_HOURLY_RATE_KEY: DEFAULT_HOURLY_RATE,
            INTRODUCTION_DONE_KEY: False,
            "udgifter": DEFAULT_FIXED_EXPENSES,
            "budget kategorier": [],
            "ønsket rådighedsbeløb": 1000,
            "løn start": 15,
            "løn slut": 14,
            PAY_PERIOD_TYPE_KEY: PAY_PERIOD_TYPE_MONTH,
            PAY_PERIOD_WEEKS_KEY: DEFAULT_PAY_PERIOD_WEEKS,
            PAY_PERIOD_ANCHOR_KEY: DEFAULT_PAY_PERIOD_ANCHOR,
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


def new_entry_id():
    return uuid4().hex


def settings_snapshot(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    snapshot = {
        key: deepcopy(settings.get(key))
        for key in ENTRY_SETTINGS_SNAPSHOT_KEYS
        if key in settings
    }
    snapshot["udgifter"] = sum(
        max(0.0, float(category.get("beløb", 0) or 0))
        for category in snapshot.get("budget kategorier", [])
        if isinstance(category, dict)
    )
    return normalize_settings(snapshot)


def get_entry_id(løn_info):
    if not isinstance(løn_info, dict):
        return None
    entry_id = løn_info.get(ENTRY_ID_KEY)
    return str(entry_id) if entry_id else None


def get_entry_settings(løn_info, fallback_settings=None):
    if isinstance(fallback_settings, dict):
        base_settings = settings_snapshot(fallback_settings)
    else:
        base_settings = settings_snapshot()

    if isinstance(løn_info, dict) and isinstance(løn_info.get(ENTRY_SETTINGS_KEY), dict):
        base_settings.update(deepcopy(løn_info.get(ENTRY_SETTINGS_KEY)))

    return normalize_settings(base_settings)


def normalize_entry_info(løn_info, settings=None, date_key=None, entry_id=None):
    clean_info = deepcopy(løn_info) if isinstance(løn_info, dict) else {}
    clean_info[ENTRY_ID_KEY] = str(entry_id or clean_info.get(ENTRY_ID_KEY) or new_entry_id())
    clean_info.setdefault(ENTRY_CREATED_KEY, datetime.now().isoformat(timespec="seconds"))
    if isinstance(clean_info.get(ENTRY_SETTINGS_KEY), dict):
        entry_settings = settings_snapshot(settings)
        entry_settings.update(deepcopy(clean_info.get(ENTRY_SETTINGS_KEY)))
        clean_info[ENTRY_SETTINGS_KEY] = settings_snapshot(entry_settings)
    else:
        clean_info[ENTRY_SETTINGS_KEY] = settings_snapshot(settings)

    if is_day_off(clean_info):
        clean_info[ENTRY_TYPE_KEY] = DAY_OFF_ENTRY_TYPE
        clean_info["timer"] = 0
        clean_info["timeløn"] = 0
        clean_info.pop("pause", None)
        clean_info.pop("start", None)
        clean_info.pop("slut", None)

    return clean_info


def get_period_amount_factor(period_start=None, period_end=None, settings=None):
    if period_start is None or period_end is None:
        return 1.0

    if isinstance(period_start, datetime):
        period_start = period_start.date()
    if isinstance(period_end, datetime):
        period_end = period_end.date()

    normalized = normalize_settings(settings if isinstance(settings, dict) else {})
    if normalized.get(PAY_PERIOD_TYPE_KEY) == PAY_PERIOD_TYPE_MONTH:
        return 1.0

    period_days = max(1, (period_end - period_start).days + 1)
    return period_days / AVERAGE_DAYS_PER_MONTH


def scale_monthly_amount_for_period(amount, period_start=None, period_end=None, settings=None):
    try:
        monthly_amount = float(amount or 0)
    except (TypeError, ValueError):
        monthly_amount = 0.0
    return monthly_amount * get_period_amount_factor(period_start, period_end, settings)


def _weighted_period_amount(items, period_start, period_end, fallback_settings, amount_getter):
    normalized_items = []
    for item in items or []:
        try:
            brutto = max(0.0, float(item.get("brutto", 0) or 0))
        except (TypeError, ValueError):
            brutto = 0.0
        item_settings = item.get("settings")
        if not isinstance(item_settings, dict):
            item_settings = get_entry_settings(item.get("løn_info", {}), fallback_settings)
        else:
            item_settings = normalize_settings(item_settings)
        normalized_items.append({"brutto": brutto, "settings": item_settings})

    total_brutto = sum(item["brutto"] for item in normalized_items)
    if total_brutto > 0:
        return sum(
            amount_getter(item["settings"], period_start, period_end) * (item["brutto"] / total_brutto)
            for item in normalized_items
            if item["brutto"] > 0
        )

    effective_settings = (
        normalized_items[0]["settings"]
        if normalized_items
        else normalize_settings(fallback_settings if isinstance(fallback_settings, dict) else load_settings())
    )
    return amount_getter(effective_settings, period_start, period_end)


def calculate_period_other_income(items, period_start, period_end, fallback_settings=None):
    return _weighted_period_amount(items, period_start, period_end, fallback_settings, get_other_income)


def calculate_period_budget_expenses(items, period_start, period_end, fallback_settings=None):
    return _weighted_period_amount(items, period_start, period_end, fallback_settings, calculate_budget_expenses)


def calculate_period_disposable_goal(items, period_start, period_end, fallback_settings=None):
    return _weighted_period_amount(items, period_start, period_end, fallback_settings, get_disposable_income_goal)


def _coerce_int(value, default, minimum, maximum):
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _parse_settings_date(value, default=None):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value or "").strip()
    for pattern in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue

    if default is None:
        return None
    return _parse_settings_date(default)


def _settings_date_key(value, default):
    parsed = _parse_settings_date(value, default)
    if parsed is None:
        parsed = _parse_settings_date(default)
    return parsed.strftime("%d-%m-%Y")


def _normalize_pay_period_type(value):
    text = str(value or "").strip().lower()
    if text in {
        PAY_PERIOD_TYPE_WEEKS,
        "uge",
        "ugentlig",
        "ugentligt",
        "weekly",
        "weeks",
        "14 dage",
        "14-dage",
        "14-dages",
        "14 dages løn",
        "14-dagesløn",
        "2 uger",
    }:
        return PAY_PERIOD_TYPE_WEEKS
    return PAY_PERIOD_TYPE_MONTH


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
        pension = float(normalized.get(PENSION_CONTRIBUTION_KEY, 0) or 0)
    except (TypeError, ValueError):
        pension = 0.0
    if pension > 1:
        pension = pension / 100
    normalized[PENSION_CONTRIBUTION_KEY] = max(0.0, min(pension, 1.0))

    try:
        normalized[DEFAULT_HOURLY_RATE_KEY] = max(
            0.0,
            float(normalized.get(DEFAULT_HOURLY_RATE_KEY, DEFAULT_HOURLY_RATE) or DEFAULT_HOURLY_RATE),
        )
    except (TypeError, ValueError):
        normalized[DEFAULT_HOURLY_RATE_KEY] = float(DEFAULT_HOURLY_RATE)

    old_introduction_key = "tut" + "orial gennemført"
    if INTRODUCTION_DONE_KEY not in normalized and old_introduction_key in normalized:
        normalized[INTRODUCTION_DONE_KEY] = bool(normalized.get(old_introduction_key, False))
    normalized.pop(old_introduction_key, None)
    normalized[INTRODUCTION_DONE_KEY] = bool(normalized.get(INTRODUCTION_DONE_KEY, False))

    normalized["løn start"] = _coerce_int(normalized.get("løn start", 15), 15, 1, 31)
    normalized["løn slut"] = _coerce_int(normalized.get("løn slut", 14), 14, 1, 31)
    normalized[PAY_PERIOD_TYPE_KEY] = _normalize_pay_period_type(
        normalized.get(PAY_PERIOD_TYPE_KEY, PAY_PERIOD_TYPE_MONTH)
    )
    normalized[PAY_PERIOD_WEEKS_KEY] = _coerce_int(
        normalized.get(PAY_PERIOD_WEEKS_KEY, DEFAULT_PAY_PERIOD_WEEKS),
        DEFAULT_PAY_PERIOD_WEEKS,
        1,
        52,
    )
    normalized[PAY_PERIOD_ANCHOR_KEY] = _settings_date_key(
        normalized.get(PAY_PERIOD_ANCHOR_KEY, DEFAULT_PAY_PERIOD_ANCHOR),
        DEFAULT_PAY_PERIOD_ANCHOR,
    )

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


def get_disposable_income_goal(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        monthly_goal = max(0.0, float(settings.get("ønsket rådighedsbeløb", 0) or 0))
    except (TypeError, ValueError):
        return 0.0
    return scale_monthly_amount_for_period(monthly_goal, period_start, period_end, settings)


def get_other_income(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        monthly_income = max(0.0, float(settings.get(OTHER_INCOME_KEY, 0) or 0))
    except (TypeError, ValueError):
        return 0.0
    return scale_monthly_amount_for_period(monthly_income, period_start, period_end, settings)


def get_default_hourly_rate(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, float(settings.get(DEFAULT_HOURLY_RATE_KEY, DEFAULT_HOURLY_RATE) or DEFAULT_HOURLY_RATE))
    except (TypeError, ValueError):
        return float(DEFAULT_HOURLY_RATE)


def is_introduction_completed(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    return bool(settings.get(INTRODUCTION_DONE_KEY, False))


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


def calculate_budget_expenses(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    monthly_expenses = sum(category["beløb"] for category in get_budget_categories(settings))
    return scale_monthly_amount_for_period(monthly_expenses, period_start, period_end, settings)


def calculate_disposable_income(total_income, settings=None, period_start=None, period_end=None):
    return float(total_income) - calculate_budget_expenses(settings, period_start, period_end)


def get_pension_contribution_rate(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, min(float(settings.get(PENSION_CONTRIBUTION_KEY, 0) or 0), 1.0))
    except (TypeError, ValueError):
        return 0.0


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


def _get_monthly_salary_period_for_date(dato_obj, løn_start, løn_slut):
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


def _get_week_salary_period_for_date(dato_obj, settings):
    weeks = _coerce_int(
        settings.get(PAY_PERIOD_WEEKS_KEY, DEFAULT_PAY_PERIOD_WEEKS),
        DEFAULT_PAY_PERIOD_WEEKS,
        1,
        52,
    )
    anchor = _parse_settings_date(settings.get(PAY_PERIOD_ANCHOR_KEY), DEFAULT_PAY_PERIOD_ANCHOR)
    period_days = weeks * 7
    period_offset = (dato_obj - anchor).days // period_days
    start = anchor + timedelta(days=period_offset * period_days)
    end = start + timedelta(days=period_days - 1)
    return start, end


def get_salary_period_for_date(dato_obj, løn_start=None, løn_slut=None, settings=None):
    if isinstance(løn_start, dict) and settings is None:
        settings = løn_start
        løn_start = None
        løn_slut = None

    if settings is None:
        settings = {
            "løn start": 15 if løn_start is None else løn_start,
            "løn slut": 14 if løn_slut is None else løn_slut,
        }
    else:
        settings = dict(settings)
        if løn_start is not None and "løn start" not in settings:
            settings["løn start"] = løn_start
        if løn_slut is not None and "løn slut" not in settings:
            settings["løn slut"] = løn_slut

    settings = normalize_settings(settings)
    if settings.get(PAY_PERIOD_TYPE_KEY) == PAY_PERIOD_TYPE_WEEKS:
        return _get_week_salary_period_for_date(dato_obj, settings)

    return _get_monthly_salary_period_for_date(
        dato_obj,
        settings.get("løn start", 15),
        settings.get("løn slut", 14),
    )


def get_pay_period_description(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    if settings.get(PAY_PERIOD_TYPE_KEY) == PAY_PERIOD_TYPE_WEEKS:
        weeks = _coerce_int(
            settings.get(PAY_PERIOD_WEEKS_KEY, DEFAULT_PAY_PERIOD_WEEKS),
            DEFAULT_PAY_PERIOD_WEEKS,
            1,
            52,
        )
        anchor = _parse_settings_date(settings.get(PAY_PERIOD_ANCHOR_KEY), DEFAULT_PAY_PERIOD_ANCHOR)
        if weeks == 1:
            return f"Hver uge fra {anchor.strftime('%d-%m-%Y')}"
        return f"Hver {weeks}. uge fra {anchor.strftime('%d-%m-%Y')}"

    return f"d. {settings.get('løn start', 15)} - d. {settings.get('løn slut', 14)}"


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

    periode_start, periode_slut = get_salary_period_for_date(i_dag, settings=settings)

    total_timer = 0
    total_brutto = 0
    calculation_items = []
    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()

        if periode_start <= dato_obj <= periode_slut:
            timer = get_shift_paid_hours(løn_info)
            timeløn = løn_info.get("timeløn", 0)
            brutto = timer * timeløn
            total_timer += timer
            total_brutto += brutto
            calculation_items.append(
                {
                    "brutto": brutto,
                    "settings": get_entry_settings(løn_info, settings),
                }
            )

    breakdown = calculate_period_salary_breakdown(
        calculation_items,
        periode_start,
        periode_slut,
        settings,
    )
    netto = breakdown["netto"]
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

    lønsedler = {}
    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()
        entry_settings = get_entry_settings(løn_info, settings)
        periode_start, periode_slut = get_salary_period_for_date(dato_obj, settings=entry_settings)

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
                "calculation_items": [],
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
        lønsedler[lønseddel_nøgle]["calculation_items"].append(
            {
                "brutto": brutto,
                "settings": entry_settings,
            }
        )

    sorterede_lønsedler = sorted(lønsedler.values(), key=lambda value: value["periode_start"], reverse=True)
    for lønseddel in sorterede_lønsedler:
        breakdown = calculate_period_salary_breakdown(
            lønseddel["calculation_items"],
            lønseddel["periode_start"],
            lønseddel["periode_slut"],
            settings,
        )
        lønseddel["netto"] = breakdown["netto"]
        lønseddel["pension"] = breakdown["pension"]
        lønseddel["am_grundlag"] = breakdown["am_grundlag"]
        lønseddel["am_bidrag"] = breakdown["am_bidrag"]
        lønseddel["efter_am"] = breakdown["efter_am"]
        lønseddel["fradrag"] = breakdown["fradrag"]
        lønseddel["skattegrundlag"] = breakdown["skattegrundlag"]
        lønseddel["skat"] = breakdown["skat"]
        lønseddel["anden_indkomst"] = calculate_period_other_income(
            lønseddel["calculation_items"],
            lønseddel["periode_start"],
            lønseddel["periode_slut"],
            settings,
        )
        lønseddel["budget_expenses"] = calculate_period_budget_expenses(
            lønseddel["calculation_items"],
            lønseddel["periode_start"],
            lønseddel["periode_slut"],
            settings,
        )
        lønseddel["disposable_goal"] = calculate_period_disposable_goal(
            lønseddel["calculation_items"],
            lønseddel["periode_start"],
            lønseddel["periode_slut"],
            settings,
        )

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

    periode_start, periode_slut = get_salary_period_for_date(today, settings=settings)

    total_days = (periode_slut - periode_start).days + 1
    elapsed_days = min(max((today - periode_start).days + 1, 1), total_days)
    remaining_days = max(total_days - elapsed_days, 0)
    progress_ratio = elapsed_days / total_days if total_days else 1

    current_hours = 0.0
    current_brutto = 0.0
    current_items = []
    historical_periods = {}

    for entry in data:
        dato_str, løn_info = next(iter(entry.items()))
        dato_obj = datetime.strptime(dato_str, "%d-%m-%Y").date()
        entry_settings = get_entry_settings(løn_info, settings)
        timer = get_shift_paid_hours(løn_info)
        timeløn = float(løn_info.get("timeløn", 0))
        brutto = timer * timeløn

        entry_periode_start, entry_periode_slut = get_salary_period_for_date(dato_obj, settings=entry_settings)
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
            current_items.append(
                {
                    "brutto": brutto,
                    "settings": entry_settings,
                }
            )

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
    other_income = get_other_income(settings, periode_start, periode_slut)
    if estimated_total_brutto is not None:
        estimated_total_netto = calculate_salary_breakdown_from_brutto(
            estimated_total_brutto,
            settings,
            periode_start,
            periode_slut,
        )["netto"]
        estimated_total_income = estimated_total_netto + other_income
        estimated_disposable_income = calculate_disposable_income(
            estimated_total_income,
            settings,
            periode_start,
            periode_slut,
        )

    current_netto = calculate_period_salary_breakdown(
        current_items,
        periode_start,
        periode_slut,
        settings,
    )["netto"]
    current_total_income = current_netto + other_income
    current_disposable_income = calculate_disposable_income(
        current_total_income,
        settings,
        periode_start,
        periode_slut,
    )
    budget_expenses = calculate_budget_expenses(settings, periode_start, periode_slut)

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


def calculate_salary_breakdown(
    brutto,
    skat,
    fradrag,
    am_bidrag=0.08,
    period_start=None,
    period_end=None,
    settings=None,
):
    brutto = float(brutto)
    skat = float(skat)
    settings = normalize_settings(settings if isinstance(settings, dict) else {})
    fradrag = scale_monthly_amount_for_period(fradrag, period_start, period_end, settings)
    am_bidrag = float(am_bidrag)
    pension_rate = get_pension_contribution_rate(settings)

    pension = brutto * pension_rate
    am_grundlag = max(0.0, brutto - pension)
    am_beløb = am_grundlag * am_bidrag
    efter_am = am_grundlag - am_beløb
    skattegrundlag = max(0, efter_am - fradrag)
    skat_beløb = skattegrundlag * skat
    netto = efter_am - skat_beløb

    return {
        "brutto": brutto,
        "pension": pension,
        "am_grundlag": am_grundlag,
        "am_bidrag": am_beløb,
        "efter_am": efter_am,
        "fradrag": fradrag,
        "skattegrundlag": skattegrundlag,
        "skat": skat_beløb,
        "netto": netto,
    }


def calculate_period_salary_breakdown(items, period_start, period_end, fallback_settings=None):
    calculation_items = []
    for item in items or []:
        try:
            brutto = max(0.0, float(item.get("brutto", 0) or 0))
        except (TypeError, ValueError):
            brutto = 0.0

        item_settings = item.get("settings")
        if not isinstance(item_settings, dict):
            item_settings = get_entry_settings(item.get("løn_info", {}), fallback_settings)
        else:
            item_settings = normalize_settings(item_settings)

        calculation_items.append({"brutto": brutto, "settings": item_settings})

    total_brutto = sum(item["brutto"] for item in calculation_items)
    if total_brutto <= 0:
        effective_settings = (
            calculation_items[0]["settings"]
            if calculation_items
            else normalize_settings(fallback_settings if isinstance(fallback_settings, dict) else load_settings())
        )
        breakdown = calculate_salary_breakdown(
            0,
            effective_settings.get("skat", 0),
            effective_settings.get("fradrag", 0),
            effective_settings.get("am bidrag", 0),
            period_start,
            period_end,
            effective_settings,
        )
        breakdown["item_breakdowns"] = [
            {
                "brutto": 0.0,
                "pension": 0.0,
                "am_grundlag": 0.0,
                "am_bidrag": 0.0,
                "efter_am": 0.0,
                "fradrag": 0.0,
                "skattegrundlag": 0.0,
                "skat": 0.0,
                "netto": 0.0,
            }
            for _ in calculation_items
        ]
        return breakdown

    totals = {
        "brutto": 0.0,
        "pension": 0.0,
        "am_grundlag": 0.0,
        "am_bidrag": 0.0,
        "efter_am": 0.0,
        "fradrag": 0.0,
        "skattegrundlag": 0.0,
        "skat": 0.0,
        "netto": 0.0,
    }
    item_breakdowns = []
    for item in calculation_items:
        settings = item["settings"]
        brutto = item["brutto"]
        share = brutto / total_brutto if total_brutto else 0.0
        skat_rate = float(settings.get("skat", 0) or 0)
        am_rate = float(settings.get("am bidrag", 0) or 0)
        pension_rate = get_pension_contribution_rate(settings)
        fradrag = scale_monthly_amount_for_period(
            settings.get("fradrag", 0),
            period_start,
            period_end,
            settings,
        ) * share

        pension = brutto * pension_rate
        am_grundlag = max(0.0, brutto - pension)
        am_beløb = am_grundlag * am_rate
        efter_am = am_grundlag - am_beløb
        skattegrundlag = max(0.0, efter_am - fradrag)
        skat_beløb = skattegrundlag * skat_rate
        netto = efter_am - skat_beløb
        item_breakdown = {
            "brutto": brutto,
            "pension": pension,
            "am_grundlag": am_grundlag,
            "am_bidrag": am_beløb,
            "efter_am": efter_am,
            "fradrag": fradrag,
            "skattegrundlag": skattegrundlag,
            "skat": skat_beløb,
            "netto": netto,
        }
        item_breakdowns.append(item_breakdown)
        for key in totals:
            totals[key] += item_breakdown[key]

    totals["item_breakdowns"] = item_breakdowns
    return totals


def calculate_salary_breakdown_from_brutto(brutto, settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    if period_start is None and period_end is None:
        period_start, period_end = get_salary_period_for_date(datetime.now().date(), settings=settings)

    return calculate_salary_breakdown(
        brutto,
        settings.get("skat", 1),
        settings.get("fradrag", 0),
        settings.get("am bidrag", 1),
        period_start,
        period_end,
        settings,
    )


def calculate_netto_salary_from_brutto(brutto):
    return calculate_salary_breakdown_from_brutto(brutto)["netto"]

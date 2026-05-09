import json
import os
import re
import shutil
import sys
import tempfile
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
EMPLOYER_PENSION_CONTRIBUTION_KEY = "arbejdsgiver pensionsbidrag"
TAX_ALLOWANCE_UNIT_KEY = "fradrag enhed"
ATP_ENABLED_KEY = "atp aktiveret"
ATP_CALCULATION_KEY = "atp beregning"
ATP_CALCULATION_MANUAL = "manuel"
ATP_EMPLOYEE_AMOUNT_KEY = "atp medarbejderbeløb"
ATP_EMPLOYER_AMOUNT_KEY = "atp arbejdsgiverbeløb"
BIRTH_YEAR_KEY = "fødselsår"
AM_AGE_RULE_ENABLED_KEY = "am aldersregel aktiv"
PAID_BREAK_KEY = "pause betalt"
OTHER_INCOME_UNIT_KEY = "anden indkomst enhed"
DISPOSABLE_GOAL_UNIT_KEY = "rådighedsbeløb enhed"
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
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "løn.txt")
SETTINGS_FILE = os.path.join(DATA_DIR, "oplysninger.txt")
REQUIRED_SETTINGS_KEYS = ["skat", "fradrag", "am bidrag", OTHER_INCOME_KEY, "løn start", "løn slut"]
DEFAULT_FIXED_EXPENSES = 0
DEFAULT_HOURLY_RATE = 150
DEFAULT_PAY_PERIOD_WEEKS = 2
DEFAULT_PAY_PERIOD_ANCHOR = "01-01-2024"
LEGACY_DEFAULT_FIXED_EXPENSES = 8250
LEGACY_DEFAULT_OTHER_INCOME = 9539 + 1203
AVERAGE_DAYS_PER_MONTH = 365.2425 / 12
AM_AGE_RULE_START_YEAR = 2026
AM_AGE_RULE_MINIMUM_AGE = 18
AMOUNT_UNIT_MONTH = "måned"
AMOUNT_UNIT_TWO_WEEKS = "14 dage"
AMOUNT_UNIT_WEEK = "uge"
AMOUNT_UNIT_DAY = "dag"
AMOUNT_UNIT_PERIOD = "periode"
AMOUNT_UNITS = (
    AMOUNT_UNIT_MONTH,
    AMOUNT_UNIT_TWO_WEEKS,
    AMOUNT_UNIT_WEEK,
    AMOUNT_UNIT_DAY,
    AMOUNT_UNIT_PERIOD,
)
ENTRY_SETTINGS_SNAPSHOT_KEYS = (
    "skat",
    "fradrag",
    TAX_ALLOWANCE_UNIT_KEY,
    "am bidrag",
    BIRTH_YEAR_KEY,
    AM_AGE_RULE_ENABLED_KEY,
    PENSION_CONTRIBUTION_KEY,
    EMPLOYER_PENSION_CONTRIBUTION_KEY,
    ATP_ENABLED_KEY,
    ATP_CALCULATION_KEY,
    ATP_EMPLOYEE_AMOUNT_KEY,
    ATP_EMPLOYER_AMOUNT_KEY,
    PAID_BREAK_KEY,
    OTHER_INCOME_KEY,
    OTHER_INCOME_UNIT_KEY,
    DEFAULT_HOURLY_RATE_KEY,
    "udgifter",
    "budget kategorier",
    "ønsket rådighedsbeløb",
    DISPOSABLE_GOAL_UNIT_KEY,
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


def _default_settings():
    return {
        "skat": 0.39,
        "fradrag": 0,
        TAX_ALLOWANCE_UNIT_KEY: AMOUNT_UNIT_MONTH,
        "am bidrag": 0.08,
        BIRTH_YEAR_KEY: None,
        AM_AGE_RULE_ENABLED_KEY: True,
        PENSION_CONTRIBUTION_KEY: 0,
        EMPLOYER_PENSION_CONTRIBUTION_KEY: 0,
        ATP_ENABLED_KEY: False,
        ATP_CALCULATION_KEY: ATP_CALCULATION_MANUAL,
        ATP_EMPLOYEE_AMOUNT_KEY: 0,
        ATP_EMPLOYER_AMOUNT_KEY: 0,
        PAID_BREAK_KEY: False,
        OTHER_INCOME_KEY: 0,
        OTHER_INCOME_UNIT_KEY: AMOUNT_UNIT_MONTH,
        DEFAULT_HOURLY_RATE_KEY: DEFAULT_HOURLY_RATE,
        INTRODUCTION_DONE_KEY: False,
        "udgifter": DEFAULT_FIXED_EXPENSES,
        "budget kategorier": [],
        "ønsket rådighedsbeløb": 0,
        DISPOSABLE_GOAL_UNIT_KEY: AMOUNT_UNIT_MONTH,
        "løn start": 15,
        "løn slut": 14,
        PAY_PERIOD_TYPE_KEY: PAY_PERIOD_TYPE_MONTH,
        PAY_PERIOD_WEEKS_KEY: DEFAULT_PAY_PERIOD_WEEKS,
        PAY_PERIOD_ANCHOR_KEY: DEFAULT_PAY_PERIOD_ANCHOR,
    }


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _json_backup_path(path):
    return f"{path}.bak"


def _print_json_error(message):
    print(Fore.RED + message + Style.RESET_ALL, file=sys.stderr)


def _read_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _copy_json_backup(path):
    backup_path = _json_backup_path(path)
    try:
        shutil.copy2(path, backup_path)
    except OSError as error:
        _print_json_error(f"Kunne ikke skrive backup for {path}: {error}")


def _atomic_write_json(path, payload):
    _ensure_data_dir()

    if os.path.exists(path):
        try:
            _read_json_file(path)
            _copy_json_backup(path)
        except (json.JSONDecodeError, OSError):
            # Bevar seneste gyldige backup i stedet for at overskrive den
            # med en allerede korrupt primærfil.
            pass

    directory = os.path.dirname(path) or "."
    fd, temp_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(path)}.",
        suffix=".tmp",
        dir=directory,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=4)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
        _copy_json_backup(path)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def _load_json_with_backup(path, default, label):
    _ensure_data_dir()
    if not os.path.exists(path):
        _atomic_write_json(path, default)
        return deepcopy(default)

    try:
        return _read_json_file(path)
    except json.JSONDecodeError as error:
        _print_json_error(f"{label} kunne ikke læses, fordi JSON-filen er korrupt: {error}")
    except OSError as error:
        _print_json_error(f"{label} kunne ikke læses: {error}")

    backup_path = _json_backup_path(path)
    if os.path.exists(backup_path):
        try:
            backup_data = _read_json_file(backup_path)
            _print_json_error(f"{label} er indlæst fra backup: {backup_path}")
            return backup_data
        except json.JSONDecodeError as error:
            _print_json_error(f"Backupfilen for {label} er også korrupt: {error}")
        except OSError as error:
            _print_json_error(f"Backupfilen for {label} kunne ikke læses: {error}")

    _print_json_error(f"{label} kunne ikke gendannes. Bruger sikker standardværdi.")
    return deepcopy(default)


def load_data():
    data = _load_json_with_backup(DATA_FILE, [], "Vagtdata")
    if not isinstance(data, list):
        _print_json_error("Vagtdata har forkert format. Bruger tom liste.")
        return []
    return data


def save_all_data(data):
    _atomic_write_json(DATA_FILE, data if isinstance(data, list) else [])


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

    save_all_data(data)


def load_settings():
    settings = _load_json_with_backup(SETTINGS_FILE, _default_settings(), "Indstillinger")
    if not isinstance(settings, dict):
        _print_json_error("Indstillinger har forkert format. Bruger standardindstillinger.")
        settings = _default_settings()
    return normalize_settings(settings)


def save_settings(new_settings):
    new_settings = normalize_settings(new_settings)
    if not all(key in new_settings for key in REQUIRED_SETTINGS_KEYS):
        raise ValueError("Kunne ikke gemme data: nøgle mangler")

    # Legacy compatibility only. New calculations use budget categories.
    new_settings["udgifter"] = calculate_budget_expenses(new_settings)

    _atomic_write_json(SETTINGS_FILE, new_settings)


def new_entry_id():
    return uuid4().hex


_CLOCK_TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def try_parse_clock_minutes(value):
    if value is None:
        return None
    match = _CLOCK_TIME_PATTERN.fullmatch(str(value).strip())
    if not match:
        return None
    return (int(match.group(1)) * 60) + int(match.group(2))


def parse_clock_minutes(value):
    minutes = try_parse_clock_minutes(value)
    if minutes is None:
        raise ValueError("Tidspunkt skal skrives som HH:MM, fx 14:00.")
    return minutes


def normalize_clock_text(value):
    minutes = try_parse_clock_minutes(value)
    if minutes is None:
        return None
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"


def calculate_hours_from_times(start_text, end_text):
    start_minutes = parse_clock_minutes(start_text)
    end_minutes = parse_clock_minutes(end_text)
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    hours = (end_minutes - start_minutes) / 60
    if hours <= 0:
        raise ValueError("Sluttidspunkt skal være efter starttidspunkt.")
    return hours


def shift_time_interval(row):
    if not isinstance(row, dict) or row.get("is_day_off"):
        return None

    start = row.get("start")
    slut = row.get("slut")
    if not start or not slut:
        return None

    try:
        start_minutes = parse_clock_minutes(start)
        end_minutes = parse_clock_minutes(slut)
    except ValueError:
        return None

    if end_minutes <= start_minutes:
        end_minutes += 24 * 60
    return start_minutes, end_minutes


def intervals_overlap(first, second):
    if first is None or second is None:
        return False
    return first[0] < second[1] and second[0] < first[1]


def rows_on_date(rows, target_date, exclude_ids=None):
    exclude_ids = {str(entry_id) for entry_id in (exclude_ids or set())}
    return [
        row
        for row in rows
        if row.get("dato") == target_date and str(row.get("id")) not in exclude_ids
    ]


def find_time_overlap(row, rows, exclude_ids=None):
    current_interval = shift_time_interval(row)
    if current_interval is None:
        return None

    for other in rows_on_date(rows, row.get("dato"), exclude_ids):
        if other.get("is_day_off"):
            continue
        if intervals_overlap(current_interval, shift_time_interval(other)):
            return other
    return None


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


def periodize_amount(amount, unit, period_start=None, period_end=None, settings=None):
    amount = _coerce_float(amount, 0.0)
    unit = normalize_amount_unit(unit, AMOUNT_UNIT_MONTH)
    days = _period_days(period_start, period_end)

    if unit == AMOUNT_UNIT_PERIOD or days is None:
        return amount
    if unit == AMOUNT_UNIT_MONTH:
        return scale_monthly_amount_for_period(amount, period_start, period_end, settings)
    if unit == AMOUNT_UNIT_TWO_WEEKS:
        return amount * (days / 14)
    if unit == AMOUNT_UNIT_WEEK:
        return amount * (days / 7)
    if unit == AMOUNT_UNIT_DAY:
        return amount * days
    return amount


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


def _coerce_float(value, default=0.0, minimum=None, maximum=None):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    if minimum is not None:
        parsed = max(float(minimum), parsed)
    if maximum is not None:
        parsed = min(float(maximum), parsed)
    return parsed


def _normalize_rate(value, default=0.0):
    rate = _coerce_float(value, default, 0.0)
    if rate > 1:
        rate = rate / 100
    return max(0.0, min(rate, 1.0))


def normalize_amount_unit(value, default=AMOUNT_UNIT_MONTH):
    text = str(value or default).strip().lower().replace("-", " ")
    aliases = {
        "måneds": AMOUNT_UNIT_MONTH,
        "maaned": AMOUNT_UNIT_MONTH,
        "månedligt": AMOUNT_UNIT_MONTH,
        "monthly": AMOUNT_UNIT_MONTH,
        "14": AMOUNT_UNIT_TWO_WEEKS,
        "14dage": AMOUNT_UNIT_TWO_WEEKS,
        "14 dage": AMOUNT_UNIT_TWO_WEEKS,
        "14 dages": AMOUNT_UNIT_TWO_WEEKS,
        "14 dags": AMOUNT_UNIT_TWO_WEEKS,
        "2 uger": AMOUNT_UNIT_TWO_WEEKS,
        "uge": AMOUNT_UNIT_WEEK,
        "ugentlig": AMOUNT_UNIT_WEEK,
        "weekly": AMOUNT_UNIT_WEEK,
        "dag": AMOUNT_UNIT_DAY,
        "daglig": AMOUNT_UNIT_DAY,
        "daily": AMOUNT_UNIT_DAY,
        "periode": AMOUNT_UNIT_PERIOD,
        "period": AMOUNT_UNIT_PERIOD,
    }
    return aliases.get(text, text if text in AMOUNT_UNITS else default)


def _period_days(period_start=None, period_end=None):
    if period_start is None or period_end is None:
        return None
    if isinstance(period_start, datetime):
        period_start = period_start.date()
    if isinstance(period_end, datetime):
        period_end = period_end.date()
    return max(1, (period_end - period_start).days + 1)


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
                    "enhed": normalize_amount_unit(item.get("enhed", AMOUNT_UNIT_MONTH)),
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
        normalized["ønsket rådighedsbeløb"] = float(normalized.get("rådighed advarsel", 0) or 0)
    normalized.pop("rådighed advarsel", None)

    normalized["skat"] = _normalize_rate(normalized.get("skat", 0.39), 0.39)
    normalized["fradrag"] = _coerce_float(normalized.get("fradrag", 0), 0.0, 0.0)
    normalized["am bidrag"] = _normalize_rate(normalized.get("am bidrag", 0.08), 0.08)
    normalized[PENSION_CONTRIBUTION_KEY] = _normalize_rate(
        normalized.get(PENSION_CONTRIBUTION_KEY, 0),
        0.0,
    )
    normalized[EMPLOYER_PENSION_CONTRIBUTION_KEY] = _normalize_rate(
        normalized.get(EMPLOYER_PENSION_CONTRIBUTION_KEY, 0),
        0.0,
    )
    normalized[TAX_ALLOWANCE_UNIT_KEY] = normalize_amount_unit(
        normalized.get(TAX_ALLOWANCE_UNIT_KEY, AMOUNT_UNIT_MONTH),
        AMOUNT_UNIT_MONTH,
    )
    normalized[OTHER_INCOME_UNIT_KEY] = normalize_amount_unit(
        normalized.get(OTHER_INCOME_UNIT_KEY, AMOUNT_UNIT_MONTH),
        AMOUNT_UNIT_MONTH,
    )
    normalized[DISPOSABLE_GOAL_UNIT_KEY] = normalize_amount_unit(
        normalized.get(DISPOSABLE_GOAL_UNIT_KEY, AMOUNT_UNIT_MONTH),
        AMOUNT_UNIT_MONTH,
    )

    normalized[ATP_ENABLED_KEY] = bool(normalized.get(ATP_ENABLED_KEY, False))
    atp_calculation = str(normalized.get(ATP_CALCULATION_KEY, ATP_CALCULATION_MANUAL) or "").strip().lower()
    normalized[ATP_CALCULATION_KEY] = atp_calculation if atp_calculation else ATP_CALCULATION_MANUAL
    normalized[ATP_EMPLOYEE_AMOUNT_KEY] = _coerce_float(
        normalized.get(ATP_EMPLOYEE_AMOUNT_KEY, 0),
        0.0,
        0.0,
    )
    normalized[ATP_EMPLOYER_AMOUNT_KEY] = _coerce_float(
        normalized.get(ATP_EMPLOYER_AMOUNT_KEY, 0),
        0.0,
        0.0,
    )
    normalized[AM_AGE_RULE_ENABLED_KEY] = bool(normalized.get(AM_AGE_RULE_ENABLED_KEY, True))
    normalized[PAID_BREAK_KEY] = bool(normalized.get(PAID_BREAK_KEY, False))

    birth_year = normalized.get(BIRTH_YEAR_KEY, None)
    if birth_year in ("", None):
        normalized[BIRTH_YEAR_KEY] = None
    else:
        try:
            parsed_birth_year = int(float(birth_year))
        except (TypeError, ValueError):
            parsed_birth_year = None
        current_year = datetime.now().year
        normalized[BIRTH_YEAR_KEY] = (
            parsed_birth_year
            if parsed_birth_year is not None and 1900 <= parsed_birth_year <= current_year
            else None
        )

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
                "enhed": normalize_amount_unit(item.get("enhed", AMOUNT_UNIT_MONTH)),
            }
        )
    return categories


def get_disposable_income_goal(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        monthly_goal = max(0.0, float(settings.get("ønsket rådighedsbeløb", 0) or 0))
    except (TypeError, ValueError):
        return 0.0
    return periodize_amount(
        monthly_goal,
        settings.get(DISPOSABLE_GOAL_UNIT_KEY, AMOUNT_UNIT_MONTH),
        period_start,
        period_end,
        settings,
    )


def get_other_income(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        monthly_income = max(0.0, float(settings.get(OTHER_INCOME_KEY, 0) or 0))
    except (TypeError, ValueError):
        return 0.0
    return periodize_amount(
        monthly_income,
        settings.get(OTHER_INCOME_UNIT_KEY, AMOUNT_UNIT_MONTH),
        period_start,
        period_end,
        settings,
    )


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
    pause_paid = False
    if isinstance(løn_info, dict):
        if PAID_BREAK_KEY in løn_info:
            pause_paid = bool(løn_info.get(PAID_BREAK_KEY, False))
        elif isinstance(løn_info.get(ENTRY_SETTINGS_KEY), dict):
            pause_paid = bool(løn_info.get(ENTRY_SETTINGS_KEY, {}).get(PAID_BREAK_KEY, False))
    if pause_paid:
        return get_shift_duration_hours(løn_info)
    return max(0.0, get_shift_duration_hours(løn_info) - get_shift_pause_hours(løn_info))


def calculate_budget_expenses(settings=None, period_start=None, period_end=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    return sum(
        periodize_amount(
            category["beløb"],
            category.get("enhed", AMOUNT_UNIT_MONTH),
            period_start,
            period_end,
            settings,
        )
        for category in get_budget_categories(settings)
    )


def calculate_disposable_income(total_income, settings=None, period_start=None, period_end=None):
    return float(total_income) - calculate_budget_expenses(settings, period_start, period_end)


def get_pension_contribution_rate(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, min(float(settings.get(PENSION_CONTRIBUTION_KEY, 0) or 0), 1.0))
    except (TypeError, ValueError):
        return 0.0


def get_employer_pension_contribution_rate(settings=None):
    settings = normalize_settings(settings if settings is not None else load_settings())
    try:
        return max(0.0, min(float(settings.get(EMPLOYER_PENSION_CONTRIBUTION_KEY, 0) or 0), 1.0))
    except (TypeError, ValueError):
        return 0.0


def should_pay_am_contribution(settings, period_start=None, period_end=None):
    settings = normalize_settings(settings if isinstance(settings, dict) else {})
    if not settings.get(AM_AGE_RULE_ENABLED_KEY, True):
        return True

    birth_year = settings.get(BIRTH_YEAR_KEY)
    if birth_year in ("", None):
        return True

    try:
        birth_year = int(birth_year)
    except (TypeError, ValueError):
        return True

    reference_date = period_end or period_start or datetime.now().date()
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    calculation_year = reference_date.year
    if calculation_year >= AM_AGE_RULE_START_YEAR and calculation_year < birth_year + AM_AGE_RULE_MINIMUM_AGE:
        return False
    return True


def get_effective_am_rate(settings, period_start=None, period_end=None):
    settings = normalize_settings(settings if isinstance(settings, dict) else {})
    if not should_pay_am_contribution(settings, period_start, period_end):
        return 0.0
    return _normalize_rate(settings.get("am bidrag", 0), 0.0)


def get_tax_allowance_for_period(settings, period_start=None, period_end=None, calculation_notes=None):
    settings = normalize_settings(settings if isinstance(settings, dict) else {})
    allowance = _coerce_float(settings.get("fradrag", 0), 0.0, 0.0)
    unit = normalize_amount_unit(settings.get(TAX_ALLOWANCE_UNIT_KEY, AMOUNT_UNIT_MONTH), AMOUNT_UNIT_MONTH)
    days = _period_days(period_start, period_end)

    def add_note(text):
        if calculation_notes is not None and text not in calculation_notes:
            calculation_notes.append(text)

    if unit == AMOUNT_UNIT_PERIOD or days is None:
        if days is None and unit != AMOUNT_UNIT_PERIOD:
            add_note("Fradrag er brugt uden periode, så beløbet er ikke periodiseret.")
        return allowance

    if unit == AMOUNT_UNIT_MONTH:
        if settings.get(PAY_PERIOD_TYPE_KEY) != PAY_PERIOD_TYPE_MONTH:
            add_note("Månedsfradrag er estimeret til lønperioden efter antal dage.")
        return scale_monthly_amount_for_period(allowance, period_start, period_end, settings)

    if unit == AMOUNT_UNIT_TWO_WEEKS:
        if days != 14:
            add_note("14-dages fradrag er skaleret, fordi lønperioden ikke er 14 dage.")
        return allowance if days == 14 else allowance * (days / 14)

    if unit == AMOUNT_UNIT_WEEK:
        if days != 7:
            add_note("Ugefradrag er skaleret efter antal dage i lønperioden.")
        return allowance * (days / 7)

    if unit == AMOUNT_UNIT_DAY:
        return allowance * days

    return allowance


def calculate_atp_for_period(settings, hours=0, period_start=None, period_end=None, calculation_notes=None, gross=0):
    settings = normalize_settings(settings if isinstance(settings, dict) else {})
    if not settings.get(ATP_ENABLED_KEY, False) or _coerce_float(gross, 0.0, 0.0) <= 0:
        return 0.0, 0.0

    calculation = str(settings.get(ATP_CALCULATION_KEY, ATP_CALCULATION_MANUAL) or "").strip().lower()
    if calculation == ATP_CALCULATION_MANUAL:
        return (
            _coerce_float(settings.get(ATP_EMPLOYEE_AMOUNT_KEY, 0), 0.0, 0.0),
            _coerce_float(settings.get(ATP_EMPLOYER_AMOUNT_KEY, 0), 0.0, 0.0),
        )

    if calculation_notes is not None:
        calculation_notes.append("ATP-beregning er ikke manuel, så ATP er sat til 0 i denne version.")
    return 0.0, 0.0


def get_holiday_eligible_salary(entry_info, settings=None):
    if not isinstance(entry_info, dict) or is_day_off(entry_info):
        return 0.0

    excluded_types = {
        "feriepenge",
        "løn under ferie",
        "ferietillæg",
        "diæter",
        "skattefri rejsegodtgørelse",
        "omkostningsgodtgørelse",
    }
    entry_type = str(entry_info.get(ENTRY_TYPE_KEY, "") or "").strip().lower()
    if entry_type in excluded_types:
        return 0.0

    if "ferieberettiget løn" in entry_info:
        return _coerce_float(entry_info.get("ferieberettiget løn", 0), 0.0, 0.0)

    if "brutto" in entry_info:
        return _coerce_float(entry_info.get("brutto", 0), 0.0, 0.0)

    paid_hours = get_shift_paid_hours(entry_info)
    hourly_rate = _coerce_float(entry_info.get("timeløn", 0), 0.0, 0.0)
    return paid_hours * hourly_rate


def _holiday_month_ranges(start, end):
    if end < start:
        return []
    current = date(start.year, start.month, 1)
    ranges = []
    while current <= end:
        last_day = monthrange(current.year, current.month)[1]
        month_start = current
        month_end = date(current.year, current.month, last_day)
        ranges.append((month_start, month_end))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return ranges


def get_holiday_year(today=None):
    today = today or datetime.now().date()
    if isinstance(today, datetime):
        today = today.date()
    start_year = today.year if today.month >= 9 else today.year - 1
    start = date(start_year, 9, 1)
    end = date(start_year + 1, 8, 31)
    request_end = date(start_year + 1, 12, 31)
    return start, end, request_end


def calculate_holiday_days_for_range(start, end):
    if start is None or end is None or end < start:
        return 0.0

    total = 0.0
    for month_start, month_end in _holiday_month_ranges(start, end):
        active_start = max(start, month_start)
        active_end = min(end, month_end)
        active_days = (active_end - active_start).days + 1
        full_month = active_start == month_start and active_end == month_end
        total += 2.08 if full_month else min(2.08, active_days * 0.07)
    return total


def calculate_holiday_pay_amount(eligible_salary, holiday_pay_rate):
    return _coerce_float(eligible_salary, 0.0, 0.0) * (_coerce_float(holiday_pay_rate, 0.0, 0.0) / 100)


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


def is_period_complete(period_start, period_end, today=None):
    if period_start is None or period_end is None:
        return False
    if isinstance(period_start, datetime):
        period_start = period_start.date()
    if isinstance(period_end, datetime):
        period_end = period_end.date()
    if today is None:
        today = datetime.now().date()
    elif isinstance(today, datetime):
        today = today.date()
    if not isinstance(period_start, date) or not isinstance(period_end, date):
        return False
    return period_end < today


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
                    "timer": timer,
                    "paid_hours": timer,
                    "løn_info": løn_info,
                    "dato": dato_obj,
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


def calculate_all_netto_salaries(use_entry_settings=True):
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
        entry_settings = get_entry_settings(løn_info, settings) if use_entry_settings else settings
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
        if use_entry_settings:
            timer = get_shift_paid_hours(løn_info)
        else:
            duration = get_shift_duration_hours(løn_info)
            pause = get_shift_pause_hours(løn_info)
            timer = duration if settings.get(PAID_BREAK_KEY, False) else max(0.0, duration - pause)
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
                "timer": timer,
                "paid_hours": timer,
                "løn_info": løn_info,
                "dato": dato_obj,
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
        lønseddel["breakdown"] = breakdown
        lønseddel["calculation_notes"] = breakdown.get("calculation_notes", [])
        lønseddel["netto"] = breakdown["netto"]
        lønseddel["pension"] = breakdown["pension"]
        lønseddel["employee_pension"] = breakdown["employee_pension"]
        lønseddel["arbejdsgiver_pension"] = breakdown["arbejdsgiver_pension"]
        lønseddel["employer_pension"] = breakdown["employer_pension"]
        lønseddel["atp_medarbejder"] = breakdown["atp_medarbejder"]
        lønseddel["atp_employee"] = breakdown["atp_employee"]
        lønseddel["atp_arbejdsgiver"] = breakdown["atp_arbejdsgiver"]
        lønseddel["atp_employer"] = breakdown["atp_employer"]
        lønseddel["atp_total"] = breakdown["atp_total"]
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


def calculate_salary_forecast(data=None, settings=None, today=None, use_entry_settings=True):
    settings = normalize_settings(settings if settings is not None else load_settings())
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
        entry_settings = get_entry_settings(løn_info, settings) if use_entry_settings else settings
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
                    "timer": timer,
                    "paid_hours": timer,
                    "løn_info": løn_info,
                    "dato": dato_obj,
                    "settings": entry_settings,
                }
            )

    afsluttede_perioder = [
        period
        for period in historical_periods.values()
        if is_period_complete(period["periode_start"], period["periode_slut"], today)
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
        effective_settings = select_effective_settings_for_period(current_items, settings)
        estimated_total_netto = calculate_salary_breakdown_from_brutto(
            estimated_total_brutto,
            estimated_total_hours or 0.0,
            effective_settings,
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


def _normalize_calculation_item(item, fallback_settings=None):
    item = item if isinstance(item, dict) else {}
    løn_info = item.get("løn_info") if isinstance(item.get("løn_info"), dict) else {}

    brutto = _coerce_float(item.get("brutto", løn_info.get("brutto", 0)), 0.0, 0.0)
    if "paid_hours" in item:
        hours = _coerce_float(item.get("paid_hours"), 0.0, 0.0)
    elif løn_info:
        hours = get_shift_paid_hours(løn_info)
    else:
        hours = _coerce_float(item.get("timer", 0), 0.0, 0.0)

    item_settings = item.get("settings")
    if isinstance(item_settings, dict):
        item_settings = normalize_settings(item_settings)
    elif løn_info:
        item_settings = get_entry_settings(løn_info, fallback_settings)
    else:
        item_settings = normalize_settings(fallback_settings if isinstance(fallback_settings, dict) else load_settings())

    return {
        "brutto": brutto,
        "timer": hours,
        "paid_hours": hours,
        "settings": item_settings,
        "løn_info": løn_info,
        "dato": item.get("dato"),
    }


def select_effective_settings_for_period(items, fallback_settings=None):
    selected = None
    for item in items or []:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("settings"), dict):
            selected = normalize_settings(item.get("settings"))
        elif isinstance(item.get("løn_info"), dict):
            selected = get_entry_settings(item.get("løn_info"), fallback_settings)

    if selected is not None:
        return selected
    if isinstance(fallback_settings, dict):
        return normalize_settings(fallback_settings)
    return normalize_settings(load_settings())


def _breakdown_with_aliases(values):
    gross = values.get("gross", values.get("brutto", 0.0))
    paid_hours = values.get("paid_hours", values.get("timer", 0.0))
    employee_pension = values.get("employee_pension", values.get("pension", 0.0))
    employer_pension = values.get("employer_pension", values.get("arbejdsgiver_pension", 0.0))
    atp_employee = values.get("atp_employee", values.get("atp_medarbejder", 0.0))
    atp_employer = values.get("atp_employer", values.get("atp_arbejdsgiver", 0.0))
    am_basis = values.get("am_basis", values.get("am_grundlag", 0.0))
    am_contribution = values.get("am_contribution", values.get("am_bidrag", 0.0))
    after_am = values.get("after_am", values.get("efter_am", 0.0))
    tax_allowance = values.get("tax_allowance", values.get("fradrag", 0.0))
    taxable_income = values.get("taxable_income", values.get("skattegrundlag", 0.0))
    tax = values.get("tax", values.get("skat", 0.0))
    net = values.get("net", values.get("netto", 0.0))

    result = dict(values)
    result.update(
        {
            "brutto": gross,
            "gross": gross,
            "timer": paid_hours,
            "paid_hours": paid_hours,
            "pension": employee_pension,
            "employee_pension": employee_pension,
            "arbejdsgiver_pension": employer_pension,
            "employer_pension": employer_pension,
            "atp_medarbejder": atp_employee,
            "atp_employee": atp_employee,
            "atp_arbejdsgiver": atp_employer,
            "atp_employer": atp_employer,
            "atp_total": atp_employee + atp_employer,
            "am_grundlag": am_basis,
            "am_basis": am_basis,
            "am_bidrag": am_contribution,
            "am_contribution": am_contribution,
            "efter_am": after_am,
            "after_am": after_am,
            "fradrag": tax_allowance,
            "tax_allowance": tax_allowance,
            "skattegrundlag": taxable_income,
            "taxable_income": taxable_income,
            "skat": tax,
            "tax": tax,
            "netto": net,
            "net": net,
            "trukket_i_alt": employee_pension + atp_employee + am_contribution + tax,
            "deductions_total": employee_pension + atp_employee + am_contribution + tax,
        }
    )
    return result


def calculate_salary_breakdown(
    brutto,
    skat,
    fradrag,
    am_bidrag=0.08,
    period_start=None,
    period_end=None,
    settings=None,
    hours=0,
):
    base_settings = dict(settings) if isinstance(settings, dict) else {}
    base_settings.update(
        {
            "skat": skat,
            "fradrag": fradrag,
            "am bidrag": am_bidrag,
        }
    )
    return calculate_salary_breakdown_from_brutto(
        brutto,
        hours,
        base_settings,
        period_start,
        period_end,
    )


def calculate_salary_breakdown_from_settings(
    brutto,
    fradrag=None,
    settings=None,
    hours=0,
    period_start=None,
    period_end=None,
):
    effective_settings = normalize_settings(settings if isinstance(settings, dict) else load_settings())
    if fradrag is not None:
        effective_settings["fradrag"] = _coerce_float(fradrag, 0.0, 0.0)
    return calculate_salary_breakdown_from_brutto(
        brutto,
        hours,
        effective_settings,
        period_start,
        period_end,
    )


def calculate_salary_breakdown_from_brutto(brutto, hours=0, settings=None, period_start=None, period_end=None):
    if isinstance(hours, dict):
        old_settings = hours
        old_period_start = settings
        old_period_end = period_start
        settings = old_settings
        period_start = old_period_start
        period_end = old_period_end
        hours = 0

    settings = normalize_settings(settings if isinstance(settings, dict) else load_settings())
    calculation_notes = []
    if period_start is None or period_end is None:
        period_start, period_end = get_salary_period_for_date(datetime.now().date(), settings=settings)

    gross = _coerce_float(brutto, 0.0, 0.0)
    paid_hours = _coerce_float(hours, 0.0, 0.0)
    employee_pension = gross * get_pension_contribution_rate(settings)
    employer_pension = gross * get_employer_pension_contribution_rate(settings)
    atp_employee, atp_employer = calculate_atp_for_period(
        settings,
        paid_hours,
        period_start,
        period_end,
        calculation_notes,
        gross,
    )
    effective_am_rate = get_effective_am_rate(settings, period_start, period_end)
    if effective_am_rate == 0 and _normalize_rate(settings.get("am bidrag", 0), 0.0) > 0:
        if not should_pay_am_contribution(settings, period_start, period_end):
            calculation_notes.append("AM-bidrag er sat til 0 efter aldersreglen.")

    am_basis = max(0.0, gross - employee_pension - atp_employee)
    am_contribution = am_basis * effective_am_rate
    after_am = am_basis - am_contribution
    tax_allowance = get_tax_allowance_for_period(settings, period_start, period_end, calculation_notes)
    taxable_income = max(0.0, after_am - tax_allowance)
    tax_rate = _normalize_rate(settings.get("skat", 0), 0.0)
    tax = taxable_income * tax_rate
    net = after_am - tax

    effective_settings = deepcopy(settings)
    effective_settings["effektiv am bidrag"] = effective_am_rate
    effective_settings["effektiv fradrag"] = tax_allowance

    return _breakdown_with_aliases(
        {
            "gross": gross,
            "paid_hours": paid_hours,
            "employee_pension": employee_pension,
            "employer_pension": employer_pension,
            "atp_employee": atp_employee,
            "atp_employer": atp_employer,
            "am_basis": am_basis,
            "am_contribution": am_contribution,
            "after_am": after_am,
            "tax_allowance": tax_allowance,
            "taxable_income": taxable_income,
            "tax": tax,
            "net": net,
            "skat_sats": tax_rate,
            "tax_rate": tax_rate,
            "am_sats": effective_am_rate,
            "am_rate": effective_am_rate,
            "effective_settings": effective_settings,
            "calculation_notes": calculation_notes,
            "item_breakdowns": [],
        }
    )


def _distributed_item_breakdown(item, totals, share):
    return _breakdown_with_aliases(
        {
            "gross": item["brutto"],
            "paid_hours": item["paid_hours"],
            "employee_pension": totals["employee_pension"] * share,
            "employer_pension": totals["employer_pension"] * share,
            "atp_employee": totals["atp_employee"] * share,
            "atp_employer": totals["atp_employer"] * share,
            "am_basis": totals["am_basis"] * share,
            "am_contribution": totals["am_contribution"] * share,
            "after_am": totals["after_am"] * share,
            "tax_allowance": totals["tax_allowance"] * share,
            "taxable_income": totals["taxable_income"] * share,
            "tax": totals["tax"] * share,
            "net": totals["net"] * share,
            "effective_settings": item["settings"],
            "calculation_notes": [],
            "item_breakdowns": [],
        }
    )


def calculate_period_salary_breakdown(items, period_start, period_end, fallback_settings=None):
    calculation_items = [
        _normalize_calculation_item(item, fallback_settings)
        for item in (items or [])
    ]
    effective_settings = select_effective_settings_for_period(calculation_items, fallback_settings)
    total_brutto = sum(item["brutto"] for item in calculation_items)
    total_hours = sum(item["paid_hours"] for item in calculation_items)

    breakdown = calculate_salary_breakdown_from_brutto(
        total_brutto,
        total_hours,
        effective_settings,
        period_start,
        period_end,
    )

    if total_brutto > 0:
        shares = [item["brutto"] / total_brutto for item in calculation_items]
    elif total_hours > 0:
        shares = [item["paid_hours"] / total_hours for item in calculation_items]
    else:
        shares = [0.0 for _ in calculation_items]

    item_breakdowns = [
        _distributed_item_breakdown(item, breakdown, share)
        for item, share in zip(calculation_items, shares)
    ]
    breakdown["item_breakdowns"] = item_breakdowns
    return breakdown


def calculate_netto_salary_from_brutto(brutto):
    return calculate_salary_breakdown_from_brutto(brutto)["netto"]

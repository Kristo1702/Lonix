import os
import sys
import time
from calendar import monthrange
from datetime import date, datetime, timedelta

# Qt reads some environment flags while the bindings are imported.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.pop("QT_USE_NATIVE_WINDOWS", None)

from PyQt5.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPointF,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    pyqtProperty,
)
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QTabBar,
    QStyleOptionButton,
    QStylePainter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import functions as ft
import statistik


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def find_logo_path():
    bundled_logo_path = resource_path("logo.png")
    if os.path.exists(bundled_logo_path):
        return bundled_logo_path

    localappdata_logo_path = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "lønix",
        "logo.png",
    )
    if os.path.exists(localappdata_logo_path):
        return localappdata_logo_path

    return ""


LOGO_PATH = find_logo_path()


APP_NAME = "Lønix"
REQUIRED_KEYS = ["skat", "fradrag", "am bidrag", "anden indkomst netto", "løn start", "løn slut"]

BASE_WINDOW_SIZE = QSize(1220, 780)
BASE_MINIMUM_WINDOW_SIZE = QSize(980, 650)
WINDOW_WIDTH_SETTINGS_KEY = "vindue bredde"
WINDOW_HEIGHT_SETTINGS_KEY = "vindue højde"
WINDOW_SCREEN_FILL_RATIO = 0.92
BASE_SIDEBAR_WIDTH = 224
MAX_SIDEBAR_WIDTH = 320
SIDEBAR_WINDOW_RATIO = 0.18
DASHBOARD_WIDGET_ORDER_KEY = "overblik widget rækkefølge"
DASHBOARD_DEFAULT_WIDGET_ORDER = (
    "goal",
    "progress",
    "process",
    "holiday_pay",
    "estimates",
    "stats",
    "budget",
)

DASHBOARD_AVAILABLE_WIDGET_ORDER = DASHBOARD_DEFAULT_WIDGET_ORDER + (
    "breakdown",
    "recent",
    "salary_calculator",
)
DASHBOARD_BUDGET_WIDGET_MIGRATION_KEY = "overblik budget widget tilføjet"
DASHBOARD_HOLIDAY_PAY_WIDGET_MIGRATION_KEY = "overblik feriepenge widget tilføjet"
DASHBOARD_WIDGET_TITLES = {
    "goal": "Rådighedsmål",
    "progress": "Tidslinje",
    "process": "Løn indtil videre",
    "estimates": "Estimater",
    "stats": "Statistik",
    "holiday_pay": "Feriepenge",
    "budget": "Budget",
    "breakdown": "Skatteopdeling",
    "recent": "Vagter i perioden",
    "salary_calculator": "Lønberegner",
}
HOLIDAY_PAY_RATE_KEY = "feriegodtgørelse"
HOLIDAY_PAY_EMPLOYMENT_START_KEY = "ansættelsesstart"
DEFAULT_HOLIDAY_PAY_RATE = 12.5
HOLIDAY_PAY_FORECAST_MONTHS = 6

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
SHIFT_TABLE_MONTH_NAMES = {
    1: "januar",
    2: "februar",
    3: "marts",
    4: "april",
    5: "maj",
    6: "juni",
    7: "juli",
    8: "august",
    9: "september",
    10: "oktober",
    11: "november",
    12: "december",
}
SHIFT_TABLE_TIME_COLUMN_WIDTH = 176
DEFAULT_SHIFT_START_TIME = "14:00"
DEFAULT_SHIFT_END_TIME = "18:00"
DAY_OFF_ACCENT = "#38bdf8"
DAY_OFF_TEXT = "#075985"
HISTORY_PANEL_HEIGHT = 490

APP_STYLE = """
* {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
    color: #1f2933;
}
QMainWindow, QWidget#Content {
    background: #eef1f3;
}
QWidget#Sidebar {
    background: #1f2933;
}
QFrame#SidebarSeparator {
    background: #4b5563;
    border: 0;
    min-height: 1px;
    max-height: 1px;
}
QFrame#BrandPanel {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
}
QLabel#Brand {
    color: #ffffff;
    font-family: "Segoe UI Semibold", "Segoe UI", Arial, sans-serif;
    font-size: 22pt;
    font-weight: 850;
}
QLabel#BrandSub {
    color: #aeb7c1;
    font-size: 9pt;
}
QPushButton#PrimaryNavButton {
    background: transparent;
    color: #f8fafc;
    border: 0;
    border-radius: 7px;
    padding: 9px 16px 9px 18px;
    font-size: 10pt;
    text-align: left;
    font-weight: 750;
}
QPushButton#PrimaryNavButton:hover {
    background: rgba(255, 255, 255, 0.05);
}
QPushButton#PrimaryNavButton:checked {
    background: #1f8a70;
    color: white;
}
QPushButton#NavButton {
    background: transparent;
    color: #d8dee6;
    border: 0;
    border-radius: 7px;
    padding: 9px 16px 9px 18px;
    font-size: 10pt;
    text-align: left;
    font-weight: 600;
}
QPushButton#NavButton:hover {
    background: #2d3742;
}
QPushButton#NavButton:checked {
    background: #1f8a70;
    color: white;
}
QLabel#PageTitle {
    font-size: 22pt;
    font-weight: 750;
    color: #111827;
}
QLabel#PageSubtitle {
    color: #64707d;
}
QFrame#Card, QFrame#Panel {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 8px;
}
QFrame#DashboardSection {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 8px;
}
QLabel#PanelTitle {
    color: #111827;
    font-size: 12.5pt;
    font-weight: 850;
    background: transparent;
    border: 0;
}
QLabel#MetricTitle {
    color: #66717e;
    font-weight: 650;
}
QLabel#MetricValue {
    color: #111827;
    font-size: 18pt;
    font-weight: 800;
}
QLabel#MetricSub {
    color: #6b7280;
}
QPushButton {
    background: #1f8a70;
    color: #ffffff;
    border: 0;
    border-radius: 7px;
    padding: 5px 9px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton:hover {
    background: #18735d;
}
QPushButton:pressed {
    background: #125b4a;
}
QPushButton#SecondaryButton {
    background: #e7ecef;
    color: #1f2933;
}
QPushButton#SecondaryButton:hover {
    background: #d9e1e6;
}
QPushButton#SecondaryButton:checked {
    background: #1f8a70;
    color: #ffffff;
}
QPushButton#InlineButton {
    background: transparent;
    color: #1f8a70;
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    padding: 3px 7px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#InlineButton:hover {
    background: #edf7f4;
}
QPushButton#InfoButton {
    background: #ffffff;
    color: #1f8a70;
    border: 1px solid #cfd8e3;
    border-radius: 12px;
    padding: 0;
    font-size: 9pt;
    font-weight: 900;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#InfoButton:hover {
    background: #edf7f4;
    border-color: #1f8a70;
}
QLabel#SettingsSectionLabel {
    color: #111827;
    font-size: 10pt;
    font-weight: 900;
    padding-top: 10px;
}
QLabel#SettingsSectionHint {
    color: #6b7280;
    font-size: 9pt;
}
QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 24px;
}
QComboBox {
    padding-right: 38px;
}
QComboBox::drop-down {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1px solid #cfd8e3;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background: #f4f7f9;
}
QComboBox::drop-down:hover {
    background: #e7ecef;
}
QComboBox::down-arrow {
    width: 0;
    height: 0;
    image: none;
    border: 0;
}
QListView#ModernComboPopup {
    background: #ffffff;
    border: 1px solid #cfd8e3;
    border-radius: 8px;
    padding: 5px;
    outline: 0;
    selection-background-color: transparent;
    selection-color: #111827;
}
QListView#ModernComboPopup::item {
    min-height: 30px;
    padding: 6px 10px;
    border-radius: 6px;
    color: #1f2933;
}
QListView#ModernComboPopup::item:hover {
    background: #f1f5f9;
}
QListView#ModernComboPopup::item:selected {
    background: #e5f3ef;
    color: #111827;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #1f8a70;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f7f9fb;
    border: 1px solid #dde3ea;
    border-radius: 8px;
    gridline-color: #e7ecef;
    selection-background-color: #d9f0ea;
    selection-color: #111827;
}
QHeaderView::section {
    background: #f4f7f9;
    color: #4b5563;
    border: 0;
    border-bottom: 1px solid #dde3ea;
    padding: 8px;
    font-weight: 750;
}
QCheckBox#ShiftRowCheckBox {
    background: transparent;
    spacing: 0;
}
QCheckBox#ShiftRowCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #7b8794;
    border-radius: 3px;
    background: #ffffff;
}
QCheckBox#ShiftRowCheckBox::indicator:hover {
    border: 1px solid #1f8a70;
    background: #edf7f4;
}
QCheckBox#ShiftRowCheckBox::indicator:checked {
    border: 1px solid #1f8a70;
    background: #1f8a70;
}
QCheckBox#ShiftRowCheckBox::indicator:checked:hover {
    background: #18735d;
}
QScrollArea {
    background: transparent;
    border: 0;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QWidget#PageBody {
    background: transparent;
}
QTabWidget::pane {
    border: 0;
}
QTabBar::tab {
    background: #e7ecef;
    border-radius: 7px;
    padding: 10px 18px;
    margin-right: 8px;
    min-width: 74px;
    color: #42505f;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: #1f8a70;
    color: white;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px 4px 2px;
}
QScrollBar::handle:vertical {
    background: #c7d0d9;
    border-radius: 5px;
    min-height: 34px;
}
QScrollBar::handle:vertical:hover {
    background: #9aa7b4;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
    border: 0;
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px 4px 2px 4px;
}
QScrollBar::handle:horizontal {
    background: #c7d0d9;
    border-radius: 5px;
    min-width: 34px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
    border: 0;
    width: 0;
}
"""


# Temporary startup/window debug logging. Set LONIX_WINDOW_DEBUG=1 to enable it.
# Set LONIX_WINDOW_DEBUG_VERBOSE=1 to include parent-change/hide-to-parent noise.
WINDOW_DEBUG_ENABLED = os.environ.get("LONIX_WINDOW_DEBUG", "0") == "1"
WINDOW_DEBUG_VERBOSE = os.environ.get("LONIX_WINDOW_DEBUG_VERBOSE", "0") == "1"
_WINDOW_DEBUG_START = time.monotonic()


def debug_window_log(message):
    if WINDOW_DEBUG_ENABLED:
        elapsed = time.monotonic() - _WINDOW_DEBUG_START
        print(f"[window-debug {elapsed:7.3f}s] {message}", flush=True)


def describe_widget(widget):
    parent = widget.parentWidget()
    geometry = widget.geometry()
    object_name = widget.objectName() or "-"
    title = widget.windowTitle() or "-"
    return (
        f"{type(widget).__name__}(object={object_name!r}, title={title!r}, "
        f"visible={widget.isVisible()}, isWindow={widget.isWindow()}, "
        f"native={widget.testAttribute(Qt.WA_NativeWindow)}, "
        f"parent={type(parent).__name__ if parent is not None else None}, "
        f"geom={geometry.x()},{geometry.y()} {geometry.width()}x{geometry.height()})"
    )


def debug_widget_inventory(label, limit=30):
    if not WINDOW_DEBUG_ENABLED:
        return

    app = QApplication.instance()
    if app is None:
        return

    all_widgets = list(QApplication.allWidgets())
    top_level_widgets = list(QApplication.topLevelWidgets())
    parentless_widgets = [widget for widget in all_widgets if widget.parentWidget() is None]
    native_widgets = [widget for widget in all_widgets if widget.testAttribute(Qt.WA_NativeWindow)]
    debug_window_log(
        f"{label}: all={len(all_widgets)} topLevel={len(top_level_widgets)} "
        f"parentless={len(parentless_widgets)} native={len(native_widgets)}"
    )
    for widget in top_level_widgets[:limit]:
        debug_window_log(f"  topLevel {describe_widget(widget)}")
    for widget in parentless_widgets[:limit]:
        if widget not in top_level_widgets:
            debug_window_log(f"  parentless-not-topLevel {describe_widget(widget)}")
    for widget in native_widgets[:limit]:
        if widget not in top_level_widgets and widget.parentWidget() is not None:
            debug_window_log(f"  native-child {describe_widget(widget)}")


class WindowDebugEventFilter(QObject):
    EVENT_NAMES = {
        QEvent.Close: "Close",
        QEvent.Hide: "Hide",
        QEvent.HideToParent: "HideToParent",
        QEvent.ParentChange: "ParentChange",
        QEvent.Show: "Show",
        QEvent.ShowToParent: "ShowToParent",
        QEvent.WindowActivate: "WindowActivate",
        QEvent.WindowDeactivate: "WindowDeactivate",
    }

    def eventFilter(self, obj, event):
        event_name = self.EVENT_NAMES.get(event.type())
        if event_name and isinstance(obj, QWidget):
            interesting_event = event.type() in (
                QEvent.Close,
                QEvent.Hide,
                QEvent.Show,
                QEvent.WindowActivate,
                QEvent.WindowDeactivate,
            )
            if not interesting_event and not WINDOW_DEBUG_VERBOSE:
                return super().eventFilter(obj, event)

            is_suspect = (
                obj.isWindow()
                or obj.parentWidget() is None
                or obj.testAttribute(Qt.WA_NativeWindow)
            )
            if is_suspect:
                debug_window_log(f"event {event_name}: {describe_widget(obj)}")
                if event.type() in (QEvent.Show, QEvent.Hide, QEvent.Close):
                    debug_widget_inventory(f"inventory after {event_name} {type(obj).__name__}", limit=12)
        return super().eventFilter(obj, event)


def ensure_storage():
    if not os.path.exists("data"):
        os.mkdir("data")
    ft.load_data()
    ft.load_settings()


def has_required_settings(settings):
    return isinstance(settings, dict) and all(key in settings for key in REQUIRED_KEYS)


def dashboard_widget_order(settings):
    if not isinstance(settings, dict) or DASHBOARD_WIDGET_ORDER_KEY not in settings:
        return list(DASHBOARD_DEFAULT_WIDGET_ORDER)

    raw_order = settings.get(DASHBOARD_WIDGET_ORDER_KEY, [])
    if not isinstance(raw_order, list):
        return list(DASHBOARD_DEFAULT_WIDGET_ORDER)

    seen = set()
    order = []
    for key in raw_order:
        if key not in DASHBOARD_AVAILABLE_WIDGET_ORDER or key in seen:
            continue
        seen.add(key)
        order.append(key)
    if not settings.get(DASHBOARD_BUDGET_WIDGET_MIGRATION_KEY, False) and "budget" not in order:
        insert_index = order.index("stats") + 1 if "stats" in order else len(order)
        order.insert(insert_index, "budget")
    if not settings.get(DASHBOARD_HOLIDAY_PAY_WIDGET_MIGRATION_KEY, False) and "holiday_pay" not in order:
        insert_index = order.index("process") + 1 if "process" in order else len(order)
        order.insert(insert_index, "holiday_pay")
    return order


def parse_date_key(value):
    return datetime.strptime(value, "%d-%m-%Y").date()


def date_to_key(value):
    return value.strftime("%d-%m-%Y")


def default_entry_date():
    now = datetime.now()
    entry_date = now.date()
    if now.time().hour < 4:
        entry_date = entry_date - timedelta(days=1)
    return entry_date


def first_work_entry_date(data):
    first_work_date = None
    first_any_date = None
    for entry in data or []:
        try:
            dato_str, info = next(iter(entry.items()))
            dato = parse_date_key(dato_str)
        except (StopIteration, TypeError, ValueError):
            continue

        if first_any_date is None or dato < first_any_date:
            first_any_date = dato
        if not ft.is_day_off(info) and (first_work_date is None or dato < first_work_date):
            first_work_date = dato
    return first_work_date or first_any_date


def format_number(value, decimals=2):
    if value is None:
        return "N/A"
    if decimals <= 0:
        return f"{float(value):.0f}"
    return f"{float(value):.{decimals}f}".rstrip("0").rstrip(".")


def format_money(value, decimals=0):
    if value is None:
        return "N/A"
    return f"{format_number(value, decimals)} kr."


def format_date(value):
    if value is None:
        return "N/A"
    return value.strftime("%d-%m-%Y")


def format_long_date(value):
    if value is None:
        return "N/A"
    month_name = SHIFT_TABLE_MONTH_NAMES.get(value.month, str(value.month))
    return f"{value.day:02d} {month_name} {value.year}"


def format_shift_table_date(value):
    if value is None:
        return "N/A"
    month_name = SHIFT_TABLE_MONTH_NAMES.get(value.month, str(value.month))
    text = f"{value.day:02d} {month_name}"
    if value <= datetime.now().date() - timedelta(days=365):
        text = f"{text} {value.year}"
    return text


def parse_number_text(value):
    cleaned = value.strip().lower()
    for token in ["kr.", "kr", "t.", "timer", "time", "d.", "%"]:
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.replace(" ", "")

    if "," in cleaned and "." in cleaned:
        # Dansk format: 1.234,56
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", ".")
    if not cleaned:
        raise ValueError("Tomt talfelt")
    return float(cleaned)


def parse_positive_number(field, label, allow_zero=False):
    try:
        value = parse_number_text(field.text())
    except ValueError as error:
        raise ValueError(f"{label} skal være et tal.") from error

    if allow_zero:
        if value < 0:
            raise ValueError(f"{label} må ikke være under 0.")
    elif value <= 0:
        raise ValueError(f"{label} skal være over 0.")
    return value


def parse_int_field(field, label, minimum=0, maximum=1_000_000):
    value = parse_positive_number(field, label, allow_zero=True)
    if int(value) != value:
        raise ValueError(f"{label} skal være et helt tal.")
    value = int(value)
    if value < minimum or value > maximum:
        raise ValueError(f"{label} skal være mellem {minimum} og {maximum}.")
    return value


def parse_pause_hours(field):
    if not field.text().strip():
        return 0.0
    minutes = parse_positive_number(field, "Pause", allow_zero=True)
    return minutes / 60


def parse_date_text(value):
    try:
        return datetime.strptime(value.strip(), "%d-%m-%Y").date()
    except ValueError as error:
        raise ValueError("Dato skal skrives som dd-mm-åååå, fx 02-05-2026.") from error


def parse_optional_settings_date(value):
    if not value:
        return None
    text = str(value).strip()
    for pattern in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def parse_clock_minutes(value):
    return ft.parse_clock_minutes(value)


def calculate_hours_from_times(start_text, end_text):
    return ft.calculate_hours_from_times(start_text, end_text)


def normalize_clock_text(value):
    return ft.normalize_clock_text(value)


def shift_time_interval(row):
    return ft.shift_time_interval(row)


def intervals_overlap(first, second):
    return ft.intervals_overlap(first, second)


def rows_on_date(rows, target_date, exclude_ids=None):
    return ft.rows_on_date(rows, target_date, exclude_ids)


def date_has_day_off(rows, target_date, exclude_ids=None):
    return any(row.get("is_day_off") for row in rows_on_date(rows, target_date, exclude_ids))


def find_time_overlap(row, rows, exclude_ids=None):
    return ft.find_time_overlap(row, rows, exclude_ids)


def validate_shift_conflicts(rows):
    by_date = {}
    for row in rows:
        by_date.setdefault(row.get("dato"), []).append(row)

    for row_date, date_rows in by_date.items():
        has_day_off = any(row.get("is_day_off") for row in date_rows)
        has_work = any(not row.get("is_day_off") for row in date_rows)
        if has_day_off and has_work:
            raise ValueError(f"{format_date(row_date)} er markeret som fridag og kan ikke samtidig have vagter.")

        work_rows = [row for row in date_rows if not row.get("is_day_off")]
        for index, row in enumerate(work_rows):
            overlap = find_time_overlap(row, work_rows[index + 1:])
            if overlap is not None:
                raise ValueError(
                    f"Vagterne {format_work_time(row)} og {format_work_time(overlap)} overlapper den {format_date(row_date)}."
                )


def most_used_shift_time(data, key, fallback):
    time_stats = {}
    for entry_index, entry in enumerate(data or []):
        try:
            _, info = next(iter(entry.items()))
        except (AttributeError, StopIteration):
            continue
        if ft.is_day_off(info):
            continue

        time_text = normalize_clock_text(info.get(key))
        if time_text is None:
            continue

        stats = time_stats.setdefault(time_text, {"count": 0, "latest_index": -1})
        stats["count"] += 1
        stats["latest_index"] = max(stats["latest_index"], entry_index)

    if not time_stats:
        return fallback

    return max(
        time_stats.items(),
        key=lambda item: (item[1]["count"], item[1]["latest_index"]),
    )[0]


def default_shift_times(data):
    return (
        most_used_shift_time(data, "start", DEFAULT_SHIFT_START_TIME),
        most_used_shift_time(data, "slut", DEFAULT_SHIFT_END_TIME),
    )


def set_field_number(field, value, decimals=2):
    field.setText(format_number(float(value), decimals))


def pause_minutes(value):
    return max(0.0, float(value or 0) * 60)


def format_pause_minutes(value):
    return format_number(pause_minutes(value))


def make_text_input(text="", placeholder=""):
    field = QLineEdit()
    field.setText(str(text))
    field.setPlaceholderText(placeholder)
    return field


class ModernComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setObjectName("ModernComboBox")
        self.setMinimumWidth(176)
        self.setMaxVisibleItems(8)

        popup = QListView()
        popup.setObjectName("ModernComboPopup")
        popup.setFrameShape(QFrame.NoFrame)
        popup.setUniformItemSizes(True)
        popup.setSpacing(2)
        popup.setFocusPolicy(Qt.NoFocus)
        popup.setEditTriggers(QAbstractItemView.NoEditTriggers)
        popup.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setView(popup)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#64748b"), 1.8)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        center_y = self.height() / 2 + 1
        center_x = self.width() - 17
        painter.drawLine(QPointF(center_x - 4, center_y - 2), QPointF(center_x, center_y + 2))
        painter.drawLine(QPointF(center_x, center_y + 2), QPointF(center_x + 4, center_y - 2))

    def showPopup(self):
        self.view().setMinimumWidth(self.width())
        super().showPopup()
        QTimer.singleShot(0, self._move_popup_below_field)

    def _move_popup_below_field(self):
        popup = self.view().window()
        if popup is None or not popup.isVisible():
            return

        popup_width = max(self.width(), self.view().sizeHintForColumn(0) + 34)
        popup.resize(popup_width, popup.height())
        popup.move(self.mapToGlobal(self.rect().bottomLeft()) + QPointF(0, 4).toPoint())


BasePushButton = QPushButton


class AnimatedButton(BasePushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._button_inset = 1
        self._button_inset_animation = QPropertyAnimation(self, b"buttonInset", self)
        self._button_inset_animation.setDuration(100)
        self._button_inset_animation.setEasingCurve(QEasingCurve.OutCubic)

    @pyqtProperty(int)
    def buttonInset(self):
        return self._button_inset

    @buttonInset.setter
    def buttonInset(self, value):
        self._button_inset = max(0, min(2, int(value)))
        self.update()

    def sizeHint(self):
        size = super().sizeHint()
        if self._generic_animation_enabled():
            size += QSize(4, 2)
        return size

    def minimumSizeHint(self):
        size = super().minimumSizeHint()
        if self._generic_animation_enabled():
            size += QSize(4, 2)
        return size

    def _generic_animation_enabled(self):
        return not bool(self.property("skipGenericButtonAnimation"))

    def _animate_inset(self, target, duration=120, easing=QEasingCurve.OutCubic):
        if not self._generic_animation_enabled() or not self.isEnabled():
            return
        self._button_inset_animation.stop()
        self._button_inset_animation.setStartValue(self._button_inset)
        self._button_inset_animation.setEndValue(target)
        self._button_inset_animation.setDuration(duration)
        self._button_inset_animation.setEasingCurve(easing)
        self._button_inset_animation.start()

    def enterEvent(self, event):
        self._animate_inset(0, 105, QEasingCurve.OutCubic)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_inset(1, 95, QEasingCurve.OutCubic)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._animate_inset(2, 55, QEasingCurve.OutCubic)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._animate_inset(0 if self.underMouse() else 1, 120, QEasingCurve.OutCubic)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        if not self._generic_animation_enabled():
            super().paintEvent(event)
            return

        painter = QStylePainter(self)
        bevel_option = QStyleOptionButton()
        self.initStyleOption(bevel_option)
        inset = self._button_inset
        bevel_option.rect = self.rect().adjusted(inset, inset, -inset, -inset)
        painter.drawControl(QStyle.CE_PushButtonBevel, bevel_option)

        label_option = QStyleOptionButton()
        self.initStyleOption(label_option)
        label_option.rect = self.rect().adjusted(4, 0, -4, 0)
        painter.drawControl(QStyle.CE_PushButtonLabel, label_option)


QPushButton = AnimatedButton


class SidebarNavButton(BasePushButton):
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        self._nav_progress = 0
        self._is_pressed = False
        self.nav_animation = QPropertyAnimation(self, b"navProgress", self)
        self.nav_animation.setDuration(150)
        self.nav_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("skipGenericButtonAnimation", True)
        self.toggled.connect(self._sync_nav_state)

    @pyqtProperty(int)
    def navProgress(self):
        return self._nav_progress

    @navProgress.setter
    def navProgress(self, value):
        self._nav_progress = max(0, min(100, int(value)))
        self.update()

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(size.width() + 8, max(size.height(), 34))

    def minimumSizeHint(self):
        size = super().minimumSizeHint()
        return QSize(size.width() + 8, max(size.height(), 34))

    def _animate_nav(self, target, duration=150, easing=QEasingCurve.OutCubic):
        self.nav_animation.stop()
        self.nav_animation.setStartValue(self._nav_progress)
        self.nav_animation.setEndValue(target)
        self.nav_animation.setDuration(duration)
        self.nav_animation.setEasingCurve(easing)
        self.nav_animation.start()

    def _sync_nav_state(self):
        self._animate_nav(100 if self.isChecked() or self.underMouse() else 0)

    def enterEvent(self, event):
        self._animate_nav(100, 170, QEasingCurve.OutCubic)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self._animate_nav(0, 130, QEasingCurve.OutCubic)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_pressed = False
            self._sync_nav_state()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        progress = self._nav_progress / 100
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        if self.isChecked():
            background = QColor("#18735d" if self._is_pressed else "#1f8a70")
            painter.setPen(Qt.NoPen)
            painter.setBrush(background)
            painter.drawRoundedRect(rect, 7, 7)
        elif progress > 0:
            background = QColor("#2d3742")
            background.setAlpha(int(40 + (120 * progress)))
            painter.setPen(Qt.NoPen)
            painter.setBrush(background)
            painter.drawRoundedRect(rect, 7, 7)

        normal = QColor("#f8fafc") if self.objectName() == "PrimaryNavButton" else QColor("#d8dee6")
        active = QColor("#ffffff")
        text_color = QColor(
            int(normal.red() + (active.red() - normal.red()) * progress),
            int(normal.green() + (active.green() - normal.green()) * progress),
            int(normal.blue() + (active.blue() - normal.blue()) * progress),
        )
        font = QFont(self.font())
        base_size = font.pointSizeF()
        if base_size > 0:
            font.setPointSizeF(base_size + (0.55 * progress))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(text_color)

        left = 18 + (5 * progress)
        text_rect = QRectF(left, 0, self.width() - left - 12, self.height())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())


class AnimatedSegmentedTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_index = -1
        self.pressed_index = -1
        self._tab_pop = 0
        self.pop_animation = QPropertyAnimation(self, b"tabPop", self)
        self.pop_animation.setDuration(120)
        self.pop_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setMouseTracking(True)
        self.setDrawBase(False)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 9, QFont.Bold))

    @pyqtProperty(int)
    def tabPop(self):
        return self._tab_pop

    @tabPop.setter
    def tabPop(self, value):
        self._tab_pop = max(-2, min(3, int(value)))
        self.update()

    def tabSizeHint(self, index):
        text_width = self.fontMetrics().horizontalAdvance(self.tabText(index))
        return QSize(max(text_width + 48, 118), 42)

    def _animate_pop(self, value, duration=120, easing=QEasingCurve.OutCubic):
        self.pop_animation.stop()
        self.pop_animation.setStartValue(self._tab_pop)
        self.pop_animation.setEndValue(value)
        self.pop_animation.setDuration(duration)
        self.pop_animation.setEasingCurve(easing)
        self.pop_animation.start()

    def mouseMoveEvent(self, event):
        index = self.tabAt(event.pos())
        if index != self.hovered_index:
            self.hovered_index = index
            self._animate_pop(3 if index >= 0 else 0, 130, QEasingCurve.OutBack)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_index = -1
        self.pressed_index = -1
        self._animate_pop(0, 110, QEasingCurve.OutCubic)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed_index = self.tabAt(event.pos())
            if self.pressed_index >= 0:
                self._animate_pop(-2, 70, QEasingCurve.OutCubic)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed_index = -1
            self.hovered_index = self.tabAt(event.pos())
            self._animate_pop(3 if self.hovered_index >= 0 else 0, 150, QEasingCurve.OutBack)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.count() == 0:
            return

        outer = QRectF(self.tabRect(0))
        for index in range(1, self.count()):
            outer = outer.united(QRectF(self.tabRect(index)))
        outer.adjust(2, 3, -2, -3)
        painter.setPen(QPen(QColor("#cfd8e3"), 1))
        painter.setBrush(QColor("#e7ecef"))
        painter.drawRoundedRect(outer, 10, 10)

        for index in range(self.count()):
            rect = QRectF(self.tabRect(index)).adjusted(5, 6, -5, -6)
            selected = index == self.currentIndex()
            interactive = index == self.hovered_index or index == self.pressed_index
            pop = self._tab_pop if interactive else 0
            if pop > 0:
                rect.adjust(-pop, -pop, pop, pop)
            elif pop < 0:
                rect.adjust(-pop, -pop, pop, pop)

            if selected:
                fill = QColor("#1f8a70")
                border = QColor("#1f8a70")
                text_color = QColor("#ffffff")
            elif index == self.hovered_index:
                fill = QColor("#edf7f4")
                border = QColor("#9bcfc2")
                text_color = QColor("#0f766e")
            else:
                fill = QColor("#f6f8fa")
                border = QColor("#d7dee6")
                text_color = QColor("#42505f")

            painter.setPen(QPen(border, 1.2))
            painter.setBrush(fill)
            painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(text_color)
            painter.setFont(self.font())
            painter.drawText(rect, Qt.AlignCenter, self.tabText(index))


class VisibleCheckBox(QCheckBox):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(22, 22)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = 16
        left = (self.width() - size) / 2
        top = (self.height() - size) / 2
        box = QRectF(left, top, size, size)

        checked = self.isChecked()
        hovered = self.underMouse()
        border = QColor("#1f8a70" if checked or hovered else "#7b8794")
        fill = QColor("#1f8a70" if checked else ("#edf7f4" if hovered else "#ffffff"))

        painter.setPen(QPen(border, 1.4))
        painter.setBrush(fill)
        painter.drawRoundedRect(box, 3, 3)

        if checked:
            painter.setPen(QPen(QColor("#ffffff"), 2.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(QPointF(left + 4, top + 8), QPointF(left + 7, top + 11))
            painter.drawLine(QPointF(left + 7, top + 11), QPointF(left + 12, top + 5))


def set_form_row_visible(form, field, visible):
    row_widget = field.property("form_row_widget") if hasattr(field, "property") else None
    target = row_widget if row_widget is not None else field
    label = form.labelForField(target) or form.labelForField(field)
    if hasattr(form, "setRowVisible"):
        form.setRowVisible(target, visible)
        return
    if label is not None:
        label.setVisible(visible)
    target.setVisible(visible)


def format_period(period):
    return f"{format_date(period['periode_start'])} - {format_date(period['periode_slut'])}"


def format_short_date(value):
    if value is None:
        return "N/A"
    return value.strftime("%d-%m")


def format_short_date_with_month(value, include_year=False):
    if value is None:
        return "N/A"
    month_name = SHIFT_TABLE_MONTH_NAMES.get(value.month, str(value.month))
    text = f"{value.day:02d} {month_name}"
    if include_year:
        text = f"{text} {value.year}"
    return text


def format_period_without_year(period):
    include_year = period["periode_slut"] <= datetime.now().date() - timedelta(days=365)
    return (
        f"{format_short_date_with_month(period['periode_start'], include_year)} - "
        f"{format_short_date_with_month(period['periode_slut'], include_year)}"
    )


def month_title(period):
    month_name = MONTH_NAMES.get(period["periode_slut"].month, str(period["periode_slut"].month))
    return f"{month_name} {period['periode_slut'].year}"


def signed_number(value, suffix=""):
    if value is None:
        return "N/A"
    prefix = "+" if value > 0 else ""
    return f"{prefix}{format_number(value)}{suffix}"


def signed_money(value):
    if value is None:
        return "N/A"
    prefix = "+" if value > 0 else ""
    return f"{prefix}{format_money(value)}"


def average_or_none(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def entry_rows(data, settings=None):
    rows = []
    for index, entry in enumerate(data):
        dato_str, info = next(iter(entry.items()))
        dato = parse_date_key(dato_str)
        entry_id = ft.get_entry_id(info) or f"legacy-{dato_str}-{index}"
        entry_settings = ft.get_entry_settings(info, settings)
        is_day_off = ft.is_day_off(info)
        duration = ft.get_shift_duration_hours(info)
        pause = ft.get_shift_pause_hours(info)
        timer = ft.get_shift_paid_hours(info)
        timeløn = float(info.get("timeløn", 0))

        row = {
            "id": entry_id,
            "registreret": str(info.get(ft.ENTRY_CREATED_KEY, "")) if isinstance(info, dict) else "",
            "dato": dato,
            "varighed": duration,
            "timer": timer,
            "pause": pause,
            "timeløn": timeløn,
            "brutto": timer * timeløn,
            "is_day_off": is_day_off,
            "settings": entry_settings,
        }

        if info.get("start"):
            row["start"] = str(info.get("start"))

        if info.get("slut"):
            row["slut"] = str(info.get("slut"))

        rows.append(row)

    try:
        settings = settings if settings is not None else ft.load_settings()
        if has_required_settings(settings):
            periods = {}
            for row in rows:
                period_key = ft.get_salary_period_for_date(
                    row["dato"],
                    settings=row.get("settings", settings),
                )
                periods.setdefault(period_key, []).append(row)

            for (period_start, period_end), period_rows in periods.items():
                breakdown = ft.calculate_period_salary_breakdown(
                    [
                        {
                            "brutto": row["brutto"],
                            "timer": row["timer"],
                            "paid_hours": row["timer"],
                            "settings": row.get("settings", settings),
                        }
                        for row in period_rows
                    ],
                    period_start,
                    period_end,
                    settings,
                )
                for row, row_breakdown in zip(period_rows, breakdown.get("item_breakdowns", [])):
                    row["netto"] = row_breakdown["netto"]
    except (OSError, ValueError, TypeError):
        for row in rows:
            row["netto"] = 0.0

    for row in rows:
        row.setdefault("netto", 0.0)

    return sorted(
        rows,
        key=lambda row: (
            row["dato"],
            str(row.get("start", "")),
            str(row.get("id", "")),
        ),
        reverse=True,
    )


def save_entry_rows(rows):
    ensure_storage()
    clean_rows = sorted(rows, key=lambda row: row["dato"])
    validate_shift_conflicts(clean_rows)

    payload = []
    for row in clean_rows:
        entry_settings = ft.settings_snapshot(row.get("settings"))
        entry_id = str(row.get("id") or ft.new_entry_id())
        created_at = str(row.get("registreret") or datetime.now().isoformat(timespec="seconds"))
        if row.get("is_day_off"):
            payload.append(
                {
                    date_to_key(row["dato"]): {
                        ft.ENTRY_ID_KEY: entry_id,
                        ft.ENTRY_CREATED_KEY: created_at,
                        ft.ENTRY_SETTINGS_KEY: entry_settings,
                        ft.ENTRY_TYPE_KEY: ft.DAY_OFF_ENTRY_TYPE,
                        "timer": 0,
                        "timeløn": 0,
                    }
                }
            )
            continue

        pause = max(0.0, float(row.get("pause", 0) or 0))
        duration = max(0.0, float(row.get("varighed", float(row["timer"]) + pause) or 0))
        entry_info = {
            ft.ENTRY_ID_KEY: entry_id,
            ft.ENTRY_CREATED_KEY: created_at,
            ft.ENTRY_SETTINGS_KEY: entry_settings,
            "timer": duration,
            "timeløn": float(row["timeløn"]),
        }

        if pause > 0:
            entry_info["pause"] = pause

        start = row.get("start")
        slut = row.get("slut")
        if start and slut:
            entry_info["start"] = str(start)
            entry_info["slut"] = str(slut)

        payload.append(
            {
                date_to_key(row["dato"]): entry_info
            }
        )

    ft.save_all_data(payload)


def upsert_entry(
    entry_date,
    hours,
    rate,
    original_id=None,
    start=None,
    slut=None,
    pause=0,
    entry_settings=None,
    replace_date=False,
):
    rows = entry_rows(ft.load_data())
    new_id = str(original_id or ft.new_entry_id())
    existing_row = next((row for row in rows if str(row.get("id")) == new_id), {})
    if replace_date:
        rows = [row for row in rows if row["dato"] != entry_date]
    else:
        rows = [row for row in rows if str(row.get("id")) != new_id]

    duration = float(hours)
    pause = max(0.0, float(pause or 0))
    paid_hours = max(0.0, duration - pause)

    new_row = {
        "id": new_id,
        "dato": entry_date,
        "varighed": duration,
        "timer": paid_hours,
        "pause": pause,
        "timeløn": float(rate),
        "brutto": paid_hours * float(rate),
        "settings": ft.settings_snapshot(entry_settings),
    }
    if existing_row.get("registreret"):
        new_row["registreret"] = existing_row.get("registreret")

    if start and slut:
        new_row["start"] = str(start)
        new_row["slut"] = str(slut)

    rows.append(new_row)
    save_entry_rows(rows)
    return new_id


def upsert_day_off(entry_date, original_id=None, entry_settings=None):
    rows = entry_rows(ft.load_data())
    new_id = str(original_id or ft.new_entry_id())
    rows = [row for row in rows if str(row.get("id")) != new_id]
    rows.append(
        {
            "id": new_id,
            "dato": entry_date,
            "varighed": 0.0,
            "timer": 0.0,
            "pause": 0.0,
            "timeløn": 0.0,
            "brutto": 0.0,
            "is_day_off": True,
            "settings": ft.settings_snapshot(entry_settings),
        }
    )
    save_entry_rows(rows)
    return new_id


def delete_entry(entry_id):
    rows = [row for row in entry_rows(ft.load_data()) if str(row.get("id")) != str(entry_id)]
    save_entry_rows(rows)


def last_rate(data, settings=None):
    rows = entry_rows(data, settings)
    for row in rows:
        if not row.get("is_day_off"):
            return row["timeløn"]
    return ft.get_default_hourly_rate(settings)


def overview_row_with_current_settings(row, settings):
    settings = ft.normalize_settings(settings)
    clean_row = dict(row)
    clean_row["settings"] = settings
    if clean_row.get("is_day_off"):
        clean_row["timer"] = 0.0
        clean_row["brutto"] = 0.0
        return clean_row

    duration = max(0.0, float(clean_row.get("varighed", 0) or 0))
    pause = max(0.0, float(clean_row.get("pause", 0) or 0))
    paid_hours = duration if settings.get(ft.PAID_BREAK_KEY, False) else max(0.0, duration - pause)
    hourly_rate = float(clean_row.get("timeløn", 0) or 0)
    clean_row["timer"] = paid_hours
    clean_row["brutto"] = paid_hours * hourly_rate
    return clean_row


def current_period_summary(data, settings, today=None):
    today = today or datetime.now().date()
    if not has_required_settings(settings):
        return None

    current_settings = ft.normalize_settings(settings)
    periode_start, periode_slut = ft.get_salary_period_for_date(
        today,
        settings=current_settings,
    )

    rows = [
        overview_row_with_current_settings(row, current_settings)
        for row in entry_rows(data, current_settings)
        if periode_start <= row["dato"] <= periode_slut
    ]

    work_rows = [row for row in rows if not row.get("is_day_off")]
    day_off_rows = [row for row in rows if row.get("is_day_off")]
    timer = sum(row["timer"] for row in work_rows)
    brutto = sum(row["brutto"] for row in work_rows)
    calculation_items = [
        {
            "brutto": row["brutto"],
            "timer": row["timer"],
            "paid_hours": row["timer"],
            "settings": current_settings,
        }
        for row in rows
    ]
    breakdown = ft.calculate_period_salary_breakdown(
        calculation_items,
        periode_start,
        periode_slut,
        current_settings,
    )
    for row, row_breakdown in zip(rows, breakdown.get("item_breakdowns", [])):
        row["netto"] = row_breakdown["netto"]
        row["settings"] = current_settings

    return {
        "periode_start": periode_start,
        "periode_slut": periode_slut,
        "timer": timer,
        "brutto": brutto,
        "netto": breakdown["netto"],
        "breakdown": breakdown,
        "other_income": ft.get_other_income(current_settings, periode_start, periode_slut),
        "budget_expenses": ft.calculate_budget_expenses(current_settings, periode_start, periode_slut),
        "disposable_goal": ft.get_disposable_income_goal(current_settings, periode_start, periode_slut),
        "rows": rows,
        "work_rows": work_rows,
        "day_off_rows": day_off_rows,
    }


def last_complete_period_info(data, settings, today=None):
    today = today or datetime.now().date()
    if not has_required_settings(settings):
        return None

    current_settings = ft.normalize_settings(settings)
    periods, _ = build_periods(data, current_settings)
    past_periods = [
        period
        for period in periods
        if ft.is_period_complete(period["periode_start"], period["periode_slut"], today)
    ]
    if not past_periods:
        return None

    period = max(past_periods, key=lambda item: item["periode_slut"])
    other_income = period.get("anden_indkomst", 0)
    budget_expenses = period.get("budget_expenses", 0)
    total_income = period["netto"] + other_income
    return {
        "periode_start": period["periode_start"],
        "periode_slut": period["periode_slut"],
        "netto": period["netto"],
        "other_income": other_income,
        "budget_expenses": budget_expenses,
        "available": total_income - budget_expenses,
    }


def next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def month_range(start, end):
    if end < start:
        return []
    current = date(start.year, start.month, 1)
    months = []
    while current <= end:
        last_day = monthrange(current.year, current.month)[1]
        month_start = current
        month_end = date(current.year, current.month, last_day)
        months.append((month_start, month_end))
        next_year, next_month_number = next_month(current.year, current.month)
        current = date(next_year, next_month_number, 1)
    return months


def current_holiday_year(today=None):
    return ft.get_holiday_year(today)


def holiday_pay_settings(settings):
    settings = settings if isinstance(settings, dict) else {}
    try:
        raw_rate = settings.get(HOLIDAY_PAY_RATE_KEY, DEFAULT_HOLIDAY_PAY_RATE)
        rate = parse_number_text(str(raw_rate)) if isinstance(raw_rate, str) else float(raw_rate or DEFAULT_HOLIDAY_PAY_RATE)
        rate = max(0.0, rate)
    except (TypeError, ValueError):
        rate = DEFAULT_HOLIDAY_PAY_RATE
    return {
        "rate": rate,
        "employment_start": parse_optional_settings_date(settings.get(HOLIDAY_PAY_EMPLOYMENT_START_KEY)),
    }


def holiday_days_for_range(start, end):
    return ft.calculate_holiday_days_for_range(start, end)


def _blend_rate(current_rate, historical_rate, progress_ratio):
    if current_rate is None and historical_rate is None:
        return None
    if current_rate is None:
        return historical_rate
    if historical_rate is None:
        return current_rate
    progress_ratio = max(0.0, min(float(progress_ratio), 1.0))
    return (historical_rate * (1 - progress_ratio)) + (current_rate * progress_ratio)


def _holiday_pay_forecast_daily_salary(rows, settings, today):
    if not has_required_settings(settings):
        return None

    period_start, period_end = ft.get_salary_period_for_date(today, settings=settings)
    period_days = max(1, (period_end - period_start).days + 1)
    elapsed_days = min(max((today - period_start).days + 1, 1), period_days)
    progress_ratio = elapsed_days / period_days

    current_brutto = sum(
        ft.get_holiday_eligible_salary(row, row.get("settings", settings))
        for row in rows
        if not row.get("is_day_off") and period_start <= row["dato"] <= today
    )
    current_daily_brutto = current_brutto / elapsed_days

    historical_periods = {}
    for row in rows:
        if row.get("is_day_off"):
            continue

        entry_period_start, entry_period_end = ft.get_salary_period_for_date(
            row["dato"],
            settings=settings,
        )
        if entry_period_end >= period_start:
            continue

        period = historical_periods.setdefault(
            (entry_period_start, entry_period_end),
            {
                "brutto": 0.0,
                "days": (entry_period_end - entry_period_start).days + 1,
            },
        )
        period["brutto"] += ft.get_holiday_eligible_salary(row, row.get("settings", settings))

    historical_daily_brutto = None
    if historical_periods:
        historical_days = sum(period["days"] for period in historical_periods.values())
        historical_brutto = sum(period["brutto"] for period in historical_periods.values())
        if historical_days > 0:
            historical_daily_brutto = historical_brutto / historical_days
    else:
        past_rows = [
            row
            for row in rows
            if not row.get("is_day_off") and row["dato"] <= today
        ]
        if past_rows:
            first_date = min(row["dato"] for row in past_rows)
            observed_days = max(1, (today - first_date).days + 1)
            historical_daily_brutto = sum(
                ft.get_holiday_eligible_salary(row, row.get("settings", settings))
                for row in past_rows
            ) / observed_days

    return _blend_rate(current_daily_brutto, historical_daily_brutto, progress_ratio)


def estimate_holiday_pay_total(rows, settings, today, calculation_start, calculation_end, ferie_end, current_holiday_pay, rate):
    forecast_horizon = add_months(today, HOLIDAY_PAY_FORECAST_MONTHS)
    forecast_end = min(forecast_horizon, ferie_end)
    forecast_holiday_days = holiday_days_for_range(calculation_start, forecast_end) if forecast_end >= calculation_start else 0.0
    if forecast_end <= calculation_end:
        return {
            "forecast_horizon": forecast_horizon,
            "forecast_end": forecast_end,
            "forecast_total_holiday_pay": current_holiday_pay,
            "forecast_future_holiday_pay": 0.0,
            "forecast_holiday_days": forecast_holiday_days,
        }

    forecast_start = max(calculation_end + timedelta(days=1), calculation_start)
    if forecast_start > forecast_end:
        future_salary = 0.0
    else:
        future_rows = [
            row
            for row in rows
            if not row.get("is_day_off") and forecast_start <= row["dato"] <= forecast_end
        ]
        known_future_salary = sum(
            ft.get_holiday_eligible_salary(row, row.get("settings", settings))
            for row in future_rows
        )
        known_future_dates = {row["dato"] for row in future_rows}
        future_days = (forecast_end - forecast_start).days + 1
        unknown_future_days = max(0, future_days - len(known_future_dates))
        daily_brutto = _holiday_pay_forecast_daily_salary(rows, settings, today)
        estimated_future_salary = (daily_brutto or 0.0) * unknown_future_days
        future_salary = known_future_salary + estimated_future_salary

    future_holiday_pay = ft.calculate_holiday_pay_amount(future_salary, rate)
    return {
        "forecast_horizon": forecast_horizon,
        "forecast_end": forecast_end,
        "forecast_total_holiday_pay": current_holiday_pay + future_holiday_pay,
        "forecast_future_holiday_pay": future_holiday_pay,
        "forecast_holiday_days": forecast_holiday_days,
    }


def month_label(value):
    month_name = MONTH_NAMES.get(value.month, str(value.month))
    return f"{month_name} {value.year}"


def holiday_pay_calculation(data, settings, today=None):
    today = today or datetime.now().date()
    settings = ft.normalize_settings(settings if isinstance(settings, dict) else {})
    config = holiday_pay_settings(settings)
    ferie_start, ferie_end, request_end = current_holiday_year(today)
    request_start = ferie_start

    base = {
        "configured": False,
        "rate": config["rate"],
        "employment_start": config["employment_start"],
        "ferie_start": ferie_start,
        "ferie_end": ferie_end,
        "request_start": request_start,
        "request_end": request_end,
        "reason": "",
    }
    if config["employment_start"] is None:
        config["employment_start"] = first_work_entry_date(data)
        if config["employment_start"] is None:
            base["reason"] = "Angiv ansættelsesstart for at beregne feriepenge."
            return base
        base["employment_start"] = config["employment_start"]

    calculation_start = max(ferie_start, config["employment_start"])
    calculation_end = min(today, ferie_end)
    has_active_range = calculation_end >= calculation_start
    rows = [
        overview_row_with_current_settings(row, settings)
        for row in entry_rows(data, settings)
    ]
    work_rows = [
        row
        for row in rows
        if not row.get("is_day_off") and has_active_range and calculation_start <= row["dato"] <= calculation_end
    ]
    eligible_salary = sum(ft.get_holiday_eligible_salary(row, row.get("settings", settings)) for row in work_rows)
    holiday_pay = ft.calculate_holiday_pay_amount(eligible_salary, config["rate"])
    holiday_days = holiday_days_for_range(calculation_start, calculation_end) if has_active_range else 0.0
    period_eligible_salary = 0.0
    period_holiday_pay = 0.0
    period_start = None
    period_end = None
    if has_required_settings(settings):
        period_start, period_end = ft.get_salary_period_for_date(
            today,
            settings=settings,
        )
        period_eligible_salary = sum(
            ft.get_holiday_eligible_salary(row, row.get("settings", settings))
            for row in work_rows
            if period_start <= row["dato"] <= period_end
        )
        period_holiday_pay = ft.calculate_holiday_pay_amount(period_eligible_salary, config["rate"])

    monthly_rows = []
    if has_active_range:
        for month_start, month_end in month_range(calculation_start, calculation_end):
            active_start = max(calculation_start, month_start)
            active_end = min(calculation_end, month_end)
            salary = sum(
                ft.get_holiday_eligible_salary(row, row.get("settings", settings))
                for row in work_rows
                if active_start <= row["dato"] <= active_end
            )
            monthly_rows.append(
                {
                    "label": month_label(month_start),
                    "start": active_start,
                    "end": active_end,
                    "salary": salary,
                    "holiday_pay": ft.calculate_holiday_pay_amount(salary, config["rate"]),
                    "holiday_days": holiday_days_for_range(active_start, active_end),
                }
            )

    forecast = estimate_holiday_pay_total(
        rows,
        settings,
        today,
        calculation_start,
        calculation_end if has_active_range else calculation_start - timedelta(days=1),
        ferie_end,
        holiday_pay,
        config["rate"],
    )

    base.update(
        {
            "configured": True,
            "calculation_start": calculation_start,
            "calculation_end": calculation_end if has_active_range else calculation_start,
            "eligible_salary": eligible_salary,
            "holiday_pay": holiday_pay,
            "period_start": period_start,
            "period_end": period_end,
            "period_eligible_salary": period_eligible_salary,
            "period_holiday_pay": period_holiday_pay,
            "holiday_days": holiday_days,
            "work_rows": work_rows,
            "monthly_rows": monthly_rows,
            "request_available_now": request_start <= today <= request_end,
            **forecast,
        }
    )
    return base


def build_periods(data, settings):
    if not data or not has_required_settings(settings):
        return [], []
    _, periods, complete_periods, _, _ = statistik._build_dataset_context(data, settings)
    return periods, complete_periods


def table_item(value, align=Qt.AlignLeft | Qt.AlignVCenter):
    item = QTableWidgetItem(str(value))
    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    item.setTextAlignment(align)
    return item


def day_off_table_item(value, align=Qt.AlignLeft | Qt.AlignVCenter):
    item = table_item(value, align)
    item.setForeground(QBrush(QColor(DAY_OFF_TEXT)))
    font = item.font()
    font.setBold(True)
    item.setFont(font)
    return item


def count_work_rows(rows):
    return sum(1 for row in rows if not row.get("is_day_off"))


def count_day_off_rows(rows):
    return sum(1 for row in rows if row.get("is_day_off"))


def format_work_time(row):
    if row.get("is_day_off"):
        return "Fridag"

    start = row.get("start")
    slut = row.get("slut")
    hours_text = f"{format_number(row['timer'])} t."

    if start and slut:
        return f"{start} - {slut}\n{hours_text}"

    return hours_text


def load_logo_pixmap(size=None):
    if not LOGO_PATH or not os.path.exists(LOGO_PATH):
        return QPixmap()
    pixmap = QPixmap(LOGO_PATH)
    if pixmap.isNull() or size is None:
        return pixmap
    return pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def make_logo_label(size, object_name=None):
    pixmap = load_logo_pixmap(size)
    if pixmap.isNull():
        return None
    label = QLabel()
    if object_name:
        label.setObjectName(object_name)
    label.setPixmap(pixmap)
    label.setFixedSize(size)
    label.setAlignment(Qt.AlignCenter)
    return label


def app_icon():
    pixmap = load_logo_pixmap()
    return QIcon(pixmap) if not pixmap.isNull() else QIcon()


def success_icon_pixmap(size=42):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#16a34a"))
    margin = 3
    painter.drawEllipse(QRectF(margin, margin, size - (margin * 2), size - (margin * 2)))
    painter.setPen(QPen(QColor("#ffffff"), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawLine(QPointF(size * 0.28, size * 0.52), QPointF(size * 0.43, size * 0.67))
    painter.drawLine(QPointF(size * 0.43, size * 0.67), QPointF(size * 0.73, size * 0.35))
    painter.end()
    return pixmap


def show_success_message(parent, title, text):
    message = QMessageBox(parent)
    message.setWindowTitle(title)
    message.setWindowIcon(app_icon())
    message.setText(text)
    message.setIconPixmap(success_icon_pixmap())
    message.setStandardButtons(QMessageBox.Ok)
    message.exec_()


def setup_table(table, headers):
    table.setMinimumWidth(0)
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


def setup_shift_table_columns(table, time_column, check_column=None):
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    for column in range(table.columnCount()):
        header.setSectionResizeMode(column, QHeaderView.Stretch)
    header.setSectionResizeMode(time_column, QHeaderView.Interactive)
    table.setColumnWidth(time_column, SHIFT_TABLE_TIME_COLUMN_WIDTH)
    if check_column is not None:
        header.setSectionResizeMode(check_column, QHeaderView.ResizeToContents)
        table.setColumnWidth(check_column, 44)


def fit_table_height(table, row_count, max_rows=20, min_rows=1, bottom_padding=8):
    table.resizeRowsToContents()
    visible_rows = min(max(row_count, min_rows), max_rows)
    default_row_height = max(table.verticalHeader().defaultSectionSize(), table.fontMetrics().height() + 14, 30)
    row_height = sum(
        max(table.rowHeight(index), default_row_height) if index < row_count else default_row_height
        for index in range(visible_rows)
    )
    header_height = max(table.horizontalHeader().height(), table.horizontalHeader().sizeHint().height(), 34)
    height = header_height + row_height + (table.frameWidth() * 2) + bottom_padding
    table.setFixedHeight(max(header_height + default_row_height + 10, height))


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            clear_layout(child_layout)


def make_panel(title):
    panel = QFrame()
    panel.setObjectName("Panel")
    panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(16, 14, 16, 16)
    layout.setSpacing(12)
    if title:
        title_label = QLabel(title)
        title_label.setObjectName("PanelTitle")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(title_label)
    return panel, layout


def make_message(text):
    label = QLabel(text)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #66717e; padding: 26px;")
    return label


def bounded_window_sizes():
    screen = QApplication.primaryScreen()
    if screen is None:
        return BASE_WINDOW_SIZE, BASE_MINIMUM_WINDOW_SIZE

    available = screen.availableGeometry().size()
    max_width = max(720, int(available.width() * WINDOW_SCREEN_FILL_RATIO))
    max_height = max(520, int(available.height() * WINDOW_SCREEN_FILL_RATIO))

    minimum_width = min(BASE_MINIMUM_WINDOW_SIZE.width(), max_width)
    minimum_height = min(BASE_MINIMUM_WINDOW_SIZE.height(), max_height)
    target_width = min(BASE_WINDOW_SIZE.width(), max_width)
    target_height = min(BASE_WINDOW_SIZE.height(), max_height)

    return (
        QSize(max(target_width, minimum_width), max(target_height, minimum_height)),
        QSize(minimum_width, minimum_height),
    )


def saved_window_size(settings, fallback_size, minimum_size):
    if not isinstance(settings, dict):
        return fallback_size

    try:
        width = int(float(settings.get(WINDOW_WIDTH_SETTINGS_KEY, 0)))
        height = int(float(settings.get(WINDOW_HEIGHT_SETTINGS_KEY, 0)))
    except (TypeError, ValueError):
        return fallback_size

    if width <= 0 or height <= 0:
        return fallback_size

    screen = QApplication.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry().size()
        width = min(width, available.width())
        height = min(height, available.height())

    return QSize(
        max(width, minimum_size.width()),
        max(height, minimum_size.height()),
    )


def center_on_primary_screen(window):
    screen = QApplication.primaryScreen()
    if screen is None:
        return

    frame = window.frameGeometry()
    frame.moveCenter(screen.availableGeometry().center())
    window.move(frame.topLeft())


class MetricCard(QFrame):
    def __init__(self, title, value="-", subtitle="", accent="#1f8a70"):
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMinimumHeight(106)
        self.setMinimumWidth(0)
        self.accent = accent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        accent_bar = QFrame()
        accent_bar.setFixedSize(42, 4)
        accent_bar.setStyleSheet(f"background: {accent}; border-radius: 2px;")
        layout.addWidget(accent_bar, 0, Qt.AlignLeft)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")
        self.title_label.setWordWrap(True)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setWordWrap(True)
        self.value_label.setMinimumHeight(40)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("MetricSub")
        self.subtitle_label.setWordWrap(True)
        for label in [self.title_label, self.value_label, self.subtitle_label]:
            label.setMinimumWidth(0)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)
        self.subtitle_label.setVisible(bool(subtitle))
        layout.addStretch()

        self.setStyleSheet(
            f"""
            QFrame#Card {{
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-radius: 8px;
            }}
            """
        )

    def set_values(self, value, subtitle=""):
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))


class DashboardMetricItem(QWidget):
    def __init__(self, title, value="-", subtitle="", accent="#1f8a70"):
        super().__init__()
        self.setObjectName("DashboardMetricItem")
        self.setMinimumHeight(76)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setStyleSheet(
            f"""
            QWidget#DashboardMetricItem {{
                background: #f8fafc;
                border: 1px solid #e3e8ef;
                border-radius: 8px;
                border-left: 3px solid {accent};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #5d6a78; font-size: 8.5pt; font-weight: 800;")
        self.value_label = QLabel(value)
        self.value_label.setWordWrap(True)
        self.value_label.setStyleSheet("color: #111827; font-size: 15pt; font-weight: 850;")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("color: #6b7280; font-size: 8.5pt; line-height: 125%;")

        for label in [self.title_label, self.value_label, self.subtitle_label]:
            label.setMinimumWidth(0)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

    def set_values(self, value, subtitle=""):
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)


class DashboardMetricStrip(QWidget):
    def __init__(self, title, columns=3, embedded=False):
        super().__init__()
        self.items = []
        self.columns = max(1, columns)
        self.setObjectName("DashboardMetricStripEmbedded" if embedded else "DashboardSection")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        if embedded:
            self.setStyleSheet("QWidget#DashboardMetricStripEmbedded { background: transparent; border: 0; }")
        else:
            self.setStyleSheet(
                """
                QWidget#DashboardSection {
                    background: #ffffff;
                    border: 1px solid #dde3ea;
                    border-radius: 8px;
                }
                """
            )

        layout = QVBoxLayout(self)
        if embedded:
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10 if embedded else 14)

        if title:
            heading = QLabel(title)
            heading.setStyleSheet("color: #111827; font-size: 12.5pt; font-weight: 850;")
            layout.addWidget(heading)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        layout.addLayout(self.grid)

    def add_item(self, item):
        self.items.append(item)
        self.set_visible_items(self.items)

    def set_visible_items(self, items):
        for item in self.items:
            self.grid.removeWidget(item)
            item.setVisible(False)

        for index, item in enumerate(items):
            row = index // self.columns
            column = index % self.columns
            self.grid.addWidget(item, row, column)
            item.setVisible(True)
            self.grid.setColumnStretch(column, 1)


class DashboardIconButton(QPushButton):
    def __init__(self, icon_name, tooltip="", checkable=False, parent=None, label_text=""):
        super().__init__(parent)
        self.setProperty("skipGenericButtonAnimation", True)
        self.icon_name = icon_name
        self.label_text = label_text
        self.base_width = 42
        self.expanded_width = 116 if label_text else self.base_width
        self._expansion = 0
        self._expansion_animation = QPropertyAnimation(self, b"expansion", self)
        self.setCheckable(checkable)
        self.setFixedSize(self.base_width, 38)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setToolTip(tooltip)
        self.toggled.connect(lambda checked: self._animate_expansion(checked or self.underMouse()))

    @pyqtProperty(int)
    def expansion(self):
        return self._expansion

    @expansion.setter
    def expansion(self, value):
        self._expansion = max(0, int(value))
        self.setFixedWidth(self.base_width + self._expansion)
        self.update()

    def _target_expansion(self):
        return self.expanded_width - self.base_width

    def _animate_expansion(self, expanded):
        if not self.label_text:
            return

        self._expansion_animation.stop()
        self._expansion_animation.setStartValue(self._expansion)
        self._expansion_animation.setEndValue(self._target_expansion() if expanded else 0)
        self._expansion_animation.setDuration(210 if expanded else 140)
        self._expansion_animation.setEasingCurve(QEasingCurve.OutBack if expanded else QEasingCurve.InOutCubic)
        self._expansion_animation.start()

    def enterEvent(self, event):
        self._animate_expansion(True)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_expansion(self.isChecked())
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        hovered = self.underMouse()
        active = self.isDown() or self.isChecked()
        if self.icon_name == "remove":
            icon_color = QColor("#b91c1c")
            hover_fill = QColor("#fef2f2")
            active_fill = QColor("#fee2e2")
            border = QColor("#f0c7c7")
        else:
            icon_color = QColor("#0f766e")
            hover_fill = QColor("#edf7f4")
            active_fill = QColor("#d9f0ea")
            border = QColor("#c7d8d3")

        button_rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        painter.setPen(QPen(border if hovered or active else QColor(0, 0, 0, 0), 1))
        painter.setBrush(active_fill if active else (hover_fill if hovered else QColor(0, 0, 0, 0)))
        painter.drawRoundedRect(button_rect, 7, 7)

        if self.label_text and self._expansion > 6:
            painter.save()
            font = QFont(self.font())
            font.setWeight(QFont.DemiBold)
            painter.setFont(font)
            painter.setOpacity(min(1.0, self._expansion / max(1, self._target_expansion())))
            painter.setPen(icon_color)
            text_rect = QRectF(12, 0, max(0, self.width() - self.base_width + 10), self.height())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.label_text)
            painter.restore()

        painter.setPen(QPen(icon_color, 2.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        icon_center_x = self.width() - (self.base_width / 2) if self.label_text else self.width() / 2
        center = QPointF(icon_center_x, self.height() / 2)

        if self.icon_name == "add":
            length = 12
            painter.drawLine(QPointF(center.x() - length / 2, center.y()), QPointF(center.x() + length / 2, center.y()))
            painter.drawLine(QPointF(center.x(), center.y() - length / 2), QPointF(center.x(), center.y() + length / 2))
        elif self.icon_name == "remove":
            length = 12
            painter.drawLine(
                QPointF(center.x() - length / 2, center.y() - length / 2),
                QPointF(center.x() + length / 2, center.y() + length / 2),
            )
            painter.drawLine(
                QPointF(center.x() + length / 2, center.y() - length / 2),
                QPointF(center.x() - length / 2, center.y() + length / 2),
            )
        elif self.icon_name == "widgets":
            painter.setPen(QPen(icon_color, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            size = 8
            gap = 4
            left = center.x() - size - gap / 2
            top = center.y() - size - gap / 2
            for row in range(2):
                for column in range(2):
                    rect = QRectF(left + column * (size + gap), top + row * (size + gap), size, size)
                    painter.drawRoundedRect(rect, 2, 2)


class DashboardDropIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(16)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        y = self.height() / 2
        left = 6
        right = self.width() - 6
        color = QColor("#1f8a70")
        painter.setPen(QPen(color, 2.4, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(left + 7, y), QPointF(right - 7, y))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(left, y), 3.4, 3.4)
        painter.drawEllipse(QPointF(right, y), 3.4, 3.4)


class DashboardDragHandle(QWidget):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.pressed = False
        self.dragging = False
        self.press_global_pos = None
        self.setFixedWidth(26)
        self.setMinimumHeight(34)
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip("Træk for at flytte widget")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#94a3b8"), 2, Qt.DotLine, Qt.RoundCap)
        painter.setPen(pen)
        center_x = self.width() / 2
        top = 6
        bottom = self.height() - 6
        painter.drawLine(QPointF(center_x - 4, top), QPointF(center_x - 4, bottom))
        painter.drawLine(QPointF(center_x + 4, top), QPointF(center_x + 4, bottom))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.frame.edit_mode:
            self.pressed = True
            self.dragging = False
            self.press_global_pos = event.globalPos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.pressed or not self.frame.edit_mode:
            super().mouseMoveEvent(event)
            return

        if not self.dragging:
            distance = event.globalPos() - self.press_global_pos
            if distance.manhattanLength() < QApplication.startDragDistance():
                event.accept()
                return
            self.dragging = True
            self.frame.start_drag(self.press_global_pos)

        self.frame.drag_move(event.globalPos())
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.pressed:
            if self.dragging:
                self.frame.finish_drag()
            self.pressed = False
            self.dragging = False
            self.press_global_pos = None
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class DashboardWidgetFrame(QFrame):
    def __init__(
        self,
        title,
        key,
        drag_start_callback,
        drag_move_callback,
        drag_finish_callback,
        remove_callback,
        parent=None,
    ):
        super().__init__(parent)
        self.key = key
        self.drag_start_callback = drag_start_callback
        self.drag_move_callback = drag_move_callback
        self.drag_finish_callback = drag_finish_callback
        self.remove_callback = remove_callback
        self.edit_mode = False
        self.setObjectName("DashboardSection")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        root.addLayout(header)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #111827; font-size: 12.5pt; font-weight: 850;")
        title_label.setWordWrap(True)
        header.addWidget(title_label, 1)

        self.remove_button = DashboardIconButton("remove", "Fjern widget", parent=self, label_text="Fjern")
        self.remove_button.clicked.connect(lambda checked=False: self.remove_callback(self.key))
        header.addWidget(self.remove_button)

        self.drag_handle = DashboardDragHandle(self)
        header.addWidget(self.drag_handle, 0, Qt.AlignTop)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        root.addLayout(self.content_layout)

        self.set_reorder_mode(False)

    def addWidget(self, widget, stretch=0):
        self.content_layout.addWidget(widget, stretch)

    def addLayout(self, layout, stretch=0):
        self.content_layout.addLayout(layout, stretch)

    def set_reorder_mode(self, enabled):
        self.edit_mode = enabled
        self.drag_handle.setVisible(enabled)
        self.remove_button.setVisible(enabled)

    def set_drag_active(self, active):
        if active:
            self.setStyleSheet(
                """
                QFrame#DashboardSection {
                    background: #f8fafc;
                    border: 1px solid #1f8a70;
                    border-radius: 8px;
                }
                """
            )
        else:
            self.setStyleSheet("")

    def start_drag(self, global_pos):
        self.drag_start_callback(self.key, global_pos)

    def drag_move(self, global_pos):
        self.drag_move_callback(self.key, global_pos)

    def finish_drag(self):
        self.drag_finish_callback(self.key)


class DashboardWidgetPreview(QFrame):
    def __init__(self, key, title, select_callback, parent=None):
        super().__init__(parent)
        self.key = key
        self.title = title
        self.select_callback = select_callback
        self.hovered = False

        self.setObjectName("DashboardWidgetPreviewSlot")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(152)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        slot_layout = QVBoxLayout(self)
        slot_layout.setContentsMargins(0, 0, 0, 0)
        slot_layout.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("DashboardWidgetPreviewCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        slot_layout.addWidget(self.card)

        self.root = QVBoxLayout(self.card)
        self.root.setContentsMargins(14, 12, 14, 12)
        self.root.setSpacing(9)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        self.root.addLayout(header)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #0f172a; font-size: 11.5pt; font-weight: 900;")
        title_label.setWordWrap(False)
        header.addWidget(title_label, 1)

        add_hint = QLabel("Tilføj")
        add_hint.setAlignment(Qt.AlignCenter)
        add_hint.setStyleSheet(
            """
            QLabel {
                color: #0f766e;
                background: #ecfdf5;
                border: 1px solid #bbf7d0;
                border-radius: 11px;
                padding: 3px 9px;
                font-size: 8.5pt;
                font-weight: 850;
            }
            """
        )
        header.addWidget(add_hint, 0, Qt.AlignRight | Qt.AlignVCenter)

        self.preview_layout = QVBoxLayout()
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(7)
        self.root.addLayout(self.preview_layout, 1)

        self._build_preview()
        self._set_hovered(False)

    def enterEvent(self, event):
        self._set_hovered(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._set_hovered(False)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.select_callback(self.key)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _set_hovered(self, hovered):
        self.hovered = hovered
        self.setStyleSheet(
            f"""
            QFrame#DashboardWidgetPreviewSlot {{
                background: transparent;
                border: 0;
                padding: 0;
            }}
            QFrame#DashboardWidgetPreviewCard {{
                background: {'#f8fffc' if hovered else '#ffffff'};
                border: 1px solid {'#1f8a70' if hovered else '#dbe3ec'};
                border-radius: 9px;
            }}
            QFrame#DashboardWidgetPreviewCard QLabel {{
                background: transparent;
                border: 0;
            }}
            """
        )

    def _build_preview(self):
        if self.key == "goal":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Rådighed", "2.400 kr.", "#1f8a70"),
                        ("Mål", "2.000 kr.", "#d97706"),
                        ("Status", "Nået", "#16a34a"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Viser om du er på vej mod dit rådighedsmål."))

        elif self.key == "progress":
            self.preview_layout.addWidget(self._progress_preview("22 / 30 dage", 73))
            self.preview_layout.addLayout(
                self._mini_stats(
                    [
                        ("Vagter", "4"),
                        ("Brutto", "600 kr."),
                        ("Tilbage", "8 dage"),
                    ]
                )
            )

        elif self.key == "process":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Netto", "3.312 kr.", "#1f8a70"),
                        ("Rådighed", "1.850 kr.", "#d97706"),
                        ("Timer", "22 t.", "#7c3aed"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Nuværende lønperiode indtil videre."))

        elif self.key == "estimates":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Est. netto", "4.920 kr.", "#1f8a70"),
                        ("Est. rådighed", "2.150 kr.", "#d97706"),
                        ("Est. timer", "32 t.", "#7c3aed"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Forventer slutresultatet for perioden."))

        elif self.key == "stats":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Snit/vagt", "331 kr.", "#475569"),
                        ("Snit/uge", "77 kr.", "#2563eb"),
                        ("Perioden", "1.408 kr.", "#1f8a70"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Nøgletal for den nuværende lønperiode."))

        elif self.key == "holiday_pay":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Denne periode", "197 kr.", "#1f8a70"),
                        ("Total", "1.250 kr.", "#0f766e"),
                        ("Feriedage", "4,16", "#2563eb"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Optjent feriepenge og anmodningsperiode."))

        elif self.key == "budget":
            self.preview_layout.addLayout(
                self._metric_row(
                    [
                        ("Udgifter", "0 kr.", "#d97706"),
                        ("Poster", "0", "#475569"),
                        ("Budget", "Åbn", "#1f8a70"),
                    ]
                )
            )
            self.preview_layout.addWidget(self._note("Faste udgifter brugt i rådighedsberegningen."))

        elif self.key == "breakdown":
            self.preview_layout.addWidget(self._list_row("AM-bidrag", "-288 kr.", "#dc2626"))
            self.preview_layout.addWidget(self._list_row("Netto løn", "3.312 kr.", "#1f8a70"))
            self.preview_layout.addWidget(self._note("Viser skatteopdeling for lønperioden."))

        elif self.key == "recent":
            self.preview_layout.addWidget(self._list_row("05-05-2026", "6 t. · 900 kr.", "#2563eb"))
            self.preview_layout.addWidget(self._list_row("03-05-2026", "4 t. · 600 kr.", "#2563eb"))
            self.preview_layout.addWidget(self._note("Seneste vagter i den aktuelle periode."))

        elif self.key == "salary_calculator":
            self.preview_layout.addLayout(
                self._calculator_preview()
            )
            self.preview_layout.addWidget(self._note("Brutto eller timer + timeløn → netto."))

    def _metric_row(self, items):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        for title, value, accent in items:
            row.addWidget(self._metric_chip(title, value, accent), 1)

        return row

    def _metric_chip(self, title, value, accent):
        chip = QFrame()
        chip.setFixedHeight(58)
        chip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        chip.setStyleSheet(
            f"""
            QFrame {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: 0;
            }}
            """
        )

        layout = QVBoxLayout(chip)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setSpacing(2)

        accent_bar = QFrame()
        accent_bar.setFixedHeight(3)
        accent_bar.setStyleSheet(f"background: {accent}; border: 0; border-radius: 1px;")
        layout.addWidget(accent_bar)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 8pt; font-weight: 800;")
        title_label.setWordWrap(False)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("color: #0f172a; font-size: 10.5pt; font-weight: 900;")
        value_label.setWordWrap(False)
        layout.addWidget(value_label)

        return chip

    def _progress_preview(self, label, percent):
        wrapper = QFrame()
        wrapper.setFixedHeight(54)
        wrapper.setStyleSheet(
            """
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                border: 0;
            }
            """
        )

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #0f172a; font-size: 9pt; font-weight: 900;")
        top.addWidget(label_widget)

        percent_label = QLabel(f"{percent}%")
        percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        percent_label.setStyleSheet("color: #64748b; font-size: 8.5pt; font-weight: 800;")
        top.addWidget(percent_label)

        layout.addLayout(top)

        track = QFrame()
        track.setFixedHeight(9)
        track.setStyleSheet("background: #e2e8f0; border: 0; border-radius: 4px;")

        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)

        fill = QFrame()
        fill.setStyleSheet("background: #1f8a70; border: 0; border-radius: 4px;")
        track_layout.addWidget(fill, max(1, percent))
        track_layout.addStretch(max(1, 100 - percent))

        layout.addWidget(track)

        return wrapper

    def _mini_stats(self, items):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(7)

        for title, value in items:
            row.addWidget(self._tiny_stat(title, value), 1)

        return row

    def _tiny_stat(self, title, value):
        box = QFrame()
        box.setFixedHeight(30)
        box.setStyleSheet(
            """
            QFrame {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 7px;
            }
            QLabel {
                background: transparent;
                border: 0;
            }
            """
        )

        layout = QHBoxLayout(box)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 8pt; font-weight: 800;")
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value_label.setStyleSheet("color: #0f172a; font-size: 8.5pt; font-weight: 900;")

        layout.addWidget(title_label, 1)
        layout.addWidget(value_label, 0)

        return box

    def _list_row(self, left, right, accent):
        row = QFrame()
        row.setFixedHeight(32)
        row.setStyleSheet(
            f"""
            QFrame {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 7px;
            }}
            QLabel {{
                background: transparent;
                border: 0;
            }}
            """
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(9, 5, 9, 5)
        layout.setSpacing(8)

        dot = QFrame()
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(f"background: {accent}; border: 0; border-radius: 3px;")
        layout.addWidget(dot, 0, Qt.AlignVCenter)

        left_label = QLabel(left)
        left_label.setStyleSheet("color: #334155; font-size: 8.8pt; font-weight: 850;")
        left_label.setWordWrap(False)

        right_label = QLabel(right)
        right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_label.setStyleSheet("color: #0f172a; font-size: 8.8pt; font-weight: 900;")
        right_label.setWordWrap(False)

        layout.addWidget(left_label, 1)
        layout.addWidget(right_label, 1)

        return row

    def _calculator_preview(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        row.addWidget(self._metric_chip("Brutto", "3.000 kr.", "#2563eb"), 1)
        row.addWidget(self._arrow_label(), 0)
        row.addWidget(self._metric_chip("Netto", "1.920 kr.", "#1f8a70"), 1)

        return row

    def _arrow_label(self):
        label = QLabel("→")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(22)
        label.setStyleSheet("color: #94a3b8; font-size: 15pt; font-weight: 900;")
        return label

    def _note(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: #64748b; font-size: 8.5pt;")
        label.setWordWrap(False)
        label.setMinimumHeight(18)
        return label


class DashboardAddWidgetDialog(QDialog):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.selected_key = None
        self.setModal(True)
        self.setWindowTitle("Tilføj widget")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        if not options:
            empty_label = QLabel("Der er ikke flere widgets at tilføje.")
            empty_label.setWordWrap(True)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #64748b; padding: 26px;")
            layout.addWidget(empty_label)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setMaximumHeight(640)

            body = QWidget()
            body_layout = QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(12)
            for key, title in options:
                preview = DashboardWidgetPreview(key, title, self._select, self)
                body_layout.addWidget(preview)
            body_layout.addStretch()
            scroll.setWidget(body)
            layout.addWidget(scroll)

        layout.addStretch()

        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

    def _select(self, key):
        self.selected_key = key
        self.accept()


class GoalStatusCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        self.status_pill = QLabel()
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setMinimumWidth(86)
        layout.addWidget(self.status_pill, 0, Qt.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_label = QLabel("Rådighedsmål")
        self.title_label.setStyleSheet("color: #475569; font-size: 8.5pt; font-weight: 850;")
        self.value_label = QLabel("Ikke beregnet")
        self.value_label.setStyleSheet("color: #111827; font-size: 17pt; font-weight: 850;")
        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #475569;")
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)
        text_layout.addWidget(self.detail_label)
        layout.addLayout(text_layout, 1)

        self.set_status("neutral", "Ikke beregnet", "Rådighedsmål ikke beregnet")

    def set_status(self, state, value, detail):
        styles = {
            "success": ("NÅET", "#16a34a", "#ecfdf5", "#86efac"),
            "warning": ("PÅ VEJ", "#d97706", "#fffbeb", "#fbbf24"),
            "danger": ("UNDER", "#dc2626", "#fef2f2", "#fca5a5"),
            "neutral": ("IKKE SAT", "#64748b", "#f8fafc", "#cbd5e1"),
        }
        label, color, background, border = styles.get(state, styles["neutral"])
        self.status_pill.setText(label)
        self.value_label.setText(value)
        self.detail_label.setText(detail)
        self.setStyleSheet(
            f"""
            QFrame#GoalStatusCard {{
                background: {background};
                border: 1px solid {border};
                border-left: 5px solid {color};
                border-radius: 8px;
            }}
            """
        )
        self.status_pill.setStyleSheet(
            f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 14px;
                padding: 7px 12px;
                font-size: 8.5pt;
                font-weight: 850;
            }}
            """
        )


class GoalHeaderWidget(QWidget):
    def __init__(self, show_title=True, add_shifts_callback=None, settings_callback=None, budget_callback=None):
        super().__init__()
        self.add_shifts_callback = add_shifts_callback
        self.settings_callback = settings_callback
        self.budget_callback = budget_callback
        self.active_action_callback = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)
        root.addLayout(top)

        if show_title:
            title = QLabel("Rådighedsmål")
            title.setStyleSheet("color: #111827; font-size: 12.5pt; font-weight: 850;")
            top.addWidget(title)

        self.status_pill = QLabel()
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setMinimumWidth(76)
        top.addWidget(self.status_pill, 0, Qt.AlignVCenter)

        self.action_button = QPushButton("")
        self.action_button.setObjectName("InlineButton")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.hide()
        self.action_button.clicked.connect(self._run_action)
        top.addWidget(self.action_button, 0, Qt.AlignVCenter)

        top.addStretch()

        content = QHBoxLayout()
        content.setSpacing(18)
        root.addLayout(content)

        main = QVBoxLayout()
        main.setSpacing(8)

        self.value_label = QLabel("Ikke beregnet")
        self.value_label.setStyleSheet("color: #111827; font-size: 15pt; font-weight: 900;")
        self.value_label.setWordWrap(True)

        self.metrics_widget = QWidget()
        self.metrics_layout = QHBoxLayout(self.metrics_widget)
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)
        self.metrics_layout.setSpacing(8)
        self.current_metric = self._goal_metric_box("Rådighed nu", "#1f8a70")
        self.target_metric = self._goal_metric_box("Periodemål", "#2563eb")
        self.estimate_metric = self._goal_metric_box("Forventet", "#d97706")
        self.metrics_layout.addWidget(self.current_metric, 1)
        self.metrics_layout.addWidget(self.target_metric, 1)
        self.metrics_layout.addWidget(self.estimate_metric, 1)

        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #475569;")

        main.addWidget(self.value_label)
        main.addWidget(self.metrics_widget)
        main.addWidget(self.detail_label)
        content.addLayout(main, 3)

        previous = QVBoxLayout()
        previous.setSpacing(2)

        previous_title = QLabel("Sidste lønperiode")
        previous_title.setStyleSheet("color: #64707d; font-size: 8.5pt; font-weight: 850;")

        self.previous_label = QLabel("Ingen afsluttet periode")
        self.previous_label.setStyleSheet("color: #334155; font-size: 11pt; font-weight: 850;")

        self.previous_detail_label = QLabel("Når en periode er afsluttet, vises rådighedsbeløbet her.")
        self.previous_detail_label.setWordWrap(True)
        self.previous_detail_label.setStyleSheet("color: #64707d; font-size: 8.5pt;")

        previous.addWidget(previous_title)
        previous.addWidget(self.previous_label)
        previous.addWidget(self.previous_detail_label)
        content.addLayout(previous, 1)

        self.set_status("neutral", "Ikke beregnet", "Målet kan ikke vurderes endnu.", None)

    def _goal_metric_box(self, title, accent):
        box = QFrame()
        box.setObjectName("Card")
        box.setMinimumHeight(82)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        box.setStyleSheet(
            f"""
            QFrame#Card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                border-left: 3px solid {accent};
            }}
            QLabel {{
                background: transparent;
                border: 0;
            }}
            """
        )
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(3)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 8.5pt; font-weight: 850;")
        value_label = QLabel("-")
        value_label.setStyleSheet("color: #111827; font-size: 13pt; font-weight: 900;")
        value_label.setWordWrap(True)
        subtitle_label = QLabel("")
        subtitle_label.setStyleSheet("color: #64748b; font-size: 8.5pt;")
        subtitle_label.setWordWrap(True)
        subtitle_label.hide()
        box.value_label = value_label
        box.subtitle_label = subtitle_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        return box

    def _run_action(self):
        if self.active_action_callback is not None:
            self.active_action_callback()

    def _set_action_button(self, text="", callback=None):
        self.active_action_callback = callback
        self.action_button.setText(text)
        self.action_button.setVisible(bool(text and callback))

    def set_status(
        self,
        state,
        value,
        detail,
        previous_period=None,
        show_add_shifts_button=False,
        show_settings_button=False,
        show_budget_button=False,
        current_amount=None,
        target_amount=None,
        estimate_amount=None,
        monthly_target_amount=None,
    ):
        styles = {
            "success": ("MÅLET ER OPNÅET", "#16a34a"),
            "warning": ("FORVENTES AT OPNÅ", "#d97706"),
            "danger": ("FORVENTES IKKE AT OPNÅ", "#dc2626"),
            "neutral": ("IKKE INDSTILLET", "#64748b"),
            "empty": ("INGEN VAGTER", "#64748b"),
        }

        label, color = styles.get(state, styles["neutral"])

        self.status_pill.setText(label)
        self.value_label.setText(value)
        self.detail_label.setText(detail)

        metrics = [
            (self.current_metric, current_amount),
            (self.target_metric, target_amount),
            (self.estimate_metric, estimate_amount),
        ]
        has_metrics = any(amount is not None for _, amount in metrics)
        self.metrics_widget.setVisible(has_metrics)
        for metric, amount in metrics:
            metric.setVisible(amount is not None)
            if amount is not None:
                metric.value_label.setText(format_money(amount))
            if hasattr(metric, "subtitle_label"):
                metric.subtitle_label.hide()
                metric.subtitle_label.setText("")
        if target_amount is not None and monthly_target_amount is not None:
            self.target_metric.subtitle_label.setText(f"Månedsmål: {format_money(monthly_target_amount)}")
            self.target_metric.subtitle_label.show()

        if show_add_shifts_button:
            self._set_action_button("Tilføj vagter", self.add_shifts_callback)
        elif show_settings_button:
            self._set_action_button("Indstil nu", self.settings_callback)
        elif show_budget_button:
            self._set_action_button("Indstil budget", self.budget_callback)
        else:
            self._set_action_button()

        if previous_period:
            self.previous_label.setText(f"Rådighed: {format_money(previous_period['available'])}")
            self.previous_detail_label.setText("")
        else:
            self.previous_label.setText("Ingen afsluttet periode")
            self.previous_detail_label.setText("Når en periode er afsluttet, vises sidste rådighedsbeløbet her.")

        self.status_pill.setStyleSheet(
            f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 13px;
                padding: 6px 11px;
                font-size: 8.5pt;
                font-weight: 850;
            }}
            """
        )


class PeriodProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.period_start = None
        self.period_end = None
        self.today = None
        self.rows = []
        self.progress_ratio = 0
        self.hovered_index = None
        self.marker_rects = []
        self.setMinimumHeight(184)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def set_period(self, period_start, period_end, today, rows, progress_ratio):
        self.period_start = period_start
        self.period_end = period_end
        self.today = today
        self.rows = sorted(rows, key=lambda row: row["dato"])
        self.progress_ratio = max(0, min(float(progress_ratio or 0), 1))
        self.hovered_index = None
        self.setToolTip("")
        self.update()

    def clear(self, message=""):
        self.period_start = None
        self.period_end = None
        self.today = None
        self.rows = []
        self.progress_ratio = 0
        self.hovered_index = None
        self.marker_rects = []
        self.setToolTip(message)
        self.update()

    def _track_geometry(self, rect):
        track_left = rect.left() + 18
        track_right = rect.right() - 18
        track_width = max(1, track_right - track_left)
        track_y = rect.top() + 104
        track_height = 18
        return track_left, track_right, track_width, track_y, track_height


    def _x_for_date(self, value, track_left, track_width, total_days):
        day_index = min(max((value - self.period_start).days, 0), total_days - 1)
        ratio = day_index / max(1, total_days - 1)
        return track_left + (track_width * ratio)


    def _week_markers(self):
        if not self.period_start or not self.period_end:
            return []

        markers = []

        current = self.period_start
        while current <= self.period_end:
            # Vis altid periodens første dag som starten på den første viste uge-del.
            if current == self.period_start or current.weekday() == 0:
                week_number = current.isocalendar().week
                markers.append((current, f"Uge {week_number}"))
            current += timedelta(days=1)

        return markers

    def _marker_data(self, rect):
        if not self.period_start or not self.period_end:
            return []

        total_days = max(1, (self.period_end - self.period_start).days + 1)
        track_left, _, track_width, track_y, _ = self._track_geometry(rect)
        marker_width = max(2.5, min(5, int(track_width / max(total_days, 1) * 0.28)))

        markers = []
        for index, row in enumerate(self.rows):
            x = self._x_for_date(row["dato"], track_left, track_width, total_days)
            marker = QRectF(x - marker_width / 2, track_y + 3, marker_width, 12)
            markers.append((index, row, marker, x))
        return markers

    def mouseMoveEvent(self, event):
        hovered = None
        for index, row, marker, _ in self.marker_rects:
            hit_rect = QRectF(marker)
            hit_rect.adjust(-5, -8, 5, 12)
            if hit_rect.contains(event.pos()):
                hovered = index
                if row.get("is_day_off"):
                    self.setToolTip(
                        f"{format_date(row['dato'])}\n"
                        "Fridag\n"
                        "Ingen timer eller løn registreret"
                    )
                else:
                    self.setToolTip(
                        f"{format_date(row['dato'])}\n"
                        f"{format_number(row['timer'])} betalte timer · Pause: {format_pause_minutes(row.get('pause', 0))} min.\n"
                        f"{format_money(row['brutto'])} brutto\n"
                        f"Timeløn: {format_money(row['timeløn'])}"
                    )
                break
        if hovered is None:
            self.setToolTip("")
        if hovered != self.hovered_index:
            self.hovered_index = hovered
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_index = None
        self.setToolTip("")
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(4, 4, -4, -4)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#f8fafc"))
        painter.drawRoundedRect(rect, 8, 8)

        if not self.period_start or not self.period_end:
            painter.setPen(QColor("#64748b"))
            painter.drawText(rect, Qt.AlignCenter, "Udfyld indstillingerne for at se periodens forløb")
            return

        total_days = max(1, (self.period_end - self.period_start).days + 1)
        elapsed_days = min(max((self.today - self.period_start).days + 1, 0), total_days) if self.today else 0
        work_rows = [row for row in self.rows if not row.get("is_day_off")]
        day_off_count = count_day_off_rows(self.rows)
        total_brutto = sum(row["brutto"] for row in work_rows)
        best_shift = max(work_rows, key=lambda row: row.get("netto", 0)) if work_rows else None

        painter.setPen(QColor("#334155"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(
            QRectF(rect.left() + 14, rect.top() + 10, rect.width() - 28, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{elapsed_days} / {total_days} dage",
        )

        painter.setPen(QColor("#64748b"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(
            QRectF(rect.left() + 14, rect.top() + 34, rect.width() - 28, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{len(work_rows)} vagter · {day_off_count} fridage · {format_money(total_brutto)} brutto",
        )

        track_left, track_right, track_width, track_y, track_height = self._track_geometry(rect)

        # Ugemarkører
        week_markers = []
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for week_date, week_label in self._week_markers():
            x = self._x_for_date(week_date, track_left, track_width, total_days)
            week_markers.append((x, week_label))

            painter.setPen(QPen(QColor("#cbd5e1"), 1))
            painter.drawLine(
                int(x),
                int(track_y - 16),
                int(x),
                int(track_y + track_height + 4),
            )

            painter.setPen(QColor("#64748b"))
            painter.drawText(
                QRectF(x - 34, track_y - 36, 68, 16),
                Qt.AlignCenter,
                week_label,
            )

        # Progressbar
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e5eaf0"))
        painter.drawRoundedRect(QRectF(track_left, track_y, track_width, track_height), 9, 9)

        painter.setBrush(QColor("#1f8a70"))
        painter.drawRoundedRect(QRectF(track_left, track_y, track_width * self.progress_ratio, track_height), 9, 9)

        # I dag-markør
        if self.today:
            today_x = self._x_for_date(self.today, track_left, track_width, total_days)

            overlaps_week_label = any(abs(today_x - week_x) < 44 for week_x, _ in week_markers)
            today_label_y = track_y - 54 if overlaps_week_label else track_y - 38

            painter.setPen(QPen(QColor("#0f172a"), 2))
            painter.drawLine(
                int(today_x),
                int(track_y - 24),
                int(today_x),
                int(track_y + track_height + 10),
            )

            painter.setPen(QColor("#0f172a"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(
                QRectF(today_x - 30, today_label_y, 60, 18),
                Qt.AlignCenter,
                "I dag",
            )

        self.marker_rects = self._marker_data(rect)
        for index, row, marker, x in self.marker_rects:
            painter.setPen(Qt.NoPen)
            color = QColor(DAY_OFF_ACCENT) if row.get("is_day_off") else QColor("#ffffff")
            painter.setBrush(color)
            painter.drawRoundedRect(marker, 2, 2)

        footer_y = rect.bottom() - 30
        painter.setPen(QColor("#64748b"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            QRectF(rect.left() + 14, footer_y, rect.width() / 2 - 20, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{format_date(self.period_start)} - {format_date(self.period_end)}",
        )
        best_text = f"Bedste vagt: {format_money(best_shift.get('netto', 0))}" if best_shift else "Ingen vagter registreret endnu"
        painter.drawText(
            QRectF(rect.center().x(), footer_y, rect.width() / 2 - 18, 18),
            Qt.AlignRight | Qt.AlignVCenter,
            best_text,
        )


class DashboardBudgetWidget(QWidget):
    VISIBLE_ROWS = 5
    ROW_HEIGHT = 32
    ROW_SPACING = 6

    def __init__(self, open_budget_callback):
        super().__init__()
        self.open_budget_callback = open_budget_callback
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        root.addLayout(header)

        self.total_label = QLabel("Samlede udgifter pr. måned: 0 kr.")
        self.total_label.setStyleSheet("color: #111827; font-size: 16pt; font-weight: 900;")
        header.addWidget(self.total_label, 1)

        self.open_budget_button = QPushButton("Gå til budget")
        self.open_budget_button.setObjectName("InlineButton")
        self.open_budget_button.setCursor(Qt.PointingHandCursor)
        self.open_budget_button.clicked.connect(self.open_budget_callback)
        header.addWidget(self.open_budget_button, 0, Qt.AlignRight | Qt.AlignVCenter)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setMaximumHeight(self._scroll_height(self.VISIBLE_ROWS))
        root.addWidget(self.scroll)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(self.ROW_SPACING)
        self.scroll.setWidget(self.body)

    def update_budget(self, categories):
        clear_layout(self.body_layout)
        budget_total = sum(item["beløb"] for item in categories)
        self.total_label.setText(f"Samlede udgifter pr. måned: {format_money(budget_total)}")

        if not categories:
            empty = QLabel("Ingen budgetposter endnu.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                "color: #64748b; background: #f8fafc; border: 1px solid #e3e8ef; "
                "border-radius: 7px; padding: 18px;"
            )
            self.body_layout.addWidget(empty)
            self.scroll.setFixedHeight(64)
            return

        for category in categories:
            row = self._row(category["navn"], format_money(category["beløb"]))
            self.body_layout.addWidget(row)

        self.body_layout.addStretch()
        self.scroll.setFixedHeight(self._scroll_height(min(self.VISIBLE_ROWS, len(categories))))

    def _scroll_height(self, visible_rows):
        return (visible_rows * self.ROW_HEIGHT) + max(0, visible_rows - 1) * self.ROW_SPACING + 4

    def _row(self, left, right):
        row = QFrame()
        row.setFixedHeight(self.ROW_HEIGHT)
        row.setStyleSheet(
            """
            QFrame {
                background: #f8fafc;
                border: 1px solid #e3e8ef;
                border-radius: 7px;
            }
            QLabel {
                background: transparent;
                border: 0;
            }
            """
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        left_label = QLabel(left)
        left_label.setStyleSheet("color: #334155; font-weight: 750;")

        right_label = QLabel(right)
        right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_label.setStyleSheet("color: #111827; font-weight: 850;")

        layout.addWidget(left_label, 1)
        layout.addWidget(right_label, 0)

        return row
    

class DashboardSalaryCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        root.addLayout(form)

        self.gross_field = make_text_input(placeholder="Brutto løn")
        self.hours_field = make_text_input(placeholder="Timer")
        self.rate_field = make_text_input(placeholder="Timeløn")
        for field in [self.gross_field, self.hours_field, self.rate_field]:
            field.textChanged.connect(self._calculate)

        form.addWidget(QLabel("Brutto"), 0, 0)
        form.addWidget(self.gross_field, 0, 1, 1, 3)
        form.addWidget(QLabel("Timer"), 1, 0)
        form.addWidget(self.hours_field, 1, 1)
        form.addWidget(QLabel("Timeløn"), 1, 2)
        form.addWidget(self.rate_field, 1, 3)

        self.net_label = QLabel("Netto løn: N/A")
        self.net_label.setStyleSheet("color: #111827; font-size: 17pt; font-weight: 900;")
        root.addWidget(self.net_label)

        self.detail_label = QLabel("Brug bruttofeltet eller timer + timeløn.")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #64748b;")
        root.addWidget(self.detail_label)

    def set_settings(self, settings):
        self.settings = settings if isinstance(settings, dict) else {}
        self._calculate()

    def _calculate(self):
        if not has_required_settings(self.settings):
            self.net_label.setText("Netto løn: N/A")
            self.detail_label.setText("Indstillinger mangler.")
            return

        try:
            gross, hours = self._calculation_values()
        except ValueError as error:
            self.net_label.setText("Netto løn: N/A")
            self.detail_label.setText(str(error))
            return

        if gross is None:
            self.net_label.setText("Netto løn: N/A")
            self.detail_label.setText("Brug bruttofeltet eller timer + timeløn.")
            return

        breakdown = ft.calculate_salary_breakdown_from_brutto(gross, hours, self.settings)
        self.net_label.setText(f"Netto løn: {format_money(breakdown['netto'])}")
        self.detail_label.setText(
            f"Brutto: {format_money(gross)} · Pension: {format_number(ft.get_pension_contribution_rate(self.settings) * 100)}% · Skat: {format_number(float(self.settings.get('skat', 0)) * 100)}%"
        )

    def _calculation_values(self):
        gross_text = self.gross_field.text().strip()
        if gross_text:
            return parse_positive_number(self.gross_field, "Brutto løn", allow_zero=True), 0.0

        hours_text = self.hours_field.text().strip()
        rate_text = self.rate_field.text().strip()
        if not hours_text and not rate_text:
            return None, 0.0
        if not hours_text or not rate_text:
            raise ValueError("Udfyld både timer og timeløn.")

        hours = parse_positive_number(self.hours_field, "Timer", allow_zero=True)
        rate = parse_positive_number(self.rate_field, "Timeløn", allow_zero=True)
        return hours * rate, hours


class DashboardHolidayPayWidget(QWidget):
    def __init__(self, setup_callback, details_callback):
        super().__init__()
        self.setup_callback = setup_callback
        self.details_callback = details_callback
        self.calculation = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(22)
        root.addLayout(content)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(8)
        content.addLayout(left, 3)

        right = QVBoxLayout()
        right.setContentsMargins(0, 2, 0, 0)
        right.setSpacing(6)
        content.addLayout(right, 2)

        self.amount_label = QLabel("Optjent denne lønperiode: N/A")
        self.amount_label.setStyleSheet("color: #111827; font-size: 17pt; font-weight: 900;")
        self.amount_label.setWordWrap(True)
        left.addWidget(self.amount_label)

        self.total_amount_label = QLabel("Total optjent: N/A")
        self.total_amount_label.setStyleSheet("color: #475569; font-size: 10.5pt; font-weight: 800;")
        self.total_amount_label.setWordWrap(True)
        left.addWidget(self.total_amount_label)

        self.info_row = QHBoxLayout()
        self.info_row.setContentsMargins(0, 0, 0, 0)
        self.info_row.setSpacing(8)
        left.addLayout(self.info_row)

        self.days_chip = self._chip("Feriedage", "-", "#2563eb")
        self.info_row.addWidget(self.days_chip, 0, Qt.AlignLeft)
        self.forecast_days_chip = self._chip("Forventet feriedage om ½ år", "-", "#0f766e")
        self.info_row.addWidget(self.forecast_days_chip, 0, Qt.AlignLeft)
        self.info_row.addStretch()

        self.detail_label = QLabel()
        self.detail_label.setObjectName("PageSubtitle")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right.addWidget(self.detail_label)
        right.addStretch()

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        left.addLayout(button_row)

        self.details_button = QPushButton("Detaljer")
        self.details_button.setObjectName("InlineButton")
        self.details_button.clicked.connect(self._open_details)
        button_row.addWidget(self.details_button, 0, Qt.AlignLeft)

        self.setup_button = QPushButton("Indstil feriepenge beregneren")
        self.setup_button.setObjectName("InlineButton")
        self.setup_button.clicked.connect(self.setup_callback)
        button_row.addWidget(self.setup_button, 0, Qt.AlignLeft)
        button_row.addStretch()

    def _chip(self, title, value, accent):
        chip = QFrame()
        chip.setObjectName("Card")
        chip.setFixedSize(210, 88)
        chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chip.setStyleSheet(
            f"""
            QFrame#Card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 7px;
            }}
            QLabel {{
                background: transparent;
                border: 0;
            }}
            """
        )
        layout = QVBoxLayout(chip)
        layout.setContentsMargins(10, 8, 10, 11)
        layout.setSpacing(4)

        accent_bar = QFrame()
        accent_bar.setFixedHeight(3)
        accent_bar.setStyleSheet(f"background: {accent}; border: 0; border-radius: 1px;")
        layout.addWidget(accent_bar)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 8.5pt; font-weight: 800;")
        title_label.setWordWrap(True)
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #0f172a; font-size: 12pt; font-weight: 900;")
        value_label.setMinimumHeight(28)
        chip.value_label = value_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return chip

    def update_calculation(self, calculation):
        self.calculation = calculation
        configured = bool(calculation and calculation.get("configured"))
        self.details_button.setVisible(configured)
        self.days_chip.setVisible(configured)
        self.forecast_days_chip.setVisible(configured)
        self.total_amount_label.setVisible(configured)
        self.setup_button.setVisible(not configured)

        if not configured:
            reason = calculation.get("reason") if calculation else "Indstillinger mangler."
            self.amount_label.setText("Feriepenge: Ikke indstillet")
            self.detail_label.setText(reason)
            return

        request_text = f"Ferie kan holdes frem til {format_long_date(calculation['request_end'])}.\n"
        self.amount_label.setText(f"Optjent denne lønperiode: {format_money(calculation.get('period_holiday_pay', 0))}")
        forecast_total = calculation.get("forecast_total_holiday_pay")
        if forecast_total is None:
            self.total_amount_label.setText(f"Total optjent: {format_money(calculation['holiday_pay'])}")
        else:
            self.total_amount_label.setText(
                f"Total optjent: {format_money(calculation['holiday_pay'])}\n"
                f"Total forventet om ½ år: {format_money(forecast_total)} estimeret."
            )
        self.detail_label.setText(
            f"• {request_text}\n"
            "• Udbetaling: tidligst 1 måned før første feriedag.\n\n"
            f"• Beregnet fra {format_long_date(calculation['calculation_start'])} til {format_long_date(calculation['calculation_end'])}."
        )
        self.days_chip.value_label.setText(f"{format_number(calculation['holiday_days'])} dage")
        forecast_days = calculation.get("forecast_holiday_days")
        self.forecast_days_chip.value_label.setText(
            f"{format_number(forecast_days)} dage" if forecast_days is not None else "N/A"
        )

    def _open_details(self):
        if self.calculation and self.calculation.get("configured"):
            self.details_callback(self.calculation)


class HolidayPayDetailsDialog(QDialog):
    def __init__(self, parent, calculation):
        super().__init__(parent)
        self.calculation = calculation
        self.setModal(True)
        self.setWindowTitle("Feriepenge")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(760, 680)
        self.resize(840, 720)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll, 1)

        scroll_body = QWidget()
        scroll.setWidget(scroll_body)
        scroll_layout = QVBoxLayout(scroll_body)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)

        panel, layout = make_panel("Feriepenge")
        scroll_layout.addWidget(panel)

        metric_grid = QGridLayout()
        metric_grid.setSpacing(10)
        metrics = [
            ("Feriepenge", format_money(calculation["holiday_pay"]), "#1f8a70"),
            ("Ferieberettiget løn", format_money(calculation["eligible_salary"]), "#2563eb"),
            ("Feriedage", f"{format_number(calculation['holiday_days'])} dage", "#0f766e"),
        ]
        for index, (title, value, accent) in enumerate(metrics):
            card = MetricCard(title, value, accent=accent)
            card.setMinimumHeight(126)
            metric_grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(metric_grid)

        period_label = QLabel(
            f"Beregnet fra {format_long_date(calculation['calculation_start'])} til {format_long_date(calculation['calculation_end'])}.\n"
            f"Ferieafholdelsesperiode: {format_long_date(calculation['request_start'])} - {format_long_date(calculation['request_end'])}.\n"
            "FerieKonto udbetaler tidligst 1 måned før første feriedag.\n"
        )
        period_label.setObjectName("PageSubtitle")
        period_label.setWordWrap(True)
        layout.addWidget(period_label)

        table = QTableWidget()
        setup_table(table, ["Måned", "Ferieberettiget løn", "Feriepenge", "Feriedage"])
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        monthly_rows = calculation.get("monthly_rows", [])
        table.setRowCount(len(monthly_rows))
        for row_index, row in enumerate(monthly_rows):
            table.setItem(row_index, 0, table_item(row["label"]))
            table.setItem(row_index, 1, table_item(format_money(row["salary"]), Qt.AlignRight | Qt.AlignVCenter))
            table.setItem(row_index, 2, table_item(format_money(row["holiday_pay"]), Qt.AlignRight | Qt.AlignVCenter))
            table.setItem(row_index, 3, table_item(format_number(row["holiday_days"]), Qt.AlignRight | Qt.AlignVCenter))
        visible_months = min(8, max(4, len(monthly_rows)))
        fit_table_height(table, len(monthly_rows), max_rows=8, min_rows=visible_months, bottom_padding=12)
        layout.addWidget(table)
        scroll_layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton("Luk")
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)
        outer.addLayout(button_row)


class LineChart(QWidget):
    def __init__(self):
        super().__init__()
        self.series = []
        self.labels = []
        self.setMinimumHeight(250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, labels, series):
        self.labels = labels
        self.series = series
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.fillRect(rect, QColor("#ffffff"))

        if not self.series or not self.labels:
            painter.setPen(QColor("#6b7280"))
            painter.drawText(rect, Qt.AlignCenter, "Ingen data endnu")
            return

        left, right, top, bottom = 62, 24, 24, 46
        width = max(1, rect.width() - left - right)
        height = max(1, rect.height() - top - bottom)
        chart_left = left
        chart_right = left + width
        chart_top = top
        chart_bottom = top + height

        values = [value for _, data, _ in self.series for value in data if value is not None]
        if not values:
            painter.setPen(QColor("#6b7280"))
            painter.drawText(rect, Qt.AlignCenter, "Ingen data endnu")
            return

        minimum = min(0, min(values))
        maximum = max(values)
        if maximum == minimum:
            maximum = minimum + 1
        padding = (maximum - minimum) * 0.08
        minimum -= padding
        maximum += padding

        painter.setPen(QPen(QColor("#d9e1e6"), 1))
        for index in range(5):
            y = chart_bottom - (height * index / 4)
            painter.drawLine(chart_left, int(y), chart_right, int(y))
            label_value = minimum + ((maximum - minimum) * index / 4)
            painter.setPen(QColor("#6b7280"))
            painter.drawText(4, int(y) - 8, left - 10, 18, Qt.AlignRight, format_number(label_value, 0))
            painter.setPen(QPen(QColor("#d9e1e6"), 1))

        painter.setPen(QPen(QColor("#a8b3bf"), 1))
        painter.drawLine(chart_left, chart_top, chart_left, chart_bottom)
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)

        point_count = len(self.labels)

        def point_for(value, index):
            x = chart_left + (width * index / max(1, point_count - 1))
            y = chart_bottom - ((value - minimum) / (maximum - minimum) * height)
            return QPointF(x, y)

        legend_x = chart_left
        for name, data, color in self.series:
            painter.setPen(QPen(QColor(color), 2.4))
            points = [point_for(value, index) for index, value in enumerate(data) if value is not None]
            for index in range(1, len(points)):
                painter.drawLine(points[index - 1], points[index])
            painter.setBrush(QColor(color))
            for point in points:
                painter.drawEllipse(point, 3.2, 3.2)

            painter.setPen(QColor("#334155"))
            painter.drawText(legend_x + 18, 12, name)
            painter.fillRect(legend_x, 7, 12, 4, QColor(color))
            legend_x += 110

        painter.setPen(QColor("#6b7280"))
        if point_count == 1:
            painter.drawText(chart_left - 20, chart_bottom + 16, 90, 22, Qt.AlignLeft, self.labels[0])
        else:
            label_indexes = sorted({0, point_count // 2, point_count - 1})
            for index in label_indexes:
                x = chart_left + (width * index / max(1, point_count - 1))
                painter.drawText(int(x) - 55, chart_bottom + 16, 110, 22, Qt.AlignCenter, self.labels[index])


class BasePage(QWidget):
    def __init__(self, window, title, subtitle):
        super().__init__(window if isinstance(window, QWidget) else None)
        self.window = window

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page_layout.addWidget(self.scroll_area)

        self.page_body = QWidget(self.scroll_area)
        self.page_body.setObjectName("PageBody")
        self.scroll_area.setWidget(self.page_body)

        self.root = QVBoxLayout(self.page_body)
        self.root.setContentsMargins(28, 24, 28, 24)
        self.root.setSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)

        self.root.addWidget(title_label)
        if subtitle:
            self.root.addWidget(subtitle_label)

    @property
    def data(self):
        return self.window.data

    @property
    def settings(self):
        return self.window.settings

    def refresh(self):
        pass

class CompactScrollPage(BasePage):
    MIN_VALID_VIEWPORT_WIDTH = 320

    def __init__(self, window, title, subtitle):
        super().__init__(window, title, subtitle)

        # Vigtigt:
        # BasePage bruger setWidgetResizable(True), hvilket tvinger page_body
        # til at fylde hele scroll-området. Det giver tom plads nederst,
        # når indholdet er lavere end vinduet.
        self.scroll_area.setWidgetResizable(False)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_compact_body_size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_compact_body_size()

    def _sync_compact_body_size(self):
        viewport_width = self.scroll_area.viewport().width()

        if viewport_width < self.MIN_VALID_VIEWPORT_WIDTH:
            QTimer.singleShot(0, self._sync_compact_body_size)
            return

        self.page_body.setFixedWidth(viewport_width)

        self.root.invalidate()
        self.root.activate()

        height = self.page_body.sizeHint().height()
        self.page_body.setFixedHeight(height)


class DashboardPage(CompactScrollPage):
    def __init__(self, window):
        super().__init__(
            window,
            "Overblik - Nuværende lønperiode",
            "",
        )
        self.root.setAlignment(Qt.AlignTop)

        self.widget_order = []
        self.dashboard_widgets = {}
        self.dragged_widget_key = None
        self.drag_last_global_pos = None
        self.drag_ghost = None
        self.drag_ghost_offset = None
        self.drag_scroll_delta = 0
        self.dashboard_layout_animation = None
        self.drag_autoscroll_timer = QTimer(self)
        self.drag_autoscroll_timer.setInterval(16)
        self.drag_autoscroll_timer.timeout.connect(self._auto_scroll_drag)

        reorder_toolbar = QHBoxLayout()
        reorder_toolbar.setContentsMargins(0, 0, 0, 0)
        reorder_toolbar.setSpacing(8)
        self.root.addLayout(reorder_toolbar)

        reorder_toolbar.addStretch()

        self.add_widget_button = DashboardIconButton("add", "Tilføj widget", parent=self, label_text="Tilføj")
        self.add_widget_button.clicked.connect(self._show_add_widget_dialog)
        self.add_widget_button.hide()
        reorder_toolbar.addWidget(self.add_widget_button, 0, Qt.AlignRight)

        self.reorder_button = DashboardIconButton("widgets", "Rediger widgets", checkable=True, parent=self, label_text="Widgets")
        self.reorder_button.toggled.connect(self._set_reorder_mode)
        reorder_toolbar.addWidget(self.reorder_button, 0, Qt.AlignRight)

        self.dashboard_container = QWidget()
        self.dashboard_container.setObjectName("DashboardContainer")
        self.dashboard_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.dashboard_layout = QVBoxLayout(self.dashboard_container)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_layout.setSpacing(16)

        self.root.addWidget(self.dashboard_container, 0, Qt.AlignTop)

        self.drop_indicator = DashboardDropIndicator(self.dashboard_container)

        goal_panel = self._make_widget_frame("Rådighedsmål", "goal")
        self.goal_card = GoalHeaderWidget(
            show_title=False,
            add_shifts_callback=self._go_to_history_page,
            settings_callback=self._go_to_settings_goal_field,
            budget_callback=self._go_to_budget_page,
        )
        goal_panel.addWidget(self.goal_card)
        self.dashboard_widgets["goal"] = goal_panel

        progress_panel = self._make_widget_frame("Tidslinje", "progress")
        self.period_progress = PeriodProgressWidget()
        self.progress_detail = QLabel()
        self.progress_detail.setObjectName("PageSubtitle")
        self.progress_detail.setWordWrap(True)
        progress_panel.addWidget(self.period_progress)
        progress_panel.addWidget(self.progress_detail)
        self.dashboard_widgets["progress"] = progress_panel

        process_panel = self._make_widget_frame("Løn indtil videre", "process")
        self.summary_strip = DashboardMetricStrip("", columns=3, embedded=True)
        process_panel.addWidget(self.summary_strip)
        self.dashboard_widgets["process"] = process_panel

        self.net_card = DashboardMetricItem("Netto løn", accent="#1f8a70")
        self.total_card = DashboardMetricItem("Total indkomst", accent="#2563eb")
        self.available_card = DashboardMetricItem("Til rådighed", accent="#d97706")
        self.hours_card = DashboardMetricItem("Timer", accent="#7c3aed")
        self.gross_card = DashboardMetricItem("Brutto løn", accent="#0f766e")
        self.period_card = DashboardMetricItem("Lønperiode", accent="#475569")

        self.summary_cards = [
            self.net_card,
            self.total_card,
            self.available_card,
            self.hours_card,
            self.gross_card,
            self.period_card,
        ]
        for card in self.summary_cards:
            self.summary_strip.add_item(card)

        estimate_panel = self._make_widget_frame("Estimater", "estimates")
        self.estimate_strip = DashboardMetricStrip("", columns=3, embedded=True)
        estimate_panel.addWidget(self.estimate_strip)
        self.dashboard_widgets["estimates"] = estimate_panel
        self.estimate_net_card = DashboardMetricItem("Netto løn", accent="#1f8a70")
        self.estimate_total_card = DashboardMetricItem("Total indkomst", accent="#2563eb")
        self.estimate_available_card = DashboardMetricItem("Til rådighed", accent="#d97706")
        self.estimate_hours_card = DashboardMetricItem("Timer", accent="#7c3aed")
        self.estimate_cards = [
            self.estimate_net_card,
            self.estimate_total_card,
            self.estimate_available_card,
            self.estimate_hours_card,
        ]
        for card in self.estimate_cards:
            self.estimate_strip.add_item(card)

        stats_panel = self._make_widget_frame("Statistik", "stats")
        stats_panel.addLayout(self._make_dashboard_link_row("Gå til statistik", self._go_to_statistics_page))
        self.stats_strip = DashboardMetricStrip("", columns=3, embedded=True)
        stats_panel.addWidget(self.stats_strip)
        self.dashboard_widgets["stats"] = stats_panel
        self.stat_average_card = DashboardMetricItem("Snit pr. vagt", accent="#475569")
        self.stat_week_card = DashboardMetricItem("Snit pr. uge", accent="#2563eb")
        self.stat_total_net_card = DashboardMetricItem("Bedste vagt", accent="#1f8a70")
        self.stats_cards = [self.stat_average_card, self.stat_week_card, self.stat_total_net_card]
        for card in self.stats_cards:
            self.stats_strip.add_item(card)

        holiday_panel = self._make_widget_frame("Feriepenge", "holiday_pay")
        self.holiday_pay_widget = DashboardHolidayPayWidget(
            self._go_to_settings_holiday_pay_field,
            self._open_holiday_pay_details,
        )
        holiday_panel.addWidget(self.holiday_pay_widget)
        self.dashboard_widgets["holiday_pay"] = holiday_panel

        budget_panel = self._make_widget_frame("Budget", "budget")
        self.budget_widget = DashboardBudgetWidget(self._go_to_budget_page)
        budget_panel.addWidget(self.budget_widget)
        self.dashboard_widgets["budget"] = budget_panel

        breakdown_panel = self._make_widget_frame("Skatteopdeling", "breakdown")
        self.breakdown_table = QTableWidget()
        setup_table(self.breakdown_table, ["Post", "Beløb"])
        breakdown_panel.addWidget(self.breakdown_table)
        self.dashboard_widgets["breakdown"] = breakdown_panel

        recent_panel = self._make_widget_frame("Vagter i perioden", "recent")
        recent_panel.addLayout(self._make_dashboard_link_row("Gå til vagter", self._go_to_history_page))
        self.recent_table = QTableWidget()
        setup_table(self.recent_table, ["Dato", "Timer", "Pause", "Netto"])
        setup_shift_table_columns(self.recent_table, 1)
        recent_panel.addWidget(self.recent_table)
        self.dashboard_widgets["recent"] = recent_panel

        calculator_panel = self._make_widget_frame("Lønberegner", "salary_calculator")
        calculator_panel.addLayout(self._make_dashboard_link_row("Gå til lønberegner", self._go_to_calculator_page))
        self.salary_calculator_widget = DashboardSalaryCalculatorWidget()
        calculator_panel.addWidget(self.salary_calculator_widget)
        self.dashboard_widgets["salary_calculator"] = calculator_panel

        self._apply_widget_order()

    def _make_widget_frame(self, title, key):
        return DashboardWidgetFrame(
            title,
            key,
            self._start_widget_drag,
            self._drag_widget,
            self._finish_widget_drag,
            self._remove_widget,
            parent=self.page_body,
        )

    def _apply_widget_order(self):
        self.widget_order = [
            key
            for key in dashboard_widget_order(self.settings)
            if key in self.dashboard_widgets
        ]
        self._render_widget_order()

    def _render_widget_order(self, animate=False, extra_start_geometries=None):
        scroll_value = self.scroll_area.verticalScrollBar().value()
        edit_mode = self.reorder_button.isChecked()
        dragged_key = self.dragged_widget_key
        visible_order = [key for key in self.widget_order if key != dragged_key]
        drop_index = self.widget_order.index(dragged_key) if dragged_key in self.widget_order else None
        start_geometries = self._capture_dashboard_geometries() if animate else {}
        if extra_start_geometries:
            start_geometries.update(extra_start_geometries)

        for widget in self.dashboard_widgets.values():
            self.dashboard_layout.removeWidget(widget)
            widget.setVisible(False)
        self.dashboard_layout.removeWidget(self.drop_indicator)
        self.drop_indicator.hide()

        for index, key in enumerate(visible_order):
            if drop_index == index:
                self.dashboard_layout.addWidget(self.drop_indicator)
                self.drop_indicator.show()
            widget = self.dashboard_widgets[key]
            widget.set_reorder_mode(edit_mode)
            self.dashboard_layout.addWidget(widget)
            widget.setVisible(True)

        if drop_index == len(visible_order):
            self.dashboard_layout.addWidget(self.drop_indicator)
            self.drop_indicator.show()

        self._update_add_widget_button()

        self.dashboard_container.updateGeometry()
        self._sync_compact_body_size()

        self._restore_scroll_position(scroll_value)

        if animate:
            self._animate_dashboard_reflow(start_geometries)

    def _dashboard_reflow_widgets(self):
        return list(self.dashboard_widgets.values()) + [self.drop_indicator]

    def _capture_dashboard_geometries(self):
        self.dashboard_layout.activate()
        self.page_body.layout().activate()
        geometries = {}
        for widget in self._dashboard_reflow_widgets():
            if widget.isVisible():
                geometries[widget] = QRect(widget.geometry())
        return geometries

    def _stop_dashboard_reflow_animation(self):
        if self.dashboard_layout_animation is not None:
            self.dashboard_layout_animation.stop()
            self.dashboard_layout_animation.deleteLater()
            self.dashboard_layout_animation = None

            self.dashboard_layout.invalidate()
            self.dashboard_layout.activate()
            self.dashboard_container.updateGeometry()

            self.page_body.layout().invalidate()
            self.page_body.layout().activate()

    def _animate_dashboard_reflow(self, start_geometries):
        self._stop_dashboard_reflow_animation()

        self.dashboard_layout.activate()
        self.dashboard_container.updateGeometry()
        self.page_body.layout().activate()
        QApplication.processEvents()

        end_geometries = self._capture_dashboard_geometries()

        animation_group = QParallelAnimationGroup(self)

        for widget, end_geometry in end_geometries.items():
            start_geometry = start_geometries.get(widget)
            if start_geometry is None:
                continue

            start_pos = start_geometry.topLeft()
            end_pos = end_geometry.topLeft()

            if start_pos == end_pos:
                continue

            widget.move(start_pos)
            widget.raise_()
            self.dashboard_container.raise_()

            animation = QPropertyAnimation(widget, b"pos", animation_group)
            animation.setStartValue(start_pos)
            animation.setEndValue(end_pos)
            animation.setDuration(170)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation_group.addAnimation(animation)

        if animation_group.animationCount() == 0:
            animation_group.deleteLater()
            return

        self.dashboard_layout_animation = animation_group
        animation_group.finished.connect(lambda: self._finish_dashboard_reflow_animation(animation_group))
        animation_group.start()

    def _finish_dashboard_reflow_animation(self, animation_group):
        if self.dashboard_layout_animation is animation_group:
            self.dashboard_layout_animation = None

        for widget in self._dashboard_reflow_widgets():
            if widget.isVisible():
                widget.updateGeometry()

        self.dashboard_layout.invalidate()
        self.dashboard_layout.activate()
        self.dashboard_container.updateGeometry()

        self.page_body.layout().invalidate()
        self.page_body.layout().activate()

        animation_group.deleteLater()

    def _restore_scroll_position(self, value):
        def restore():
            bar = self.scroll_area.verticalScrollBar()
            bar.setValue(max(bar.minimum(), min(value, bar.maximum())))

        restore()
        QTimer.singleShot(0, restore)

    def _set_reorder_mode(self, enabled):
        for widget in self.dashboard_widgets.values():
            widget.set_reorder_mode(enabled)
        self._update_add_widget_button()

    def _hidden_widget_options(self):
        return [
            (key, DASHBOARD_WIDGET_TITLES[key])
            for key in DASHBOARD_AVAILABLE_WIDGET_ORDER
            if key not in self.widget_order
        ]

    def _update_add_widget_button(self):
        self.add_widget_button.setVisible(self.reorder_button.isChecked())
        self.add_widget_button.setEnabled(True)

    def _show_add_widget_dialog(self):
        hidden_options = self._hidden_widget_options()
        dialog = DashboardAddWidgetDialog(self, hidden_options)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_key:
            self._add_widget(dialog.selected_key)

    def _add_widget(self, key):
        if key not in DASHBOARD_AVAILABLE_WIDGET_ORDER or key in self.widget_order:
            return

        self.widget_order.insert(0, key)
        self._save_widget_order()
        self._render_widget_order()

    def _make_dashboard_link_row(self, text, callback):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.addStretch()

        button = QPushButton(text)
        button.setObjectName("InlineButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(callback)

        row.addWidget(button, 0, Qt.AlignRight | Qt.AlignVCenter)
        return row

    def _go_to_budget_page(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, BudgetPage):
                self.window.go_to_page(index)
                return

    def _go_to_history_page(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, HistoryPage):
                self.window.go_to_page(index)
                return

    def _go_to_settings_goal_field(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, SettingsPage):
                self.window.go_to_page(index)
                QTimer.singleShot(0, page.focus_disposable_goal)
                return

    def _go_to_settings_holiday_pay_field(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, SettingsPage):
                self.window.go_to_page(index)
                QTimer.singleShot(0, page.focus_holiday_pay)
                return

    def _go_to_statistics_page(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, StatisticsPage):
                self.window.go_to_page(index)
                return


    def _go_to_calculator_page(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, CalculatorPage):
                self.window.go_to_page(index)
                return

    def _open_holiday_pay_details(self, calculation):
        dialog = HolidayPayDetailsDialog(self, calculation)
        dialog.exec_()
        
    def _start_widget_drag(self, key, global_pos):
        if not self.reorder_button.isChecked() or key not in self.widget_order:
            return

        self.dragged_widget_key = key
        self.drag_last_global_pos = global_pos
        self._create_drag_ghost(key, global_pos)
        self._render_widget_order(animate=True)
        self._update_drag_order(global_pos)
        self._update_auto_scroll(global_pos)

    def _drag_widget(self, key, global_pos):
        if key != self.dragged_widget_key:
            return

        self.drag_last_global_pos = global_pos
        self._move_drag_ghost(global_pos)
        self._update_drag_order(global_pos)
        self._update_auto_scroll(global_pos)

    def _finish_widget_drag(self, key):
        if key != self.dragged_widget_key:
            return

        self._stop_auto_scroll()
        finish_start_geometries = self._drag_finish_start_geometries(key)
        self._clear_drag_ghost()
        self.dragged_widget_key = None
        self.drag_last_global_pos = None
        self._save_widget_order()
        self._render_widget_order(animate=True, extra_start_geometries=finish_start_geometries)

    def _update_drag_order(self, global_pos):
        key = self.dragged_widget_key
        if key not in self.widget_order:
            return

        target_index = self._drag_target_index(global_pos)
        reordered = [widget_key for widget_key in self.widget_order if widget_key != key]
        target_index = max(0, min(target_index, len(reordered)))
        reordered.insert(target_index, key)
        if reordered == self.widget_order:
            return

        self.widget_order = reordered
        self._render_widget_order(animate=True)

    def _drag_finish_start_geometries(self, key):
        if self.drag_ghost is None or key not in self.dashboard_widgets:
            return {}

        top_left = self.dashboard_container.mapFromGlobal(self.drag_ghost.mapToGlobal(QPoint(0, 0)))
        return {self.dashboard_widgets[key]: QRect(top_left, self.drag_ghost.size())}

    def _create_drag_ghost(self, key, global_pos):
        self._clear_drag_ghost()
        widget = self.dashboard_widgets[key]
        pixmap = widget.grab()
        if pixmap.isNull():
            return

        ghost_pixmap = QPixmap(pixmap.size())
        ghost_pixmap.fill(Qt.transparent)
        painter = QPainter(ghost_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(0.88)
        painter.drawPixmap(0, 0, pixmap)
        painter.setOpacity(1)
        painter.setPen(QPen(QColor("#1f8a70"), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(1, 1, pixmap.width() - 2, pixmap.height() - 2), 8, 8)
        painter.end()

        self.drag_ghost_offset = global_pos - widget.mapToGlobal(widget.rect().topLeft())
        ghost_parent = self.window if isinstance(self.window, QWidget) else self
        self.drag_ghost = QLabel(ghost_parent)
        self.drag_ghost.setPixmap(ghost_pixmap)
        self.drag_ghost.setFixedSize(ghost_pixmap.size())
        self.drag_ghost.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._move_drag_ghost(global_pos)
        self.drag_ghost.show()
        self.drag_ghost.raise_()

    def _move_drag_ghost(self, global_pos):
        if self.drag_ghost is None or self.drag_ghost_offset is None:
            return

        top_left_global = global_pos - self.drag_ghost_offset
        parent = self.drag_ghost.parentWidget()
        self.drag_ghost.move(parent.mapFromGlobal(top_left_global))
        self.drag_ghost.raise_()

    def _clear_drag_ghost(self):
        if self.drag_ghost is not None:
            self.drag_ghost.hide()
            self.drag_ghost.deleteLater()
        self.drag_ghost = None
        self.drag_ghost_offset = None

    def _drag_target_index(self, global_pos):
        cursor_y = self.dashboard_container.mapFromGlobal(global_pos).y()
        target_index = 0

        for key in self.widget_order:
            if key == self.dragged_widget_key:
                continue

            widget = self.dashboard_widgets[key]
            center_y = widget.mapTo(self.dashboard_container, widget.rect().center()).y()

            if cursor_y > center_y:
                target_index += 1

        return target_index

    def _update_auto_scroll(self, global_pos):
        viewport = self.scroll_area.viewport()
        cursor_pos = viewport.mapFromGlobal(global_pos)
        threshold = 72
        max_delta = 22
        delta = 0

        if cursor_pos.y() < threshold:
            distance = threshold - max(cursor_pos.y(), 0)
            delta = -max(3, int(max_delta * min(distance / threshold, 1)))
        elif cursor_pos.y() > viewport.height() - threshold:
            distance = threshold - max(viewport.height() - cursor_pos.y(), 0)
            delta = max(3, int(max_delta * min(distance / threshold, 1)))

        self.drag_scroll_delta = delta
        if delta and not self.drag_autoscroll_timer.isActive():
            self.drag_autoscroll_timer.start()
        elif not delta:
            self._stop_auto_scroll()

    def _auto_scroll_drag(self):
        if self.dragged_widget_key is None or not self.drag_scroll_delta:
            self._stop_auto_scroll()
            return

        bar = self.scroll_area.verticalScrollBar()
        previous_value = bar.value()
        bar.setValue(previous_value + self.drag_scroll_delta)
        if bar.value() == previous_value:
            self._stop_auto_scroll()
            return

        if self.drag_last_global_pos is not None:
            self._update_drag_order(self.drag_last_global_pos)

    def _stop_auto_scroll(self):
        self.drag_scroll_delta = 0
        if self.drag_autoscroll_timer.isActive():
            self.drag_autoscroll_timer.stop()

    def _remove_widget(self, key):
        if key not in self.widget_order:
            return

        self.widget_order = [widget_key for widget_key in self.widget_order if widget_key != key]
        self._save_widget_order()
        self._render_widget_order()

    def _save_widget_order(self):
        try:
            new_settings = dict(self.settings) if isinstance(self.settings, dict) else ft.load_settings()
            new_settings[DASHBOARD_WIDGET_ORDER_KEY] = list(self.widget_order)
            new_settings[DASHBOARD_BUDGET_WIDGET_MIGRATION_KEY] = True
            new_settings[DASHBOARD_HOLIDAY_PAY_WIDGET_MIGRATION_KEY] = True
            ft.save_settings(new_settings, history_reason="Gem rækkefølge på overblik-widgets")
            self.window.settings = ft.load_settings()
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.warning(self, "Rækkefølge kunne ikke gemmes", str(error))

    def leave_page(self):
        if self.dragged_widget_key is not None:
            self._stop_auto_scroll()
            self._clear_drag_ghost()
            self.dragged_widget_key = None
            self.drag_last_global_pos = None
            self._render_widget_order()

        if self.reorder_button.isChecked():
            self.reorder_button.setChecked(False)
            self._set_reorder_mode(False)

        self.add_widget_button.hide()

    def refresh(self):
        self._apply_widget_order()
        budget_categories = ft.get_budget_categories(self.settings)
        self.budget_widget.update_budget(budget_categories)
        self.salary_calculator_widget.set_settings(self.settings)
        if not has_required_settings(self.settings):
            self._show_missing_settings()
            return

        summary = current_period_summary(self.data, self.settings)
        forecast = ft.calculate_salary_forecast(self.data, self.settings, use_entry_settings=False)
        other_income = summary.get("other_income", ft.get_other_income(self.settings, summary["periode_start"], summary["periode_slut"]))
        budget_expenses = summary.get("budget_expenses", ft.calculate_budget_expenses(self.settings, summary["periode_start"], summary["periode_slut"]))
        previous_period = self._last_complete_period_info()

        total_now = summary["netto"] + other_income
        available_now = total_now - budget_expenses
        estimated_total = forecast.get("estimated_total_income") if forecast else None
        estimated_available = forecast.get("estimated_disposable_income") if forecast else None
        estimated_netto = forecast.get("estimated_netto") if forecast else None
        estimated_brutto = forecast.get("estimated_brutto") if forecast else None
        estimated_hours = forecast.get("estimated_hours") if forecast else None
        disposable_goal = ft.get_disposable_income_goal(self.settings, summary["periode_start"], summary["periode_slut"])
        monthly_disposable_goal = float(ft.normalize_settings(self.settings).get("ønsket rådighedsbeløb", 0) or 0)
        show_other_income = other_income > 0
        self._arrange_cards(show_other_income)
        today = datetime.now().date()
        self.holiday_pay_widget.update_calculation(holiday_pay_calculation(self.data, self.settings, today))
        total_days = max(1, (summary["periode_slut"] - summary["periode_start"]).days + 1)
        elapsed_days = min(max((today - summary["periode_start"]).days + 1, 0), total_days)
        remaining_days = max(total_days - elapsed_days, 0)
        progress_ratio = elapsed_days / total_days if total_days else 0

        self.net_card.set_values(format_money(summary["netto"]), "Efter skat")
        if show_other_income:
            self.total_card.set_values(format_money(total_now), "Netto løn nu + anden indkomst")
        self.available_card.set_values(format_money(available_now), f"Efter udgifter: {format_money(budget_expenses)}")
        work_count = len(summary.get("work_rows", []))
        day_off_count = len(summary.get("day_off_rows", []))
        day_off_suffix = f" · {day_off_count} fridage" if day_off_count else ""
        self.hours_card.set_values(f"{format_number(summary['timer'])} t.", f"{work_count} vagter i perioden{day_off_suffix}")
        self.gross_card.set_values(format_money(summary["brutto"]), "Før skat")
        self.period_card.set_values(
            ft.get_pay_period_description(self.settings),
            format_period(summary),
        )
        estimated_hours_text = f"{format_number(estimated_hours)} t." if estimated_hours is not None else "N/A"
        self.estimate_net_card.set_values(format_money(estimated_netto), "For hele lønperioden")
        if show_other_income:
            self.estimate_total_card.set_values(format_money(estimated_total), "Estimeret netto + anden indkomst")
        self.estimate_available_card.set_values(format_money(estimated_available), f"Efter faste udgifter: {format_money(budget_expenses)}")
        self.estimate_hours_card.set_values(estimated_hours_text, f"Estimeret brutto: {format_money(estimated_brutto)}")

        if forecast:
            progress_ratio = forecast.get("progress_ratio", progress_ratio)
            elapsed_days = forecast.get("elapsed_days", elapsed_days)
            total_days = forecast.get("total_days", total_days)
            remaining_days = forecast.get("remaining_days", remaining_days)
        self.period_progress.set_period(
            summary["periode_start"],
            summary["periode_slut"],
            today,
            summary["rows"],
            progress_ratio,
        )
        if summary["rows"]:
            registration_text = f"{work_count} vagter"
            if day_off_count:
                registration_text += f" og {day_off_count} fridage"
            self.progress_detail.setText(
                f"{elapsed_days} af {total_days} dage er gået. {remaining_days} dage tilbage. "
                f"{registration_text} i perioden. Netto løn: {format_money(summary['netto'])}."
            )
        else:
            self.progress_detail.setText(
                f"{elapsed_days} af {total_days} dage er gået. {remaining_days} dage tilbage. "
                "Ingen vagter registreret i perioden endnu."
            )

        self._update_goal_status(
            available_now,
            estimated_available,
            disposable_goal,
            previous_period,
            summary["rows"],
            budget_categories,
            monthly_disposable_goal,
        )
        self._update_stats(summary)
        self._fill_breakdown(summary["breakdown"])
        self._fill_recent(summary["rows"])

        self.dashboard_container.updateGeometry()
        self._sync_compact_body_size()

    def _arrange_cards(self, show_other_income):
        summary_cards = [
            self.net_card,
            self.available_card,
            self.hours_card,
            self.gross_card,
            self.period_card,
        ]
        if show_other_income:
            summary_cards.insert(1, self.total_card)
        self.summary_strip.set_visible_items(summary_cards)

        estimate_cards = [
            self.estimate_net_card,
            self.estimate_available_card,
            self.estimate_hours_card,
        ]
        if show_other_income:
            estimate_cards.insert(1, self.estimate_total_card)
        self.estimate_strip.set_visible_items(estimate_cards)

    def _show_missing_settings(self):
        self.budget_widget.update_budget(ft.get_budget_categories(self.settings))
        self.salary_calculator_widget.set_settings(self.settings)
        self.holiday_pay_widget.update_calculation(holiday_pay_calculation(self.data, self.settings))
        self._arrange_cards(True)
        for card in [
            self.net_card,
            self.total_card,
            self.available_card,
            self.hours_card,
            self.gross_card,
            self.period_card,
            self.estimate_net_card,
            self.estimate_total_card,
            self.estimate_available_card,
            self.estimate_hours_card,
            self.stat_average_card,
            self.stat_week_card,
            self.stat_total_net_card,
        ]:
            card.set_values("N/A", "Indstillinger mangler")
        self.period_progress.clear()
        self.progress_detail.setText("Udfyld indstillingerne før beregninger kan vises.")
        self.goal_card.set_status("neutral", "Ikke beregnet", "Udfyld indstillingerne før målet kan vurderes.", None)
        self.breakdown_table.setRowCount(0)
        self.recent_table.setRowCount(0)
        fit_table_height(self.breakdown_table, 0, max_rows=8, min_rows=1)
        fit_table_height(self.recent_table, 0, max_rows=20, min_rows=1, bottom_padding=0)

        self.dashboard_container.updateGeometry()
        self._sync_compact_body_size()

    def _last_complete_period_info(self):
        return last_complete_period_info(self.data, self.settings)

    def _update_stats(self, summary):
        rows = summary.get("work_rows", summary["rows"])
        if not rows:
            self.stat_average_card.set_values("N/A", "Ingen vagter i perioden")
            self.stat_week_card.set_values("N/A", "Ingen vagter i perioden")
            self.stat_total_net_card.set_values("N/A", "Ingen vagter i perioden")
            return

        avg_netto = summary["netto"] / len(rows)
        avg_hours = average_or_none(row["timer"] for row in rows)
        total_weeks = max(1 / 7, ((summary["periode_slut"] - summary["periode_start"]).days + 1) / 7)
        weekly_netto = summary["netto"] / total_weeks
        weekly_hours = summary["timer"] / total_weeks
        best_shift = max(rows, key=lambda row: (row.get("netto", 0), row.get("brutto", 0), row["dato"]))
        self.stat_average_card.set_values(format_money(avg_netto), f"{format_number(avg_hours)} timer · denne periode")
        self.stat_week_card.set_values(format_money(weekly_netto), f"{format_number(weekly_hours)} timer/uge · denne periode")
        self.stat_total_net_card.set_values(
            format_money(best_shift.get("netto", 0)),
            f"{format_date(best_shift['dato'])} · {format_number(best_shift['timer'])} t.",
        )

    def _update_goal_status(self, available_now, estimated_available, disposable_goal, previous_period, current_rows, budget_categories, monthly_disposable_goal):
        has_any_shifts = any(not ft.is_day_off(next(iter(entry.values()))) for entry in self.data)
        has_budget_posts = bool(budget_categories)
        show_budget_button = has_any_shifts and disposable_goal > 0 and not has_budget_posts
        goal_text = (
            f"Månedsmål: {format_money(monthly_disposable_goal)}. "
            f"Mål for denne lønperiode: {format_money(disposable_goal)}."
        )

        if disposable_goal <= 0:
            self.goal_card.set_status(
                "neutral",
                "Ikke indstillet",
                "Angiv et ønsket rådighedsbeløb i Indstillinger for at følge målet.",
                previous_period,
                show_settings_button=True,
            )
        elif not has_any_shifts:
            self.goal_card.set_status(
                "empty",
                "Ingen vagter registreret",
                f"{goal_text}\nDer findes endnu ingen vagter i databasen.",
                previous_period,
                show_add_shifts_button=True,
                target_amount=disposable_goal,
                monthly_target_amount=monthly_disposable_goal,
            )
        elif available_now >= disposable_goal:
            self.goal_card.set_status(
                "success",
                "Målet er nået",
                f"Målet er nået for den nuværende lønperiode.\n{goal_text}",
                previous_period,
                show_budget_button=show_budget_button,
                current_amount=available_now,
                target_amount=disposable_goal,
                monthly_target_amount=monthly_disposable_goal,
            )
        elif estimated_available is not None and estimated_available >= disposable_goal:
            missing_now = max(0, disposable_goal - available_now)
            self.goal_card.set_status(
                "warning",
                "Estimatet når målet",
                f"Der mangler {format_money(missing_now)} lige nu, men prognosen ligger over periodemålet.\n{goal_text}",
                previous_period,
                show_budget_button=show_budget_button,
                current_amount=available_now,
                target_amount=disposable_goal,
                estimate_amount=estimated_available,
                monthly_target_amount=monthly_disposable_goal,
            )
        elif estimated_available is None:
            self.goal_card.set_status(
                "neutral",
                "Budget mangler",
                "Indstil dit budget i Budget-sektionen for at beregne rådighedsmål.",
                previous_period,
                show_budget_button=show_budget_button,
                current_amount=available_now,
                target_amount=disposable_goal,
                monthly_target_amount=monthly_disposable_goal,
            )
        else:
            missing_estimate = max(0, disposable_goal - estimated_available)
            self.goal_card.set_status(
                "danger",
                "Prognosen er under målet",
                f"Forventet rådighed ligger {format_money(missing_estimate)} under periodemålet.\n{goal_text}",
                previous_period,
                show_budget_button=show_budget_button,
                current_amount=available_now,
                target_amount=disposable_goal,
                estimate_amount=estimated_available,
                monthly_target_amount=monthly_disposable_goal,
            )

    def _fill_breakdown(self, breakdown):
        rows = [
            ("Brutto løn", format_money(breakdown["brutto"])),
            ("Pension", f"-{format_money(breakdown.get('pension', 0))}"),
        ]
        if breakdown.get("atp_medarbejder", 0) > 0:
            rows.append(("ATP medarbejder", f"-{format_money(breakdown.get('atp_medarbejder', 0))}"))
        rows.extend(
            [
                ("AM-bidrag", f"-{format_money(breakdown['am_bidrag'])}"),
                ("Efter AM-bidrag", format_money(breakdown["efter_am"])),
                ("Fradrag", format_money(breakdown["fradrag"])),
                ("Skattegrundlag", format_money(breakdown["skattegrundlag"])),
                ("Skat", f"-{format_money(breakdown['skat'])}"),
                ("Netto løn", format_money(breakdown["netto"])),
            ]
        )
        if breakdown.get("arbejdsgiver_pension", 0) > 0:
            rows.append(("Arbejdsgiverpension", format_money(breakdown.get("arbejdsgiver_pension", 0))))
        if breakdown.get("atp_arbejdsgiver", 0) > 0:
            rows.append(("ATP arbejdsgiver", format_money(breakdown.get("atp_arbejdsgiver", 0))))
        self.breakdown_table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.breakdown_table.setItem(row_index, 0, table_item(label))
            self.breakdown_table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(self.breakdown_table, len(rows), max_rows=len(rows), min_rows=len(rows))

    def _fill_recent(self, rows):
        self.recent_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            if row.get("is_day_off"):
                self.recent_table.setItem(row_index, 0, day_off_table_item(format_shift_table_date(row["dato"])))
                self.recent_table.setItem(row_index, 1, day_off_table_item("Fridag", Qt.AlignRight | Qt.AlignVCenter))
                self.recent_table.setItem(row_index, 2, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
                self.recent_table.setItem(row_index, 3, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
            else:
                self.recent_table.setItem(row_index, 0, table_item(format_shift_table_date(row["dato"])))
                self.recent_table.setItem(row_index, 1, table_item(format_work_time(row), Qt.AlignRight | Qt.AlignVCenter))
                self.recent_table.setItem(row_index, 2, table_item(format_pause_minutes(row["pause"]), Qt.AlignRight | Qt.AlignVCenter))
                self.recent_table.setItem(row_index, 3, table_item(format_money(row["netto"]), Qt.AlignRight | Qt.AlignVCenter))
        setup_shift_table_columns(self.recent_table, 1)
        fit_table_height(self.recent_table, len(rows), max_rows=20, min_rows=min(3, max(1, len(rows))), bottom_padding=0)


class ShiftEntryDialog(QDialog):
    def __init__(self, parent, window):
        super().__init__(parent)
        self.window = window
        self.saved_date = None
        self.saved_id = None

        self.setModal(True)
        self.setWindowTitle("Tilføj vagt")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(420, 460)
        self.resize(460, 500)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        form_panel, form_layout = make_panel("Ny vagt")
        form_panel.setMinimumWidth(380)
        root.addWidget(form_panel, 1)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setVerticalSpacing(12)
        form_layout.addLayout(form)
        self.entry_form = form

        self.date_edit = make_text_input(placeholder="dd-mm-åååå")
        self.date_edit.textChanged.connect(self._update_summary)
        form.addRow("Dato", self.date_edit)

        self.mode_combo = ModernComboBox()
        self.mode_combo.addItems(["Start/slut", "Antal timer"])
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentIndexChanged.connect(self._update_mode)
        form.addRow("Metode", self.mode_combo)

        self.hours_field = make_text_input("4", "fx 4,5")
        self.hours_field.textChanged.connect(self._update_summary)
        form.addRow("Timer", self.hours_field)

        self.start_field = make_text_input("14:00", "HH:MM")
        self.start_field.textChanged.connect(self._update_summary)
        form.addRow("Start", self.start_field)

        self.end_field = make_text_input("18:00", "HH:MM")
        self.end_field.textChanged.connect(self._update_summary)
        form.addRow("Slut", self.end_field)

        self.rate_field = make_text_input("150", "fx 150")
        self.rate_field.textChanged.connect(self._update_summary)
        form.addRow("Timeløn", self.rate_field)

        self.pause_field = make_text_input("0", "fx 30")
        self.pause_field.textChanged.connect(self._update_summary)
        form.addRow("Pause (minutter)", self.pause_field)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("color: #42505f; padding-top: 8px;")
        form_layout.addWidget(self.summary_label)

        button_row = QHBoxLayout()
        form_layout.addLayout(button_row)
        self.save_button = QPushButton("Gem vagt")
        self.save_button.clicked.connect(self._save_entry)
        button_row.addWidget(self.save_button)
        reset_button = QPushButton("Nulstil")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self._set_defaults)
        button_row.addWidget(reset_button)
        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        self._set_defaults()

    @property
    def data(self):
        return self.window.data

    @property
    def settings(self):
        return self.window.settings

    def _set_defaults(self):
        entry_date = default_entry_date()
        start_time, end_time = default_shift_times(self.window.data)
        try:
            default_duration = calculate_hours_from_times(start_time, end_time)
        except ValueError:
            start_time, end_time = DEFAULT_SHIFT_START_TIME, DEFAULT_SHIFT_END_TIME
            default_duration = 4

        self.date_edit.setText(format_date(entry_date))
        self.mode_combo.setCurrentIndex(0)
        self.hours_field.setText(format_number(default_duration))
        self.start_field.setText(start_time)
        self.end_field.setText(end_time)
        self.pause_field.setText("0")
        set_field_number(self.rate_field, last_rate(self.window.data, self.window.settings))
        self._update_mode()

    def _update_mode(self):
        use_time = self.mode_combo.currentIndex() == 0
        set_form_row_visible(self.entry_form, self.hours_field, not use_time)
        set_form_row_visible(self.entry_form, self.start_field, use_time)
        set_form_row_visible(self.entry_form, self.end_field, use_time)
        self._update_summary()

    def _selected_duration(self):
        if self.mode_combo.currentIndex() == 1:
            return parse_positive_number(self.hours_field, "Timer")
        return calculate_hours_from_times(self.start_field.text(), self.end_field.text())

    def _selected_hours_and_pause(self):
        duration = self._selected_duration()
        pause = parse_pause_hours(self.pause_field)
        paid_hours = duration - pause
        if paid_hours <= 0:
            raise ValueError("Pause må ikke være lige så lang som eller længere end vagten.")
        return duration, paid_hours, pause

    def _update_summary(self):
        try:
            duration, hours, pause = self._selected_hours_and_pause()
            rate = parse_positive_number(self.rate_field, "Timeløn")
        except ValueError:
            self.summary_label.setText("Udfyld timer, pause og timeløn for at se beregningen.")
            return

        brutto = hours * rate
        netto = None
        if has_required_settings(self.settings):
            try:
                selected_date = parse_date_text(self.date_edit.text())
                period_start, period_end = ft.get_salary_period_for_date(selected_date, settings=self.settings)
                netto = ft.calculate_salary_breakdown_from_brutto(
                    brutto,
                    hours,
                    self.settings,
                    period_start,
                    period_end,
                )["netto"]
            except ValueError:
                netto = ft.calculate_salary_breakdown_from_brutto(brutto, hours, self.settings)["netto"]
        pause_text = f" | Pause: {format_pause_minutes(pause)} min." if pause > 0 else ""
        self.summary_label.setText(
            f"Vagt: {format_number(hours)} betalte timer á {format_money(rate)}{pause_text}\n"
            f"Brutto: {format_money(brutto)}  |  Netto: {format_money(netto)}"
        )

    def _existing_date_choice(self, selected_date, existing_rows):
        date_rows = rows_on_date(existing_rows, selected_date)
        if not date_rows:
            return "add", None

        if any(row.get("is_day_off") for row in date_rows):
            QMessageBox.warning(
                self,
                "Dato er fridag",
                f"{format_date(selected_date)} er markeret som fridag. Fjern fridagen før du indberetter en vagt på datoen.",
            )
            return None, None

        message = QMessageBox(self)
        message.setWindowTitle("Dato findes allerede")
        message.setWindowIcon(app_icon())
        message.setText(
            f"{format_date(selected_date)} findes allerede i databasen.\n\n"
            "Vil du overskrive en eksisterende vagt eller tilføje en ny vagt?"
        )
        overwrite_button = message.addButton("Overskriv vagt", QMessageBox.AcceptRole)
        add_button = message.addButton("Tilføj ny vagt", QMessageBox.ActionRole)
        cancel_button = message.addButton("Annuller", QMessageBox.RejectRole)
        message.exec_()

        clicked = message.clickedButton()
        if clicked == overwrite_button:
            if len(date_rows) == 1:
                return "overwrite", str(date_rows[0].get("id"))

            options = []
            option_rows = {}
            for index, row in enumerate(date_rows, start=1):
                label = (
                    f"{index}. {format_work_time(row).replace(chr(10), ' · ')} · "
                    f"{format_money(row.get('timeløn'))}"
                )
                options.append(label)
                option_rows[label] = row

            selected_label, accepted = QInputDialog.getItem(
                self,
                "Vælg vagt",
                "Vagt der skal overskrives:",
                options,
                0,
                False,
            )
            if not accepted:
                return None, None
            return "overwrite", str(option_rows[selected_label].get("id"))
        if clicked == add_button:
            return "add", None
        if clicked == cancel_button:
            return None, None
        return None, None

    def _save_entry(self):
        try:
            selected_date = parse_date_text(self.date_edit.text())
            duration, hours, pause = self._selected_hours_and_pause()
            rate = parse_positive_number(self.rate_field, "Timeløn")

            start_time = None
            end_time = None

            if self.mode_combo.currentIndex() == 0:
                start_time = self.start_field.text().strip()
                end_time = self.end_field.text().strip()

        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig vagt", str(error))
            return

        key = date_to_key(selected_date)
        existing_rows = entry_rows(ft.load_data(), self.settings)
        choice, overwrite_id = self._existing_date_choice(selected_date, existing_rows)
        if choice is None:
            return

        try:
            self.saved_id = upsert_entry(
                selected_date,
                duration,
                rate,
                start=start_time,
                slut=end_time,
                pause=pause,
                entry_settings=self.settings,
                original_id=overwrite_id if choice == "overwrite" else None,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Vagt kan ikke gemmes", str(error))
            return
        self.saved_date = selected_date

        show_success_message(
            self,
            "Vagt gemt",
            f"{key} blev gemt med {format_number(hours)} betalte timer á {format_money(rate)}.",
        )
        self.accept()


class DayOffEntryDialog(QDialog):
    def __init__(self, parent, window):
        super().__init__(parent)
        self.window = window
        self.saved_date = None
        self.saved_id = None

        self.setModal(True)
        self.setWindowTitle("Indberet fridag")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(380, 260)
        self.resize(420, 280)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        form_panel, form_layout = make_panel("Ny fridag")
        root.addWidget(form_panel, 1)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setVerticalSpacing(12)
        form_layout.addLayout(form)

        self.date_edit = make_text_input(format_date(default_entry_date()), "dd-mm-åååå")
        form.addRow("Dato", self.date_edit)

        note = QLabel("Fridagen gemmes uden timer og løn, men vises i tidslinje, lønsedler, statistik og vagt-tabeller.")
        note.setObjectName("PageSubtitle")
        note.setWordWrap(True)
        form_layout.addWidget(note)

        button_row = QHBoxLayout()
        form_layout.addLayout(button_row)
        save_button = QPushButton("Gem fridag")
        save_button.clicked.connect(self._save_entry)
        button_row.addWidget(save_button)
        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

    def _save_entry(self):
        try:
            selected_date = parse_date_text(self.date_edit.text())
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig fridag", str(error))
            return

        key = date_to_key(selected_date)
        existing_rows = entry_rows(ft.load_data(), self.window.settings)
        if rows_on_date(existing_rows, selected_date):
            QMessageBox.warning(
                self,
                "Dato findes allerede",
                f"{format_date(selected_date)} findes allerede i databasen. Fjern registreringerne på datoen før du markerer den som fridag.",
            )
            return

        try:
            self.saved_id = upsert_day_off(selected_date, entry_settings=self.window.settings)
        except ValueError as error:
            QMessageBox.warning(self, "Fridag kan ikke gemmes", str(error))
            return
        self.saved_date = selected_date
        show_success_message(self, "Fridag gemt", f"{key} blev gemt som fridag.")
        self.accept()


class CalculatorPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Lønberegner",
            "Beregn netto ud fra bruttoløn eller timer og timeløn.",
        )

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        input_panel, input_layout = make_panel("Input")
        input_panel.setMinimumWidth(430)
        content.addWidget(input_panel, 0)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("CalculatorTabs")
        self.tabs.setTabBar(AnimatedSegmentedTabBar())
        self.tabs.setUsesScrollButtons(False)
        self.tabs.tabBar().setExpanding(False)
        input_layout.addWidget(self.tabs)

        brutto_tab = QWidget()
        brutto_form = QFormLayout(brutto_tab)
        brutto_form.setContentsMargins(6, 12, 6, 6)
        self.brutto_field = make_text_input("3000", "fx 3000")
        self.brutto_field.textChanged.connect(self._calculate)
        brutto_form.addRow("Bruttoløn", self.brutto_field)
        self.tabs.addTab(brutto_tab, "Bruttoløn")

        hours_tab = QWidget()
        hours_form = QFormLayout(hours_tab)
        hours_form.setContentsMargins(6, 12, 6, 6)
        self.calc_hours_field = make_text_input("20", "fx 20")
        self.calc_hours_field.textChanged.connect(self._calculate)
        self.calc_rate_field = make_text_input("150", "fx 150")
        self.calc_rate_field.textChanged.connect(self._calculate)
        hours_form.addRow("Timer", self.calc_hours_field)
        hours_form.addRow("Timeløn", self.calc_rate_field)
        self.tabs.addTab(hours_tab, "Timer")
        self.tabs.currentChanged.connect(self._calculate)

        tax_form = QFormLayout()
        tax_form.setContentsMargins(6, 10, 6, 6)
        tax_form.setVerticalSpacing(12)
        input_layout.addLayout(tax_form)
        self.fradrag_field = make_text_input("0", "fx 0")
        self.fradrag_field.textChanged.connect(self._calculate)
        self.tax_field = make_text_input("40", "fx 39 eller 0,39")
        self.tax_field.textChanged.connect(self._calculate)
        self.am_field = make_text_input("8", "fx 8")
        self.am_field.textChanged.connect(self._calculate)
        self.pension_field = make_text_input("0", "fx 5")
        self.pension_field.textChanged.connect(self._calculate)
        tax_form.addRow("Fradrag pr. måned", self.fradrag_field)
        tax_form.addRow("Skat %", self.tax_field)
        tax_form.addRow("AM-bidrag %", self.am_field)
        tax_form.addRow("Pension %", self.pension_field)

        tax_note = QLabel("Du kan se dine skatteoplysninger på borger.dk -> TastSelv.")
        tax_note.setObjectName("PageSubtitle")
        tax_note.setWordWrap(True)
        input_layout.addWidget(tax_note)

        result_panel, result_layout = make_panel("Resultat")
        content.addWidget(result_panel, 1)

        self.net_result = MetricCard("Netto løn", accent="#1f8a70")
        result_layout.addWidget(self.net_result)

        self.result_table = QTableWidget()
        setup_table(self.result_table, ["Post", "Beløb"])
        result_layout.addWidget(self.result_table)

    def refresh(self):
        if has_required_settings(self.settings):
            set_field_number(self.calc_rate_field, last_rate(self.data, self.settings))
            set_field_number(self.fradrag_field, float(self.settings.get("fradrag", 0)))
            set_field_number(self.tax_field, float(self.settings.get("skat", 0)) * 100)
            set_field_number(self.am_field, float(self.settings.get("am bidrag", 0)) * 100)
            set_field_number(self.pension_field, ft.get_pension_contribution_rate(self.settings) * 100)
        self._calculate()

    def _gross_and_hours(self):
        if self.tabs.currentIndex() == 0:
            return parse_positive_number(self.brutto_field, "Bruttoløn", allow_zero=True), 0.0
        hours = parse_positive_number(self.calc_hours_field, "Timer", allow_zero=True)
        rate = parse_positive_number(self.calc_rate_field, "Timeløn", allow_zero=True)
        return hours * rate, hours

    def _calculate(self):
        try:
            brutto, hours = self._gross_and_hours()
            tax_value = parse_positive_number(self.tax_field, "Skat", allow_zero=True)
            am_value = parse_positive_number(self.am_field, "AM-bidrag", allow_zero=True)
            tax_rate = tax_value / 100 if tax_value > 1 else tax_value
            am_rate = am_value / 100 if am_value > 1 else am_value
            pension_value = parse_positive_number(self.pension_field, "Pension", allow_zero=True)
            pension_rate = pension_value / 100 if pension_value > 1 else pension_value
            fradrag = parse_positive_number(self.fradrag_field, "Fradrag", allow_zero=True)
        except ValueError as error:
            self.net_result.set_values("N/A", str(error))
            self.result_table.setRowCount(0)
            return

        breakdown = ft.calculate_salary_breakdown(
            brutto,
            tax_rate,
            fradrag,
            am_rate,
            settings={ft.PENSION_CONTRIBUTION_KEY: pension_rate},
            hours=hours,
        )
        self.net_result.set_values(
            format_money(breakdown["netto"]),
            f"Brutto: {format_money(brutto)} | Skat: {format_number(tax_rate * 100)}%",
        )
        rows = [
            ("Brutto løn", format_money(breakdown["brutto"])),
            ("Pension", f"-{format_money(breakdown.get('pension', 0))}"),
        ]
        if breakdown.get("atp_medarbejder", 0) > 0:
            rows.append(("ATP medarbejder", f"-{format_money(breakdown.get('atp_medarbejder', 0))}"))
        rows.extend(
            [
                ("AM-bidrag", f"-{format_money(breakdown['am_bidrag'])}"),
                ("Efter AM-bidrag", format_money(breakdown["efter_am"])),
                ("Fradrag", format_money(breakdown["fradrag"])),
                ("Skattegrundlag", format_money(breakdown["skattegrundlag"])),
                ("Skat", f"-{format_money(breakdown['skat'])}"),
                ("Netto løn", format_money(breakdown["netto"])),
            ]
        )
        self.result_table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.result_table.setItem(row_index, 0, table_item(label))
            self.result_table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))


class PayrollSlipDialog(QDialog):
    def __init__(self, parent, period, settings):
        super().__init__(parent)
        self.parent_page = parent
        self.window = getattr(parent, "window", parent)
        self.period = period
        self.settings = settings
        self.setModal(True)
        self.setWindowTitle(f"Lønseddel - {month_title(period)}")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(720, 620)
        self.resize(820, 700)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        root = QVBoxLayout(body)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._build_header(root)
        self._build_metrics(root)
        self._build_budget(root)
        self._build_shifts(root)
        self._build_breakdown(root)

        button_row = QHBoxLayout()
        button_row.addStretch()
        edit_settings_button = QPushButton("Rediger indstillinger")
        edit_settings_button.setObjectName("SecondaryButton")
        edit_settings_button.clicked.connect(self._edit_period_settings)
        button_row.addWidget(edit_settings_button)
        close_button = QPushButton("Luk")
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)
        outer.addLayout(button_row)

    def _label(self, text, style="", word_wrap=False):
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setWordWrap(word_wrap)
        return label

    def _build_header(self, root):
        panel = QFrame()
        panel.setStyleSheet(
            """
            QFrame {
                background: #ffffff;
                border: 1px solid #dbe3ec;
                border-radius: 8px;
            }
            QLabel {
                border: 0;
                background: transparent;
            }
            """
        )
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(18)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(self._label("Lønseddel", "color: #64748b; font-weight: 850;"))
        title_box.addWidget(self._label(month_title(self.period), "color: #0f172a; font-size: 22pt; font-weight: 900;"))
        title_box.addWidget(
            self._label(
                f"Periode {format_period_without_year(self.period)}",
                "color: #475569; font-size: 10.5pt;",
            )
        )
        layout.addLayout(title_box, 1)

        other_income = self.period.get(
            "anden_indkomst",
            ft.get_other_income(self.settings, self.period["periode_start"], self.period["periode_slut"]),
        )
        total = self.period["netto"] + other_income
        total_box = QVBoxLayout()
        total_box.setSpacing(4)
        total_box.addWidget(self._label("Total udbetalt", "color: #64748b; font-weight: 850;"))
        total_box.addWidget(
            self._label(format_money(total), "color: #1f8a70; font-size: 20pt; font-weight: 900;")
        )
        layout.addLayout(total_box)
        root.addWidget(panel)

    def _period_settings(self):
        items = self.period.get("calculation_items", [])
        if items:
            return ft.select_effective_settings_for_period(items, self.settings)
        shifts = self.period.get("shifts", [])
        for shift in reversed(shifts):
            if isinstance(shift.get("settings"), dict):
                return ft.normalize_settings(shift.get("settings"))
        return ft.normalize_settings(self.settings)

    def _period_other_income(self):
        return self.period.get(
            "anden_indkomst",
            ft.get_other_income(self.settings, self.period["periode_start"], self.period["periode_slut"]),
        )

    def _period_budget_expenses(self):
        return self.period.get(
            "budget_expenses",
            ft.calculate_budget_expenses(self.settings, self.period["periode_start"], self.period["periode_slut"]),
        )

    def _holiday_pay_values(self):
        period_settings = self._period_settings()
        config = holiday_pay_settings(period_settings)
        rate = config["rate"]
        period_holiday_eligible = sum(
            max(0.0, float(shift.get("brutto", 0) or 0))
            for shift in self.period.get("shifts", [])
            if not shift.get("is_day_off")
        )
        earned_in_period = ft.calculate_holiday_pay_amount(period_holiday_eligible, rate)

        ferie_start, ferie_end, _ = current_holiday_year(self.period["periode_slut"])
        employment_start = config["employment_start"] or first_work_entry_date(getattr(self.window, "data", []))
        calculation_start = max(ferie_start, employment_start) if employment_start else ferie_start
        calculation_end = min(self.period["periode_slut"], ferie_end)
        if calculation_end < calculation_start:
            return earned_in_period, 0.0

        total_eligible = sum(
            max(0.0, float(row.get("brutto", 0) or 0))
            for row in entry_rows(getattr(self.window, "data", []), self.settings)
            if not row.get("is_day_off") and calculation_start <= row["dato"] <= calculation_end
        )
        return earned_in_period, ft.calculate_holiday_pay_amount(total_eligible, rate)

    def _build_metrics(self, root):
        shift_count = int(self.period.get("vagter", 0))
        if not shift_count:
            shift_count = sum(1 for shift in self.period.get("shifts", []) if not shift.get("is_day_off"))
        day_off_count = int(self.period.get("fridage", 0))
        pause = self.period.get("pause", 0)
        duration = self.period.get("varighed", self.period["timer"] + pause)
        avg_rate = self.period["brutto"] / self.period["timer"] if self.period["timer"] else None
        other_income = self._period_other_income()
        budget_expenses = self._period_budget_expenses()
        disposable_amount = self.period["netto"] + other_income - budget_expenses
        earned_holiday_pay, total_holiday_pay = self._holiday_pay_values()

        grid = QGridLayout()
        grid.setSpacing(10)
        metrics = [
            ("Udbetalt (Netto)", format_money(self.period["netto"]), "#1f8a70"),
            ("Rådighedsbeløb", format_money(disposable_amount), "#1f8a70", f"Efter udgifter: {format_money(budget_expenses)}"),
            ("Feriepenge", format_money(earned_holiday_pay), "#d97706", f"Total feriepenge: {format_money(total_holiday_pay)}"),
            ("Betalte timer", f"{format_number(self.period['timer'])} t.", "#7c3aed"),
            ("Antal vagter", str(shift_count), "#475569"),
            ("Fridage", str(day_off_count), DAY_OFF_ACCENT),
            ("Pension", format_money(self.period.get("pension", 0)), "#0f766e"),
            ("Gns. timeløn", format_money(avg_rate), "#0f766e"),
            ("Timer før pause", f"{format_number(duration)} t.", "#2563eb"),
            ("Pause", f"{format_pause_minutes(pause)} min.", "#d97706"),
        ]
        for index, metric in enumerate(metrics):
            title, value, accent = metric[:3]
            subtitle = metric[3] if len(metric) > 3 else ""
            grid.addWidget(MetricCard(title, value, subtitle=subtitle, accent=accent), index // 3, index % 3)
        root.addLayout(grid)

    def _edit_period_settings(self):
        dialog = PeriodSettingsDialog(self, self.window, self.period)
        if dialog.exec_() != QDialog.Accepted:
            return
        self.window.refresh_all()
        self.accept()

    def _build_budget(self, root):
        period_settings = self._period_settings()
        categories = ft.get_budget_categories(period_settings)

        panel, layout = make_panel("Budgetposter")
        root.addWidget(panel)
        if not categories:
            empty_label = QLabel("Ingen budgetposter gemt på denne lønperiode.")
            empty_label.setObjectName("PageSubtitle")
            empty_label.setWordWrap(True)
            layout.addWidget(empty_label)
            return

        table = QTableWidget()
        setup_table(table, ["Post", "Pr. måned", "Denne periode"])
        table.setSelectionMode(QAbstractItemView.NoSelection)
        rows = []
        period_total = 0.0
        for category in categories:
            amount = max(0.0, float(category.get("beløb", 0) or 0))
            period_amount = ft.periodize_amount(
                amount,
                category.get("enhed", ft.AMOUNT_UNIT_MONTH),
                self.period["periode_start"],
                self.period["periode_slut"],
                period_settings,
            )
            period_total += period_amount
            rows.append((str(category.get("navn", "Budgetpost")), amount, period_amount))
        rows.append(("I alt", sum(row[1] for row in rows), period_total))

        table.setRowCount(len(rows))
        for row_index, (name, monthly_amount, period_amount) in enumerate(rows):
            item_name = table_item(name)
            if row_index == len(rows) - 1:
                font = item_name.font()
                font.setBold(True)
                item_name.setFont(font)
            table.setItem(row_index, 0, item_name)
            table.setItem(row_index, 1, table_item(format_money(monthly_amount), Qt.AlignRight | Qt.AlignVCenter))
            table.setItem(row_index, 2, table_item(format_money(period_amount), Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(table, len(rows), max_rows=8, min_rows=min(3, len(rows)), bottom_padding=0)
        layout.addWidget(table)

    def _build_breakdown(self, root):
        panel, layout = make_panel("Beregning")
        root.addWidget(panel)

        other_income = self.period.get(
            "anden_indkomst",
            ft.get_other_income(self.settings, self.period["periode_start"], self.period["periode_slut"]),
        )
        total = self.period["netto"] + other_income
        rows = [
            ("Brutto løn", format_money(self.period["brutto"])),
            ("Pension", f"-{format_money(self.period.get('pension', 0))}"),
        ]
        if self.period.get("atp_medarbejder", 0) > 0:
            rows.append(("ATP medarbejder", f"-{format_money(self.period.get('atp_medarbejder', 0))}"))
        rows.extend(
            [
                ("AM-bidrag", f"-{format_money(self.period['am_bidrag'])}"),
                ("Efter AM-bidrag", format_money(self.period.get("efter_am"))),
                ("Fradrag", format_money(self.period.get("fradrag"))),
                ("Skattegrundlag", format_money(self.period.get("skattegrundlag"))),
                ("Skat", f"-{format_money(self.period['skat'])}"),
                ("Netto løn", format_money(self.period["netto"])),
                ("Anden indkomst (netto)", format_money(other_income)),
                ("Total udbetalt", format_money(total)),
            ]
        )
        if self.period.get("arbejdsgiver_pension", 0) > 0:
            rows.append(("Arbejdsgiverpension", format_money(self.period.get("arbejdsgiver_pension", 0))))
        if self.period.get("atp_arbejdsgiver", 0) > 0:
            rows.append(("ATP arbejdsgiver", format_money(self.period.get("atp_arbejdsgiver", 0))))

        table = QTableWidget()
        setup_table(table, ["Post", "Beløb"])
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            table.setItem(row_index, 0, table_item(label))
            table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(table, len(rows), max_rows=len(rows), min_rows=len(rows), bottom_padding=0)
        layout.addWidget(table)

    def _build_shifts(self, root):
        shifts = sorted(self.period.get("shifts", []), key=lambda shift: shift["dato"])
        if not shifts:
            return

        panel, layout = make_panel("Vagter i perioden")
        root.addWidget(panel)
        table = QTableWidget()
        setup_table(table, ["Dato", "Timer", "Pause", "Timeløn", "Netto"])
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setRowCount(len(shifts))
        for row_index, shift in enumerate(shifts):
            if shift.get("is_day_off"):
                table.setItem(row_index, 0, day_off_table_item(format_shift_table_date(shift["dato"])))
                table.setItem(row_index, 1, day_off_table_item("Fridag", Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 2, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 3, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 4, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
            else:
                table.setItem(row_index, 0, table_item(format_shift_table_date(shift["dato"])))
                table.setItem(row_index, 1, table_item(f"{format_number(shift['timer'])} t.", Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 2, table_item(f"{format_pause_minutes(shift.get('pause', 0))} min.", Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 3, table_item(format_money(shift.get("timeløn")), Qt.AlignRight | Qt.AlignVCenter))
                table.setItem(row_index, 4, table_item(format_money(shift.get("netto")), Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(table, len(shifts), max_rows=8, min_rows=min(3, len(shifts)), bottom_padding=0)
        layout.addWidget(table)


class PeriodBudgetDialog(QDialog):
    def __init__(self, parent, categories):
        super().__init__(parent)
        self.setWindowTitle("Rediger budgetposter")
        self.setWindowIcon(app_icon())
        self.setModal(True)
        self.setMinimumSize(620, 520)
        self.resize(700, 560)
        self.categories = [dict(category) for category in categories]

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        self.total_label = QLabel()
        self.total_label.setWordWrap(True)
        self.total_label.setStyleSheet("color: #111827; font-size: 20pt; font-weight: 900; padding: 2px 0 6px 0;")
        root.addWidget(self.total_label)

        panel, layout = make_panel("Budgetposter")
        root.addWidget(panel, 1)
        header = QHBoxLayout()
        header.setSpacing(10)
        intro = QLabel("Posterne gemmes på alle registreringer i denne lønperiode som månedlige beløb.")
        intro.setObjectName("PageSubtitle")
        intro.setWordWrap(True)
        header.addWidget(intro, 1)
        add_button = QPushButton("Tilføj ny post")
        add_button.clicked.connect(self._add_category)
        header.addWidget(add_button)
        layout.addLayout(header)

        self.table = QTableWidget()
        setup_table(self.table, ["Post", "Beløb", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(230)
        layout.addWidget(self.table)

        button_row = QHBoxLayout()
        root.addLayout(button_row)
        save_button = QPushButton("Gem budgetposter")
        save_button.clicked.connect(self.accept)
        button_row.addWidget(save_button)
        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        button_row.addStretch()

        self._fill_table()
        self._update_total_label()

    def _budget_total(self):
        return sum(max(0.0, float(item.get("beløb", 0) or 0)) for item in self.categories)

    def _update_total_label(self):
        self.total_label.setText(f"Samlede udgifter pr. måned: {format_money(self._budget_total())}")

    def _fill_table(self):
        self.table.setRowCount(len(self.categories))
        for row_index, item in enumerate(self.categories):
            self.table.setItem(row_index, 0, table_item(item.get("navn", "Budgetpost")))
            self.table.setItem(
                row_index,
                1,
                table_item(format_money(item.get("beløb", 0)), Qt.AlignRight | Qt.AlignVCenter),
            )
            edit_button = QPushButton("Rediger")
            edit_button.setObjectName("InlineButton")
            edit_button.clicked.connect(lambda checked=False, index=row_index: self._edit_category(index))
            self.table.setCellWidget(row_index, 2, edit_button)
        self.table.resizeRowsToContents()
        self.table.setMinimumHeight(min(460, 96 + (len(self.categories) * 36)))

    def _add_category(self):
        dialog = BudgetEntryDialog(self, "Tilføj ny post")
        if dialog.exec_() == QDialog.Accepted and dialog.entry:
            self.categories.append(dialog.entry)
            self._fill_table()
            self._update_total_label()

    def _edit_category(self, index):
        if index < 0 or index >= len(self.categories):
            return
        dialog = BudgetEntryDialog(self, "Rediger post", self.categories[index], allow_delete=True)
        if dialog.exec_() != QDialog.Accepted:
            return
        if dialog.deleted:
            del self.categories[index]
        elif dialog.entry:
            self.categories[index] = dialog.entry
        self._fill_table()
        self._update_total_label()


class PeriodSettingsDialog(QDialog):
    def __init__(self, parent, window, period):
        super().__init__(parent)
        self.window = window
        self.period = period
        self.setModal(True)
        self.setWindowTitle("Rediger lønseddel-indstillinger")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(720, 680)
        self.resize(780, 740)
        self.budget_categories = []

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)

        panel, layout = make_panel("Indstillinger for perioden")
        body_layout.addWidget(panel)
        form = QFormLayout()
        form.setVerticalSpacing(18)
        form.setHorizontalSpacing(24)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addLayout(form)

        self.tax_field = make_text_input()
        self.fradrag_field = make_text_input()
        self.fradrag_unit_combo = ModernComboBox()
        for label, value in [
            ("Måned", ft.AMOUNT_UNIT_MONTH),
            ("14 dage", ft.AMOUNT_UNIT_TWO_WEEKS),
            ("Uge", ft.AMOUNT_UNIT_WEEK),
            ("Dag", ft.AMOUNT_UNIT_DAY),
            ("Periode", ft.AMOUNT_UNIT_PERIOD),
        ]:
            self.fradrag_unit_combo.addItem(label, value)
        self.am_field = make_text_input()
        self.pension_field = make_text_input()
        self.employer_pension_field = make_text_input()
        self.atp_enabled_checkbox = QCheckBox("ATP aktiv")
        self.atp_employee_field = make_text_input()
        self.atp_employer_field = make_text_input()
        self.other_income_field = make_text_input()
        self.budget_total_label = QLabel()
        self.budget_total_label.setObjectName("PageSubtitle")
        self.budget_total_label.setWordWrap(True)
        self.edit_budget_button = QPushButton("Rediger budgetposter")
        self.edit_budget_button.setObjectName("InlineButton")
        self.edit_budget_button.clicked.connect(self._edit_budget_categories)
        self.budget_row = QWidget()
        budget_row_layout = QHBoxLayout(self.budget_row)
        budget_row_layout.setContentsMargins(0, 0, 0, 0)
        budget_row_layout.setSpacing(10)
        budget_row_layout.addWidget(self.budget_total_label, 1)
        budget_row_layout.addWidget(self.edit_budget_button, 0, Qt.AlignVCenter)
        self.goal_field = make_text_input()

        form.addRow("Skat %", self.tax_field)
        form.addRow("Fradrag", self.fradrag_field)
        form.addRow("Fradrag enhed", self.fradrag_unit_combo)
        form.addRow("AM-bidrag %", self.am_field)
        form.addRow("Eget pensionsbidrag %", self.pension_field)
        form.addRow("Arbejdsgiver pension %", self.employer_pension_field)
        form.addRow("ATP", self.atp_enabled_checkbox)
        form.addRow("ATP medarbejder pr. periode", self.atp_employee_field)
        form.addRow("ATP arbejdsgiver pr. periode", self.atp_employer_field)
        form.addRow("Anden indkomst netto pr. måned", self.other_income_field)
        form.addRow("Budget pr. måned", self.budget_row)
        form.addRow("Rådighedsmål pr. måned", self.goal_field)

        body_layout.addStretch()

        note = QLabel(
            "Når du gemmer, får alle registreringer i denne lønperiode de samme gemte indstillinger. "
            "Timer, datoer, pauser og timeløn ændres ikke."
        )
        note.setObjectName("PageSubtitle")
        note.setWordWrap(True)
        root.addWidget(note)

        button_row = QHBoxLayout()
        root.addLayout(button_row)
        save_button = QPushButton("Gem på lønperiode")
        save_button.clicked.connect(self._save)
        button_row.addWidget(save_button)
        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        button_row.addStretch()

        self._fill_values()

    def _base_settings(self):
        items = self.period.get("calculation_items", [])
        if items:
            return ft.select_effective_settings_for_period(items, self.window.settings)
        shifts = self.period.get("shifts", [])
        for shift in reversed(shifts):
            if isinstance(shift.get("settings"), dict):
                return ft.normalize_settings(shift.get("settings"))
        return ft.normalize_settings(self.window.settings)

    def _fill_values(self):
        settings = self._base_settings()
        set_field_number(self.tax_field, float(settings.get("skat", 0)) * 100)
        set_field_number(self.fradrag_field, float(settings.get("fradrag", 0)))
        fradrag_unit_index = self.fradrag_unit_combo.findData(settings.get(ft.TAX_ALLOWANCE_UNIT_KEY, ft.AMOUNT_UNIT_MONTH))
        self.fradrag_unit_combo.setCurrentIndex(max(0, fradrag_unit_index))
        set_field_number(self.am_field, float(settings.get("am bidrag", 0)) * 100)
        set_field_number(self.pension_field, ft.get_pension_contribution_rate(settings) * 100)
        set_field_number(self.employer_pension_field, ft.get_employer_pension_contribution_rate(settings) * 100)
        self.atp_enabled_checkbox.setChecked(bool(settings.get(ft.ATP_ENABLED_KEY, False)))
        set_field_number(self.atp_employee_field, float(settings.get(ft.ATP_EMPLOYEE_AMOUNT_KEY, 0)))
        set_field_number(self.atp_employer_field, float(settings.get(ft.ATP_EMPLOYER_AMOUNT_KEY, 0)))
        set_field_number(self.other_income_field, ft.get_other_income(settings))
        self.budget_categories = [dict(category) for category in ft.get_budget_categories(settings)]
        self._update_budget_summary()
        set_field_number(self.goal_field, ft.get_disposable_income_goal(settings))

    def _budget_total(self):
        return sum(max(0.0, float(item.get("beløb", 0) or 0)) for item in self.budget_categories)

    def _update_budget_summary(self):
        count = len(self.budget_categories)
        post_text = "post" if count == 1 else "poster"
        self.budget_total_label.setText(f"{format_money(self._budget_total())} pr. måned · {count} {post_text}")

    def _edit_budget_categories(self):
        dialog = PeriodBudgetDialog(self, self.budget_categories)
        if dialog.exec_() != QDialog.Accepted:
            return
        self.budget_categories = [dict(category) for category in dialog.categories]
        self._update_budget_summary()

    def _settings_from_fields(self):
        tax = parse_positive_number(self.tax_field, "Skat", allow_zero=True)
        am = parse_positive_number(self.am_field, "AM-bidrag", allow_zero=True)
        pension = parse_positive_number(self.pension_field, "Eget pensionsbidrag", allow_zero=True)
        employer_pension = parse_positive_number(self.employer_pension_field, "Arbejdsgiver pension", allow_zero=True)

        base_settings = self._base_settings()
        settings = ft.settings_snapshot(base_settings)
        settings["skat"] = tax / 100 if tax > 1 else tax
        settings["fradrag"] = parse_positive_number(self.fradrag_field, "Fradrag", allow_zero=True)
        settings[ft.TAX_ALLOWANCE_UNIT_KEY] = self.fradrag_unit_combo.currentData() or ft.AMOUNT_UNIT_MONTH
        settings["am bidrag"] = am / 100 if am > 1 else am
        settings[ft.PENSION_CONTRIBUTION_KEY] = pension / 100 if pension > 1 else pension
        settings[ft.EMPLOYER_PENSION_CONTRIBUTION_KEY] = employer_pension / 100 if employer_pension > 1 else employer_pension
        settings[ft.ATP_ENABLED_KEY] = self.atp_enabled_checkbox.isChecked()
        settings[ft.ATP_CALCULATION_KEY] = ft.ATP_CALCULATION_MANUAL
        settings[ft.ATP_EMPLOYEE_AMOUNT_KEY] = parse_positive_number(self.atp_employee_field, "ATP medarbejder", allow_zero=True)
        settings[ft.ATP_EMPLOYER_AMOUNT_KEY] = parse_positive_number(self.atp_employer_field, "ATP arbejdsgiver", allow_zero=True)
        settings[ft.OTHER_INCOME_KEY] = parse_positive_number(self.other_income_field, "Anden indkomst", allow_zero=True)
        settings["budget kategorier"] = [dict(category) for category in self.budget_categories]
        settings["udgifter"] = self._budget_total()
        settings["ønsket rådighedsbeløb"] = parse_positive_number(self.goal_field, "Rådighedsmål", allow_zero=True)
        return ft.settings_snapshot(settings)

    def _save(self):
        try:
            new_settings = self._settings_from_fields()
            target_ids = {str(shift.get("id")) for shift in self.period.get("shifts", []) if shift.get("id")}
            if not target_ids:
                raise ValueError("Der blev ikke fundet nogen registreringer i lønperioden.")

            rows = []
            for row in entry_rows(ft.load_data(), self.window.settings):
                updated = dict(row)
                if str(updated.get("id")) in target_ids:
                    updated["settings"] = new_settings
                rows.append(updated)
            save_entry_rows(rows)
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldige indstillinger", str(error))


class PaymentsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Lønsedler",
            "Afsluttede lønperioder med løn, anden indkomst og total udbetaling.",
        )

        table_panel, table_layout = make_panel("Afsluttede lønperioder")
        self.table_panel = table_panel
        self.table_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        table_layout.setAlignment(Qt.AlignTop)
        self.root.addWidget(table_panel, 0, Qt.AlignTop)
        self.payments_table = QTableWidget()
        setup_table(self.payments_table, ["Periode", "Vagter", "Fridage", "Timer", "Netto", "Total", "Detaljer"])
        self.payments_table.setSelectionMode(QAbstractItemView.NoSelection)
        table_layout.addWidget(self.payments_table)
        self.root.addStretch()

        self.payments = []

    def refresh(self):
        _, complete_periods = build_periods(self.data, self.settings)
        self.payments = list(reversed(complete_periods))
        self.payments_table.setRowCount(len(self.payments))
        for row_index, period in enumerate(self.payments):
            other_income = period.get(
                "anden_indkomst",
                ft.get_other_income(self.settings, period["periode_start"], period["periode_slut"]) if has_required_settings(self.settings) else 0,
            )
            total = period["netto"] + other_income
            shift_count = int(period.get("vagter", 0))
            if not shift_count:
                shift_count = sum(1 for shift in period.get("shifts", []) if not shift.get("is_day_off"))
            day_off_count = int(period.get("fridage", 0))
            period_label = format_period_without_year(period)
            self.payments_table.setItem(row_index, 0, table_item(period_label))
            self.payments_table.setItem(row_index, 1, table_item(str(shift_count), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 2, table_item(str(day_off_count), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 3, table_item(f"{format_number(period['timer'])} t.", Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 4, table_item(format_money(period["netto"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 5, table_item(format_money(total), Qt.AlignRight | Qt.AlignVCenter))
            self._set_detail_button(row_index)

        self._resize_payment_columns()
        self._fit_payment_table_height()

    def _set_detail_button(self, row_index):
        button = QPushButton("Detaljer")
        button.setObjectName("InlineButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, index=row_index: self._open_detail(index))

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        self.payments_table.setCellWidget(row_index, 6, wrapper)

    def _resize_payment_columns(self):
        header = self.payments_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.payments_table.setColumnWidth(0, 170)
        for column in range(1, self.payments_table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

    def _fit_payment_table_height(self):
        row_height = 64
        for row_index in range(self.payments_table.rowCount()):
            self.payments_table.setRowHeight(row_index, row_height)
        header_height = max(
            self.payments_table.horizontalHeader().height(),
            self.payments_table.horizontalHeader().sizeHint().height(),
            42,
        )
        visible_rows = min(max(self.payments_table.rowCount(), 1), 12)
        height = header_height + (visible_rows * row_height) + (self.payments_table.frameWidth() * 2)
        self.payments_table.setFixedHeight(height)
        self.table_panel.setFixedHeight(self.table_panel.sizeHint().height())

    def _open_detail(self, index):
        if index < 0 or index >= len(self.payments):
            return
        dialog = PayrollSlipDialog(self, self.payments[index], self.settings)
        dialog.exec_()


class StatisticsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Statistik",
            "Nøgletal, rekorder, prognose og grafer samlet ét sted.",
        )

        self.tabs = QTabWidget()
        self.tabs.setTabBar(AnimatedSegmentedTabBar())
        self.tabs.setUsesScrollButtons(False)
        self.tabs.tabBar().setExpanding(False)
        self.root.addWidget(self.tabs, 1)

        numbers_tab = QWidget()
        numbers_layout = QVBoxLayout(numbers_tab)
        numbers_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(16)
        self.scroll.setWidget(self.body)
        numbers_layout.addWidget(self.scroll)
        self.tabs.addTab(numbers_tab, "Nøgletal")

        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_scroll = QScrollArea()
        self.charts_scroll.setWidgetResizable(True)
        self.charts_scroll.setFrameShape(QFrame.NoFrame)
        self.charts_body = QWidget()
        self.charts_body_layout = QVBoxLayout(self.charts_body)
        self.charts_body_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_body_layout.setSpacing(16)
        self.charts_scroll.setWidget(self.charts_body)
        charts_layout.addWidget(self.charts_scroll)
        self.tabs.addTab(charts_tab, "Grafer")

        self.hours_chart = LineChart()
        self.salary_chart = LineChart()
        self.development_chart = LineChart()
        for title, chart in [
            ("Timer pr. lønperiode", self.hours_chart),
            ("Brutto/netto pr. lønperiode", self.salary_chart),
            ("Udvikling i netto løn", self.development_chart),
        ]:
            panel, layout = make_panel(title)
            layout.addWidget(chart)
            self.charts_body_layout.addWidget(panel)
        self.charts_body_layout.addStretch()

    def refresh(self):
        clear_layout(self.body_layout)
        if not self.data:
            self.body_layout.addWidget(make_message("Der er ingen løndata endnu. Tilføj en vagt først."))
            self.body_layout.addStretch()
            self._refresh_charts()
            return
        if not has_required_settings(self.settings):
            self.body_layout.addWidget(make_message("Indstillingerne mangler nøgler, så statistik kan ikke beregnes."))
            self.body_layout.addStretch()
            self._refresh_charts()
            return

        try:
            stats = statistik._build_statistics(self.data, self.settings)
        except Exception as error:
            self.body_layout.addWidget(make_message(f"Kunne ikke beregne statistik:\n{error}"))
            self.body_layout.addStretch()
            self._refresh_charts()
            return

        self._add_metric_grid(stats)
        self._add_averages(stats)
        self._add_history(stats)
        self._add_records(stats)
        self._add_periods(stats)
        self._add_development(stats)
        self._add_patterns(stats)
        self._add_deductions(stats)
        self._add_forecast(stats)
        self.body_layout.addStretch()
        self._refresh_charts()

    def _refresh_charts(self):
        periods, _ = build_periods(self.data, self.settings)
        labels = [month_title(period) for period in periods]

        self.hours_chart.set_data(
            labels,
            [("Timer", [period["timer"] for period in periods], "#1f8a70")],
        )
        self.salary_chart.set_data(
            labels,
            [
                ("Brutto", [period["brutto"] for period in periods], "#2563eb"),
                ("Netto", [period["netto"] for period in periods], "#1f8a70"),
            ],
        )

        net_development = []
        previous = None
        for period in periods:
            if previous is None:
                net_development.append(0)
            else:
                net_development.append(period["netto"] - previous)
            previous = period["netto"]
        self.development_chart.set_data(
            labels,
            [("Ændring", net_development, "#d97706")],
        )

    def _add_metric_grid(self, stats):
        grid = QGridLayout()
        grid.setSpacing(14)
        cards = [
            MetricCard("Timer i alt", f"{format_number(stats['totals']['timer'])} t.", "Alle registrerede vagter"),
            MetricCard("Vagter i alt", str(stats["shift_counts"]["total"]), f"I år: {stats['shift_counts']['year']}"),
            MetricCard(
                "Løn i alt",
                format_money(stats["totals"]["brutto"]),
                f"Efter skat: {format_money(stats['totals']['netto'])}",
            ),
            MetricCard(
                "Trukket i alt",
                format_money(
                    stats["deductions"].get("pension", 0)
                    + stats["deductions"].get("atp_medarbejder", 0)
                    + stats["deductions"]["am_bidrag"]
                    + stats["deductions"]["skat"]
                ),
                "Pension, ATP, AM-bidrag og skat",
            ),
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 4, index % 4)
        self.body_layout.addLayout(grid)

    def _add_table(self, title, headers, rows):
        panel, layout = make_panel(title)
        table = QTableWidget()
        setup_table(table, headers)
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                align = Qt.AlignRight | Qt.AlignVCenter if col_index else Qt.AlignLeft | Qt.AlignVCenter
                table.setItem(row_index, col_index, table_item(value, align))
        table.resizeRowsToContents()
        table.setMinimumHeight(min(420, 82 + (len(rows) * 33)))
        layout.addWidget(table)
        self.body_layout.addWidget(panel)

    def _add_averages(self, stats):
        hours_shift, hours_period, hours_year = stats["averages"]["hours"]
        before_shift, before_period, before_year = stats["averages"]["salary_before_tax"]
        after_shift, after_period, after_year = stats["averages"]["salary_after_tax"]
        self._add_table(
            "Gennemsnit",
            ["Måling", "Vagt", "Lønperiode", "År"],
            [
                ["Timer", format_number(hours_shift), format_number(hours_period), format_number(hours_year)],
                ["Løn før skat", format_money(before_shift), format_money(before_period), format_money(before_year)],
                ["Løn efter skat", format_money(after_shift), format_money(after_period), format_money(after_year)],
            ],
        )

    def _add_history(self, stats):
        self._add_table(
            "Vagter",
            ["Måling", "Værdi"],
            [
                ["Pause i alt", f"{format_pause_minutes(stats['totals'].get('pause', 0))} min."],
                ["Nuværende lønperiode", stats["current_period_label"]],
                ["Vagter i nuværende lønperiode", stats["shift_counts"]["current_period"]],
                ["Fridage i nuværende lønperiode", stats["day_off_counts"]["current_period"]],
                ["Vagter pr. lønperiode i snit", format_number(stats["shift_counts"]["per_period"])],
                ["Fridage pr. lønperiode i snit", format_number(stats["day_off_counts"]["per_period"])],
            ],
        )

    def _shift_row(self, label, shift):
        if shift is None:
            return [label, "N/A", "N/A", "N/A", "N/A", "N/A"]
        return [
            label,
            format_date(shift["dato"]),
            format_number(shift["timer"]),
            format_pause_minutes(shift.get("pause", 0)),
            format_money(shift["brutto"]),
            format_money(shift["netto"]),
        ]

    def _period_row(self, label, period):
        if period is None:
            return [label, "N/A", "N/A", "N/A", "N/A", "N/A"]
        return [
            label,
            f"{month_title(period)} ({format_date(period['periode_start'])} - {format_date(period['periode_slut'])})",
            format_number(period["timer"]),
            format_pause_minutes(period.get("pause", 0)),
            format_money(period["brutto"]),
            format_money(period["netto"]),
        ]

    def _add_records(self, stats):
        self._add_table(
            "Rekorder",
            ["Kategori", "Dato", "Timer", "Pause", "Før skat", "Efter skat"],
            [
                self._shift_row("Længste vagt", stats["records"]["longest"]),
                self._shift_row("Korteste vagt", stats["records"]["shortest"]),
                self._shift_row("Højeste dag", stats["records"]["highest_paid"]),
            ],
        )

    def _add_periods(self, stats):
        self._add_table(
            "Lønperioder",
            ["Måling", "Periode", "Timer", "Pause", "Før skat", "Efter skat"],
            [
                self._period_row("Bedst på timer", stats["periods"]["best_timer"]),
                self._period_row("Bedst på brutto", stats["periods"]["best_brutto"]),
                self._period_row("Bedst på netto", stats["periods"]["best_netto"]),
                self._period_row("Lavest på timer", stats["periods"]["worst_timer"]),
                self._period_row("Lavest på brutto", stats["periods"]["worst_brutto"]),
                self._period_row("Lavest på netto", stats["periods"]["worst_netto"]),
            ],
        )

    def _add_development(self, stats):
        development = stats["development"]
        if development is None:
            rows = [["Timer", "N/A", "N/A", "N/A", "N/A"], ["Løn før skat", "N/A", "N/A", "N/A", "N/A"], ["Løn efter skat", "N/A", "N/A", "N/A", "N/A"]]
        else:
            rows = [
                [
                    "Timer",
                    format_number(development["latest"]["timer"]),
                    format_number(development["previous"]["timer"]),
                    signed_number(development["timer_delta"]),
                    signed_number(development["timer_percent"], "%"),
                ],
                [
                    "Løn før skat",
                    format_money(development["latest"]["brutto"]),
                    format_money(development["previous"]["brutto"]),
                    signed_money(development["brutto_delta"]),
                    signed_number(development["brutto_percent"], "%"),
                ],
                [
                    "Løn efter skat",
                    format_money(development["latest"]["netto"]),
                    format_money(development["previous"]["netto"]),
                    signed_money(development["netto_delta"]),
                    signed_number(development["netto_percent"], "%"),
                ],
            ]
        self._add_table("Udvikling", ["Måling", "Seneste", "Forrige", "Ændring", "Pct."], rows)

    def _add_patterns(self, stats):
        streak = stats["patterns"]["longest_streak"]
        if not streak or streak.get("length", 0) <= 0 or streak.get("start") is None or streak.get("end") is None:
            streak_text = "N/A"
        else:
            streak_text = f"{streak['length']} dage ({format_date(streak['start'])} - {format_date(streak['end'])})"
        self._add_table(
            "Arbejdsmønster",
            ["Måling", "Værdi"],
            [
                ["Gennemsnitlige dage mellem vagter", format_number(stats["patterns"]["average_gap"])],
                ["Længste streak", streak_text],
            ],
        )

    def _add_deductions(self, stats):
        rows = [
            ["Samlet pension", format_money(stats["deductions"].get("pension", 0))],
        ]
        if stats["deductions"].get("atp_medarbejder", 0) > 0:
            rows.append(["Samlet ATP medarbejder", format_money(stats["deductions"].get("atp_medarbejder", 0))])
        rows.extend(
            [
                ["Samlet AM-bidrag", format_money(stats["deductions"]["am_bidrag"])],
                ["Samlet skat", format_money(stats["deductions"]["skat"])],
                [
                    "Samlet trukket",
                    format_money(
                        stats["deductions"].get("pension", 0)
                        + stats["deductions"].get("atp_medarbejder", 0)
                        + stats["deductions"]["am_bidrag"]
                        + stats["deductions"]["skat"]
                    ),
                ],
            ]
        )
        if stats["deductions"].get("arbejdsgiver_pension", 0) > 0:
            rows.append(["Arbejdsgiverpension", format_money(stats["deductions"].get("arbejdsgiver_pension", 0))])
        if stats["deductions"].get("atp_arbejdsgiver", 0) > 0:
            rows.append(["ATP arbejdsgiver", format_money(stats["deductions"].get("atp_arbejdsgiver", 0))])
        self._add_table(
            "Fradrag",
            ["Måling", "Beløb"],
            rows,
        )

    def _add_forecast(self, stats):
        forecast = stats["forecast"]
        if not forecast:
            rows = [["Prognose", "N/A"]]
        else:
            rows = [
                ["Forløb", f"{forecast['elapsed_days']} / {forecast['total_days']} dage"],
                ["Registreret løn nu", f"{format_money(forecast['current_brutto'])} / {format_money(forecast['current_netto'])}"],
                ["Registrerede timer", format_number(forecast["current_hours"])],
                ["Estimerede timer", format_number(forecast["estimated_hours"])],
                ["Forventet løn", f"{format_money(forecast['estimated_brutto'])} / {format_money(forecast['estimated_netto'])}"],
                ["Forventet total inkl. anden indkomst", format_money(forecast["estimated_total_income"])],
                ["Udgifter i lønperioden", format_money(forecast["budget_expenses"])],
                ["Forventet rådighedsbeløb", format_money(forecast["estimated_disposable_income"])],
            ]
        self._add_table("Prognose", ["Måling", "Værdi"], rows)


class ShiftBulkEditDialog(QDialog):
    def __init__(self, parent, window, rows):
        super().__init__(parent)
        self.window = window
        self.rows = [dict(row) for row in rows]
        self.saved_ids = []

        count = len(self.rows)
        self.setModal(True)
        self.setWindowTitle(f"Rediger {count} markeret")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(520, 620)
        self.resize(620, 720)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)

        shift_panel, shift_layout = make_panel("Vagt")
        body_layout.addWidget(shift_panel)
        shift_form = QFormLayout()
        shift_form.setVerticalSpacing(12)
        shift_layout.addLayout(shift_form)

        self.date_field = make_text_input(placeholder="Behold datoer")
        self.hours_field = make_text_input(placeholder="Behold timer")
        self.start_field = make_text_input(placeholder="Behold start")
        self.end_field = make_text_input(placeholder="Behold slut")
        self.rate_field = make_text_input(placeholder="Behold timeløn")
        self.pause_field = make_text_input(placeholder="Behold pause")

        shift_form.addRow("Dato", self.date_field)
        shift_form.addRow("Timer før pause", self.hours_field)
        shift_form.addRow("Start", self.start_field)
        shift_form.addRow("Slut", self.end_field)
        shift_form.addRow("Timeløn", self.rate_field)
        shift_form.addRow("Pause (minutter)", self.pause_field)

        settings_panel, settings_layout = make_panel("Gemte indstillinger")
        body_layout.addWidget(settings_panel)
        settings_form = QFormLayout()
        settings_form.setVerticalSpacing(12)
        settings_layout.addLayout(settings_form)

        self.tax_field = make_text_input(placeholder="Behold skat")
        self.fradrag_field = make_text_input(placeholder="Behold fradrag")
        self.am_field = make_text_input(placeholder="Behold AM-bidrag")
        self.pension_field = make_text_input(placeholder="Behold pension")
        self.other_income_field = make_text_input(placeholder="Behold anden indkomst")
        self.budget_field = make_text_input(placeholder="Behold budget")
        self.goal_field = make_text_input(placeholder="Behold rådighedsmål")

        settings_form.addRow("Skat %", self.tax_field)
        settings_form.addRow("Fradrag pr. måned", self.fradrag_field)
        settings_form.addRow("AM-bidrag %", self.am_field)
        settings_form.addRow("Eget pensionsbidrag %", self.pension_field)
        settings_form.addRow("Anden indkomst pr. måned", self.other_income_field)
        settings_form.addRow("Budget pr. måned", self.budget_field)
        settings_form.addRow("Rådighedsmål pr. måned", self.goal_field)

        note = QLabel(
            "Tomme felter bevarer den enkelte vagts værdi. Fradrag, budget, anden indkomst og rådighedsmål gemmes som månedstal på vagten."
        )
        note.setObjectName("PageSubtitle")
        note.setWordWrap(True)
        body_layout.addWidget(note)

        button_row = QHBoxLayout()
        root.addLayout(button_row)
        save_button = QPushButton(f"Gem {count} markeret")
        save_button.clicked.connect(self._save)
        button_row.addWidget(save_button)
        cancel_button = QPushButton("Annuller")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        button_row.addStretch()

        self._fill_common_values()

    def _common(self, values):
        cleaned = list(values)
        if not cleaned:
            return None
        first = cleaned[0]
        if all(value == first for value in cleaned):
            return first
        return None

    def _fill_number_if_common(self, field, values, decimals=2, scale=1.0):
        value = self._common(values)
        if value is None:
            return
        set_field_number(field, float(value) * scale, decimals=decimals)

    def _fill_common_values(self):
        common_date = self._common([row["dato"] for row in self.rows])
        if common_date is not None:
            self.date_field.setText(format_date(common_date))

        work_rows = [row for row in self.rows if not row.get("is_day_off")]
        self._fill_number_if_common(self.hours_field, [row.get("varighed", row.get("timer", 0)) for row in work_rows])
        common_start = self._common([row.get("start", "") for row in work_rows])
        common_end = self._common([row.get("slut", "") for row in work_rows])
        if common_start:
            self.start_field.setText(str(common_start))
        if common_end:
            self.end_field.setText(str(common_end))
        self._fill_number_if_common(self.rate_field, [row.get("timeløn", 0) for row in work_rows])
        self._fill_number_if_common(self.pause_field, [pause_minutes(row.get("pause", 0)) for row in work_rows])

        settings_rows = [ft.normalize_settings(row.get("settings", self.window.settings)) for row in self.rows]
        self._fill_number_if_common(self.tax_field, [settings.get("skat", 0) for settings in settings_rows], scale=100)
        self._fill_number_if_common(self.fradrag_field, [settings.get("fradrag", 0) for settings in settings_rows])
        self._fill_number_if_common(self.am_field, [settings.get("am bidrag", 0) for settings in settings_rows], scale=100)
        self._fill_number_if_common(self.pension_field, [ft.get_pension_contribution_rate(settings) for settings in settings_rows], scale=100)
        self._fill_number_if_common(self.other_income_field, [ft.get_other_income(settings) for settings in settings_rows])
        self._fill_number_if_common(self.budget_field, [ft.calculate_budget_expenses(settings) for settings in settings_rows])
        self._fill_number_if_common(self.goal_field, [ft.get_disposable_income_goal(settings) for settings in settings_rows])

    def _optional_number(self, field, label, allow_zero=True):
        if not field.text().strip():
            return None
        return parse_positive_number(field, label, allow_zero=allow_zero)

    def _updated_settings(self, current_settings):
        settings = ft.settings_snapshot(current_settings)
        tax = self._optional_number(self.tax_field, "Skat", allow_zero=True)
        fradrag = self._optional_number(self.fradrag_field, "Fradrag", allow_zero=True)
        am = self._optional_number(self.am_field, "AM-bidrag", allow_zero=True)
        pension = self._optional_number(self.pension_field, "Eget pensionsbidrag", allow_zero=True)
        other_income = self._optional_number(self.other_income_field, "Anden indkomst", allow_zero=True)
        budget = self._optional_number(self.budget_field, "Budget", allow_zero=True)
        goal = self._optional_number(self.goal_field, "Rådighedsmål", allow_zero=True)

        if tax is not None:
            settings["skat"] = tax / 100 if tax > 1 else tax
        if fradrag is not None:
            settings["fradrag"] = fradrag
        if am is not None:
            settings["am bidrag"] = am / 100 if am > 1 else am
        if pension is not None:
            settings[ft.PENSION_CONTRIBUTION_KEY] = pension / 100 if pension > 1 else pension
        if other_income is not None:
            settings["anden indkomst netto"] = other_income
        if budget is not None:
            settings["budget kategorier"] = (
                [{"navn": "Faste udgifter", "beløb": budget}]
                if budget > 0
                else []
            )
            settings["udgifter"] = budget
        if goal is not None:
            settings["ønsket rådighedsbeløb"] = goal

        return ft.settings_snapshot(settings)

    def _save(self):
        try:
            selected_date = parse_date_text(self.date_field.text()) if self.date_field.text().strip() else None
            duration_value = self._optional_number(self.hours_field, "Timer", allow_zero=False)
            rate_value = self._optional_number(self.rate_field, "Timeløn", allow_zero=False)
            pause_value = self._optional_number(self.pause_field, "Pause", allow_zero=True)
            pause_hours_value = None if pause_value is None else max(0.0, pause_value / 60)

            start = self.start_field.text().strip()
            end = self.end_field.text().strip()
            if bool(start) != bool(end):
                raise ValueError("Start og slut skal enten begge udfyldes eller begge være tomme.")
            duration_from_time = calculate_hours_from_times(start, end) if start and end else None

            target_ids = {str(row.get("id")) for row in self.rows}
            all_rows = entry_rows(ft.load_data(), self.window.settings)
            updated_rows = []
            for row in all_rows:
                if str(row.get("id")) not in target_ids:
                    updated_rows.append(row)
                    continue

                updated = dict(row)
                if selected_date is not None:
                    updated["dato"] = selected_date
                updated["settings"] = self._updated_settings(updated.get("settings", self.window.settings))

                if not updated.get("is_day_off"):
                    if duration_from_time is not None:
                        updated["start"] = start
                        updated["slut"] = end
                        updated["varighed"] = duration_from_time
                    elif duration_value is not None:
                        updated["varighed"] = duration_value
                        updated.pop("start", None)
                        updated.pop("slut", None)

                    if pause_hours_value is not None:
                        updated["pause"] = pause_hours_value
                    if rate_value is not None:
                        updated["timeløn"] = rate_value

                    updated["timer"] = max(0.0, float(updated.get("varighed", 0) or 0) - float(updated.get("pause", 0) or 0))
                    if updated["timer"] <= 0:
                        raise ValueError("Pause må ikke være lige så lang som eller længere end vagten.")
                    updated["brutto"] = updated["timer"] * float(updated.get("timeløn", 0) or 0)

                updated_rows.append(updated)

            save_entry_rows(updated_rows)
            self.saved_ids = list(target_ids)
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig ændring", str(error))


class HistoryPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Vagter",
            "Alle registrerede vagter og fridage sorteret med nyeste først. Marker rækker for at redigere eller slette flere på én gang.",
        )
        self.rows = []
        self.selected_original_date = None
        self.selected_original_id = None
        self.selected_has_time = False
        self.selected_is_day_off = False
        self.pending_select_date = None
        self.pending_select_id = None
        self.pending_select_row = None

        top = QHBoxLayout()
        top.setSpacing(14)
        self.root.addLayout(top)
        self.total_card = MetricCard("Registreringer", accent="#1f8a70")
        self.hours_card = MetricCard("Timer i alt", accent="#2563eb")
        self.gross_card = MetricCard("Netto i alt", accent="#d97706")
        top.addWidget(self.total_card)
        top.addWidget(self.hours_card)
        top.addWidget(self.gross_card)

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        panel, layout = make_panel("Vagter")
        self.shift_panel = panel
        self.shift_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.shift_panel.setFixedHeight(HISTORY_PANEL_HEIGHT)
        content.addWidget(panel, 2)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        layout.addLayout(toolbar)
        add_button = QPushButton("Tilføj vagt")
        add_button.clicked.connect(self._add_shift)
        toolbar.addWidget(add_button)
        day_off_button = QPushButton("Indberet fridag")
        day_off_button.setObjectName("SecondaryButton")
        day_off_button.clicked.connect(self._add_day_off)
        toolbar.addWidget(day_off_button)
        toolbar.addStretch()
        self.edit_checked_button = QPushButton("Rediger 0 markeret")
        self.edit_checked_button.clicked.connect(self._edit_checked_rows)
        self.edit_checked_button.hide()
        toolbar.addWidget(self.edit_checked_button)
        self.delete_checked_button = QPushButton("Slet markerede")
        self.delete_checked_button.setObjectName("SecondaryButton")
        self.delete_checked_button.clicked.connect(self._delete_checked_rows)
        self.delete_checked_button.hide()
        toolbar.addWidget(self.delete_checked_button)

        self.table = QTableWidget()
        setup_table(self.table, ["", "Dato", "Timer", "Pause", "Netto"])
        setup_shift_table_columns(self.table, 2, check_column=0)
        self.table.itemSelectionChanged.connect(self._load_selected_row)
        self.table.cellClicked.connect(self._toggle_row_check)
        layout.addWidget(self.table)

        edit_panel, edit_layout = make_panel("Rediger valgt registrering")
        self.edit_panel = edit_panel
        self.edit_panel.hide()
        self.edit_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.edit_panel.setFixedHeight(HISTORY_PANEL_HEIGHT)
        content.addWidget(edit_panel, 1)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        edit_layout.addLayout(form)
        self.edit_form = form

        self.edit_date_field = make_text_input(placeholder="dd-mm-åååå")
        self.edit_hours_field = make_text_input(placeholder="fx 4,5")
        self.edit_start_field = make_text_input(placeholder="HH:MM")
        self.edit_end_field = make_text_input(placeholder="HH:MM")
        self.edit_rate_field = make_text_input(placeholder="fx 150")
        self.edit_pause_field = make_text_input(placeholder="minutter")

        self.edit_date_field.textChanged.connect(self._update_edit_preview)
        self.edit_hours_field.textChanged.connect(self._update_edit_preview)
        self.edit_start_field.textChanged.connect(self._update_edit_preview)
        self.edit_end_field.textChanged.connect(self._update_edit_preview)
        self.edit_rate_field.textChanged.connect(self._update_edit_preview)
        self.edit_pause_field.textChanged.connect(self._update_edit_preview)

        form.addRow("Dato", self.edit_date_field)
        form.addRow("Timer", self.edit_hours_field)
        form.addRow("Start", self.edit_start_field)
        form.addRow("Slut", self.edit_end_field)
        form.addRow("Timeløn", self.edit_rate_field)
        form.addRow("Pause", self.edit_pause_field)

        self.edit_preview = QLabel("Vælg en vagt i tabellen.")
        self.edit_preview.setObjectName("PageSubtitle")
        self.edit_preview.setWordWrap(True)
        edit_layout.addWidget(self.edit_preview)

        button_row = QHBoxLayout()
        edit_layout.addLayout(button_row)
        self.save_edit_button = QPushButton("Gem ændring")
        self.save_edit_button.clicked.connect(self._save_selected_row)
        button_row.addWidget(self.save_edit_button)
        self.delete_button = QPushButton("Slet")
        self.delete_button.setObjectName("SecondaryButton")
        self.delete_button.clicked.connect(self._delete_selected_row)
        button_row.addWidget(self.delete_button)
        edit_layout.addStretch()

        self._update_edit_mode(False)

    def refresh(self):
        previous_selected_id = self.selected_original_id
        self.rows = entry_rows(self.data, self.settings)
        work_count = count_work_rows(self.rows)
        day_off_count = count_day_off_rows(self.rows)
        day_off_subtitle = f"{day_off_count} fridage" if day_off_count else "Ingen fridage"
        self.total_card.set_values(str(len(self.rows)), f"{work_count} vagter · {day_off_subtitle}")
        self.hours_card.set_values(f"{format_number(sum(row['timer'] for row in self.rows))} t.", "Alle vagter")
        self.gross_card.set_values(format_money(sum(row["netto"] for row in self.rows)), "Efter skat")

        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))

        for row_index, row in enumerate(self.rows):
            self._set_check_widget(row_index)
            if row.get("is_day_off"):
                self.table.setItem(row_index, 1, day_off_table_item(format_shift_table_date(row["dato"])))
                self.table.setItem(row_index, 2, day_off_table_item("Fridag", Qt.AlignRight | Qt.AlignVCenter))
                self.table.setItem(row_index, 3, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
                self.table.setItem(row_index, 4, day_off_table_item("-", Qt.AlignRight | Qt.AlignVCenter))
            else:
                self.table.setItem(row_index, 1, table_item(format_shift_table_date(row["dato"])))
                self.table.setItem(row_index, 2, table_item(format_work_time(row), Qt.AlignRight | Qt.AlignVCenter))
                self.table.setItem(row_index, 3, table_item(format_pause_minutes(row["pause"]), Qt.AlignRight | Qt.AlignVCenter))
                self.table.setItem(row_index, 4, table_item(format_money(row["netto"]), Qt.AlignRight | Qt.AlignVCenter))

        self.table.resizeRowsToContents()
        setup_shift_table_columns(self.table, 2, check_column=0)
        self.table.blockSignals(False)
        self._update_checked_rows()
        self._select_after_refresh(previous_selected_id)

    def _set_check_widget(self, row_index):
        checkbox = VisibleCheckBox()
        checkbox.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        checkbox.stateChanged.connect(self._update_checked_rows)

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(checkbox)
        self.table.setCellWidget(row_index, 0, wrapper)

    def _row_index_for_id(self, target_id):
        if target_id is None:
            return None
        for row_index, row in enumerate(self.rows):
            if str(row.get("id")) == str(target_id):
                return row_index
        return None

    def _select_after_refresh(self, previous_selected_id):
        self.table.clearSelection()

        if not self.rows:
            self.pending_select_date = None
            self.pending_select_id = None
            self.pending_select_row = None
            self._clear_edit_fields()
            return

        selected_index = self._row_index_for_id(self.pending_select_id)

        if selected_index is None and self.pending_select_row is not None:
            selected_index = min(self.pending_select_row, len(self.rows) - 1)

        if selected_index is None:
            selected_index = self._row_index_for_id(previous_selected_id)

        if selected_index is None:
            selected_index = 0

        self.pending_select_date = None
        self.pending_select_id = None
        self.pending_select_row = None
        self.table.selectRow(selected_index)

    def _checked_row_indexes(self):
        checked_rows = []
        for row_index in range(self.table.rowCount()):
            wrapper = self.table.cellWidget(row_index, 0)
            checkbox = wrapper.findChild(QCheckBox) if wrapper is not None else None
            if checkbox is not None and checkbox.isChecked():
                checked_rows.append(row_index)
        return checked_rows

    def _update_checked_rows(self, state=None):
        count = len(self._checked_row_indexes())
        self.edit_checked_button.setVisible(count > 0)
        self.delete_checked_button.setVisible(count > 0)
        if count == 1:
            self.edit_checked_button.setText("Rediger 1 markeret")
            self.delete_checked_button.setText("Slet 1 markeret")
        else:
            self.edit_checked_button.setText(f"Rediger {count} markerede")
            self.delete_checked_button.setText(f"Slet {count} markerede")

    def _toggle_row_check(self, row_index, column_index):
        if row_index < 0 or row_index >= self.table.rowCount():
            return
        wrapper = self.table.cellWidget(row_index, 0)
        checkbox = wrapper.findChild(QCheckBox) if wrapper is not None else None
        if checkbox is None:
            return
        checkbox.blockSignals(True)
        checkbox.setChecked(not checkbox.isChecked())
        checkbox.blockSignals(False)
        self._update_checked_rows()

    def _add_shift(self):
        dialog = ShiftEntryDialog(self, self.window)
        if dialog.exec_() == QDialog.Accepted and dialog.saved_date is not None:
            self.pending_select_date = dialog.saved_date
            self.pending_select_id = dialog.saved_id
            self.window.refresh_all()

    def _add_day_off(self):
        dialog = DayOffEntryDialog(self, self.window)
        if dialog.exec_() == QDialog.Accepted and dialog.saved_date is not None:
            self.pending_select_date = dialog.saved_date
            self.pending_select_id = dialog.saved_id
            self.window.refresh_all()

    def _edit_checked_rows(self):
        checked_indexes = self._checked_row_indexes()
        checked_rows = [
            self.rows[row_index]
            for row_index in checked_indexes
            if 0 <= row_index < len(self.rows)
        ]
        if not checked_rows:
            return

        dialog = ShiftBulkEditDialog(self, self.window, checked_rows)
        if dialog.exec_() == QDialog.Accepted:
            self.pending_select_id = dialog.saved_ids[0] if dialog.saved_ids else None
            self.pending_select_row = min(checked_indexes)
            self.window.refresh_all()

    def _update_edit_mode(self, has_time):
        self.selected_has_time = bool(has_time)

        is_day_off = bool(self.selected_is_day_off)
        set_form_row_visible(self.edit_form, self.edit_hours_field, not self.selected_has_time and not is_day_off)
        set_form_row_visible(self.edit_form, self.edit_start_field, self.selected_has_time and not is_day_off)
        set_form_row_visible(self.edit_form, self.edit_end_field, self.selected_has_time and not is_day_off)
        set_form_row_visible(self.edit_form, self.edit_rate_field, not is_day_off)
        set_form_row_visible(self.edit_form, self.edit_pause_field, not is_day_off)

    def _load_selected_row(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.rows):
            self._clear_edit_fields()
            return

        row = self.rows[selected]
        self.selected_original_date = row["dato"]
        self.selected_original_id = row.get("id")
        self.selected_is_day_off = bool(row.get("is_day_off"))

        has_time = bool(row.get("start") and row.get("slut")) and not self.selected_is_day_off
        self._update_edit_mode(has_time)

        self.edit_date_field.setText(format_date(row["dato"]))
        if self.selected_is_day_off:
            self.edit_rate_field.clear()
            self.edit_pause_field.clear()
            self.edit_hours_field.clear()
            self.edit_start_field.clear()
            self.edit_end_field.clear()
            self.edit_preview.setText(f"{format_date(row['dato'])}: Fridag uden timer og løn.")
            return

        set_field_number(self.edit_rate_field, row["timeløn"])
        set_field_number(self.edit_pause_field, pause_minutes(row.get("pause", 0)))

        if has_time:
            self.edit_start_field.setText(str(row.get("start", "")))
            self.edit_end_field.setText(str(row.get("slut", "")))
            self.edit_hours_field.clear()
        else:
            set_field_number(self.edit_hours_field, row.get("varighed", row["timer"] + row.get("pause", 0)))
            self.edit_start_field.clear()
            self.edit_end_field.clear()

        self._update_edit_preview()

    def _clear_edit_fields(self):
        self.selected_original_date = None
        self.selected_original_id = None
        self.selected_has_time = False
        self.selected_is_day_off = False

        self.edit_date_field.clear()
        self.edit_hours_field.clear()
        self.edit_start_field.clear()
        self.edit_end_field.clear()
        self.edit_rate_field.clear()
        self.edit_pause_field.clear()

        self._update_edit_mode(False)
        self.edit_preview.setText("Vælg en vagt i tabellen.")

    def _edited_hours_and_times(self):
        if self.selected_has_time:
            start = self.edit_start_field.text().strip()
            slut = self.edit_end_field.text().strip()

            if not start or not slut:
                raise ValueError("Start og slut skal udfyldes.")

            duration = calculate_hours_from_times(start, slut)
            pause = parse_pause_hours(self.edit_pause_field)
            hours = duration - pause
            if hours <= 0:
                raise ValueError("Pause må ikke være lige så lang som eller længere end vagten.")
            return duration, hours, start, slut, pause

        duration = parse_positive_number(self.edit_hours_field, "Timer")
        pause = parse_pause_hours(self.edit_pause_field)
        hours = duration - pause
        if hours <= 0:
            raise ValueError("Pause må ikke være lige så lang som eller længere end vagten.")
        return duration, hours, None, None, pause

    def _update_edit_preview(self):
        if self.selected_original_date is None:
            return

        if self.selected_is_day_off:
            try:
                selected_date = parse_date_text(self.edit_date_field.text())
            except ValueError:
                self.edit_preview.setText("Udfyld en gyldig dato for fridagen.")
                return
            self.edit_preview.setText(f"{format_date(selected_date)}: Fridag uden timer og løn.")
            return

        try:
            selected_date = parse_date_text(self.edit_date_field.text())
            duration, hours, start, slut, pause = self._edited_hours_and_times()
            rate = parse_positive_number(self.edit_rate_field, "Timeløn")
        except ValueError:
            if self.selected_has_time:
                self.edit_preview.setText("Udfyld gyldig dato, start, slut, pause og timeløn.")
            else:
                self.edit_preview.setText("Udfyld gyldig dato, timer, pause og timeløn.")
            return

        brutto = hours * rate
        pause_text = f" | Pause: {format_pause_minutes(pause)} min." if pause > 0 else ""

        if self.selected_has_time:
            self.edit_preview.setText(
                f"{format_date(selected_date)}: {start} - {slut} ({format_number(hours)} betalte timer) á {format_money(rate)}{pause_text}\n"
                f"Brutto: {format_money(brutto)}"
            )
        else:
            self.edit_preview.setText(
                f"{format_date(selected_date)}: {format_number(hours)} betalte timer á {format_money(rate)}{pause_text}\n"
                f"Brutto: {format_money(brutto)}"
            )

    def _save_selected_row(self):
        if self.selected_original_id is None:
            QMessageBox.information(self, "Ingen registrering valgt", "Vælg først en registrering i tabellen.")
            return

        try:
            selected_date = parse_date_text(self.edit_date_field.text())
            if self.selected_is_day_off:
                duration = None
                start = None
                slut = None
                pause = 0
                rate = 0
            else:
                duration, hours, start, slut, pause = self._edited_hours_and_times()
                rate = parse_positive_number(self.edit_rate_field, "Timeløn")
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig ændring", str(error))
            return

        try:
            if self.selected_is_day_off:
                new_id = upsert_day_off(selected_date, self.selected_original_id, self.window.settings)
            else:
                new_id = upsert_entry(
                    selected_date,
                    duration,
                    rate,
                    self.selected_original_id,
                    start=start,
                    slut=slut,
                    pause=pause,
                    entry_settings=self.window.settings,
                )
        except ValueError as error:
            QMessageBox.warning(self, "Registrering kan ikke gemmes", str(error))
            return

        self.pending_select_date = selected_date
        self.pending_select_id = new_id
        self.window.refresh_all()

    def _delete_selected_row(self):
        if self.selected_original_id is None:
            QMessageBox.information(self, "Ingen registrering valgt", "Vælg først en registrering i tabellen.")
            return

        selected_index = self.table.currentRow()
        label = "fridagen" if self.selected_is_day_off else "vagten"
        answer = QMessageBox.question(
            self,
            "Slet registrering",
            f"Vil du slette {label} for {format_date(self.selected_original_date)}?",
        )

        if answer != QMessageBox.Yes:
            return

        delete_entry(self.selected_original_id)
        self.pending_select_row = selected_index
        self.window.refresh_all()

    def _delete_checked_rows(self):
        checked_indexes = self._checked_row_indexes()
        if not checked_indexes:
            return

        checked_ids = {
            str(self.rows[row_index].get("id"))
            for row_index in checked_indexes
            if 0 <= row_index < len(self.rows)
        }
        if not checked_ids:
            return

        count = len(checked_ids)
        label = "registrering" if count == 1 else "registreringer"
        answer = QMessageBox.question(
            self,
            "Slet markerede registreringer",
            f"Vil du slette {count} markerede {label}?",
        )

        if answer != QMessageBox.Yes:
            return

        remaining_rows = [
            row
            for row in entry_rows(ft.load_data())
            if str(row.get("id")) not in checked_ids
        ]
        save_entry_rows(remaining_rows)
        self.pending_select_row = min(checked_indexes)
        self.window.refresh_all()


class BudgetEntryDialog(QDialog):
    def __init__(self, parent, title, item=None, allow_delete=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.deleted = False
        self.entry = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        layout.addLayout(form)

        self.name_field = make_text_input(item.get("navn", "") if item else "", "fx Husleje")
        self.amount_field = make_text_input(placeholder="fx 5200")
        if item:
            set_field_number(self.amount_field, item.get("beløb", 0))

        form.addRow("Navn", self.name_field)
        form.addRow("Beløb", self.amount_field)

        buttons = QDialogButtonBox()
        save_button = buttons.addButton("Gem", QDialogButtonBox.AcceptRole)
        cancel_button = buttons.addButton("Annuller", QDialogButtonBox.RejectRole)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        if allow_delete:
            delete_button = buttons.addButton("Slet post", QDialogButtonBox.DestructiveRole)
            delete_button.setObjectName("SecondaryButton")
            delete_button.clicked.connect(self._delete_post)
        layout.addWidget(buttons)

    def accept(self):
        name = self.name_field.text().strip()
        if not name:
            QMessageBox.warning(self, "Ugyldig post", "Posten skal have et navn.")
            return
        try:
            amount = parse_positive_number(self.amount_field, "Beløb", allow_zero=True)
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig post", str(error))
            return
        self.entry = {"navn": name, "beløb": amount}
        super().accept()

    def _delete_post(self):
        answer = QMessageBox.question(self, "Slet post", "Vil du slette denne budgetpost?")
        if answer == QMessageBox.Yes:
            self.deleted = True
            super().accept()


class BudgetPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Budget",
            "Planlæg faste månedlige udgifter, som automatisk tilpasses lønperioden i rådighedsberegningerne.",
        )
        self.categories = []

        self.total_expenses_label = QLabel()
        self.total_expenses_label.setWordWrap(True)
        self.total_expenses_label.setStyleSheet(
            "color: #111827; font-size: 26pt; font-weight: 900; padding: 6px 0 10px 0;"
        )
        self.root.addWidget(self.total_expenses_label)

        table_panel, table_layout = make_panel("Budgetposter")
        self.root.addWidget(table_panel, 1)
        header = QHBoxLayout()
        header.setSpacing(10)
        intro = QLabel("Posterne her er månedlige beløb. Lønix omregner dem automatisk til den valgte lønperiode.")
        intro.setObjectName("PageSubtitle")
        intro.setWordWrap(True)
        header.addWidget(intro, 1)
        add_button = QPushButton("Tilføj ny post")
        add_button.clicked.connect(self._add_category)
        header.addWidget(add_button)
        table_layout.addLayout(header)

        self.table = QTableWidget()
        setup_table(self.table, ["Post", "Beløb", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(230)
        table_layout.addWidget(self.table)

    def refresh(self):
        self.categories = self._categories_from_settings()
        self._fill_table()
        self._update_total_label()

    def _categories_from_settings(self):
        return ft.get_budget_categories(self.settings)

    def _budget_total(self):
        return sum(item["beløb"] for item in self.categories)

    def _update_total_label(self):
        self.total_expenses_label.setText(f"Samlede udgifter pr. måned: {format_money(self._budget_total())}")

    def _fill_table(self):
        self.table.setRowCount(len(self.categories))
        for row_index, item in enumerate(self.categories):
            self.table.setItem(row_index, 0, table_item(item["navn"]))
            self.table.setItem(row_index, 1, table_item(format_money(item["beløb"]), Qt.AlignRight | Qt.AlignVCenter))
            edit_button = QPushButton("Rediger")
            edit_button.setObjectName("InlineButton")
            edit_button.clicked.connect(lambda checked=False, index=row_index: self._edit_category(index))
            self.table.setCellWidget(row_index, 2, edit_button)
        self.table.resizeRowsToContents()
        self.table.setMinimumHeight(min(460, 96 + (len(self.categories) * 36)))

    def _settings_with_budget(self):
        new_settings = dict(self.settings) if isinstance(self.settings, dict) else {}
        new_settings["budget kategorier"] = self.categories
        return new_settings

    def _save_budget(self):
        ft.save_settings(self._settings_with_budget(), history_reason="Gem budget")
        self.window.refresh_all()

    def _add_category(self):
        dialog = BudgetEntryDialog(self, "Tilføj ny post")
        if dialog.exec_() == QDialog.Accepted and dialog.entry:
            self.categories.append(dialog.entry)
            self._save_budget()

    def _edit_category(self, index):
        if index < 0 or index >= len(self.categories):
            return
        dialog = BudgetEntryDialog(self, "Rediger post", self.categories[index], allow_delete=True)
        if dialog.exec_() != QDialog.Accepted:
            return
        if dialog.deleted:
            del self.categories[index]
        elif dialog.entry:
            self.categories[index] = dialog.entry
        self._save_budget()


class SettingsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Indstillinger",
            "Tilpas skat, månedstal, rådighedsmål og lønperiode. Faste udgifter styres på Budget-siden.",
        )

        self.action_history_widget = ActionHistorySettingsWidget(window)
        self.root.addWidget(self.action_history_widget)

        def add_settings_form(title):
            panel, layout = make_panel(title)
            self.root.addWidget(panel)
            form = QFormLayout()
            form.setVerticalSpacing(12)
            form.setHorizontalSpacing(18)
            form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            layout.addLayout(form)
            return form

        tax_form = add_settings_form("Skat og indkomst")
        self.tax_form = tax_form
        goal_form = add_settings_form("Mål og lønperiode")
        holiday_form = add_settings_form("Feriepenge")

        self.tax_field = make_text_input(placeholder="fx 49")
        self.fradrag_field = make_text_input(placeholder="fx 0")
        self.fradrag_unit_combo = ModernComboBox()
        for label, value in [
            ("Måned", ft.AMOUNT_UNIT_MONTH),
            ("14 dage", ft.AMOUNT_UNIT_TWO_WEEKS),
            ("Uge", ft.AMOUNT_UNIT_WEEK),
            ("Dag", ft.AMOUNT_UNIT_DAY),
            ("Periode", ft.AMOUNT_UNIT_PERIOD),
        ]:
            self.fradrag_unit_combo.addItem(label, value)
        self.am_field = make_text_input(placeholder="fx 8")
        self.birth_year_field = make_text_input(placeholder="fx 2008")
        self.am_age_rule_checkbox = QCheckBox("Brug AM-aldersregel")
        self.pension_field = make_text_input(placeholder="fx 5")
        self.employer_pension_field = make_text_input(placeholder="fx 10")
        self.atp_enabled_checkbox = QCheckBox("ATP aktiv")
        self.atp_employee_field = make_text_input(placeholder="kr pr. periode")
        self.atp_employer_field = make_text_input(placeholder="kr pr. periode")
        self.other_income_field = make_text_input(placeholder="fx 10742")
        self.disposable_goal_field = make_text_input(placeholder="fx 0")
        self.default_rate_field = make_text_input(placeholder="fx 150")
        self.period_type_combo = ModernComboBox()
        self.period_type_combo.addItem("Måned", ft.PAY_PERIOD_TYPE_MONTH)
        self.period_type_combo.addItem("Uger", ft.PAY_PERIOD_TYPE_WEEKS)
        self.start_day_field = make_text_input(placeholder="1-31")
        self.end_day_field = make_text_input(placeholder="1-31")
        self.period_weeks_field = make_text_input(placeholder="fx 2")
        self.period_anchor_field = make_text_input(placeholder="dd-mm-åååå")
        self.holiday_rate_field = make_text_input(placeholder="12,5")
        self.employment_start_field = make_text_input(placeholder="dd-mm-åååå")
        self.use_first_work_entry_button = QPushButton("Benyt første vagt")
        self.use_first_work_entry_button.setObjectName("InlineButton")
        self.use_first_work_entry_button.setCursor(Qt.PointingHandCursor)
        self.use_first_work_entry_button.setVisible(False)
        self.use_first_work_entry_button.clicked.connect(self._use_first_work_entry_date)
        self.employment_start_row = QWidget()
        employment_start_layout = QHBoxLayout(self.employment_start_row)
        employment_start_layout.setContentsMargins(0, 0, 0, 0)
        employment_start_layout.setSpacing(8)
        employment_start_layout.addWidget(self.employment_start_field, 1)
        employment_start_layout.addWidget(self.use_first_work_entry_button, 0, Qt.AlignVCenter)
        self.employment_start_field.textChanged.connect(self._update_use_first_work_entry_button)

        self._add_settings_section(
            tax_form,
            "Grundtal",
            "De få tal Lønix bruger mest. Skat, AM og fradrag må gerne være 0, hvis det passer til dit skattekort.",
        )
        self._add_info_row(
            tax_form,
            "Timeløn",
            self.default_rate_field,
            "Timeløn",
            "Timeløn er det du får før skat for én betalt arbejdstime. Den bruges som forslag, når du opretter nye vagter.",
            required=True,
        )
        self._add_info_row(
            tax_form,
            "Skat %",
            self.tax_field,
            "Skat %",
            "A-skat er den almindelige skat, der trækkes af din løn efter AM-bidrag og fradrag. Skriv din trækprocent fra skattekortet, fx 39. Skriv 0 hvis du ikke betaler A-skat.",
        )
        self._add_info_row(
            tax_form,
            "AM-bidrag %",
            self.am_field,
            "AM-bidrag %",
            "AM-bidrag er arbejdsmarkedsbidrag. Det trækkes normalt før A-skat. For de fleste er det 8. Skriv 0 hvis du er fritaget.",
        )
        self._add_settings_section(
            tax_form,
            "Fradrag",
            "Fradrag sænker kun A-skatten. Det sænker ikke AM-bidraget.",
        )
        self._add_info_row(
            tax_form,
            "Fradrag",
            self.fradrag_field,
            "Fradrag",
            "Fradrag er det beløb du kan tjene, før der trækkes A-skat. Skriv beløbet fra skattekortet, eller 0 hvis du ikke har et fradrag.",
        )
        self._add_info_row(
            tax_form,
            "Fradrag enhed",
            self.fradrag_unit_combo,
            "Fradrag enhed",
            "Her vælger du, hvad fradragsbeløbet dækker. Hvis dit skattekort viser fradrag pr. måned, skal du vælge Måned.",
        )
        self._add_settings_section(
            tax_form,
            "Pension og ATP",
            "Valgfrit. Brug kun felterne hvis pension eller ATP står på din lønseddel.",
        )
        self._add_info_row(
            tax_form,
            "Eget pensionsbidrag %",
            self.pension_field,
            "Eget pensionsbidrag %",
            "Eget pensionsbidrag er den del af lønnen, du selv betaler til pension. Den trækkes fra før AM-bidrag. Skriv 0 hvis du ikke betaler pension.",
        )
        self._add_info_row(
            tax_form,
            "Arbejdsgiver pension %",
            self.employer_pension_field,
            "Arbejdsgiver pension %",
            "Arbejdsgiverpension er pension, din arbejdsgiver betaler oveni. Den trækkes ikke fra din nettoløn. Skriv 0 hvis du ikke bruger den.",
        )
        self._add_info_row(
            tax_form,
            "ATP aktiv",
            self.atp_enabled_checkbox,
            "ATP aktiv",
            "ATP er en lille lovpligtig pensionsordning for mange lønmodtagere. Slå den kun til, hvis ATP står på din lønseddel.",
        )
        self._add_info_row(
            tax_form,
            "ATP medarbejder",
            self.atp_employee_field,
            "ATP medarbejder",
            "Det ATP-beløb du selv betaler i én lønperiode. Det trækkes fra før AM-bidrag.",
        )
        self._add_info_row(
            tax_form,
            "ATP arbejdsgiver",
            self.atp_employer_field,
            "ATP arbejdsgiver",
            "Det ATP-beløb arbejdsgiver betaler for én lønperiode. Det trækkes ikke fra din nettoløn.",
        )
        self._add_settings_section(
            tax_form,
            "Aldersregel",
            "Kun relevant hvis du er under 18, eller registrerer løn for en ung medarbejder.",
        )
        self._add_info_row(
            tax_form,
            "AM-aldersregel",
            self.am_age_rule_checkbox,
            "AM-aldersregel",
            "Slå den til, hvis Lønix skal tage højde for, at unge under 18 fra 2026 ikke altid betaler AM-bidrag.",
        )
        self._add_info_row(
            tax_form,
            "Fødselsår",
            self.birth_year_field,
            "Fødselsår",
            "Dit fødselsår bruges kun til AM-reglen for unge. Skriv fx 2008, eller lad feltet være tomt.",
        )
        self._add_settings_section(
            tax_form,
            "Anden indkomst",
            "Valgfrit. Beløb her lægges til efter lønskat.",
        )
        self._add_info_row(
            tax_form,
            "Anden indkomst netto pr. måned",
            self.other_income_field,
            "Anden indkomst netto",
            "Anden indkomst netto er penge du får udbetalt efter skat ved siden af lønnen, fx SU. Beløbet lægges til efter lønskat. Skriv 0 hvis du ikke har anden indkomst.",
        )

        self._add_info_row(
            goal_form,
            "Ønsket rådighedsbeløb pr. måned",
            self.disposable_goal_field,
            "Ønsket rådighedsbeløb",
            "Rådighedsbeløb er de penge du har tilbage efter løn, anden indkomst og budgetudgifter. Skriv dit mål pr. måned, eller 0 hvis du ikke vil bruge målet.",
        )
        self._add_info_row(
            goal_form,
            "Lønperiode type",
            self.period_type_combo,
            "Lønperiode type",
            "En lønperiode er den periode, lønsedlen dækker. Vælg måned hvis perioden følger datoer i måneden, eller uger hvis den kører i faste ugeblokke.",
            required=True,
        )
        self._add_info_row(
            goal_form,
            "Lønperiode starter d.",
            self.start_day_field,
            "Lønperiode starter",
            "Datoen i måneden hvor din månedlige lønperiode starter. Skriv fx 15.",
            required=True,
        )
        self._add_info_row(
            goal_form,
            "Lønperiode slutter d.",
            self.end_day_field,
            "Lønperiode slutter",
            "Datoen i måneden hvor din månedlige lønperiode slutter. Skriv fx 14.",
            required=True,
        )
        self._add_info_row(
            goal_form,
            "Antal uger",
            self.period_weeks_field,
            "Antal uger",
            "Hvor mange uger der er i én lønperiode, hvis du har valgt Uger. Skriv fx 2 for 14-dages løn.",
            required=True,
        )
        self._add_info_row(
            goal_form,
            "Første periode starter",
            self.period_anchor_field,
            "Første periode starter",
            "Startdato for en kendt lønperiode, hvis du har valgt Uger. Lønix tæller de næste perioder ud fra den dato.",
        )
        self.pay_period_form = goal_form
        self.period_type_combo.currentIndexChanged.connect(self._update_pay_period_fields)
        self.atp_enabled_checkbox.toggled.connect(self._update_optional_tax_fields)
        self.am_age_rule_checkbox.toggled.connect(self._update_optional_tax_fields)

        self._add_info_row(
            holiday_form,
            "Feriegodtgørelse %",
            self.holiday_rate_field,
            "Feriegodtgørelse %",
            "Feriegodtgørelse er feriepenge optjent af ferieberettiget løn. Ofte er satsen 12,5.",
            required=True,
        )
        self._add_info_row(
            holiday_form,
            "Ansættelsesstart",
            self.employment_start_row,
            "Ansættelsesstart",
            "Datoen du startede i jobbet. Den bruges til feriepenge og feriedage. Feltet kan være tomt.",
        )

        button_row = QHBoxLayout()
        self.root.addLayout(button_row)
        save_button = QPushButton("Gem indstillinger")
        save_button.clicked.connect(self._save_settings)
        button_row.addWidget(save_button)
        reset_button = QPushButton("Genindlæs")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self.refresh)
        button_row.addWidget(reset_button)
        introduction_button = QPushButton("Start introduktion")
        introduction_button.setObjectName("SecondaryButton")
        introduction_button.clicked.connect(lambda: self.window.start_introduction(force=True))
        button_row.addWidget(introduction_button)
        button_row.addStretch()

        note = QLabel(
            "Du kan se dine skatteoplysninger på borger.dk -> TastSelv. "
            "Eget pensionsbidrag og medarbejder-ATP trækkes fra brutto før AM-bidrag og skat. Anden indkomst er netto og lægges til efter skat."
        )
        note.setObjectName("PageSubtitle")
        note.setWordWrap(True)
        self.root.addWidget(note)
        required_note = QLabel("* betyder, at feltet er nødvendigt for beregningen og ikke kan stå tomt eller være 0.")
        required_note.setObjectName("PageSubtitle")
        required_note.setWordWrap(True)
        self.root.addWidget(required_note)
        self.root.addStretch()

    def _add_settings_section(self, form, title, hint=""):
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 8, 0, 0)
        section_layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("SettingsSectionLabel")
        section_layout.addWidget(title_label)
        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("SettingsSectionHint")
            hint_label.setWordWrap(True)
            section_layout.addWidget(hint_label)
        form.addRow(section_widget)

    def _add_info_row(self, form, label, field, title, help_text, required=False):
        label_widget = QWidget()
        label_layout = QHBoxLayout(label_widget)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(7)
        info_button = QPushButton("i")
        info_button.setObjectName("InfoButton")
        info_button.setCursor(Qt.PointingHandCursor)
        info_button.setToolTip(f"Forklaring: {label}")
        info_button.clicked.connect(lambda checked=False, dialog_title=title, text=help_text: self._show_setting_help(dialog_title, text))
        label_layout.addWidget(info_button, 0, Qt.AlignVCenter)
        text_label = QLabel(f"{label}{' *' if required else ''}")
        label_layout.addWidget(text_label, 1, Qt.AlignVCenter)
        form.addRow(label_widget, field)

    def _show_setting_help(self, title, text):
        QMessageBox.information(self, title, text)

    def refresh(self):
        settings = self.settings if has_required_settings(self.settings) else {
            "skat": 0.39,
            "fradrag": 0,
            ft.TAX_ALLOWANCE_UNIT_KEY: ft.AMOUNT_UNIT_MONTH,
            "am bidrag": 0.08,
            ft.BIRTH_YEAR_KEY: None,
            ft.AM_AGE_RULE_ENABLED_KEY: True,
            ft.PENSION_CONTRIBUTION_KEY: 0,
            ft.EMPLOYER_PENSION_CONTRIBUTION_KEY: 0,
            ft.ATP_ENABLED_KEY: False,
            ft.ATP_CALCULATION_KEY: ft.ATP_CALCULATION_MANUAL,
            ft.ATP_EMPLOYEE_AMOUNT_KEY: 0,
            ft.ATP_EMPLOYER_AMOUNT_KEY: 0,
            "anden indkomst netto": 0,
            "ønsket rådighedsbeløb": 0,
            "standard timeløn": 150,
            "løn start": 21,
            "løn slut": 20,
            ft.PAY_PERIOD_TYPE_KEY: ft.PAY_PERIOD_TYPE_MONTH,
            ft.PAY_PERIOD_WEEKS_KEY: ft.DEFAULT_PAY_PERIOD_WEEKS,
            ft.PAY_PERIOD_ANCHOR_KEY: ft.DEFAULT_PAY_PERIOD_ANCHOR,
            HOLIDAY_PAY_RATE_KEY: DEFAULT_HOLIDAY_PAY_RATE,
            HOLIDAY_PAY_EMPLOYMENT_START_KEY: "",
        }
        settings = ft.normalize_settings(settings)
        set_field_number(self.tax_field, float(settings.get("skat", 0)) * 100)
        set_field_number(self.fradrag_field, float(settings.get("fradrag", 0)))
        fradrag_unit_index = self.fradrag_unit_combo.findData(settings.get(ft.TAX_ALLOWANCE_UNIT_KEY, ft.AMOUNT_UNIT_MONTH))
        self.fradrag_unit_combo.setCurrentIndex(max(0, fradrag_unit_index))
        set_field_number(self.am_field, float(settings.get("am bidrag", 0)) * 100)
        self.birth_year_field.setText("" if settings.get(ft.BIRTH_YEAR_KEY) in ("", None) else str(settings.get(ft.BIRTH_YEAR_KEY)))
        self.am_age_rule_checkbox.setChecked(bool(settings.get(ft.AM_AGE_RULE_ENABLED_KEY, True)))
        set_field_number(self.pension_field, ft.get_pension_contribution_rate(settings) * 100)
        set_field_number(self.employer_pension_field, ft.get_employer_pension_contribution_rate(settings) * 100)
        self.atp_enabled_checkbox.setChecked(bool(settings.get(ft.ATP_ENABLED_KEY, False)))
        set_field_number(self.atp_employee_field, float(settings.get(ft.ATP_EMPLOYEE_AMOUNT_KEY, 0)))
        set_field_number(self.atp_employer_field, float(settings.get(ft.ATP_EMPLOYER_AMOUNT_KEY, 0)))
        set_field_number(self.other_income_field, ft.get_other_income(settings))
        set_field_number(self.disposable_goal_field, float(settings.get("ønsket rådighedsbeløb", 0)))
        set_field_number(self.default_rate_field, ft.get_default_hourly_rate(settings))
        period_type_index = self.period_type_combo.findData(settings.get(ft.PAY_PERIOD_TYPE_KEY, ft.PAY_PERIOD_TYPE_MONTH))
        if period_type_index < 0:
            period_type_index = 0
        self.period_type_combo.blockSignals(True)
        self.period_type_combo.setCurrentIndex(period_type_index)
        self.period_type_combo.blockSignals(False)
        self.start_day_field.setText(str(int(settings.get("løn start", 15))))
        self.end_day_field.setText(str(int(settings.get("løn slut", 14))))
        self.period_weeks_field.setText(str(int(settings.get(ft.PAY_PERIOD_WEEKS_KEY, ft.DEFAULT_PAY_PERIOD_WEEKS))))
        self.period_anchor_field.setText(str(settings.get(ft.PAY_PERIOD_ANCHOR_KEY, ft.DEFAULT_PAY_PERIOD_ANCHOR)))
        self._update_optional_tax_fields()
        self._update_pay_period_fields()
        holiday_settings = holiday_pay_settings(settings)
        set_field_number(self.holiday_rate_field, holiday_settings["rate"])
        employment_start = holiday_settings["employment_start"] or first_work_entry_date(self.data)
        self.employment_start_field.setText(format_date(employment_start) if employment_start else "")
        self._update_use_first_work_entry_button()

    def _update_optional_tax_fields(self, *_args):
        set_form_row_visible(self.tax_form, self.atp_employee_field, self.atp_enabled_checkbox.isChecked())
        set_form_row_visible(self.tax_form, self.atp_employer_field, self.atp_enabled_checkbox.isChecked())
        set_form_row_visible(self.tax_form, self.birth_year_field, self.am_age_rule_checkbox.isChecked())

    def _field_employment_start(self):
        text = self.employment_start_field.text().strip()
        if not text:
            return None
        try:
            return parse_date_text(text)
        except ValueError:
            return None

    def _update_use_first_work_entry_button(self, *_args):
        first_entry_date = first_work_entry_date(self.data)
        if first_entry_date is None:
            self.use_first_work_entry_button.setVisible(False)
            return
        self.use_first_work_entry_button.setToolTip(f"Sæt ansættelsesstart til {format_date(first_entry_date)}")
        self.use_first_work_entry_button.setVisible(self._field_employment_start() != first_entry_date)

    def _use_first_work_entry_date(self):
        first_entry_date = first_work_entry_date(self.data)
        if first_entry_date is None:
            return
        self.employment_start_field.setText(format_date(first_entry_date))
        self._update_use_first_work_entry_button()

    def _update_pay_period_fields(self, *_args):
        is_week_period = self.period_type_combo.currentData() == ft.PAY_PERIOD_TYPE_WEEKS
        set_form_row_visible(self.pay_period_form, self.start_day_field, not is_week_period)
        set_form_row_visible(self.pay_period_form, self.end_day_field, not is_week_period)
        set_form_row_visible(self.pay_period_form, self.period_weeks_field, is_week_period)
        set_form_row_visible(self.pay_period_form, self.period_anchor_field, is_week_period)

    def focus_disposable_goal(self):
        self.disposable_goal_field.setFocus()
        self.disposable_goal_field.selectAll()

        if hasattr(self, "scroll_area"):
            self.scroll_area.ensureWidgetVisible(self.disposable_goal_field, 80, 80)

    def focus_holiday_pay(self):
        target = self.employment_start_field
        target.setFocus()
        target.selectAll()

        if hasattr(self, "scroll_area"):
            self.scroll_area.ensureWidgetVisible(target, 80, 80)

    def _save_settings(self):
        try:
            tax = parse_positive_number(self.tax_field, "Skat", allow_zero=True)
            am = parse_positive_number(self.am_field, "AM-bidrag", allow_zero=True)
            pension = parse_positive_number(self.pension_field, "Eget pensionsbidrag", allow_zero=True)
            employer_pension = parse_positive_number(self.employer_pension_field, "Arbejdsgiver pension", allow_zero=True)
            birth_year_text = self.birth_year_field.text().strip()
            birth_year = int(birth_year_text) if birth_year_text else None
            if birth_year is not None and (birth_year < 1900 or birth_year > datetime.now().year):
                raise ValueError("Fødselsår skal være et gyldigt årstal.")
            holiday_rate = parse_positive_number(self.holiday_rate_field, "Feriegodtgørelse")
            employment_start_text = self.employment_start_field.text().strip()
            employment_start = (
                parse_date_text(employment_start_text)
                if employment_start_text
                else first_work_entry_date(self.data)
            )
            new_settings = dict(self.settings) if isinstance(self.settings, dict) else {}
            existing_pay_period = ft.normalize_settings(new_settings)
            period_type = self.period_type_combo.currentData() or ft.PAY_PERIOD_TYPE_MONTH
            period_weeks = (
                parse_int_field(self.period_weeks_field, "Antal uger", 1, 52)
                if self.period_weeks_field.text().strip()
                else int(existing_pay_period.get(ft.PAY_PERIOD_WEEKS_KEY, ft.DEFAULT_PAY_PERIOD_WEEKS))
            )
            period_anchor_text = self.period_anchor_field.text().strip()
            period_anchor = (
                parse_date_text(period_anchor_text)
                if period_anchor_text
                else parse_optional_settings_date(existing_pay_period.get(ft.PAY_PERIOD_ANCHOR_KEY))
            )
            updated_settings = {
                "skat": tax / 100 if tax > 1 else tax,
                "fradrag": parse_positive_number(self.fradrag_field, "Fradrag", allow_zero=True),
                ft.TAX_ALLOWANCE_UNIT_KEY: self.fradrag_unit_combo.currentData() or ft.AMOUNT_UNIT_MONTH,
                "am bidrag": am / 100 if am > 1 else am,
                ft.BIRTH_YEAR_KEY: birth_year,
                ft.AM_AGE_RULE_ENABLED_KEY: self.am_age_rule_checkbox.isChecked(),
                ft.PENSION_CONTRIBUTION_KEY: pension / 100 if pension > 1 else pension,
                ft.EMPLOYER_PENSION_CONTRIBUTION_KEY: employer_pension / 100 if employer_pension > 1 else employer_pension,
                ft.ATP_ENABLED_KEY: self.atp_enabled_checkbox.isChecked(),
                ft.ATP_CALCULATION_KEY: ft.ATP_CALCULATION_MANUAL,
                ft.ATP_EMPLOYEE_AMOUNT_KEY: parse_positive_number(
                    self.atp_employee_field,
                    "ATP medarbejder",
                    allow_zero=True,
                ),
                ft.ATP_EMPLOYER_AMOUNT_KEY: parse_positive_number(
                    self.atp_employer_field,
                    "ATP arbejdsgiver",
                    allow_zero=True,
                ),
                "anden indkomst netto": parse_positive_number(
                    self.other_income_field,
                    "Anden indkomst",
                    allow_zero=True,
                ),
                "standard timeløn": parse_positive_number(
                    self.default_rate_field,
                    "Timeløn",
                ),
                "ønsket rådighedsbeløb": parse_positive_number(
                    self.disposable_goal_field,
                    "Ønsket rådighedsbeløb",
                    allow_zero=True,
                ),
                "løn start": parse_int_field(self.start_day_field, "Lønperiode starter", 1, 31),
                "løn slut": parse_int_field(self.end_day_field, "Lønperiode slutter", 1, 31),
                ft.PAY_PERIOD_TYPE_KEY: period_type,
                ft.PAY_PERIOD_WEEKS_KEY: period_weeks,
                ft.PAY_PERIOD_ANCHOR_KEY: date_to_key(period_anchor) if period_anchor else ft.DEFAULT_PAY_PERIOD_ANCHOR,
                HOLIDAY_PAY_RATE_KEY: holiday_rate,
                HOLIDAY_PAY_EMPLOYMENT_START_KEY: date_to_key(employment_start) if employment_start else "",
            }
            new_settings.update(updated_settings)
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldige indstillinger", str(error))
            return

        ft.save_settings(new_settings, history_reason="Gem indstillinger")
        QMessageBox.information(self, "Indstillinger gemt", "Indstillingerne er gemt.")
        self.window.refresh_all()


class IntroductionDialog(QDialog):
    def __init__(self, window, force=False):
        debug_window_log(f"IntroductionDialog.__init__ start force={force}")
        super().__init__(window)
        self.window = window
        self.force = force
        self.step_index = 0
        self._last_setup_changed = False
        self._setup_precision_hint_shown = False
        self._initial_setup_input_state = None
        self.setModal(True)
        self.setWindowTitle("Introduktion")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(820, 700)
        self.resize(900, 760)

        self.steps = [
            {
                "key": "welcome",
                "title": "Velkommen til Lønix",
                "text": (
                    "Denne korte introduktion hjælper dig med at sætte programmet op og forstå de vigtigste sider.\n\n"
                    "Lønix registrerer vagter og fridage, beregner løn efter skat, pension og fradrag, "
                    "holder styr på månedlige budgetposter og viser hvor meget du har til rådighed i lønperioden."
                ),
            },
            {
                "key": "overview",
                "page": 0,
                "title": "Overblik",
                "text": (
                    "Overblik viser den aktuelle lønperiode.\n\n"
                    "Siden består af widgets, som viser forskellige dele af din økonomi: løn, timer, budget, "
                    "rådighedsbeløb, estimater, feriepenge, feriedage og statistik.\n\n"
                    "Fradrag, budget, anden indkomst og rådighedsmål indtastes som månedstal. Lønix omregner dem "
                    "automatisk til den valgte lønperiode i beregningerne.\n\n"
                    "Du kan personliggøre Overblik ved at trykke på widget-knappen øverst til højre. "
                    "Her kan du flytte, fjerne og tilføje widgets, så forsiden passer til det du bruger mest."
                ),
            },
            {
                "key": "history",
                "page": 1,
                "title": "Vagter",
                "text": (
                    "Vagter viser alle registrerede vagter.\n\n"
                    "Her kan du tilføje flere vagter på samme dag, indberette fridage, angive pause i minutter, "
                    "rette fejl, markere flere registreringer og redigere eller slette dem samlet.\n\n"
                    "En fridag blokerer for vagter på datoen, og vagter med start- og sluttid må ikke overlappe. "
                    "Hver registrering gemmes med sit eget ID og en kopi af de indstillinger, der gjaldt på tidspunktet."
                ),
            },
            {
                "key": "budget",
                "page": 2,
                "title": "Budget",
                "text": (
                    "Budget er dine faste månedlige udgifter.\n\n"
                    "Tilføj de poster du faktisk har, for eksempel husleje, abonnementer eller forsikring. "
                    "Budgettet bruges til at beregne rådighedsbeløb, og beløbene skaleres automatisk til lønperioden."
                ),
            },
            {
                "key": "payments",
                "page": 3,
                "title": "Lønsedler",
                "text": (
                    "Lønsedler viser afsluttede lønperioder.\n\n"
                    "Her kan du se vagter, fridage, betalte timer, pauser, brutto, pension, skat, netto og total "
                    "udbetaling for tidligere perioder. Gamle lønsedler bruger de gemte vagtindstillinger, så de ikke "
                    "ændrer sig bare fordi du senere retter skat, fradrag, pension eller budget."
                ),
            },
            {
                "key": "statistics",
                "page": 4,
                "title": "Statistik",
                "text": (
                    "Statistik samler nøgletal og grafer.\n\n"
                    "Brug siden til at se gennemsnit, rekorder, lønperioder, udvikling, arbejdsmønstre, fradrag "
                    "og prognoser over tid."
                ),
            },
            {
                "key": "calculator",
                "page": 5,
                "title": "Lønberegner",
                "text": (
                    "Lønberegneren er til hurtige beregninger.\n\n"
                    "Du kan beregne netto ud fra bruttoløn eller ud fra timer og timeløn uden at gemme en vagt. "
                    "Beregningen tager højde for fradrag pr. måned, AM-bidrag, skat og eget pensionsbidrag."
                ),
            },
            {
                "key": "settings",
                "page": 6,
                "title": "Indstillinger",
                "text": (
                    "Indstillinger styrer skat, eget pensionsbidrag, fradrag pr. måned, anden indkomst pr. måned, "
                    "standardtimeløn, rådighedsmål pr. måned, lønperiode og feriepenge.\n\n"
                    "Budgetposter redigeres på Budget-siden, men de gemmes også som månedstal og bruges i alle "
                    "rådighedsberegninger."
                ),
            },
            {
                "key": "setup",
                "page": 6,
                "title": "Dine grundoplysninger",
                "text": (
                    "Udfyld de vigtigste tal. De gemmes i Indstillinger og bruges i resten af programmet.\n\n"
                    "Her viser Lønix kun de vigtigste felter: timeløn, skat, fradrag, rådighedsmål, lønperiode "
                    "og ansættelsesstart. Mere detaljerede felter kan tilføjes senere i Indstillinger."
                ),
            },
            {
                "key": "done",
                "title": "Du er klar",
                "text": (
                    "Introduktionen er færdig.\n\n"
                    "Start med at tilføje dine vagter og dine faste månedlige udgifter i Budget. "
                    "Du kan altid starte introduktionen igen fra Indstillinger, og du kan konvertere gamle data "
                    "med database converter script.py hvis en ældre database mangler vagt-ID eller gemte indstillinger."
                ),
            },
        ]

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 18)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(12)
        root.addLayout(header)
        self.title_label = QLabel()
        self.title_label.setObjectName("PageTitle")
        self.title_label.setWordWrap(True)
        header.addWidget(self.title_label, 1)
        self.step_label = QLabel()
        self.step_label.setObjectName("PageSubtitle")
        header.addWidget(self.step_label)

        self.body_label = QLabel()
        self.body_label.setObjectName("PageSubtitle")
        self.body_label.setWordWrap(True)
        self.body_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        root.addWidget(self.body_label)

        self.visual_frame = QFrame()
        self.visual_frame.setObjectName("Card")
        self.visual_frame.setMinimumHeight(275)
        self.visual_frame.setStyleSheet(
            """
            QFrame#Card {
                background: #f8fafc;
                border: 1px solid #dde3ea;
                border-radius: 8px;
            }
            """
        )
        self.visual_layout = QVBoxLayout(self.visual_frame)
        self.visual_layout.setContentsMargins(20, 18, 20, 18)
        self.visual_layout.setSpacing(12)
        root.addWidget(self.visual_frame, 1)

        self.setup_widget = self._build_setup_widget()
        self.setup_scroll = QScrollArea()
        self.setup_scroll.setWidgetResizable(True)
        self.setup_scroll.setFrameShape(QFrame.NoFrame)
        self.setup_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setup_scroll.setWidget(self.setup_widget)
        root.addWidget(self.setup_scroll, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.back_button = QPushButton("Tilbage")
        self.back_button.setObjectName("SecondaryButton")
        self.back_button.clicked.connect(self._back)
        button_row.addWidget(self.back_button)
        self.next_button = QPushButton("Næste")
        self.next_button.clicked.connect(self._next)
        button_row.addWidget(self.next_button)
        root.addLayout(button_row)

        self._fill_existing_values() if self.force else None
        self._initial_setup_input_state = self._setup_input_state()
        self._show_step()
        debug_widget_inventory("IntroductionDialog.__init__ end", limit=12)

    def _build_setup_widget(self):
        wrapper = QFrame()
        wrapper.setObjectName("Card")
        wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        wrapper.setMinimumHeight(470)
        wrapper.setStyleSheet(
            """
            QFrame#Card {
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-radius: 8px;
            }
            QLabel#SetupTitle {
                color: #111827;
                font-size: 12pt;
                font-weight: 850;
                border: 0;
                background: transparent;
            }
            QLabel#SetupHint {
                color: #64748b;
                border: 0;
                background: transparent;
            }
            QLabel#SetupFieldLabel {
                color: #334155;
                font-size: 9pt;
                font-weight: 800;
                border: 0;
                background: transparent;
            }
            QWidget#SetupCell {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            """
        )

        root = QVBoxLayout(wrapper)
        root.setContentsMargins(14, 12, 14, 14)
        root.setSpacing(10)

        title = QLabel("Indtast dine oplysninger nu")
        title.setObjectName("SetupTitle")
        root.addWidget(title)

        hint = QLabel(
            "Skriv de tal du kender. Du kan lade resten stå og ændre dem senere i Indstillinger."
        )
        hint.setObjectName("SetupHint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        root.addLayout(grid)

        self.setup_tax = make_text_input(placeholder="39%")
        self.setup_fradrag = make_text_input(placeholder="0 kr")
        self.setup_fradrag_unit = ModernComboBox()
        for label, value in [
            ("Måned", ft.AMOUNT_UNIT_MONTH),
            ("14 dage", ft.AMOUNT_UNIT_TWO_WEEKS),
            ("Uge", ft.AMOUNT_UNIT_WEEK),
            ("Dag", ft.AMOUNT_UNIT_DAY),
            ("Periode", ft.AMOUNT_UNIT_PERIOD),
        ]:
            self.setup_fradrag_unit.addItem(label, value)
        self.setup_goal = make_text_input(placeholder="0 kr")
        self.setup_period_type = ModernComboBox()
        self.setup_period_type.addItem("Måned", ft.PAY_PERIOD_TYPE_MONTH)
        self.setup_period_type.addItem("Uger", ft.PAY_PERIOD_TYPE_WEEKS)
        self.setup_start = make_text_input(placeholder="15")
        self.setup_end = make_text_input(placeholder="14")
        self.setup_period_weeks = make_text_input(placeholder="2")
        self.setup_period_anchor = make_text_input(placeholder=ft.DEFAULT_PAY_PERIOD_ANCHOR)
        self.setup_rate = make_text_input(placeholder="150 kr")
        self.setup_employment_start = make_text_input(placeholder="dd-mm-åååå")

        fields = [
            ("Timeløn", self.setup_rate),
            ("Skat %", self.setup_tax),
            ("Fradrag", self.setup_fradrag),
            ("Fradrag enhed", self.setup_fradrag_unit),
            ("Ønsket rådighedsbeløb pr. måned", self.setup_goal),
            ("Lønperiode type", self.setup_period_type),
            ("Lønperiode startdag", self.setup_start, "month_start"),
            ("Lønperiode slutdag", self.setup_end, "month_end"),
            ("Antal uger", self.setup_period_weeks, "weeks"),
            ("Første periode starter", self.setup_period_anchor, "anchor"),
            ("Ansættelsesstart", self.setup_employment_start),
        ]
        self.setup_period_cells = {}

        def add_field(index, label_text, field, key=None):
            row = index // 2
            column = index % 2

            cell = QWidget()
            cell.setObjectName("SetupCell")
            cell.setMinimumHeight(68)
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(8, 7, 8, 8)
            cell_layout.setSpacing(4)

            label = QLabel(label_text)
            label.setObjectName("SetupFieldLabel")
            label.setWordWrap(False)

            field.setMinimumWidth(220)
            field.setFixedHeight(34)

            cell_layout.addWidget(label)
            cell_layout.addWidget(field)
            grid.addWidget(cell, row, column)
            if key:
                self.setup_period_cells[key] = cell

        for index, field_info in enumerate(fields):
            label_text, field = field_info[:2]
            key = field_info[2] if len(field_info) > 2 else None
            add_field(index, label_text, field, key)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self.setup_period_type.currentIndexChanged.connect(self._update_setup_pay_period_fields)
        self._update_setup_pay_period_fields()

        return wrapper

    def _update_setup_pay_period_fields(self, *_args):
        is_week_period = self.setup_period_type.currentData() == ft.PAY_PERIOD_TYPE_WEEKS
        for key in ("month_start", "month_end"):
            cell = self.setup_period_cells.get(key)
            if cell is not None:
                cell.setVisible(not is_week_period)
        for key in ("weeks", "anchor"):
            cell = self.setup_period_cells.get(key)
            if cell is not None:
                cell.setVisible(is_week_period)

    def _fill_existing_values(self):
        settings = ft.normalize_settings(self.window.settings)
        set_field_number(self.setup_tax, float(settings.get("skat", 0.39)) * 100)
        set_field_number(self.setup_fradrag, float(settings.get("fradrag", 0)))
        fradrag_unit_index = self.setup_fradrag_unit.findData(settings.get(ft.TAX_ALLOWANCE_UNIT_KEY, ft.AMOUNT_UNIT_MONTH))
        self.setup_fradrag_unit.setCurrentIndex(max(0, fradrag_unit_index))
        set_field_number(self.setup_goal, ft.get_disposable_income_goal(settings))
        period_type_index = self.setup_period_type.findData(settings.get(ft.PAY_PERIOD_TYPE_KEY, ft.PAY_PERIOD_TYPE_MONTH))
        if period_type_index < 0:
            period_type_index = 0
        self.setup_period_type.blockSignals(True)
        self.setup_period_type.setCurrentIndex(period_type_index)
        self.setup_period_type.blockSignals(False)
        self.setup_start.setText(str(int(settings.get("løn start", 15))))
        self.setup_end.setText(str(int(settings.get("løn slut", 14))))
        self.setup_period_weeks.setText(str(int(settings.get(ft.PAY_PERIOD_WEEKS_KEY, ft.DEFAULT_PAY_PERIOD_WEEKS))))
        self.setup_period_anchor.setText(str(settings.get(ft.PAY_PERIOD_ANCHOR_KEY, ft.DEFAULT_PAY_PERIOD_ANCHOR)))
        set_field_number(self.setup_rate, ft.get_default_hourly_rate(settings))
        holiday_settings = holiday_pay_settings(settings)
        employment_start = holiday_settings["employment_start"] or first_work_entry_date(getattr(self.window, "data", []))
        self.setup_employment_start.setText(format_date(employment_start) if employment_start else "")
        self._update_setup_pay_period_fields()

    def _current_step(self):
        return self.steps[self.step_index]

    def _show_step(self):
        step = self._current_step()
        debug_window_log(f"IntroductionDialog._show_step index={self.step_index} key={step['key']}")
        is_setup_step = step["key"] == "setup"

        self.title_label.setText(step["title"])
        self.body_label.setText(step["text"])
        self.step_label.setText(f"{self.step_index + 1} / {len(self.steps)}")

        self.setup_scroll.setVisible(is_setup_step)

        if is_setup_step:
            self.visual_frame.hide()
            self.body_label.setMinimumHeight(0)
        else:
            self.visual_frame.show()
            self.body_label.setMinimumHeight(0)
            self.visual_frame.setMinimumHeight(275)
            self.visual_frame.setMaximumHeight(16777215)
            self._set_visual(step["key"])

        if "page" in step:
            self.window.go_to_page(step["page"])

        self.back_button.setEnabled(self.step_index > 0)
        self.next_button.setText("Afslut" if step["key"] == "done" else "Næste")

    def _set_visual(self, key):
        clear_layout(self.visual_layout)
        builders = {
            "welcome": self._visual_welcome,
            "overview": self._visual_overview,
            "entry": self._visual_entry,
            "payments": self._visual_payments,
            "statistics": self._visual_statistics,
            "budget": self._visual_budget,
            "history": self._visual_history,
            "calculator": self._visual_calculator,
            "settings": self._visual_settings,
            "setup": self._visual_setup,
            "done": self._visual_done,
        }
        builders.get(key, self._visual_welcome)()

    def _visual_title(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: #0f172a; font-size: 11.5pt; font-weight: 850;")
        label.setWordWrap(True)
        self.visual_layout.addWidget(label)

    def _mini_card(self, title, value, accent="#1f8a70", subtitle=""):
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background: #ffffff;
                border: 1px solid #dbe3ec;
                border-radius: 8px;
            }
            QLabel {
                border: 0;
                background: transparent;
            }
            """
        )
        card.setMinimumHeight(100)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(4)
        accent_bar = QFrame()
        accent_bar.setFixedSize(34, 4)
        accent_bar.setStyleSheet(f"background: {accent}; border-radius: 2px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 800;")
        title_label.setWordWrap(True)
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #0f172a; font-size: 13pt; font-weight: 900;")
        value_label.setMinimumHeight(24)
        layout.addWidget(accent_bar, 0, Qt.AlignLeft)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #64748b; font-size: 9pt;")
            subtitle_label.setWordWrap(True)
            subtitle_label.setMinimumHeight(18)
            layout.addWidget(subtitle_label)
        return card

    def _mini_row(self, left, right="", accent=False):
        row = QFrame()
        row.setMinimumHeight(36)
        row.setStyleSheet(
            f"""
            QFrame {{
                background: {'#ecfdf5' if accent else '#ffffff'};
                border: 1px solid {'#86efac' if accent else '#dde3ea'};
                border-radius: 7px;
            }}
            QLabel {{
                border: 0;
                background: transparent;
            }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        left_label = QLabel(left)
        left_label.setStyleSheet("font-weight: 800; color: #334155;")
        right_label = QLabel(right)
        right_label.setStyleSheet("color: #475569;")
        right_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        right_label.setWordWrap(False)
        layout.addWidget(left_label, 1)
        layout.addWidget(right_label, 1)
        return row

    def _mini_bar(self, label, value, color="#1f8a70"):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #475569; font-weight: 800;")
        bar_back = QFrame()
        bar_back.setFixedHeight(10)
        bar_back.setStyleSheet("background: #e2e8f0; border-radius: 5px;")
        bar_layout = QHBoxLayout(bar_back)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        fill = QFrame()
        fill.setStyleSheet(f"background: {color}; border-radius: 5px;")
        bar_layout.addWidget(fill, max(1, value))
        bar_layout.addStretch(max(1, 100 - value))
        layout.addWidget(label_widget)
        layout.addWidget(bar_back)
        return wrapper

    def _flow_node(self, title, subtitle, accent):
        node = QFrame()
        node.setMinimumHeight(82)
        node.setStyleSheet(
            """
            QFrame {
                background: #ffffff;
                border: 1px solid #dbe3ec;
                border-radius: 8px;
            }
            QLabel {
                border: 0;
                background: transparent;
            }
            """
        )
        layout = QVBoxLayout(node)
        layout.setContentsMargins(13, 11, 13, 11)
        layout.setSpacing(5)
        dot = QFrame()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background: {accent}; border-radius: 5px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #0f172a; font-size: 12pt; font-weight: 900;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #64748b;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(dot)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return node

    def _visual_flow(self, items):
        row = QHBoxLayout()
        row.setSpacing(10)
        for index, (title, subtitle, accent) in enumerate(items):
            row.addWidget(self._flow_node(title, subtitle, accent), 1)
            if index < len(items) - 1:
                arrow = QLabel("→")
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setStyleSheet("color: #94a3b8; font-size: 18pt; font-weight: 800;")
                row.addWidget(arrow)
        self.visual_layout.addLayout(row)

    def _visual_welcome(self):
        self._visual_title("Et roligt overblik over det, du faktisk skal bruge")
        self._visual_flow(
            [
                ("Vagter", "Gem timer, pause og fridage", "#1f8a70"),
                ("Beregning", "Skat, pension og fradrag", "#2563eb"),
                ("Rådighed", "Budget og mål pr. periode", "#d97706"),
            ]
        )
        self.visual_layout.addWidget(self._mini_bar("Rådighed i perioden", 62))

    def _visual_overview(self):
        self._visual_title("Overblik er bygget af små widgets")
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._mini_card("Netto løn", "3.600 kr.", "#1f8a70", "Efter pension og skat"), 0, 0)
        grid.addWidget(self._mini_card("Rådighed", "1.850 kr.", "#d97706", "Månedstal skaleret"), 0, 1)
        grid.addWidget(self._mini_card("Ferie", "8,7 dage", "#7c3aed", "Inkl. ½-års estimat"), 1, 0)
        grid.addWidget(self._mini_card("Widgets", "Tilpas", "#0f766e", "Flyt, fjern og tilføj"), 1, 1)
        self.visual_layout.addLayout(grid)

    def _visual_entry(self):
        self._visual_title("Tilføj en vagt uden at tænke på beregningen")
        form = QGridLayout()
        form.setSpacing(9)
        for index, (left, right) in enumerate(
            [
                ("Dato", "06 maj"),
                ("Start", "14:00"),
                ("Slut", "18:00"),
                ("Pause", "0 min."),
                ("Timeløn", "150 kr."),
                ("Netto", "331 kr."),
                ("ID", "Gemmes automatisk"),
                ("Snapshot", "Dine satser gemmes"),
            ]
        ):
            form.addWidget(self._mini_row(left, right), index // 2, index % 2)
        self.visual_layout.addLayout(form)

    def _visual_payments(self):
        self._visual_title("Afsluttede lønperioder står som korte lønsedler")
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addWidget(self._mini_row("Maj 2026", "Netto 8.240 kr."))
        rows.addWidget(self._mini_row("Vagter og timer", "8 vagter · 52 t."))
        rows.addWidget(self._mini_row("Detaljer", "Pause · pension · skat · total"))
        rows.addWidget(self._mini_row("Historik", "Bruger gemte vagtindstillinger"))
        self.visual_layout.addLayout(rows)

    def _visual_statistics(self):
        self._visual_title("Statistik viser mønstre uden at fylde hele skærmen")
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(self._mini_bar("Timer pr. periode", 78, "#7c3aed"), 0, 0)
        grid.addWidget(self._mini_bar("Netto løn", 64, "#1f8a70"), 1, 0)
        grid.addWidget(self._mini_bar("Udvikling", 52, "#2563eb"), 2, 0)
        grid.addWidget(self._mini_card("Nøgletal", "Snit", "#475569", "Rekorder, fradrag og prognose"), 0, 1, 3, 1)
        self.visual_layout.addLayout(grid)

    def _visual_budget(self):
        self._visual_title("Budget er månedlige faste poster")
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addWidget(self._mini_row("Husleje", "5.200 kr."))
        rows.addWidget(self._mini_row("Forsikring", "350 kr."))
        rows.addWidget(self._mini_row("Abonnementer", "199 kr."))
        rows.addWidget(self._mini_row("Omregning", "Tilpasses lønperioden"))
        rows.addWidget(self._mini_row("Rådighed", "Indkomst minus budget"))
        self.visual_layout.addLayout(rows)

    def _visual_history(self):
        self._visual_title("Vagter giver dig en enkel liste, du kan rette i")
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addWidget(self._mini_row("Tilføj vagt/fridag", "Dato · tid · pause"))
        rows.addWidget(self._mini_row("Flere vagter", "Samme dato uden overlap"))
        rows.addWidget(self._mini_row("Fridag", "Blokerer for vagter"))
        rows.addWidget(self._mini_row("Rediger markerede", "En eller flere på én gang"))
        rows.addWidget(self._mini_row("Snapshot", "Satser gemmes pr. vagt"))
        self.visual_layout.addLayout(rows)

    def _visual_calculator(self):
        self._visual_title("Lønberegneren er en hurtig testberegning")
        self._visual_flow(
            [
                ("Brutto", "3.000 kr.", "#2563eb"),
                ("Satser", "Fradrag og pension", "#64748b"),
                ("Netto", "1.795 kr.", "#1f8a70"),
            ]
        )
        self.visual_layout.addWidget(self._mini_row("Gemmes ikke", "Kun en beregning"))

    def _visual_settings(self):
        self._visual_title("Indstillinger er de tal resten af appen regner med")
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addWidget(self._mini_row("Skat, AM og pension", "Netto løn"))
        rows.addWidget(self._mini_row("Månedstal", "Fradrag, indkomst og mål"))
        rows.addWidget(self._mini_row("Lønperiode", "Måned eller uger"))
        rows.addWidget(self._mini_row("Feriepenge", "Beløb og feriedage"))
        self.visual_layout.addLayout(rows)

    def _visual_setup(self):
        self._visual_title("Udfyld kun de tal, du kender nu")
        self.visual_layout.addWidget(self._mini_row("Skat", "39%"))
        self.visual_layout.addWidget(self._mini_row("Pension", "0%"))
        self.visual_layout.addWidget(self._mini_row("Timeløn", "150 kr."))
        self.visual_layout.addWidget(self._mini_row("Månedstal", "Fradrag og mål"))

    def _visual_done(self):
        self._visual_title("Klar til at bruge Lønix")
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addWidget(self._mini_row("1. Tilføj vagter", "Vagter-sektionen"))
        rows.addWidget(self._mini_row("2. Tilføj månedligt budget", "Budget-sektionen"))
        rows.addWidget(self._mini_row("3. Følg med", "Overblik åbner nu"))
        self.visual_layout.addLayout(rows)

    def _field_number(self, field, default, label, allow_zero=True):
        if not field.text().strip():
            return default
        return parse_positive_number(field, label, allow_zero=allow_zero)

    def _field_int(self, field, default, label):
        if not field.text().strip():
            return default
        return parse_int_field(field, label, 1, 31)

    def _setup_input_state(self):
        return {
            "tax": self.setup_tax.text().strip(),
            "fradrag": self.setup_fradrag.text().strip(),
            "fradrag_unit": self.setup_fradrag_unit.currentData(),
            "goal": self.setup_goal.text().strip(),
            "period_type": self.setup_period_type.currentData(),
            "start": self.setup_start.text().strip(),
            "end": self.setup_end.text().strip(),
            "weeks": self.setup_period_weeks.text().strip(),
            "anchor": self.setup_period_anchor.text().strip(),
            "rate": self.setup_rate.text().strip(),
            "employment_start": self.setup_employment_start.text().strip(),
        }

    def _save_setup_step(self):
        debug_window_log("IntroductionDialog._save_setup_step")
        try:
            new_settings = dict(self.window.settings) if isinstance(self.window.settings, dict) else {}
            existing_settings = ft.normalize_settings(new_settings)
            tax_value = self._field_number(
                self.setup_tax,
                float(existing_settings.get("skat", 0.39)) * 100,
                "Skatteprocent",
                allow_zero=True,
            )
            period_type = self.setup_period_type.currentData() or ft.PAY_PERIOD_TYPE_MONTH
            employment_start_text = self.setup_employment_start.text().strip()
            existing_holiday_settings = holiday_pay_settings(existing_settings)
            employment_start = (
                parse_date_text(employment_start_text)
                if employment_start_text
                else existing_holiday_settings.get("employment_start") or first_work_entry_date(getattr(self.window, "data", []))
            )
            updated_settings = {
                "skat": tax_value / 100 if tax_value > 1 else tax_value,
                "fradrag": self._field_number(
                    self.setup_fradrag,
                    float(existing_settings.get("fradrag", 0) or 0),
                    "Fradrag",
                    allow_zero=True,
                ),
                ft.TAX_ALLOWANCE_UNIT_KEY: self.setup_fradrag_unit.currentData() or ft.AMOUNT_UNIT_MONTH,
                "ønsket rådighedsbeløb": self._field_number(
                    self.setup_goal,
                    float(existing_settings.get("ønsket rådighedsbeløb", 0) or 0),
                    "Ønsket rådighedsbeløb",
                    allow_zero=True,
                ),
                "standard timeløn": self._field_number(
                    self.setup_rate,
                    ft.get_default_hourly_rate(existing_settings),
                    "Timeløn",
                    allow_zero=False,
                ),
                ft.PAY_PERIOD_TYPE_KEY: period_type,
                HOLIDAY_PAY_EMPLOYMENT_START_KEY: date_to_key(employment_start) if employment_start else "",
            }
            if period_type == ft.PAY_PERIOD_TYPE_WEEKS:
                anchor_text = self.setup_period_anchor.text().strip()
                updated_settings.update(
                    {
                        "løn start": int(existing_settings.get("løn start", 15)),
                        "løn slut": int(existing_settings.get("løn slut", 14)),
                        ft.PAY_PERIOD_WEEKS_KEY: (
                            parse_int_field(self.setup_period_weeks, "Antal uger", 1, 52)
                            if self.setup_period_weeks.text().strip()
                            else int(existing_settings.get(ft.PAY_PERIOD_WEEKS_KEY, ft.DEFAULT_PAY_PERIOD_WEEKS))
                        ),
                        ft.PAY_PERIOD_ANCHOR_KEY: (
                            date_to_key(parse_date_text(anchor_text))
                            if anchor_text
                            else existing_settings.get(ft.PAY_PERIOD_ANCHOR_KEY, ft.DEFAULT_PAY_PERIOD_ANCHOR)
                        ),
                    }
                )
            else:
                updated_settings.update(
                    {
                        "løn start": self._field_int(
                            self.setup_start,
                            int(existing_settings.get("løn start", 15)),
                            "Lønperiode start",
                        ),
                        "løn slut": self._field_int(
                            self.setup_end,
                            int(existing_settings.get("løn slut", 14)),
                            "Lønperiode slut",
                        ),
                        ft.PAY_PERIOD_WEEKS_KEY: int(existing_settings.get(ft.PAY_PERIOD_WEEKS_KEY, ft.DEFAULT_PAY_PERIOD_WEEKS)),
                        ft.PAY_PERIOD_ANCHOR_KEY: existing_settings.get(ft.PAY_PERIOD_ANCHOR_KEY, ft.DEFAULT_PAY_PERIOD_ANCHOR),
                    }
                )
            new_settings.update(updated_settings)
            self._last_setup_changed = self._setup_input_state() != (self._initial_setup_input_state or {})
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldige oplysninger", str(error))
            return False

        ft.save_settings(new_settings, history_reason="Gem introduktionsopsætning")
        self.window.refresh_all_quietly()
        return True

    def _complete_introduction(self):
        debug_window_log("IntroductionDialog._complete_introduction")
        new_settings = dict(self.window.settings) if isinstance(self.window.settings, dict) else {}
        new_settings[ft.INTRODUCTION_DONE_KEY] = True
        ft.save_settings(new_settings, history_reason="Marker introduktion som gennemført")
        self.window.settings = ft.load_settings()
        self.window.go_to_page(0)
        self.accept()

    def _next(self):
        step = self._current_step()
        if step["key"] == "done":
            self._complete_introduction()
            return
        if step["key"] == "setup" and not self._save_setup_step():
            return
        if step["key"] == "setup" and self._last_setup_changed and not self._setup_precision_hint_shown:
            QMessageBox.information(
                self,
                "Flere oplysninger kan tilføjes senere",
                "Dine grundoplysninger er gemt.\n\n"
                "Du kan tilføje flere oplysninger i Indstillinger, fx pension, ATP, AM-regler og anden indkomst. "
                "Det kan gøre beregningerne mere præcise.",
            )
            self._setup_precision_hint_shown = True
        self.step_index += 1
        self._show_step()

    def _back(self):
        if self.step_index <= 0:
            return
        self.step_index -= 1
        self._show_step()


class ActionHistoryChevronButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.expanded = False
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("skipGenericButtonAnimation", True)
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

    def set_expanded(self, expanded):
        self.expanded = bool(expanded)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        hovered = self.underMouse()
        pressed = self.isDown()

        background = QColor("#f8fafc")
        border = QColor("#d7e0ea")
        text_color = QColor("#0f172a")
        chevron_color = QColor("#334155")

        if hovered:
            background = QColor("#f1f8f5")
            border = QColor("#b8d9d0")
            text_color = QColor("#0f766e")
            chevron_color = QColor("#0f766e")

        if pressed:
            background = QColor("#e5f3ef")
            border = QColor("#8fc8b9")

        painter.setPen(QPen(border, 1))
        painter.setBrush(background)
        painter.drawRoundedRect(rect, 9, 9)

        font = QFont(self.font())
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setWeight(QFont.DemiBold)
        painter.setFont(font)
        painter.setPen(text_color)

        text_rect = QRectF(14, 0, self.width() - 48, self.height())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())

        center = QPointF(self.width() - 24, self.height() / 2)
        size = 5.5

        painter.setPen(QPen(chevron_color, 2.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        if self.expanded:
            painter.drawLine(
                QPointF(center.x() - size, center.y() - 2),
                QPointF(center.x(), center.y() + 4),
            )
            painter.drawLine(
                QPointF(center.x(), center.y() + 4),
                QPointF(center.x() + size, center.y() - 2),
            )
        else:
            painter.drawLine(
                QPointF(center.x() - size, center.y() + 2),
                QPointF(center.x(), center.y() - 4),
            )
            painter.drawLine(
                QPointF(center.x(), center.y() - 4),
                QPointF(center.x() + size, center.y() + 2),
            )


class ActionHistoryActionButton(QPushButton):
    def __init__(self, label, icon_name, parent=None):
        super().__init__(parent)
        self.label = label
        self.icon_name = icon_name
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setProperty("skipGenericButtonAnimation", True)
        self.setMinimumHeight(42)
        self.setMinimumWidth(224)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        hovered = self.underMouse()
        pressed = self.isDown()

        background = QColor("#ffffff")
        border = QColor("#cfd8e3")
        text_color = QColor("#0f172a")
        icon_color = QColor("#0f766e")

        if hovered:
            background = QColor("#f0fdfa")
            border = QColor("#99d8c9")
            text_color = QColor("#0f766e")

        if pressed:
            background = QColor("#d9f0ea")
            border = QColor("#72b8a8")

        painter.setPen(QPen(border, 1))
        painter.setBrush(background)
        painter.drawRoundedRect(rect, 8, 8)

        icon_rect = QRectF(13, 0, 22, self.height())
        self._draw_icon(painter, icon_rect, icon_color)

        font = QFont(self.font())
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        font.setWeight(QFont.DemiBold)
        painter.setFont(font)
        painter.setPen(text_color)

        text_rect = QRectF(42, 0, self.width() - 54, self.height())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.label)

    def _draw_icon(self, painter, rect, color):
        painter.save()
        painter.setPen(QPen(color, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        cx = rect.center().x()
        cy = rect.center().y()

        if self.icon_name == "undo":
            painter.drawArc(QRectF(cx - 8, cy - 8, 16, 16), 45 * 16, 245 * 16)
            painter.drawLine(QPointF(cx - 8, cy - 1), QPointF(cx - 13, cy - 1))
            painter.drawLine(QPointF(cx - 13, cy - 1), QPointF(cx - 10, cy - 5))
            painter.drawLine(QPointF(cx - 13, cy - 1), QPointF(cx - 10, cy + 3))

        elif self.icon_name == "history":
            painter.drawEllipse(QRectF(cx - 8, cy - 8, 16, 16))
            painter.drawLine(QPointF(cx, cy), QPointF(cx, cy - 5))
            painter.drawLine(QPointF(cx, cy), QPointF(cx + 5, cy + 3))

        painter.restore()


class ActionHistorySettingsWidget(QFrame):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.expanded = False

        self.setObjectName("ActionHistorySettingsWidget")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setStyleSheet(
            """
            QFrame#ActionHistorySettingsWidget {
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-radius: 10px;
            }

            QLabel#ActionHistoryTitle {
                color: #0f172a;
                font-size: 12.5pt;
                font-weight: 900;
                background: transparent;
                border: 0;
            }

            QLabel#ActionHistoryHint {
                color: #64748b;
                background: transparent;
                border: 0;
                font-size: 10pt;
            }

            QPushButton#ActionHistoryInfoButton {
                background: #ffffff;
                color: #475569;
                border: 1px solid #cfd8e3;
                border-radius: 13px;
                padding: 0;
                font-size: 10pt;
                font-weight: 900;
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
            }

            QPushButton#ActionHistoryInfoButton:hover {
                background: #edf7f4;
                color: #0f766e;
                border-color: #1f8a70;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        title_label = QLabel("Backups")
        title_label.setObjectName("ActionHistoryTitle")
        root.addWidget(title_label)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        root.addLayout(header_row)

        self.info_button = QPushButton("i")
        self.info_button.setObjectName("ActionHistoryInfoButton")
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.setToolTip("Hvad er backups?")
        self.info_button.clicked.connect(self._show_info)
        header_row.addWidget(self.info_button, 0, Qt.AlignVCenter)

        self.header_button = ActionHistoryChevronButton("Vis backup- og versionsværktøjer", self)
        self.header_button.clicked.connect(self._toggle)
        header_row.addWidget(self.header_button, 1)

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content.setMaximumHeight(0)
        self.content.setMinimumHeight(0)

        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 2, 0, 0)
        content_layout.setSpacing(10)

        hint = QLabel(
            "Fortryd den seneste ændring, eller åbn versionshistorikken og indlæs en tidligere version."
        )
        hint.setObjectName("ActionHistoryHint")
        hint.setWordWrap(True)
        content_layout.addWidget(hint)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        content_layout.addLayout(button_row)

        self.undo_button = ActionHistoryActionButton("Fortryd sidste ændring", "undo", self)
        self.undo_button.clicked.connect(self.window._undo_last_change)

        self.history_button = ActionHistoryActionButton("Versionshistorik", "history", self)
        self.history_button.clicked.connect(self.window._open_version_history)

        button_row.addWidget(self.undo_button)
        button_row.addWidget(self.history_button)
        button_row.addStretch()

        root.addWidget(self.content)

        self.expand_animation = QParallelAnimationGroup(self)

        self.content_min_animation = QPropertyAnimation(self.content, b"minimumHeight", self)
        self.content_max_animation = QPropertyAnimation(self.content, b"maximumHeight", self)

        for animation in (self.content_min_animation, self.content_max_animation):
            animation.setDuration(220)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            self.expand_animation.addAnimation(animation)

        self.expand_animation.finished.connect(self._finish_animation)

        self._sync_state(animated=False)

    def _toggle(self):
        self.expanded = not self.expanded
        self._sync_state(animated=True)

    def _sync_state(self, animated=True):
        self.header_button.set_expanded(self.expanded)

        target_height = self.content.sizeHint().height() if self.expanded else 0

        if not animated:
            self.content.setMinimumHeight(target_height)
            self.content.setMaximumHeight(target_height)
            return

        if self.expanded:
            self.content.setMaximumHeight(0)
            self.content.setMinimumHeight(0)

        self.expand_animation.stop()

        for animation in (self.content_min_animation, self.content_max_animation):
            animation.setStartValue(self.content.maximumHeight())
            animation.setEndValue(target_height)

        self.expand_animation.start()

    def _finish_animation(self):
        if self.expanded:
            self.content.setMinimumHeight(0)
            self.content.setMaximumHeight(16777215)
        else:
            self.content.setMinimumHeight(0)
            self.content.setMaximumHeight(0)

    def _show_info(self):
        QMessageBox.information(
            self,
            "Backups",
            "Backups gemmer de seneste ændringer i Lønix.\n\n"
            "Du kan fortryde den seneste ændring eller åbne versionshistorikken og indlæse en tidligere version.",
        )


class VersionHistoryDialog(QDialog):
    MAX_ROWS = 20

    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent
        self.events = []

        self.setModal(True)
        self.setWindowTitle("Versionshistorik")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(860, 560)
        self.resize(940, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header_panel = QFrame()
        header_panel.setObjectName("Card")
        header_panel.setStyleSheet(
            """
            QFrame#Card {
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
                border: 0;
            }
            """
        )
        header_layout = QVBoxLayout(header_panel)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(4)

        title = QLabel("Versionshistorik")
        title.setStyleSheet("color: #111827; font-size: 18pt; font-weight: 900;")
        subtitle = QLabel(
            "Her vises de 20 seneste gemte ændringer. Du kan indlæse en bestemt version, hvis du vil gå tilbage til den tilstand."
        )
        subtitle.setObjectName("PageSubtitle")
        subtitle.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addWidget(header_panel)

        table_panel = QFrame()
        table_panel.setObjectName("Card")
        table_panel.setStyleSheet(
            """
            QFrame#Card {
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-radius: 10px;
            }
            QTableWidget {
                background: #ffffff;
                alternate-background-color: #f8fafc;
                border: 0;
                border-radius: 8px;
                gridline-color: #edf2f7;
                selection-background-color: #e5f3ef;
                selection-color: #111827;
            }
            QHeaderView::section {
                background: #f4f7f9;
                color: #475569;
                border: 0;
                border-bottom: 1px solid #dde3ea;
                padding: 9px;
                font-weight: 850;
            }
            """
        )
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(10)
        root.addWidget(table_panel, 1)

        self.table = QTableWidget()
        setup_table(self.table, ["Tidspunkt", "Handling", "Område", "Beskrivelse", ""])
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(46)
        table_layout.addWidget(self.table, 1)

        button_row = QHBoxLayout()
        root.addLayout(button_row)

        refresh_button = QPushButton("Genindlæs")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.clicked.connect(self._fill_table)

        close_button = QPushButton("Luk")
        close_button.clicked.connect(self.accept)

        button_row.addWidget(refresh_button)
        button_row.addStretch()
        button_row.addWidget(close_button)

        self._fill_table()

    def _fill_table(self):
        if hasattr(ft, "prune_history_events"):
            ft.prune_history_events()

        if not hasattr(ft, "get_history_events"):
            self.table.setRowCount(0)
            return

        self.events = ft.get_history_events(limit=self.MAX_ROWS)
        self.table.setRowCount(len(self.events))

        for row_index, event in enumerate(self.events):
            operation = event.get("operation", "")
            target = event.get("target", "")

            operation_label = {
                "save": "Gemt",
                "undo": "Fortrudt",
                "restore": "Indlæst",
            }.get(operation, operation)

            target_label = {
                "settings": "Indstillinger",
                "data": "Løndata",
            }.get(target, target)

            timestamp_item = table_item(event.get("timestamp", ""))
            operation_item = table_item(operation_label)
            target_item = table_item(target_label)

            summary = (
                ft.summarize_history_event(event)
                if hasattr(ft, "summarize_history_event")
                else str(event.get("reason", ""))
            )
            summary_item = table_item(summary)

            if operation == "undo":
                operation_item.setForeground(QBrush(QColor("#d97706")))
            elif operation == "restore":
                operation_item.setForeground(QBrush(QColor("#2563eb")))
            else:
                operation_item.setForeground(QBrush(QColor("#1f8a70")))

            font = operation_item.font()
            font.setBold(True)
            operation_item.setFont(font)

            self.table.setItem(row_index, 0, timestamp_item)
            self.table.setItem(row_index, 1, operation_item)
            self.table.setItem(row_index, 2, target_item)
            self.table.setItem(row_index, 3, summary_item)
            self._set_restore_button(row_index)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setColumnWidth(0, 165)
        self.table.setColumnWidth(1, 95)
        self.table.setColumnWidth(2, 105)
        self.table.resizeRowsToContents()

    def _set_restore_button(self, row_index):
        button = QPushButton("Indlæs")
        button.setObjectName("InlineButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setToolTip("Indlæs denne version")
        button.clicked.connect(lambda checked=False, index=row_index: self._restore_version(index))

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)

        self.table.setCellWidget(row_index, 4, wrapper)

    def _restore_version(self, index):
        if index < 0 or index >= len(self.events):
            return

        event = self.events[index]
        summary = (
            ft.summarize_history_event(event)
            if hasattr(ft, "summarize_history_event")
            else "denne version"
        )

        answer = QMessageBox.question(
            self,
            "Indlæs version",
            f"Vil du indlæse denne version?\n\n{summary}\n\n"
            "Den nuværende tilstand bliver gemt i historikken, så ændringen kan fortrydes igen.",
        )

        if answer != QMessageBox.Yes:
            return

        try:
            ft.restore_history_event_version(event)
        except ValueError as error:
            QMessageBox.warning(self, "Version kunne ikke indlæses", str(error))
            return
        except Exception as error:
            QMessageBox.warning(self, "Version kunne ikke indlæses", str(error))
            return

        QMessageBox.information(self, "Version indlæst", "Versionen er indlæst.")
        if hasattr(self.window, "refresh_all"):
            self.window.refresh_all()
        self._fill_table()


class MainWindow(QMainWindow):
    def __init__(self):
        debug_window_log("MainWindow.__init__ start")
        super().__init__()
        self.setUpdatesEnabled(False)
        self._startup_revealed = False
        self._startup_reveal_scheduled = False
        ensure_storage()
        self.data = ft.load_data()
        self.settings = ft.load_settings()
        self.pages = []
        self.nav_buttons = []

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        window_size, minimum_size = bounded_window_sizes()
        self.setMinimumSize(minimum_size)
        self.resize(saved_window_size(self.settings, window_size, minimum_size))

        root = QWidget(self)
        root.setObjectName("Content")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget(root)
        sidebar.setObjectName("Sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar.setMinimumWidth(BASE_SIDEBAR_WIDTH)
        self.sidebar = sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 18)
        sidebar_layout.setSpacing(8)
        layout.addWidget(sidebar)

        brand_panel = QFrame(sidebar)
        brand_panel.setObjectName("BrandPanel")
        brand_panel_layout = QHBoxLayout(brand_panel)
        brand_panel_layout.setContentsMargins(12, 11, 12, 11)
        brand_panel_layout.setSpacing(10)
        brand_logo = make_logo_label(QSize(44, 44))
        if brand_logo is not None:
            brand_panel_layout.addWidget(brand_logo, 0, Qt.AlignTop)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        self.brand_label = QLabel(APP_NAME)
        self.brand_label.setObjectName("Brand")
        self.brand_sub_label = QLabel("Løn, budget og overblik")
        self.brand_sub_label.setObjectName("BrandSub")
        self.brand_sub_label.setWordWrap(True)
        brand_text.addWidget(self.brand_label)
        brand_text.addWidget(self.brand_sub_label)
        brand_panel_layout.addLayout(brand_text, 1)
        sidebar_layout.addWidget(brand_panel)
        sidebar_layout.addSpacing(18)

        self.stack = QStackedWidget(root)
        layout.addWidget(self.stack, 1)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self._add_page(sidebar_layout, "Overblik", DashboardPage(self), primary=True)
        self._add_sidebar_separator(sidebar_layout)
        self._add_page(sidebar_layout, "Vagter", HistoryPage(self))
        self._add_page(sidebar_layout, "Budget", BudgetPage(self))
        self._add_page(sidebar_layout, "Lønsedler", PaymentsPage(self))
        self._add_sidebar_separator(sidebar_layout)
        self._add_page(sidebar_layout, "Statistik", StatisticsPage(self))
        self._add_page(sidebar_layout, "Lønberegner", CalculatorPage(self))

        sidebar_layout.addStretch()

        self._add_footer_page(sidebar_layout, "Indstillinger", SettingsPage(self))

        self.introduction_overlay = QWidget(root)
        self.introduction_overlay.setStyleSheet("background: rgba(15, 23, 42, 150);")
        self.introduction_overlay.hide()
        self._introduction_dialog = None

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)
        self._update_sidebar_width()
        center_on_primary_screen(self)
        self.refresh_all()
        debug_widget_inventory("MainWindow.__init__ end")

    def _ui_px(self, value):
        font_height = max(1, self.fontMetrics().height())
        scale = max(0.9, min(1.35, font_height / 17))
        return max(1, int(round(value * scale)))

    def _sidebar_minimum_width(self):
        metrics = self.fontMetrics()
        nav_text_width = max(
            [metrics.horizontalAdvance(button.text()) for button in self.nav_buttons] or [0]
        )
        brand_text_width = 0
        if hasattr(self, "brand_label"):
            brand_text_width = max(brand_text_width, metrics.horizontalAdvance(self.brand_label.text()))
        if hasattr(self, "brand_sub_label"):
            brand_text_width = max(brand_text_width, metrics.horizontalAdvance(self.brand_sub_label.text()))

        nav_width = nav_text_width + self._ui_px(46)
        brand_width = self._ui_px(44 + 10) + brand_text_width
        sidebar_padding = self._ui_px(36)
        return max(self._ui_px(BASE_SIDEBAR_WIDTH), nav_width + sidebar_padding, brand_width + sidebar_padding)

    def _sidebar_target_width(self):
        content_width = self.centralWidget().width() if self.centralWidget() is not None else self.width()
        ratio_width = int(max(1, content_width) * SIDEBAR_WINDOW_RATIO)
        minimum_width = self._sidebar_minimum_width()
        maximum_width = self._ui_px(MAX_SIDEBAR_WIDTH)
        return max(self._ui_px(BASE_SIDEBAR_WIDTH), min(max(minimum_width, ratio_width), maximum_width))

    def _update_sidebar_width(self):
        if not hasattr(self, "sidebar"):
            return

        width = self._sidebar_target_width()
        if self.sidebar.width() != width:
            self.sidebar.setFixedWidth(width)

    def _add_sidebar_separator(self, sidebar_layout):
        separator = QFrame()
        separator.setObjectName("SidebarSeparator")
        separator.setFixedHeight(1)
        sidebar_layout.addSpacing(6)
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(6)

    def _add_page(self, sidebar_layout, label, page, primary=False):
        index = len(self.pages)
        button = SidebarNavButton(label)
        button.setObjectName("PrimaryNavButton" if primary else "NavButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, page_index=index: self.go_to_page(page_index))
        self.button_group.addButton(button)
        self.nav_buttons.append(button)
        sidebar_layout.addWidget(button)
        self.pages.append(page)
        self.stack.addWidget(page)

    def _add_footer_page(self, sidebar_layout, label, page):
        index = len(self.pages)
        button = SidebarNavButton(label)
        button.setObjectName("NavButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, page_index=index: self.go_to_page(page_index))
        self.button_group.addButton(button)
        self.nav_buttons.append(button)
        sidebar_layout.addWidget(button)
        self.pages.append(page)
        self.stack.addWidget(page)

    def _undo_last_change(self):
        if not hasattr(ft, "undo_last_change"):
            QMessageBox.warning(
                self,
                "Undo mangler",
                "Undo-funktionen findes ikke i functions.py.",
            )
            return

        answer = QMessageBox.question(
            self,
            "Fortryd sidste ændring",
            "Vil du fortryde den seneste gemte ændring?\n\n"
            "Historikken bliver ikke slettet.",
        )

        if answer != QMessageBox.Yes:
            return

        try:
            undone_event = ft.undo_last_change()
        except ValueError as error:
            QMessageBox.warning(self, "Kan ikke fortryde", str(error))
            return
        except Exception as error:
            QMessageBox.warning(self, "Undo fejlede", str(error))
            return

        summary = (
            ft.summarize_history_event(undone_event)
            if hasattr(ft, "summarize_history_event")
            else "Seneste ændring blev fortrudt."
        )

        QMessageBox.information(
            self,
            "Ændring fortrudt",
            summary,
        )

        self.refresh_all()

    def _open_version_history(self):
        dialog = VersionHistoryDialog(self)
        dialog.exec_()

    def refresh_all(self):
        debug_window_log("MainWindow.refresh_all start")
        self.data = ft.load_data()
        self.settings = ft.load_settings()
        for page in self.pages:
            debug_window_log(f"  refreshing {type(page).__name__}")
            page.refresh()
        debug_widget_inventory("MainWindow.refresh_all end", limit=10)

    def refresh_all_quietly(self):
        debug_window_log("MainWindow.refresh_all_quietly start")
        updates_were_enabled = self.updatesEnabled()
        if updates_were_enabled:
            self.setUpdatesEnabled(False)
        try:
            self.refresh_all()
        finally:
            if updates_were_enabled:
                self.setUpdatesEnabled(True)
                self.update()
        debug_window_log("MainWindow.refresh_all_quietly end")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_sidebar_width()
        self._position_introduction_overlay()

    def showEvent(self, event):
        debug_window_log("MainWindow.showEvent")
        super().showEvent(event)
        if not self._startup_reveal_scheduled:
            self._startup_reveal_scheduled = True
            QTimer.singleShot(0, self.finalize_startup)

    def closeEvent(self, event):
        try:
            settings = dict(ft.load_settings())
            settings[WINDOW_WIDTH_SETTINGS_KEY] = self.width()
            settings[WINDOW_HEIGHT_SETTINGS_KEY] = self.height()
            ft.save_settings(settings, history_reason="Gem vinduesstørrelse")
        except (OSError, ValueError, TypeError):
            pass
        super().closeEvent(event)

    def finalize_startup(self):
        debug_window_log("MainWindow.finalize_startup")
        if self._startup_revealed:
            return
        self._startup_reveal_scheduled = True
        self._startup_revealed = True
        self.setUpdatesEnabled(True)
        self.update()
        debug_widget_inventory("after startup reveal")
        QTimer.singleShot(220, self._maybe_start_introduction)

    def _position_introduction_overlay(self):
        if hasattr(self, "introduction_overlay"):
            self.introduction_overlay.setGeometry(self.stack.geometry())

    def go_to_page(self, index):
        debug_window_log(f"MainWindow.go_to_page index={index}")
        if index < 0 or index >= len(self.pages):
            return

        current_index = self.stack.currentIndex()

        if current_index != index and 0 <= current_index < len(self.pages):
            current_page = self.pages[current_index]
            if hasattr(current_page, "leave_page"):
                current_page.leave_page()

        self.stack.setCurrentIndex(index)
        self.nav_buttons[index].setChecked(True)

        if self._introduction_dialog is not None:
            self.nav_buttons[index].raise_()

    def _maybe_start_introduction(self):
        debug_window_log("MainWindow._maybe_start_introduction")
        self.data = ft.load_data()
        self.settings = ft.load_settings()
        debug_window_log(f"  introduction_completed={ft.is_introduction_completed(self.settings)}")
        if not ft.is_introduction_completed(self.settings):
            self.start_introduction(force=False)

    def start_introduction(self, force=False):
        debug_window_log(f"MainWindow.start_introduction force={force}")
        debug_widget_inventory("before start_introduction", limit=12)
        if self._introduction_dialog is not None:
            self._introduction_dialog.raise_()
            self._introduction_dialog.activateWindow()
            return
        updates_were_enabled = self.updatesEnabled()
        if updates_were_enabled:
            self.setUpdatesEnabled(False)
        try:
            self._position_introduction_overlay()
            self._introduction_dialog = IntroductionDialog(self, force=force)
            self._introduction_dialog.finished.connect(self._finish_introduction_dialog)
            self._center_dialog_on_window(self._introduction_dialog)
            self.introduction_overlay.show()
            self.introduction_overlay.raise_()
            self._introduction_dialog.open()
            self._introduction_dialog.raise_()
        finally:
            if updates_were_enabled:
                self.setUpdatesEnabled(True)
                self.update()
        debug_widget_inventory("after start_introduction", limit=12)

    def _center_dialog_on_window(self, dialog):
        debug_window_log("MainWindow._center_dialog_on_window")
        dialog.adjustSize()
        frame = dialog.frameGeometry()
        frame.moveCenter(self.frameGeometry().center())
        dialog.move(frame.topLeft())

    def _finish_introduction_dialog(self):
        debug_window_log("MainWindow._finish_introduction_dialog")
        dialog = self._introduction_dialog
        self._introduction_dialog = None
        self.introduction_overlay.hide()
        if dialog is not None:
            dialog.deleteLater()
        debug_widget_inventory("after finish_introduction_dialog", limit=12)


def run():
    debug_window_log("run start")
    os.environ.pop("QT_USE_NATIVE_WINDOWS", None)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_NativeWindows, False)
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    app = QApplication(sys.argv)
    if WINDOW_DEBUG_ENABLED:
        app.window_debug_filter = WindowDebugEventFilter(app)
        app.installEventFilter(app.window_debug_filter)
        debug_widget_inventory("after QApplication created")
    app.setStyle("Fusion")
    app.setWindowIcon(app_icon())
    app.setStyleSheet(APP_STYLE)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    debug_widget_inventory("before window.show")
    window.show()
    debug_widget_inventory("after window.show call")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run())

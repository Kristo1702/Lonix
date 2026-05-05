import json
import os
import sys
from datetime import date, datetime, timedelta

from PyQt5.QtCore import QEvent, QPointF, QRectF, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
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
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
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
    "estimates",
    "stats",
    "budget",
    "breakdown",
    "recent",
)
DASHBOARD_AVAILABLE_WIDGET_ORDER = DASHBOARD_DEFAULT_WIDGET_ORDER + (
    "salary_calculator",
)
DASHBOARD_BUDGET_WIDGET_MIGRATION_KEY = "overblik budget widget tilføjet"
DASHBOARD_WIDGET_TITLES = {
    "goal": "Rådighedsmål",
    "progress": "Forløb",
    "process": "Process",
    "estimates": "Estimater",
    "stats": "Statistik",
    "budget": "Budget",
    "breakdown": "Lønberegning",
    "recent": "Vagter i perioden",
    "salary_calculator": "Lønberegner",
}

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
    border-left: 3px solid #2dd4bf;
    border-radius: 0;
    padding: 11px 14px 11px 11px;
    text-align: left;
    font-weight: 750;
}
QPushButton#PrimaryNavButton:hover {
    background: rgba(255, 255, 255, 0.05);
}
QPushButton#PrimaryNavButton:checked {
    background: rgba(255, 255, 255, 0.07);
    color: #ffffff;
}
QPushButton#NavButton {
    background: transparent;
    color: #d8dee6;
    border: 0;
    border-radius: 7px;
    padding: 11px 14px;
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
    padding: 9px 14px;
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
    padding: 5px 9px;
    font-weight: 700;
}
QPushButton#InlineButton:hover {
    background: #edf7f4;
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
QTabWidget#CalculatorTabs QTabBar::tab {
    min-width: 128px;
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


def parse_clock_minutes(value):
    try:
        parsed = datetime.strptime(value.strip(), "%H:%M")
    except ValueError as error:
        raise ValueError("Tidspunkt skal skrives som HH:MM, fx 14:00.") from error
    return parsed.hour * 60 + parsed.minute


def calculate_hours_from_times(start_text, end_text):
    start_minutes = parse_clock_minutes(start_text)
    end_minutes = parse_clock_minutes(end_text)
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    hours = (end_minutes - start_minutes) / 60
    if hours <= 0:
        raise ValueError("Sluttidspunkt skal være efter starttidspunkt.")
    return hours


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
    label = form.labelForField(field)
    if hasattr(form, "setRowVisible"):
        form.setRowVisible(field, visible)
        return
    if label is not None:
        label.setVisible(visible)
    field.setVisible(visible)


def format_period(period):
    return f"{format_date(period['periode_start'])} - {format_date(period['periode_slut'])}"


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


def entry_rows(data):
    rows = []
    for entry in data:
        dato_str, info = next(iter(entry.items()))
        dato = parse_date_key(dato_str)
        duration = ft.get_shift_duration_hours(info)
        pause = ft.get_shift_pause_hours(info)
        timer = ft.get_shift_paid_hours(info)
        timeløn = float(info.get("timeløn", 0))

        row = {
            "dato": dato,
            "varighed": duration,
            "timer": timer,
            "pause": pause,
            "timeløn": timeløn,
            "brutto": timer * timeløn,
        }

        if info.get("start"):
            row["start"] = str(info.get("start"))

        if info.get("slut"):
            row["slut"] = str(info.get("slut"))

        rows.append(row)

    return sorted(rows, key=lambda row: row["dato"], reverse=True)


def save_entry_rows(rows):
    ensure_storage()
    clean_rows = sorted(rows, key=lambda row: row["dato"])

    payload = []
    for row in clean_rows:
        pause = max(0.0, float(row.get("pause", 0) or 0))
        duration = max(0.0, float(row.get("varighed", float(row["timer"]) + pause) or 0))
        entry_info = {
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

    with open("data/løn.txt", "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=4)


def upsert_entry(entry_date, hours, rate, original_date=None, start=None, slut=None, pause=0):
    rows = entry_rows(ft.load_data())
    target_key = original_date or entry_date

    rows = [row for row in rows if row["dato"] != target_key]

    duration = float(hours)
    pause = max(0.0, float(pause or 0))
    paid_hours = max(0.0, duration - pause)

    new_row = {
        "dato": entry_date,
        "varighed": duration,
        "timer": paid_hours,
        "pause": pause,
        "timeløn": float(rate),
        "brutto": paid_hours * float(rate),
    }

    if start and slut:
        new_row["start"] = str(start)
        new_row["slut"] = str(slut)

    rows.append(new_row)
    save_entry_rows(rows)


def delete_entry(entry_date):
    rows = [row for row in entry_rows(ft.load_data()) if row["dato"] != entry_date]
    save_entry_rows(rows)


def last_rate(data, settings=None):
    rows = entry_rows(data)
    if not rows:
        return ft.get_default_hourly_rate(settings)
    return rows[0]["timeløn"]


def current_period_summary(data, settings, today=None):
    today = today or datetime.now().date()
    if not has_required_settings(settings):
        return None

    periode_start, periode_slut = ft.get_salary_period_for_date(
        today,
        settings.get("løn start"),
        settings.get("løn slut"),
    )

    rows = [
        row
        for row in entry_rows(data)
        if periode_start <= row["dato"] <= periode_slut
    ]
    timer = sum(row["timer"] for row in rows)
    brutto = sum(row["brutto"] for row in rows)
    breakdown = ft.calculate_salary_breakdown(
        brutto,
        settings.get("skat", 0),
        settings.get("fradrag", 0),
        settings.get("am bidrag", 0),
    )
    return {
        "periode_start": periode_start,
        "periode_slut": periode_slut,
        "timer": timer,
        "brutto": brutto,
        "netto": breakdown["netto"],
        "breakdown": breakdown,
        "rows": rows,
    }


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


def format_work_time(row):
    start = row.get("start")
    slut = row.get("slut")

    if start and slut:
        return f"{start} - {slut} ({format_number(row['timer'])}t)"

    return format_number(row["timer"])


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


def fit_table_height(table, row_count, max_rows=20, min_rows=1):
    table.resizeRowsToContents()
    visible_rows = min(max(row_count, min_rows), max_rows)
    default_row_height = max(table.verticalHeader().defaultSectionSize(), table.fontMetrics().height() + 14, 30)
    row_height = sum(
        max(table.rowHeight(index), default_row_height) if index < row_count else default_row_height
        for index in range(visible_rows)
    )
    header_height = max(table.horizontalHeader().height(), table.horizontalHeader().sizeHint().height(), 34)
    height = header_height + row_height + (table.frameWidth() * 2) + 8
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
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")
        self.title_label.setWordWrap(True)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setWordWrap(True)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("MetricSub")
        self.subtitle_label.setWordWrap(True)
        for label in [self.title_label, self.value_label, self.subtitle_label]:
            label.setMinimumWidth(0)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()

        self.setStyleSheet(
            f"""
            QFrame#Card {{
                background: #ffffff;
                border: 1px solid #dde3ea;
                border-left: 4px solid {accent};
                border-radius: 8px;
            }}
            """
        )

    def set_values(self, value, subtitle=""):
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)


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
    def __init__(self, icon_name, tooltip="", checkable=False, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setCheckable(checkable)
        self.setFixedSize(42, 38)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setToolTip(tooltip)

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
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

        painter.setPen(QPen(icon_color, 2.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        center = QPointF(self.width() / 2, self.height() / 2)

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

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

        self.remove_button = DashboardIconButton("remove", "Fjern widget", parent=self)
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
        self.select_callback = select_callback
        self.normal_margin = 8
        self.hover_margin = 0
        self.hover_height = 136
        self.setObjectName("DashboardWidgetPreviewSlot")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(self.hover_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        slot_layout = QVBoxLayout(self)
        slot_layout.setSpacing(0)
        self.slot_layout = slot_layout

        self.card = QFrame(self)
        self.card.setObjectName("DashboardWidgetPreviewCard")
        slot_layout.addWidget(self.card)

        self.root = QVBoxLayout(self.card)
        self.root.setContentsMargins(14, 12, 14, 12)
        self.root.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #111827; font-size: 11pt; font-weight: 850;")
        self.root.addWidget(title_label)

        self.preview_layout = QVBoxLayout()
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(6)
        self.root.addLayout(self.preview_layout)
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
        margin = self.hover_margin if hovered else self.normal_margin
        self.slot_layout.setContentsMargins(margin, margin, margin, margin)
        self.setStyleSheet(
            f"""
            QFrame#DashboardWidgetPreviewSlot {{
                background: transparent;
                border: 0;
            }}
            QFrame#DashboardWidgetPreviewCard {{
                background: {'#f8fffc' if hovered else '#ffffff'};
                border: 1px solid {'#1f8a70' if hovered else '#dde3ea'};
                border-radius: 8px;
            }}
            QFrame#DashboardWidgetPreviewCard QLabel {{
                border: 0;
                background: transparent;
            }}
            """
        )

    def _build_preview(self):
        if self.key == "goal":
            row = QHBoxLayout()
            row.setSpacing(8)
            row.addWidget(self._pill("NÅET", "#16a34a"))
            row.addWidget(self._text_block("2.400 / 2.000 kr.", "Sidste periode vist ved siden af"), 1)
            self.preview_layout.addLayout(row)
        elif self.key == "progress":
            self.preview_layout.addWidget(self._bar("Periodens forløb", 64))
            self.preview_layout.addWidget(self._small_text("4 vagter · 3.200 kr. brutto"))
        elif self.key == "process":
            self.preview_layout.addLayout(self._metric_row([("Netto", "3.600"), ("Rådighed", "1.850"), ("Timer", "24,5")]))
        elif self.key == "estimates":
            self.preview_layout.addLayout(self._metric_row([("Netto", "5.900"), ("Rådighed", "2.150"), ("Timer", "38")]))
        elif self.key == "stats":
            self.preview_layout.addLayout(self._metric_row([("Snit", "720"), ("Uge", "1.450"), ("I alt", "18.400")]))
        elif self.key == "budget":
            self.preview_layout.addWidget(self._mini_row("Husleje", "5.200 kr."))
            self.preview_layout.addWidget(self._mini_row("Abonnementer", "249 kr."))
        elif self.key == "breakdown":
            self.preview_layout.addWidget(self._mini_row("AM-bidrag", "-288 kr."))
            self.preview_layout.addWidget(self._mini_row("Netto løn", "3.312 kr."))
        elif self.key == "recent":
            self.preview_layout.addWidget(self._mini_row("05-05-2026", "6 t. · 900 kr."))
            self.preview_layout.addWidget(self._mini_row("03-05-2026", "4 t. · 600 kr."))
        elif self.key == "salary_calculator":
            self.preview_layout.addLayout(self._metric_row([("Brutto", "3.000"), ("Netto", "1.920")]))
            self.preview_layout.addWidget(self._small_text("Brutto eller timer + timeløn"))

    def _metric_row(self, items):
        row = QHBoxLayout()
        row.setSpacing(7)
        for title, value in items:
            cell = QFrame()
            cell.setStyleSheet("background: #f8fafc; border: 1px solid #e3e8ef; border-radius: 6px;")
            layout = QVBoxLayout(cell)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(1)
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #64748b; font-size: 8pt; font-weight: 800;")
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #111827; font-size: 11pt; font-weight: 850;")
            layout.addWidget(title_label)
            layout.addWidget(value_label)
            row.addWidget(cell)
        return row

    def _bar(self, label, value):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._small_text(label))
        track = QFrame()
        track.setFixedHeight(9)
        track.setStyleSheet("background: #e2e8f0; border: 0; border-radius: 4px;")
        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        fill = QFrame()
        fill.setStyleSheet("background: #1f8a70; border: 0; border-radius: 4px;")
        track_layout.addWidget(fill, max(1, value))
        track_layout.addStretch(max(1, 100 - value))
        layout.addWidget(track)
        return wrapper

    def _pill(self, text, color):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(64)
        label.setStyleSheet(
            f"background: {color}; color: white; border: 0; border-radius: 12px; padding: 5px; font-size: 8pt; font-weight: 850;"
        )
        return label

    def _text_block(self, value, detail):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #111827; font-size: 11pt; font-weight: 850;")
        layout.addWidget(value_label)
        layout.addWidget(self._small_text(detail))
        return wrapper

    def _small_text(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: #64748b; font-size: 8.5pt;")
        return label

    def _mini_row(self, left, right):
        row = QFrame()
        row.setStyleSheet("background: #f8fafc; border: 1px solid #e3e8ef; border-radius: 6px;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(8, 5, 8, 5)
        left_label = QLabel(left)
        left_label.setStyleSheet("color: #334155; font-size: 8.5pt; font-weight: 750;")
        right_label = QLabel(right)
        right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_label.setStyleSheet("color: #111827; font-size: 8.5pt; font-weight: 850;")
        layout.addWidget(left_label, 1)
        layout.addWidget(right_label, 1)
        return row


class DashboardAddWidgetDialog(QDialog):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.selected_key = None
        self.setModal(True)
        self.setWindowTitle("Tilføj widget")
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(500)

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
            scroll.setMaximumHeight(600)

            body = QWidget()
            body_layout = QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(10)
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
    def __init__(self, show_title=True):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(12)
        root.addLayout(top)

        if show_title:
            title = QLabel("Rådighedsmål")
            title.setStyleSheet("color: #111827; font-size: 12.5pt; font-weight: 850;")
            top.addWidget(title)

        self.status_pill = QLabel()
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setMinimumWidth(76)
        top.addWidget(self.status_pill, 0, Qt.AlignVCenter)
        top.addStretch()

        content = QHBoxLayout()
        content.setSpacing(22)
        root.addLayout(content)

        current = QVBoxLayout()
        current.setSpacing(2)
        self.value_label = QLabel("Ikke beregnet")
        self.value_label.setStyleSheet("color: #111827; font-size: 18pt; font-weight: 900;")
        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #475569;")
        current.addWidget(self.value_label)
        current.addWidget(self.detail_label)
        content.addLayout(current, 2)

        previous = QVBoxLayout()
        previous.setSpacing(2)
        previous_title = QLabel("Sidste lønperiode")
        previous_title.setStyleSheet("color: #64707d; font-size: 8.5pt; font-weight: 850;")
        self.previous_label = QLabel("Ingen afsluttet periode")
        self.previous_label.setStyleSheet("color: #334155; font-size: 11pt; font-weight: 850;")
        self.previous_detail_label = QLabel("Når en periode er afsluttet, vises netto og rådighed her.")
        self.previous_detail_label.setWordWrap(True)
        self.previous_detail_label.setStyleSheet("color: #64707d; font-size: 8.5pt;")
        previous.addWidget(previous_title)
        previous.addWidget(self.previous_label)
        previous.addWidget(self.previous_detail_label)
        content.addLayout(previous, 1)

        self.set_status("neutral", "Ikke beregnet", "Målet kan ikke vurderes endnu.", None)

    def set_status(self, state, value, detail, previous_period=None):
        styles = {
            "success": ("NÅET", "#16a34a"),
            "warning": ("PÅ VEJ", "#d97706"),
            "danger": ("UNDER", "#dc2626"),
            "neutral": ("IKKE SAT", "#64748b"),
        }
        label, color = styles.get(state, styles["neutral"])
        self.status_pill.setText(label)
        self.value_label.setText(value)
        self.detail_label.setText(detail)
        if previous_period:
            self.previous_label.setText(f"Rådighed: {format_money(previous_period['available'])}")
            self.previous_detail_label.setText("")
        else:
            self.previous_label.setText("Ingen afsluttet periode")
            self.previous_detail_label.setText("Når en periode er afsluttet, vises netto og rådighed her.")
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
        self.setMinimumHeight(168)
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

    def _marker_data(self, rect):
        if not self.period_start or not self.period_end:
            return []

        total_days = max(1, (self.period_end - self.period_start).days + 1)
        track_left = rect.left() + 18
        track_right = rect.right() - 18
        track_width = max(1, track_right - track_left)
        track_y = rect.top() + 92
        max_brutto = max([row["brutto"] for row in self.rows] or [1])
        marker_width = max(2.5, min(5, int(track_width / max(total_days, 1) * 0.28)))

        markers = []
        for index, row in enumerate(self.rows):
            day_index = min(max((row["dato"] - self.period_start).days, 0), total_days - 1)
            ratio = day_index / max(1, total_days - 1)
            x = track_left + (track_width * ratio)
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
        total_brutto = sum(row["brutto"] for row in self.rows)
        best_shift = max(self.rows, key=lambda row: row["brutto"]) if self.rows else None

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
            f"{len(self.rows)} vagter · {format_money(total_brutto)} brutto",
        )

        track_left = rect.left() + 18
        track_right = rect.right() - 18
        track_width = max(1, track_right - track_left)
        track_y = rect.top() + 92
        track_height = 18

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e5eaf0"))
        painter.drawRoundedRect(QRectF(track_left, track_y, track_width, track_height), 9, 9)
        painter.setBrush(QColor("#1f8a70"))
        painter.drawRoundedRect(QRectF(track_left, track_y, track_width * self.progress_ratio, track_height), 9, 9)

        if self.today:
            today_index = min(max((self.today - self.period_start).days, 0), total_days - 1)
            today_x = track_left + (track_width * (today_index / max(1, total_days - 1)))
            painter.setPen(QPen(QColor("#0f172a"), 2))
            painter.drawLine(int(today_x), int(track_y - 10), int(today_x), int(track_y + track_height + 18))
            painter.setPen(QColor("#0f172a"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(QRectF(today_x - 30, track_y + track_height + 18, 60, 18), Qt.AlignCenter, "I dag")

        self.marker_rects = self._marker_data(rect)
        for index, row, marker, x in self.marker_rects:
            color = QColor("#ffffff")
            painter.setPen(Qt.NoPen)
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
        best_text = f"Bedste vagt: {format_money(best_shift['brutto'])}" if best_shift else "Ingen vagter registreret endnu"
        painter.drawText(
            QRectF(rect.center().x(), footer_y, rect.width() / 2 - 18, 18),
            Qt.AlignRight | Qt.AlignVCenter,
            best_text,
        )


class DashboardBudgetWidget(QWidget):
    VISIBLE_ROWS = 5
    ROW_HEIGHT = 32
    ROW_SPACING = 6
    CLICK_MOVE_TOLERANCE = 6

    def __init__(self, open_budget_callback):
        super().__init__()
        self.open_budget_callback = open_budget_callback
        self.click_start_global_pos = None
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.total_label = QLabel("Samlede udgifter: 0 kr.")
        self.total_label.setStyleSheet("color: #111827; font-size: 16pt; font-weight: 900;")
        root.addWidget(self.total_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setMaximumHeight(self._scroll_height(self.VISIBLE_ROWS))
        self._register_click_target(self.scroll.viewport())
        root.addWidget(self.scroll)

        self.body = QWidget()
        self._register_click_target(self.body)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(self.ROW_SPACING)
        self.scroll.setWidget(self.body)

    def update_budget(self, categories):
        clear_layout(self.body_layout)
        budget_total = sum(item["beløb"] for item in categories)
        self.total_label.setText(f"Samlede udgifter: {format_money(budget_total)}")

        if not categories:
            empty = QLabel("Ingen budgetposter endnu.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #64748b; background: #f8fafc; border: 1px solid #e3e8ef; border-radius: 7px; padding: 18px;")
            self._register_click_target(empty)
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

    def _register_click_target(self, widget):
        widget.setCursor(Qt.PointingHandCursor)
        widget.setProperty("budgetClickTarget", True)
        widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched.property("budgetClickTarget"):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.click_start_global_pos = event.globalPos()
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                if self._is_click_release(event):
                    self.open_budget_callback()
                    return True
                self.click_start_global_pos = None
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_start_global_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_click_release(event):
            self.open_budget_callback()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _is_click_release(self, event):
        if self.click_start_global_pos is None:
            return False
        moved = (event.globalPos() - self.click_start_global_pos).manhattanLength()
        self.click_start_global_pos = None
        return moved <= self.CLICK_MOVE_TOLERANCE

    def _row(self, left, right):
        row = QFrame()
        row.setFixedHeight(self.ROW_HEIGHT)
        self._register_click_target(row)
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
        self._register_click_target(left_label)
        left_label.setStyleSheet("color: #334155; font-weight: 750;")
        right_label = QLabel(right)
        self._register_click_target(right_label)
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
            gross = self._gross_value()
        except ValueError as error:
            self.net_label.setText("Netto løn: N/A")
            self.detail_label.setText(str(error))
            return

        if gross is None:
            self.net_label.setText("Netto løn: N/A")
            self.detail_label.setText("Brug bruttofeltet eller timer + timeløn.")
            return

        breakdown = ft.calculate_salary_breakdown(
            gross,
            self.settings.get("skat", 0),
            self.settings.get("fradrag", 0),
            self.settings.get("am bidrag", 0),
        )
        self.net_label.setText(f"Netto løn: {format_money(breakdown['netto'])}")
        self.detail_label.setText(
            f"Brutto: {format_money(gross)} · Skat: {format_number(float(self.settings.get('skat', 0)) * 100)}%"
        )

    def _gross_value(self):
        gross_text = self.gross_field.text().strip()
        if gross_text:
            return parse_positive_number(self.gross_field, "Brutto løn", allow_zero=True)

        hours_text = self.hours_field.text().strip()
        rate_text = self.rate_field.text().strip()
        if not hours_text and not rate_text:
            return None
        if not hours_text or not rate_text:
            raise ValueError("Udfyld både timer og timeløn.")

        hours = parse_positive_number(self.hours_field, "Timer", allow_zero=True)
        rate = parse_positive_number(self.rate_field, "Timeløn", allow_zero=True)
        return hours * rate


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
        super().__init__()
        self.window = window

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page_layout.addWidget(self.scroll_area)

        self.page_body = QWidget()
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


class DashboardPage(BasePage):
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
        self.drag_autoscroll_timer = QTimer(self)
        self.drag_autoscroll_timer.setInterval(16)
        self.drag_autoscroll_timer.timeout.connect(self._auto_scroll_drag)

        reorder_toolbar = QHBoxLayout()
        reorder_toolbar.setContentsMargins(0, 0, 0, 0)
        reorder_toolbar.setSpacing(8)
        self.root.addLayout(reorder_toolbar)

        reorder_toolbar.addStretch()

        self.add_widget_button = DashboardIconButton("add", "Tilføj widget", parent=self)
        self.add_widget_button.clicked.connect(self._show_add_widget_dialog)
        self.add_widget_button.hide()
        reorder_toolbar.addWidget(self.add_widget_button, 0, Qt.AlignRight)

        self.reorder_button = DashboardIconButton("widgets", "Rediger widgets", checkable=True, parent=self)
        self.reorder_button.toggled.connect(self._set_reorder_mode)
        reorder_toolbar.addWidget(self.reorder_button, 0, Qt.AlignRight)

        self.dashboard_layout = QVBoxLayout()
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_layout.setSpacing(16)
        self.root.addLayout(self.dashboard_layout)
        self.drop_indicator = DashboardDropIndicator(self.page_body)

        goal_panel = self._make_widget_frame("Rådighedsmål", "goal")
        self.goal_card = GoalHeaderWidget(show_title=False)
        goal_panel.addWidget(self.goal_card)
        self.dashboard_widgets["goal"] = goal_panel

        progress_panel = self._make_widget_frame("Forløb", "progress")
        self.period_progress = PeriodProgressWidget()
        self.progress_detail = QLabel()
        self.progress_detail.setObjectName("PageSubtitle")
        self.progress_detail.setWordWrap(True)
        progress_panel.addWidget(self.period_progress)
        progress_panel.addWidget(self.progress_detail)
        self.dashboard_widgets["progress"] = progress_panel

        process_panel = self._make_widget_frame("Process", "process")
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
        self.stats_strip = DashboardMetricStrip("", columns=3, embedded=True)
        stats_panel.addWidget(self.stats_strip)
        self.dashboard_widgets["stats"] = stats_panel
        self.stat_average_card = DashboardMetricItem("Snit pr. vagt", accent="#475569")
        self.stat_week_card = DashboardMetricItem("Snit pr. uge", accent="#2563eb")
        self.stat_total_net_card = DashboardMetricItem("Løn i alt", accent="#1f8a70")
        self.stats_cards = [self.stat_average_card, self.stat_week_card, self.stat_total_net_card]
        for card in self.stats_cards:
            self.stats_strip.add_item(card)

        budget_panel = self._make_widget_frame("Budget", "budget")
        self.budget_widget = DashboardBudgetWidget(self._go_to_budget_page)
        budget_panel.addWidget(self.budget_widget)
        self.dashboard_widgets["budget"] = budget_panel

        breakdown_panel = self._make_widget_frame("Lønberegning", "breakdown")
        self.breakdown_table = QTableWidget()
        setup_table(self.breakdown_table, ["Post", "Beløb"])
        breakdown_panel.addWidget(self.breakdown_table)
        self.dashboard_widgets["breakdown"] = breakdown_panel

        recent_panel = self._make_widget_frame("Vagter i perioden", "recent")
        self.recent_table = QTableWidget()
        setup_table(self.recent_table, ["Dato", "Timer", "Pause", "Brutto"])
        recent_panel.addWidget(self.recent_table)
        self.dashboard_widgets["recent"] = recent_panel

        calculator_panel = self._make_widget_frame("Lønberegner", "salary_calculator")
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

    def _render_widget_order(self):
        scroll_value = self.scroll_area.verticalScrollBar().value()
        edit_mode = self.reorder_button.isChecked()
        dragged_key = self.dragged_widget_key
        visible_order = [key for key in self.widget_order if key != dragged_key]
        drop_index = self.widget_order.index(dragged_key) if dragged_key in self.widget_order else None

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
        self._restore_scroll_position(scroll_value)

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

    def _go_to_budget_page(self):
        for index, page in enumerate(getattr(self.window, "pages", [])):
            if isinstance(page, BudgetPage):
                self.window.go_to_page(index)
                return

    def _start_widget_drag(self, key, global_pos):
        if not self.reorder_button.isChecked() or key not in self.widget_order:
            return

        self.dragged_widget_key = key
        self.drag_last_global_pos = global_pos
        self._create_drag_ghost(key, global_pos)
        self._render_widget_order()
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
        self._clear_drag_ghost()
        self.dragged_widget_key = None
        self.drag_last_global_pos = None
        self._save_widget_order()
        self._render_widget_order()

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
        self._render_widget_order()

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
        cursor_y = self.page_body.mapFromGlobal(global_pos).y()
        target_index = 0
        for key in self.widget_order:
            if key == self.dragged_widget_key:
                continue
            widget = self.dashboard_widgets[key]
            center_y = widget.mapTo(self.page_body, widget.rect().center()).y()
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
            ft.save_settings(new_settings)
            self.window.settings = ft.load_settings()
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.warning(self, "Rækkefølge kunne ikke gemmes", str(error))

    def refresh(self):
        self._apply_widget_order()
        budget_categories = ft.get_budget_categories(self.settings)
        self.budget_widget.update_budget(budget_categories)
        self.salary_calculator_widget.set_settings(self.settings)
        if not has_required_settings(self.settings):
            self._show_missing_settings()
            return

        summary = current_period_summary(self.data, self.settings)
        forecast = ft.calculate_salary_forecast(self.data, self.settings)
        other_income = ft.get_other_income(self.settings)
        budget_expenses = ft.calculate_budget_expenses(self.settings)
        previous_period = self._last_complete_period_info(other_income, budget_expenses)

        total_now = summary["netto"] + other_income
        available_now = ft.calculate_disposable_income(total_now, self.settings)
        estimated_total = forecast.get("estimated_total_income") if forecast else None
        estimated_available = forecast.get("estimated_disposable_income") if forecast else None
        estimated_netto = forecast.get("estimated_netto") if forecast else None
        estimated_brutto = forecast.get("estimated_brutto") if forecast else None
        estimated_hours = forecast.get("estimated_hours") if forecast else None
        disposable_goal = ft.get_disposable_income_goal(self.settings)
        show_other_income = other_income > 0
        self._arrange_cards(show_other_income)
        today = datetime.now().date()
        total_days = max(1, (summary["periode_slut"] - summary["periode_start"]).days + 1)
        elapsed_days = min(max((today - summary["periode_start"]).days + 1, 0), total_days)
        remaining_days = max(total_days - elapsed_days, 0)
        progress_ratio = elapsed_days / total_days if total_days else 0

        self.net_card.set_values(format_money(summary["netto"]), "Efter skat")
        if show_other_income:
            self.total_card.set_values(format_money(total_now), "Netto løn nu + anden indkomst")
        self.available_card.set_values(format_money(available_now), f"Efter udgifter: {format_money(budget_expenses)}")
        self.hours_card.set_values(f"{format_number(summary['timer'])} t.", f"{len(summary['rows'])} vagter i perioden")
        self.gross_card.set_values(format_money(summary["brutto"]), "Før skat")
        self.period_card.set_values(
            f"d. {self.settings.get('løn start')} - d. {self.settings.get('løn slut')}",
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
            self.progress_detail.setText(
                f"{elapsed_days} af {total_days} dage er gået. {remaining_days} dage tilbage. "
                f"Registreret brutto i perioden: {format_money(summary['brutto'])}."
            )
        else:
            self.progress_detail.setText(
                f"{elapsed_days} af {total_days} dage er gået. {remaining_days} dage tilbage. "
                "Ingen vagter registreret i perioden endnu."
            )

        self._update_goal_status(available_now, estimated_available, disposable_goal, previous_period)
        self._update_stats(summary)
        self._fill_breakdown(summary["breakdown"])
        self._fill_recent(summary["rows"])

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
        fit_table_height(self.recent_table, 0, max_rows=20, min_rows=1)

    def _last_complete_period_info(self, other_income, budget_expenses):
        _, complete_periods = build_periods(self.data, self.settings)
        if not complete_periods:
            return None
        period = complete_periods[-1]
        total_income = period["netto"] + other_income
        return {
            "netto": period["netto"],
            "available": total_income - budget_expenses,
        }

    def _update_stats(self, summary):
        rows = summary["rows"]
        periods, _ = build_periods(self.data, self.settings)
        total_netto_all = sum(period["netto"] for period in periods) if periods else 0
        if not rows:
            self.stat_average_card.set_values("N/A", "Ingen vagter i perioden")
            self.stat_week_card.set_values("N/A", "Ingen vagter i perioden")
            self.stat_total_net_card.set_values(format_money(total_netto_all), "Netto fra alle vagter")
            return

        avg_netto = summary["netto"] / len(rows)
        avg_hours = average_or_none(row["timer"] for row in rows)
        total_weeks = max(1 / 7, ((summary["periode_slut"] - summary["periode_start"]).days + 1) / 7)
        weekly_netto = summary["netto"] / total_weeks
        weekly_hours = summary["timer"] / total_weeks
        self.stat_average_card.set_values(format_money(avg_netto), f"{format_number(avg_hours)} timer i snit")
        self.stat_week_card.set_values(format_money(weekly_netto), f"{format_number(weekly_hours)} timer i snit")
        self.stat_total_net_card.set_values(format_money(total_netto_all), "Netto fra alle vagter")

    def _update_goal_status(self, available_now, estimated_available, disposable_goal, previous_period):
        if disposable_goal <= 0:
            self.goal_card.set_status(
                "neutral",
                "Ikke sat",
                "Angiv et ønsket rådighedsbeløb i Indstillinger for at følge målet.",
                previous_period,
            )
        elif available_now >= disposable_goal:
            self.goal_card.set_status(
                "success",
                f"{format_money(available_now)} / {format_money(disposable_goal)}",
                "Målet er nået for den nuværende lønperiode.",
                previous_period,
            )
        elif estimated_available is not None and estimated_available >= disposable_goal:
            self.goal_card.set_status(
                "warning",
                f"{format_money(estimated_available)} est. / {format_money(disposable_goal)}",
                f"Estimatet når målet. Nu: {format_money(available_now)} af {format_money(disposable_goal)}.",
                previous_period,
            )
        else:
            estimated_text = format_money(estimated_available) if estimated_available is not None else "N/A"
            self.goal_card.set_status(
                "danger",
                f"{estimated_text} est. / {format_money(disposable_goal)}",
                f"Estimatet er under målet på {format_money(disposable_goal)}.",
                previous_period,
            )

    def _fill_breakdown(self, breakdown):
        rows = [
            ("Brutto løn", format_money(breakdown["brutto"])),
            ("AM-bidrag", f"-{format_money(breakdown['am_bidrag'])}"),
            ("Efter AM-bidrag", format_money(breakdown["efter_am"])),
            ("Fradrag", format_money(breakdown["fradrag"])),
            ("Skattegrundlag", format_money(breakdown["skattegrundlag"])),
            ("Skat", f"-{format_money(breakdown['skat'])}"),
            ("Netto løn", format_money(breakdown["netto"])),
        ]
        self.breakdown_table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.breakdown_table.setItem(row_index, 0, table_item(label))
            self.breakdown_table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(self.breakdown_table, len(rows), max_rows=8, min_rows=len(rows))

    def _fill_recent(self, rows):
        self.recent_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.recent_table.setItem(row_index, 0, table_item(format_date(row["dato"])))
            self.recent_table.setItem(row_index, 1, table_item(format_work_time(row), Qt.AlignRight | Qt.AlignVCenter))
            self.recent_table.setItem(row_index, 2, table_item(format_pause_minutes(row["pause"]), Qt.AlignRight | Qt.AlignVCenter))
            self.recent_table.setItem(row_index, 3, table_item(format_money(row["brutto"]), Qt.AlignRight | Qt.AlignVCenter))
        fit_table_height(self.recent_table, len(rows), max_rows=20, min_rows=min(3, max(1, len(rows))))


class ShiftEntryDialog(QDialog):
    def __init__(self, parent, window):
        super().__init__(parent)
        self.window = window
        self.saved_date = None

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
        self.date_edit.setText(format_date(entry_date))
        self.mode_combo.setCurrentIndex(0)
        self.hours_field.setText("4")
        self.start_field.setText("14:00")
        self.end_field.setText("18:00")
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
        netto = ft.calculate_salary_breakdown_from_brutto(brutto)["netto"] if has_required_settings(self.settings) else None
        pause_text = f" | Pause: {format_pause_minutes(pause)} min." if pause > 0 else ""
        self.summary_label.setText(
            f"Vagt: {format_number(hours)} betalte timer á {format_money(rate)}{pause_text}\n"
            f"Brutto: {format_money(brutto)}  |  Netto: {format_money(netto)}"
        )

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
        exists = any(key in entry for entry in ft.load_data())
        if exists:
            answer = QMessageBox.question(
                self,
                "Overskriv vagt",
                f"Der findes allerede en vagt for {key}. Vil du overskrive den?",
            )
            if answer != QMessageBox.Yes:
                return

        upsert_entry(
            selected_date,
            duration,
            rate,
            start=start_time,
            slut=end_time,
            pause=pause,
        )
        self.saved_date = selected_date

        QMessageBox.information(
            self,
            "Vagt gemt",
            f"{key} blev gemt med {format_number(hours)} betalte timer á {format_money(rate)}.",
        )
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
        input_panel.setMinimumWidth(380)
        content.addWidget(input_panel, 0)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("CalculatorTabs")
        self.tabs.setUsesScrollButtons(False)
        self.tabs.tabBar().setExpanding(True)
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
        self.tabs.addTab(hours_tab, "Timer + timeløn")
        self.tabs.tabBar().setMinimumWidth(290)
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
        tax_form.addRow("Fradrag", self.fradrag_field)
        tax_form.addRow("Skat %", self.tax_field)
        tax_form.addRow("AM-bidrag %", self.am_field)

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
        self._calculate()

    def _gross(self):
        if self.tabs.currentIndex() == 0:
            return parse_positive_number(self.brutto_field, "Bruttoløn", allow_zero=True)
        hours = parse_positive_number(self.calc_hours_field, "Timer", allow_zero=True)
        rate = parse_positive_number(self.calc_rate_field, "Timeløn", allow_zero=True)
        return hours * rate

    def _calculate(self):
        try:
            brutto = self._gross()
            tax_value = parse_positive_number(self.tax_field, "Skat", allow_zero=True)
            am_value = parse_positive_number(self.am_field, "AM-bidrag", allow_zero=True)
            tax_rate = tax_value / 100 if tax_value > 1 else tax_value
            am_rate = am_value / 100 if am_value > 1 else am_value
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
        )
        self.net_result.set_values(
            format_money(breakdown["netto"]),
            f"Brutto: {format_money(brutto)} | Skat: {format_number(tax_rate * 100)}%",
        )
        rows = [
            ("Brutto løn", format_money(breakdown["brutto"])),
            ("AM-bidrag", f"-{format_money(breakdown['am_bidrag'])}"),
            ("Efter AM-bidrag", format_money(breakdown["efter_am"])),
            ("Fradrag", format_money(breakdown["fradrag"])),
            ("Skattegrundlag", format_money(breakdown["skattegrundlag"])),
            ("Skat", f"-{format_money(breakdown['skat'])}"),
            ("Netto løn", format_money(breakdown["netto"])),
        ]
        self.result_table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.result_table.setItem(row_index, 0, table_item(label))
            self.result_table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))


class PaymentsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Lønsedler",
            "Afsluttede lønperioder med løn, anden indkomst og total udbetaling.",
        )

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        table_panel, table_layout = make_panel("Afsluttede lønsedler")
        content.addWidget(table_panel, 2)
        self.payments_table = QTableWidget()
        setup_table(self.payments_table, ["Periode", "Vagter", "Timer", "Pause", "Brutto", "Netto", "Total"])
        self.payments_table.itemSelectionChanged.connect(self._update_detail)
        table_layout.addWidget(self.payments_table)

        detail_panel, detail_layout = make_panel("Detaljer")
        content.addWidget(detail_panel, 1)
        self.detail_title = QLabel("Vælg en udbetaling")
        self.detail_title.setObjectName("MetricValue")
        self.detail_title.setWordWrap(True)
        detail_layout.addWidget(self.detail_title)
        self.detail_table = QTableWidget()
        setup_table(self.detail_table, ["Post", "Værdi"])
        detail_layout.addWidget(self.detail_table)

        self.payments = []

    def refresh(self):
        _, complete_periods = build_periods(self.data, self.settings)
        self.payments = list(reversed(complete_periods))
        self.payments_table.setRowCount(len(self.payments))
        other_income = ft.get_other_income(self.settings) if has_required_settings(self.settings) else 0

        for row_index, period in enumerate(self.payments):
            total = period["netto"] + other_income
            shift_count = len(period.get("shifts", [])) or int(period.get("vagter", 0))
            self.payments_table.setItem(row_index, 0, table_item(f"{month_title(period)}\n{format_period(period)}"))
            self.payments_table.setItem(row_index, 1, table_item(str(shift_count), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 2, table_item(format_number(period["timer"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 3, table_item(format_pause_minutes(period.get("pause", 0)), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 4, table_item(format_money(period["brutto"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 5, table_item(format_money(period["netto"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 6, table_item(format_money(total), Qt.AlignRight | Qt.AlignVCenter))

        if self.payments:
            self.payments_table.resizeRowsToContents()
            self.payments_table.selectRow(0)
            self._update_detail()
        else:
            self.detail_title.setText("Ingen afsluttede udbetalinger")
            self.detail_table.setRowCount(0)

    def _update_detail(self):
        selected = self.payments_table.currentRow()
        if selected < 0 or selected >= len(self.payments):
            return
        period = self.payments[selected]
        other_income = ft.get_other_income(self.settings)
        total = period["netto"] + other_income
        avg_rate = period["brutto"] / period["timer"] if period["timer"] else None
        shift_count = len(period.get("shifts", [])) or int(period.get("vagter", 0))
        self.detail_title.setText(month_title(period))
        rows = [
            ("Periode", format_period(period)),
            ("Vagter", str(shift_count)),
            ("Timer før pause", f"{format_number(period.get('varighed', period['timer'] + period.get('pause', 0)))} t."),
            ("Pause", f"{format_pause_minutes(period.get('pause', 0))} min."),
            ("Betalte timer", f"{format_number(period['timer'])} t."),
            ("Gns. timeløn", format_money(avg_rate)),
            ("Brutto løn", format_money(period["brutto"])),
            ("AM-bidrag", f"-{format_money(period['am_bidrag'])}"),
            ("Efter AM-bidrag", format_money(period.get("efter_am"))),
            ("Fradrag", format_money(period.get("fradrag"))),
            ("Skattegrundlag", format_money(period.get("skattegrundlag"))),
            ("Skat", f"-{format_money(period['skat'])}"),
            ("Netto løn", format_money(period["netto"])),
            ("Anden indkomst (netto)", format_money(other_income)),
            ("Total udbetalt", format_money(total)),
        ]
        self.detail_table.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.detail_table.setItem(row_index, 0, table_item(label))
            self.detail_table.setItem(row_index, 1, table_item(value, Qt.AlignRight | Qt.AlignVCenter))


class StatisticsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Statistik",
            "Nøgletal, rekorder, prognose og grafer samlet ét sted.",
        )

        self.tabs = QTabWidget()
        self.tabs.setUsesScrollButtons(False)
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
                format_money(stats["deductions"]["am_bidrag"] + stats["deductions"]["skat"]),
                "AM-bidrag og skat",
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
                ["Vagter pr. lønperiode i snit", format_number(stats["shift_counts"]["per_period"])],
            ],
        )

    def _shift_row(self, label, shift):
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
        self._add_table(
            "Arbejdsmønster",
            ["Måling", "Værdi"],
            [
                ["Gennemsnitlige dage mellem vagter", format_number(stats["patterns"]["average_gap"])],
                ["Længste streak", f"{streak['length']} dage ({format_date(streak['start'])} - {format_date(streak['end'])})"],
            ],
        )

    def _add_deductions(self, stats):
        self._add_table(
            "Fradrag",
            ["Måling", "Beløb"],
            [
                ["Samlet AM-bidrag", format_money(stats["deductions"]["am_bidrag"])],
                ["Samlet skat", format_money(stats["deductions"]["skat"])],
                ["Samlet trukket", format_money(stats["deductions"]["am_bidrag"] + stats["deductions"]["skat"])],
            ],
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
                ["Estimeret løn", f"{format_money(forecast['estimated_brutto'])} / {format_money(forecast['estimated_netto'])}"],
                ["Estimeret total inkl. anden indkomst", format_money(forecast["estimated_total_income"])],
                ["Samlede udgifter", format_money(forecast["budget_expenses"])],
                ["Estimeret rådighedsbeløb", format_money(forecast["estimated_disposable_income"])],
            ]
        self._add_table("Prognose", ["Måling", "Værdi"], rows)

class HistoryPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Vagter",
            "Alle registrerede vagter sorteret med nyeste først. Tilføj, rediger, marker eller slet vagter her.",
        )
        self.rows = []
        self.selected_original_date = None
        self.selected_has_time = False
        self.pending_select_date = None
        self.pending_select_row = None

        top = QHBoxLayout()
        top.setSpacing(14)
        self.root.addLayout(top)
        self.total_card = MetricCard("Registreringer", accent="#1f8a70")
        self.hours_card = MetricCard("Timer i alt", accent="#2563eb")
        self.gross_card = MetricCard("Brutto i alt", accent="#d97706")
        top.addWidget(self.total_card)
        top.addWidget(self.hours_card)
        top.addWidget(self.gross_card)

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        panel, layout = make_panel("Vagter")
        content.addWidget(panel, 2)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        layout.addLayout(toolbar)
        add_button = QPushButton("Tilføj vagt")
        add_button.clicked.connect(self._add_shift)
        toolbar.addWidget(add_button)
        toolbar.addStretch()
        self.delete_checked_button = QPushButton("Slet markerede")
        self.delete_checked_button.setObjectName("SecondaryButton")
        self.delete_checked_button.clicked.connect(self._delete_checked_rows)
        self.delete_checked_button.hide()
        toolbar.addWidget(self.delete_checked_button)

        self.table = QTableWidget()
        setup_table(self.table, ["", "Dato", "Timer", "Pause", "Brutto"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0, 44)
        self.table.itemSelectionChanged.connect(self._load_selected_row)
        layout.addWidget(self.table)

        edit_panel, edit_layout = make_panel("Rediger valgt vagt")
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
        previous_selected_date = self.selected_original_date
        self.rows = entry_rows(self.data)
        self.total_card.set_values(str(len(self.rows)), "Gemte vagter")
        self.hours_card.set_values(f"{format_number(sum(row['timer'] for row in self.rows))} t.", "Alle registreringer")
        self.gross_card.set_values(format_money(sum(row["brutto"] for row in self.rows)), "Før skat")

        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))

        for row_index, row in enumerate(self.rows):
            self._set_check_widget(row_index)
            self.table.setItem(row_index, 1, table_item(format_date(row["dato"])))
            self.table.setItem(row_index, 2, table_item(format_work_time(row), Qt.AlignRight | Qt.AlignVCenter))
            self.table.setItem(row_index, 3, table_item(format_pause_minutes(row["pause"]), Qt.AlignRight | Qt.AlignVCenter))
            self.table.setItem(row_index, 4, table_item(format_money(row["brutto"]), Qt.AlignRight | Qt.AlignVCenter))

        self.table.resizeRowsToContents()
        self.table.resizeColumnToContents(0)
        self.table.blockSignals(False)
        self._update_checked_rows()
        self._select_after_refresh(previous_selected_date)

    def _set_check_widget(self, row_index):
        checkbox = VisibleCheckBox()
        checkbox.stateChanged.connect(self._update_checked_rows)

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(checkbox)
        self.table.setCellWidget(row_index, 0, wrapper)

    def _row_index_for_date(self, target_date):
        if target_date is None:
            return None
        for row_index, row in enumerate(self.rows):
            if row["dato"] == target_date:
                return row_index
        return None

    def _select_after_refresh(self, previous_selected_date):
        self.table.clearSelection()

        if not self.rows:
            self.pending_select_date = None
            self.pending_select_row = None
            self._clear_edit_fields()
            return

        selected_index = self._row_index_for_date(self.pending_select_date)

        if selected_index is None and self.pending_select_row is not None:
            selected_index = min(self.pending_select_row, len(self.rows) - 1)

        if selected_index is None:
            selected_index = self._row_index_for_date(previous_selected_date)

        if selected_index is None:
            selected_index = 0

        self.pending_select_date = None
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
        self.delete_checked_button.setVisible(count > 0)
        if count == 1:
            self.delete_checked_button.setText("Slet 1 markeret")
        else:
            self.delete_checked_button.setText(f"Slet {count} markerede")

    def _add_shift(self):
        dialog = ShiftEntryDialog(self, self.window)
        if dialog.exec_() == QDialog.Accepted and dialog.saved_date is not None:
            self.pending_select_date = dialog.saved_date
            self.window.refresh_all()

    def _update_edit_mode(self, has_time):
        self.selected_has_time = bool(has_time)

        set_form_row_visible(self.edit_form, self.edit_hours_field, not self.selected_has_time)
        set_form_row_visible(self.edit_form, self.edit_start_field, self.selected_has_time)
        set_form_row_visible(self.edit_form, self.edit_end_field, self.selected_has_time)

    def _load_selected_row(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.rows):
            self._clear_edit_fields()
            return

        row = self.rows[selected]
        self.selected_original_date = row["dato"]

        has_time = bool(row.get("start") and row.get("slut"))
        self._update_edit_mode(has_time)

        self.edit_date_field.setText(format_date(row["dato"]))
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
        self.selected_has_time = False

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
        if self.selected_original_date is None:
            QMessageBox.information(self, "Ingen vagt valgt", "Vælg først en vagt i tabellen.")
            return

        try:
            selected_date = parse_date_text(self.edit_date_field.text())
            duration, hours, start, slut, pause = self._edited_hours_and_times()
            rate = parse_positive_number(self.edit_rate_field, "Timeløn")
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig ændring", str(error))
            return

        target_exists = any(
            parse_date_key(next(iter(entry.keys()))) == selected_date
            for entry in self.data
            if parse_date_key(next(iter(entry.keys()))) != self.selected_original_date
        )

        if target_exists:
            answer = QMessageBox.question(
                self,
                "Overskriv eksisterende dato",
                f"Der findes allerede en anden vagt for {format_date(selected_date)}. Vil du overskrive den?",
            )
            if answer != QMessageBox.Yes:
                return

        upsert_entry(
            selected_date,
            duration,
            rate,
            self.selected_original_date,
            start=start,
            slut=slut,
            pause=pause,
        )

        self.pending_select_date = selected_date
        self.window.refresh_all()

    def _delete_selected_row(self):
        if self.selected_original_date is None:
            QMessageBox.information(self, "Ingen vagt valgt", "Vælg først en vagt i tabellen.")
            return

        selected_index = self.table.currentRow()
        answer = QMessageBox.question(
            self,
            "Slet vagt",
            f"Vil du slette vagten for {format_date(self.selected_original_date)}?",
        )

        if answer != QMessageBox.Yes:
            return

        delete_entry(self.selected_original_date)
        self.pending_select_row = selected_index
        self.window.refresh_all()

    def _delete_checked_rows(self):
        checked_indexes = self._checked_row_indexes()
        if not checked_indexes:
            return

        checked_dates = {
            self.rows[row_index]["dato"]
            for row_index in checked_indexes
            if 0 <= row_index < len(self.rows)
        }
        if not checked_dates:
            return

        count = len(checked_dates)
        label = "vagt" if count == 1 else "vagter"
        answer = QMessageBox.question(
            self,
            "Slet markerede vagter",
            f"Vil du slette {count} markerede {label}?",
        )

        if answer != QMessageBox.Yes:
            return

        remaining_rows = [
            row
            for row in entry_rows(ft.load_data())
            if row["dato"] not in checked_dates
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
            "Planlæg faste udgifter i budgetposter, som bruges i rådighedsberegningerne.",
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
        intro = QLabel("Posterne her er dine faste udgifter for perioden.")
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
        self.total_expenses_label.setText(f"Samlede udgifter: {format_money(self._budget_total())}")

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
        ft.save_settings(self._settings_with_budget())
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
            "Tilpas skat, anden indkomst, rådighedsmål og lønperiodens datoer. Faste udgifter styres på Budget-siden.",
        )

        panel, layout = make_panel("Økonomi, mål og lønperiode")
        self.root.addWidget(panel)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        layout.addLayout(form)

        self.tax_field = make_text_input(placeholder="fx 49")
        self.fradrag_field = make_text_input(placeholder="fx 0")
        self.am_field = make_text_input(placeholder="fx 8")
        self.other_income_field = make_text_input(placeholder="fx 10742")
        self.disposable_goal_field = make_text_input(placeholder="fx 2500")
        self.default_rate_field = make_text_input(placeholder="fx 150")
        self.start_day_field = make_text_input(placeholder="1-31")
        self.end_day_field = make_text_input(placeholder="1-31")

        form.addRow("Skat %", self.tax_field)
        form.addRow("Fradrag", self.fradrag_field)
        form.addRow("AM-bidrag %", self.am_field)
        form.addRow("Anden indkomst (netto)", self.other_income_field)
        form.addRow("Ønsket rådighedsbeløb", self.disposable_goal_field)
        form.addRow("Standard timeløn", self.default_rate_field)
        form.addRow("Lønperiode starter d.", self.start_day_field)
        form.addRow("Lønperiode slutter d.", self.end_day_field)

        button_row = QHBoxLayout()
        layout.addLayout(button_row)
        save_button = QPushButton("Gem indstillinger")
        save_button.clicked.connect(self._save_settings)
        button_row.addWidget(save_button)
        reset_button = QPushButton("Genindlæs")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self.refresh)
        button_row.addWidget(reset_button)
        tutorial_button = QPushButton("Start tutorial")
        tutorial_button.setObjectName("SecondaryButton")
        tutorial_button.clicked.connect(lambda: self.window.start_tutorial(force=True))
        button_row.addWidget(tutorial_button)
        button_row.addStretch()

        note = QLabel("Ændringer påvirker beregninger og prognoser med det samme, men ændrer ikke dine gemte vagter.")
        note.setObjectName("PageSubtitle")
        note.setWordWrap(True)
        self.root.addWidget(note)
        self.root.addStretch()

    def refresh(self):
        settings = self.settings if has_required_settings(self.settings) else {
            "skat": 0.4,
            "fradrag": 0,
            "am bidrag": 0.08,
            "anden indkomst netto": 0,
            "ønsket rådighedsbeløb": 1000,
            "standard timeløn": 150,
            "løn start": 15,
            "løn slut": 14,
        }
        set_field_number(self.tax_field, float(settings.get("skat", 0)) * 100)
        set_field_number(self.fradrag_field, float(settings.get("fradrag", 0)))
        set_field_number(self.am_field, float(settings.get("am bidrag", 0)) * 100)
        set_field_number(self.other_income_field, ft.get_other_income(settings))
        set_field_number(self.disposable_goal_field, ft.get_disposable_income_goal(settings))
        set_field_number(self.default_rate_field, ft.get_default_hourly_rate(settings))
        self.start_day_field.setText(str(int(settings.get("løn start", 15))))
        self.end_day_field.setText(str(int(settings.get("løn slut", 14))))

    def _save_settings(self):
        try:
            tax = parse_positive_number(self.tax_field, "Skat", allow_zero=True)
            am = parse_positive_number(self.am_field, "AM-bidrag", allow_zero=True)
            new_settings = dict(self.settings) if isinstance(self.settings, dict) else {}
            new_settings.update(
                {
                    "skat": tax / 100 if tax > 1 else tax,
                    "fradrag": parse_positive_number(self.fradrag_field, "Fradrag", allow_zero=True),
                    "am bidrag": am / 100 if am > 1 else am,
                    "anden indkomst netto": parse_positive_number(
                        self.other_income_field,
                        "Anden indkomst",
                        allow_zero=True,
                    ),
                    "standard timeløn": parse_positive_number(
                        self.default_rate_field,
                        "Standard timeløn",
                    ),
                    "ønsket rådighedsbeløb": parse_positive_number(
                        self.disposable_goal_field,
                        "Ønsket rådighedsbeløb",
                        allow_zero=True,
                    ),
                    "løn start": parse_int_field(self.start_day_field, "Lønperiode starter", 1, 31),
                    "løn slut": parse_int_field(self.end_day_field, "Lønperiode slutter", 1, 31),
                }
            )
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldige indstillinger", str(error))
            return

        ft.save_settings(new_settings)
        QMessageBox.information(self, "Indstillinger gemt", "Indstillingerne er gemt.")
        self.window.refresh_all()


class TutorialDialog(QDialog):
    def __init__(self, window, force=False):
        super().__init__(window)
        self.window = window
        self.force = force
        self.step_index = 0
        self.setModal(True)
        self.setWindowTitle("Kom godt i gang")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(760, 620)
        self.resize(820, 680)

        self.steps = [
            {
                "key": "Velkommen!",
                "title": "Velkommen til Lønix",
                "text": (
                    "Denne korte tutorial hjælper dig med at sætte programmet op.\n\n"
                    "Lønix bruges til at registrere vagter, beregne løn, holde styr på faste udgifter "
                    "og se hvor meget du har til rådighed i lønperioden."
                ),
            },
            {
                "key": "overview",
                "page": 0,
                "title": "Overblik",
                "text": (
                    "Overblik viser den aktuelle lønperiode.\n\n"
                    "Her ser du registreret netto løn, timer, brutto løn, rådighedsbeløb efter budget "
                    "og estimater for resten af perioden."
                ),
            },
            {
                "key": "history",
                "page": 1,
                "title": "Vagter",
                "text": (
                    "Vagter viser alle registrerede vagter.\n\n"
                    "Her kan du tilføje en ny vagt, angive pause i minutter, rette fejl i gamle vagter, "
                    "markere flere vagter eller slette en vagt."
                ),
            },
            {
                "key": "budget",
                "page": 2,
                "title": "Budget",
                "text": (
                    "Budget er dine faste udgifter for perioden.\n\n"
                    "Tilføj de poster du faktisk har, for eksempel husleje, abonnementer eller forsikring. "
                    "Budgettet bruges til at beregne rådighedsbeløb."
                ),
            },
            {
                "key": "payments",
                "page": 3,
                "title": "Lønsedler",
                "text": (
                    "Lønsedler viser afsluttede lønperioder.\n\n"
                    "Her kan du se vagter, betalte timer, pauser, brutto, netto og total udbetaling "
                    "for tidligere perioder."
                ),
            },
            {
                "key": "statistics",
                "page": 4,
                "title": "Statistik",
                "text": (
                    "Statistik samler nøgletal og grafer.\n\n"
                    "Brug siden til at se udvikling i timer, løn og mønstre over tid."
                ),
            },
            {
                "key": "calculator",
                "page": 5,
                "title": "Lønberegner",
                "text": (
                    "Lønberegneren er til hurtige beregninger.\n\n"
                    "Du kan beregne netto ud fra bruttoløn eller ud fra timer og timeløn uden at gemme en vagt."
                ),
            },
            {
                "key": "settings",
                "page": 6,
                "title": "Indstillinger",
                "text": (
                    "Indstillinger styrer skat, fradrag, anden indkomst, standardtimeløn og lønperiode.\n\n"
                    "Angiv også dit ønskede rådighedsbeløb. Det bruges som mål i Overblik og Budget."
                ),
            },
            {
                "key": "setup",
                "page": 6,
                "title": "Dine grundoplysninger",
                "text": (
                    "Udfyld de vigtigste tal. De gemmes i Indstillinger og bruges i resten af programmet.\n\n"
                    "Lad et felt stå tomt, hvis du vil bruge standardværdien i feltets placeholder."
                ),
            },
            {
                "key": "done",
                "title": "Du er klar",
                "text": (
                    "Tutorialen er færdig.\n\n"
                    "Start med at tilføje dine vagter og dine faste udgifter i Budget. "
                    "Du kan altid starte tutorialen igen fra Indstillinger."
                ),
            },
        ]

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 18)
        root.setSpacing(14)

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
        self.body_label.setMinimumHeight(82)
        root.addWidget(self.body_label)

        self.visual_frame = QFrame()
        self.visual_frame.setObjectName("Card")
        self.visual_frame.setMinimumHeight(190)
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
        self.visual_layout.setContentsMargins(18, 16, 18, 16)
        self.visual_layout.setSpacing(10)
        root.addWidget(self.visual_frame)

        self.setup_widget = self._build_setup_widget()
        root.addWidget(self.setup_widget)

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
        self._show_step()

    def _build_setup_widget(self):
        wrapper = QFrame()
        wrapper.setObjectName("Card")
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
            """
        )

        root = QVBoxLayout(wrapper)
        root.setContentsMargins(18, 16, 18, 18)
        root.setSpacing(14)

        title = QLabel("Grundoplysninger")
        title.setObjectName("SetupTitle")
        root.addWidget(title)

        hint = QLabel(
            "Udfyld dine vigtigste tal her. Felterne bliver gemt i Indstillinger, "
            "når du trykker Næste."
        )
        hint.setObjectName("SetupHint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)
        root.addLayout(grid)

        self.setup_other_income = make_text_input(placeholder="0 kr")
        self.setup_tax = make_text_input(placeholder="40%")
        self.setup_fradrag = make_text_input(placeholder="0 kr")
        self.setup_goal = make_text_input(placeholder="2000 kr")
        self.setup_start = make_text_input(placeholder="15")
        self.setup_end = make_text_input(placeholder="14")
        self.setup_rate = make_text_input(placeholder="150 kr")

        fields = [
            ("Anden indkomst netto", self.setup_other_income),
            ("Skatteprocent", self.setup_tax),
            ("Fradrag", self.setup_fradrag),
            ("Ønsket rådighedsbeløb", self.setup_goal),
            ("Lønperiode startdag", self.setup_start),
            ("Lønperiode slutdag", self.setup_end),
            ("Standard timeløn", self.setup_rate),
        ]

        def add_field(index, label_text, field):
            row = index // 2
            column = index % 2

            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(5)

            label = QLabel(label_text)
            label.setObjectName("SetupFieldLabel")
            label.setWordWrap(False)

            field.setMinimumWidth(250)

            cell_layout.addWidget(label)
            cell_layout.addWidget(field)
            grid.addWidget(cell, row, column)

        for index, (label_text, field) in enumerate(fields):
            add_field(index, label_text, field)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        return wrapper

    def _fill_existing_values(self):
        settings = self.window.settings
        set_field_number(self.setup_other_income, ft.get_other_income(settings))
        set_field_number(self.setup_tax, float(settings.get("skat", 0.4)) * 100)
        set_field_number(self.setup_fradrag, float(settings.get("fradrag", 0)))
        set_field_number(self.setup_goal, ft.get_disposable_income_goal(settings))
        self.setup_start.setText(str(int(settings.get("løn start", 15))))
        self.setup_end.setText(str(int(settings.get("løn slut", 14))))
        set_field_number(self.setup_rate, ft.get_default_hourly_rate(settings))

    def _current_step(self):
        return self.steps[self.step_index]

    def _show_step(self):
        step = self._current_step()
        is_setup_step = step["key"] == "setup"

        self.title_label.setText(step["title"])
        self.body_label.setText(step["text"])
        self.step_label.setText(f"{self.step_index + 1} / {len(self.steps)}")

        self.setup_widget.setVisible(is_setup_step)

        if is_setup_step:
            self.visual_frame.hide()
            self.body_label.setMinimumHeight(48)
        else:
            self.visual_frame.show()
            self.body_label.setMinimumHeight(82)
            self.visual_frame.setMinimumHeight(190)
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
        label.setStyleSheet("color: #334155; font-weight: 800;")
        self.visual_layout.addWidget(label)

    def _mini_card(self, title, value, accent="#1f8a70", subtitle=""):
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background: #ffffff;
                border: 1px solid #dbe3ec;
                border-left: 4px solid {accent};
                border-radius: 8px;
            }}
            QLabel {{
                border: 0;
                background: transparent;
            }}
            """
        )
        card.setMinimumHeight(76)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 700;")
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #0f172a; font-size: 15pt; font-weight: 850;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #64748b;")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)
        return card

    def _mini_row(self, left, right="", accent=False):
        row = QFrame()
        row.setMinimumHeight(34)
        row.setStyleSheet(
            f"""
            QFrame {{
                background: {'#ecfdf5' if accent else '#ffffff'};
                border: 1px solid {'#99f6e4' if accent else '#dde3ea'};
                border-radius: 6px;
            }}
            QLabel {{
                border: 0;
                background: transparent;
            }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        left_label = QLabel(left)
        left_label.setStyleSheet("font-weight: 700; color: #334155;")
        left_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
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
        layout.setSpacing(5)
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #475569; font-weight: 700;")
        bar_back = QFrame()
        bar_back.setFixedHeight(11)
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

    def _visual_welcome(self):
        self._visual_title("Lønix samler løn, budget og rådighed ét sted")
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._mini_card("Vagter", "Tilføj", "#1f8a70", "Dato, timer, pause og timeløn"), 0, 0)
        grid.addWidget(self._mini_card("Beregn", "Netto", "#2563eb", "Skat og fradrag medregnes"), 0, 1)
        grid.addWidget(self._mini_card("Planlæg", "Budget", "#d97706", "Faste udgifter trækkes fra"), 0, 2)
        self.visual_layout.addLayout(grid)
        self.visual_layout.addWidget(self._mini_bar("Rådighed gennem perioden", 62))

    def _visual_overview(self):
        self._visual_title("Overblik viser status nu og estimater separat")
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._mini_card("Netto løn nu", "3.600 kr.", "#1f8a70"), 0, 0)
        grid.addWidget(self._mini_card("Til rådighed nu", "1.850 kr.", "#d97706"), 0, 1)
        grid.addWidget(self._mini_card("Timer", "24,5 t.", "#7c3aed"), 0, 2)
        self.visual_layout.addLayout(grid)
        self.visual_layout.addWidget(self._mini_bar("Periodens forløb", 40))
        self.visual_layout.addWidget(self._mini_row("Estimater", "Forventet netto, rådighed og timer"))

    def _visual_entry(self):
        self._visual_title("Vagter registrerer én vagt ad gangen")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        for left, right in [
            ("Dato", "03-05-2026"),
            ("Metode", "Start/slut"),
            ("Start og slut", "14:00 - 18:00"),
            ("Pause", "30 min."),
            ("Timeløn", "150 kr."),
        ]:
            rows.addWidget(self._mini_row(left, right))
        rows.addWidget(self._mini_row("Gem vagt", "Tilføjes til listen og beregninger", True))
        self.visual_layout.addLayout(rows)

    def _visual_payments(self):
        self._visual_title("Lønsedler samler afsluttede perioder")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        rows.addWidget(self._mini_row("April 2026", "Netto 8.240 kr. | Total 8.240 kr.", True))
        rows.addWidget(self._mini_row("Marts 2026", "6 vagter | 42 t. | 90 min. pause"))
        rows.addWidget(self._mini_row("Detaljer", "Betalte timer, pause, skat og total"))
        self.visual_layout.addLayout(rows)

    def _visual_statistics(self):
        self._visual_title("Statistik hjælper dig med at opdage mønstre")
        bars = QGridLayout()
        bars.setSpacing(12)
        bars.addWidget(self._mini_bar("Timer pr. periode", 78, "#7c3aed"), 0, 0)
        bars.addWidget(self._mini_bar("Netto løn", 64, "#1f8a70"), 1, 0)
        bars.addWidget(self._mini_bar("Brutto løn", 86, "#2563eb"), 2, 0)
        bars.addWidget(self._mini_card("Nøgletal", "Gennemsnit", "#475569", "Timer, løn og bedste periode"), 0, 1, 3, 1)
        self.visual_layout.addLayout(bars)

    def _visual_budget(self):
        self._visual_title("Budget bruges som dine faste udgifter")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        rows.addWidget(self._mini_row("Husleje", "5.200 kr.", True))
        rows.addWidget(self._mini_row("Forsikring", "350 kr."))
        rows.addWidget(self._mini_row("Abonnementer", "199 kr."))
        rows.addWidget(self._mini_row("Rådighed", "Indkomst minus budgetposter"))
        self.visual_layout.addLayout(rows)

    def _visual_history(self):
        self._visual_title("Vagter samler tilføjelse og redigering")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        rows.addWidget(self._mini_row("Tilføj vagt", "Dato, timer, pause og timeløn", True))
        rows.addWidget(self._mini_row("03-05-2026", "7 t. | Pause 30 min. | 150 kr."))
        rows.addWidget(self._mini_row("Rediger valgt vagt", "Ret dato, timer eller timeløn"))
        rows.addWidget(self._mini_row("Slet markerede", "Brug checkbokse til flere vagter"))
        self.visual_layout.addLayout(rows)

    def _visual_calculator(self):
        self._visual_title("Lønberegneren gemmer ikke noget")
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self._mini_card("Bruttoløn", "3.000 kr.", "#2563eb"), 0, 0)
        grid.addWidget(self._mini_card("Timer + timeløn", "20 t. x 150", "#7c3aed"), 0, 1)
        grid.addWidget(self._mini_card("Netto", "1.795 kr.", "#1f8a70", "Beregnet ud fra dine satser"), 1, 0, 1, 2)
        self.visual_layout.addLayout(grid)

    def _visual_settings(self):
        self._visual_title("Indstillinger styrer beregningerne")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        rows.addWidget(self._mini_row("Skat og fradrag", "Bruges til netto løn"))
        rows.addWidget(self._mini_row("Anden indkomst", "Medregnes kun hvis beløbet er over 0"))
        rows.addWidget(self._mini_row("Standard timeløn", "Forudfylder Tilføj vagt"))
        rows.addWidget(self._mini_row("Lønperiode", "Bestemmer Overblik og estimater", True))
        self.visual_layout.addLayout(rows)

    def _visual_setup(self):
        pass

    def _visual_done(self):
        self._visual_title("Klar til første vagt")
        rows = QVBoxLayout()
        rows.setSpacing(7)
        rows.addWidget(self._mini_row("Start", "Gå til Vagter og gem din første vagt", True))
        rows.addWidget(self._mini_row("Budget", "Tilføj faste udgifter når du har dem"))
        rows.addWidget(self._mini_row("Genstart tutorial", "Findes altid under Indstillinger"))
        self.visual_layout.addLayout(rows)

    def _field_number(self, field, default, label, allow_zero=True):
        if not field.text().strip():
            return default
        return parse_positive_number(field, label, allow_zero=allow_zero)

    def _field_int(self, field, default, label):
        if not field.text().strip():
            return default
        return parse_int_field(field, label, 1, 31)

    def _save_setup_step(self):
        try:
            tax_value = self._field_number(self.setup_tax, 40, "Skatteprocent", allow_zero=True)
            am_value = float(self.window.settings.get("am bidrag", 0.08))
            new_settings = dict(self.window.settings) if isinstance(self.window.settings, dict) else {}
            new_settings.update(
                {
                    "skat": tax_value / 100 if tax_value > 1 else tax_value,
                    "fradrag": self._field_number(self.setup_fradrag, 0, "Fradrag", allow_zero=True),
                    "am bidrag": am_value,
                    "anden indkomst netto": self._field_number(self.setup_other_income, 0, "Anden indkomst", allow_zero=True),
                    "ønsket rådighedsbeløb": self._field_number(
                        self.setup_goal,
                        2000,
                        "Ønsket rådighedsbeløb",
                        allow_zero=True,
                    ),
                    "standard timeløn": self._field_number(self.setup_rate, 150, "Timeløn", allow_zero=False),
                    "løn start": self._field_int(self.setup_start, 15, "Lønperiode start"),
                    "løn slut": self._field_int(self.setup_end, 14, "Lønperiode slut"),
                }
            )
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldige oplysninger", str(error))
            return False

        ft.save_settings(new_settings)
        self.window.refresh_all()
        return True

    def _complete_tutorial(self):
        new_settings = dict(self.window.settings) if isinstance(self.window.settings, dict) else {}
        new_settings[ft.TUTORIAL_DONE_KEY] = True
        ft.save_settings(new_settings)
        self.window.refresh_all()
        self.accept()

    def _next(self):
        step = self._current_step()
        if step["key"] == "done":
            self._complete_tutorial()
            return
        if step["key"] == "setup" and not self._save_setup_step():
            return
        self.step_index += 1
        self._show_step()

    def _back(self):
        if self.step_index <= 0:
            return
        self.step_index -= 1
        self._show_step()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        root = QWidget()
        root.setObjectName("Content")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar.setMinimumWidth(BASE_SIDEBAR_WIDTH)
        self.sidebar = sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 18)
        sidebar_layout.setSpacing(8)
        layout.addWidget(sidebar)

        brand_panel = QFrame()
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

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self._add_page(sidebar_layout, "Overblik", DashboardPage(self), primary=True)
        self._add_page(sidebar_layout, "Vagter", HistoryPage(self))
        self._add_page(sidebar_layout, "Budget", BudgetPage(self))
        self._add_page(sidebar_layout, "Lønsedler", PaymentsPage(self))
        self._add_page(sidebar_layout, "Statistik", StatisticsPage(self))
        self._add_page(sidebar_layout, "Lønberegner", CalculatorPage(self))

        sidebar_layout.addStretch()
        self._add_footer_page(sidebar_layout, "Indstillinger", SettingsPage(self))

        self.tutorial_overlay = QWidget(root)
        self.tutorial_overlay.setStyleSheet("background: rgba(15, 23, 42, 150);")
        self.tutorial_overlay.hide()
        self._tutorial_dialog = None

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)
        self._update_sidebar_width()
        center_on_primary_screen(self)
        self.refresh_all()
        QTimer.singleShot(250, self._maybe_start_tutorial)

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

        nav_width = nav_text_width + self._ui_px(28)
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

    def _add_page(self, sidebar_layout, label, page, primary=False):
        index = len(self.pages)
        button = QPushButton(label)
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
        button = QPushButton(label)
        button.setObjectName("SecondaryButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, page_index=index: self.go_to_page(page_index))
        self.button_group.addButton(button)
        self.nav_buttons.append(button)
        sidebar_layout.addWidget(button)
        self.pages.append(page)
        self.stack.addWidget(page)

    def refresh_all(self):
        self.data = ft.load_data()
        self.settings = ft.load_settings()
        for page in self.pages:
            page.refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_sidebar_width()
        self._position_tutorial_overlay()

    def closeEvent(self, event):
        try:
            settings = dict(ft.load_settings())
            settings[WINDOW_WIDTH_SETTINGS_KEY] = self.width()
            settings[WINDOW_HEIGHT_SETTINGS_KEY] = self.height()
            ft.save_settings(settings)
        except (OSError, ValueError, TypeError):
            pass
        super().closeEvent(event)

    def _position_tutorial_overlay(self):
        if hasattr(self, "tutorial_overlay"):
            self.tutorial_overlay.setGeometry(self.stack.geometry())

    def go_to_page(self, index):
        if index < 0 or index >= len(self.pages):
            return
        self.stack.setCurrentIndex(index)
        self.nav_buttons[index].setChecked(True)
        if self._tutorial_dialog is not None:
            self.nav_buttons[index].raise_()

    def _maybe_start_tutorial(self):
        self.refresh_all()
        if not ft.is_tutorial_completed(self.settings):
            self.start_tutorial(force=False)

    def start_tutorial(self, force=False):
        if self._tutorial_dialog is not None:
            self._tutorial_dialog.raise_()
            self._tutorial_dialog.activateWindow()
            return
        self._position_tutorial_overlay()
        self.tutorial_overlay.show()
        self.tutorial_overlay.raise_()
        self._tutorial_dialog = TutorialDialog(self, force=force)
        self._tutorial_dialog.finished.connect(self._finish_tutorial_dialog)
        self._tutorial_dialog.open()
        self._tutorial_dialog.raise_()

    def _finish_tutorial_dialog(self):
        self.tutorial_overlay.hide()
        self._tutorial_dialog = None
        self.refresh_all()


def run():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(app_icon())
    app.setStyleSheet(APP_STYLE)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run())

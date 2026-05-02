import json
import os
import sys
from datetime import date, datetime, timedelta

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
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


APP_NAME = "Lønix"
REQUIRED_KEYS = ["skat", "fradrag", "am bidrag", "su", "boligstøtte", "løn start", "løn slut"]

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
QLabel#Brand {
    color: #ffffff;
    font-size: 23pt;
    font-weight: 800;
}
QLabel#BrandSub {
    color: #aeb7c1;
    font-size: 9pt;
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
QFrame#Card, QGroupBox#Panel {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 8px;
}
QGroupBox#Panel {
    margin-top: 18px;
    padding: 16px 14px 14px 14px;
    font-weight: 700;
}
QGroupBox#Panel::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #111827;
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
QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 24px;
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
QScrollArea {
    background: transparent;
    border: 0;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QProgressBar {
    background: #e7ecef;
    border: 0;
    border-radius: 7px;
    height: 13px;
    text-align: center;
    color: #1f2933;
}
QProgressBar::chunk {
    background: #1f8a70;
    border-radius: 7px;
}
QTabWidget::pane {
    border: 0;
}
QTabBar::tab {
    background: #e7ecef;
    border-radius: 7px;
    padding: 9px 13px;
    margin-right: 6px;
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


def ensure_storage():
    if not os.path.exists("data"):
        os.mkdir("data")
    ft.load_data()
    ft.load_settings()


def has_required_settings(settings):
    return isinstance(settings, dict) and all(key in settings for key in REQUIRED_KEYS)


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


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{format_number(value * 100)}%"


def format_date(value):
    if value is None:
        return "N/A"
    return value.strftime("%d-%m-%Y")


def parse_number_text(value):
    cleaned = value.strip().lower()
    for token in ["kr.", "kr", "t.", "timer", "time", "%"]:
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.replace(" ", "").replace(",", ".")
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


def make_text_input(text="", placeholder=""):
    field = QLineEdit()
    field.setText(str(text))
    field.setPlaceholderText(placeholder)
    return field


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
        timer = float(info.get("timer", 0))
        timeløn = float(info.get("timeløn", 0))
        rows.append(
            {
                "dato": dato,
                "timer": timer,
                "timeløn": timeløn,
                "brutto": timer * timeløn,
            }
        )
    return sorted(rows, key=lambda row: row["dato"], reverse=True)


def save_entry_rows(rows):
    ensure_storage()
    clean_rows = sorted(rows, key=lambda row: row["dato"])
    payload = [
        {
            date_to_key(row["dato"]): {
                "timer": float(row["timer"]),
                "timeløn": float(row["timeløn"]),
            }
        }
        for row in clean_rows
    ]
    with open("data/løn.txt", "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=4)


def upsert_entry(entry_date, hours, rate, original_date=None):
    rows = entry_rows(ft.load_data())
    target_key = original_date or entry_date
    rows = [row for row in rows if row["dato"] != target_key]
    rows.append({"dato": entry_date, "timer": float(hours), "timeløn": float(rate), "brutto": float(hours) * float(rate)})
    save_entry_rows(rows)


def delete_entry(entry_date):
    rows = [row for row in entry_rows(ft.load_data()) if row["dato"] != entry_date]
    save_entry_rows(rows)


def last_rate(data):
    rows = entry_rows(data)
    if not rows:
        return 150.0
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
    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
    item.setTextAlignment(align)
    return item


def setup_table(table, headers):
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


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
    panel = QGroupBox(title)
    panel.setObjectName("Panel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(16, 20, 16, 16)
    layout.setSpacing(10)
    return panel, layout


def make_message(text):
    label = QLabel(text)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #66717e; padding: 26px;")
    return label


class MetricCard(QFrame):
    def __init__(self, title, value="-", subtitle="", accent="#1f8a70"):
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(118)
        self.accent = accent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setWordWrap(True)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("MetricSub")
        self.subtitle_label.setWordWrap(True)

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
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(28, 24, 28, 24)
        self.root.setSpacing(18)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)

        self.root.addWidget(title_label)
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
            "Overblik",
            "Nuværende lønperiode, registreret løn, prognose og de seneste vagter.",
        )

        grid = QGridLayout()
        grid.setSpacing(14)
        self.root.addLayout(grid)

        self.net_card = MetricCard("Netto løn nu", accent="#1f8a70")
        self.estimate_card = MetricCard("Estimeret total", accent="#d97706")
        self.available_card = MetricCard("Til rådighed", accent="#2563eb")
        self.hours_card = MetricCard("Timer", accent="#7c3aed")
        self.gross_card = MetricCard("Brutto løn", accent="#0f766e")
        self.period_card = MetricCard("Lønperiode", accent="#475569")

        cards = [
            self.net_card,
            self.estimate_card,
            self.available_card,
            self.hours_card,
            self.gross_card,
            self.period_card,
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 3, index % 3)

        progress_panel, progress_layout = make_panel("Periodens forløb")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress_detail = QLabel()
        self.progress_detail.setObjectName("PageSubtitle")
        goal_row = QHBoxLayout()
        goal_row.setSpacing(10)
        self.goal_lamp = QLabel()
        self.goal_lamp.setFixedSize(16, 16)
        self.goal_lamp.setStyleSheet("background: #94a3b8; border-radius: 8px;")
        self.goal_status = QLabel("Rådighedsmål ikke beregnet")
        self.goal_status.setObjectName("PageSubtitle")
        goal_row.addWidget(self.goal_lamp)
        goal_row.addWidget(self.goal_status, 1)
        progress_layout.addWidget(self.progress)
        progress_layout.addWidget(self.progress_detail)
        progress_layout.addLayout(goal_row)
        self.root.addWidget(progress_panel)

        lower = QHBoxLayout()
        lower.setSpacing(14)
        self.root.addLayout(lower, 1)

        breakdown_panel, breakdown_layout = make_panel("Lønberegning")
        self.breakdown_table = QTableWidget()
        setup_table(self.breakdown_table, ["Post", "Beløb"])
        breakdown_layout.addWidget(self.breakdown_table)
        lower.addWidget(breakdown_panel, 1)

        recent_panel, recent_layout = make_panel("Seneste vagter")
        self.recent_table = QTableWidget()
        setup_table(self.recent_table, ["Dato", "Timer", "Timeløn", "Brutto"])
        recent_layout.addWidget(self.recent_table)
        lower.addWidget(recent_panel, 1)

    def refresh(self):
        if not has_required_settings(self.settings):
            self._show_missing_settings()
            return

        summary = current_period_summary(self.data, self.settings)
        forecast = ft.calculate_salary_forecast(self.data, self.settings)
        su = self.settings.get("su", 0)
        bolig = self.settings.get("boligstøtte", 0)
        budget_expenses = ft.calculate_budget_expenses(self.settings)

        total_now = summary["netto"] + su + bolig
        available_now = ft.calculate_disposable_income(total_now, self.settings)
        estimated_total = forecast.get("estimated_total_with_support") if forecast else None
        estimated_available = forecast.get("estimated_disposable_income") if forecast else None
        disposable_goal = ft.get_disposable_income_goal(self.settings)

        self.net_card.set_values(format_money(summary["netto"]), f"Total inkl. SU og boligstøtte: {format_money(total_now)}")
        self.estimate_card.set_values(format_money(estimated_total), f"Estimeret rådighed: {format_money(estimated_available)}")
        self.available_card.set_values(format_money(available_now), f"Budgetterede faste udgifter: {format_money(budget_expenses)}")
        self.hours_card.set_values(f"{format_number(summary['timer'])} t.", f"{len(summary['rows'])} vagter i perioden")
        self.gross_card.set_values(format_money(summary["brutto"]), f"Skat: {format_percent(self.settings.get('skat'))}")
        self.period_card.set_values(
            f"d. {self.settings.get('løn start')} - d. {self.settings.get('løn slut')}",
            format_period(summary),
        )

        if forecast:
            percent = int(round(forecast.get("progress_ratio", 0) * 100))
            self.progress.setValue(max(0, min(percent, 100)))
            self.progress_detail.setText(
                f"{forecast['elapsed_days']} af {forecast['total_days']} dage er gået. "
                f"{forecast['remaining_days']} dage tilbage. "
                f"Estimeret netto løn: {format_money(forecast.get('estimated_netto'))}."
            )
        else:
            self.progress.setValue(0)
            self.progress_detail.setText("Der er ikke nok data til en prognose endnu.")

        self._update_goal_lamp(available_now, estimated_available, disposable_goal)
        self._fill_breakdown(summary["breakdown"])
        self._fill_recent()

    def _show_missing_settings(self):
        for card in [self.net_card, self.estimate_card, self.available_card, self.hours_card, self.gross_card, self.period_card]:
            card.set_values("N/A", "Indstillinger mangler")
        self.progress.setValue(0)
        self.progress_detail.setText("Udfyld indstillingerne før beregninger kan vises.")
        self.goal_lamp.setStyleSheet("background: #94a3b8; border-radius: 8px;")
        self.goal_status.setText("Rådighedsmål ikke beregnet")
        self.breakdown_table.setRowCount(0)
        self.recent_table.setRowCount(0)

    def _update_goal_lamp(self, available_now, estimated_available, disposable_goal):
        if disposable_goal <= 0:
            color = "#94a3b8"
            text = "Intet ønsket rådighedsbeløb er sat."
        elif available_now >= disposable_goal:
            color = "#16a34a"
            text = f"Målet er nået: {format_money(available_now)} af {format_money(disposable_goal)}"
        elif estimated_available is not None and estimated_available >= disposable_goal:
            color = "#f59e0b"
            text = f"Estimatet når målet: {format_money(estimated_available)} af {format_money(disposable_goal)}"
        else:
            color = "#dc2626"
            text = f"Under målet: {format_money(estimated_available)} estimeret af {format_money(disposable_goal)}"
        self.goal_lamp.setStyleSheet(f"background: {color}; border-radius: 8px;")
        self.goal_status.setText(text)

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

    def _fill_recent(self):
        rows = entry_rows(self.data)[:8]
        self.recent_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.recent_table.setItem(row_index, 0, table_item(format_date(row["dato"])))
            self.recent_table.setItem(row_index, 1, table_item(format_number(row["timer"]), Qt.AlignRight | Qt.AlignVCenter))
            self.recent_table.setItem(row_index, 2, table_item(format_money(row["timeløn"]), Qt.AlignRight | Qt.AlignVCenter))
            self.recent_table.setItem(row_index, 3, table_item(format_money(row["brutto"]), Qt.AlignRight | Qt.AlignVCenter))


class EntryPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Indberet",
            "Registrer en vagt med direkte timetal eller start- og sluttidspunkt.",
        )

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        form_panel, form_layout = make_panel("Ny indberetning")
        content.addWidget(form_panel, 0)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setVerticalSpacing(12)
        form_layout.addLayout(form)
        self.entry_form = form

        self.date_edit = make_text_input(placeholder="dd-mm-åååå")
        self.date_edit.textChanged.connect(self._update_summary)
        form.addRow("Dato", self.date_edit)

        self.mode_combo = QComboBox()
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

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("color: #42505f; padding-top: 8px;")
        form_layout.addWidget(self.summary_label)

        button_row = QHBoxLayout()
        form_layout.addLayout(button_row)
        self.save_button = QPushButton("Gem indberetning")
        self.save_button.clicked.connect(self._save_entry)
        button_row.addWidget(self.save_button)
        reset_button = QPushButton("Nulstil")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self._set_defaults)
        button_row.addWidget(reset_button)

        history_panel, history_layout = make_panel("Alle registreringer")
        content.addWidget(history_panel, 1)
        self.history_table = QTableWidget()
        setup_table(self.history_table, ["Dato", "Timer", "Timeløn", "Brutto"])
        history_layout.addWidget(self.history_table)

        self._set_defaults()

    def refresh(self):
        set_field_number(self.rate_field, last_rate(self.data))
        self._fill_history()
        self._update_summary()

    def _set_defaults(self):
        entry_date = default_entry_date()
        self.date_edit.setText(format_date(entry_date))
        self.mode_combo.setCurrentIndex(0)
        self.hours_field.setText("4")
        self.start_field.setText("14:00")
        self.end_field.setText("18:00")
        set_field_number(self.rate_field, last_rate(self.window.data))
        self._update_mode()

    def _update_mode(self):
        use_time = self.mode_combo.currentIndex() == 0
        set_form_row_visible(self.entry_form, self.hours_field, not use_time)
        set_form_row_visible(self.entry_form, self.start_field, use_time)
        set_form_row_visible(self.entry_form, self.end_field, use_time)
        self._update_summary()

    def _selected_hours(self):
        if self.mode_combo.currentIndex() == 1:
            return parse_positive_number(self.hours_field, "Timer")
        return calculate_hours_from_times(self.start_field.text(), self.end_field.text())

    def _update_summary(self):
        try:
            hours = self._selected_hours()
            rate = parse_positive_number(self.rate_field, "Timeløn")
        except ValueError:
            self.summary_label.setText("Udfyld timer og timeløn for at se beregningen.")
            return

        brutto = hours * rate
        netto = ft.calculate_salary_breakdown_from_brutto(brutto)["netto"] if has_required_settings(self.settings) else None
        self.summary_label.setText(
            f"Vagt: {format_number(hours)} timer á {format_money(rate)}\n"
            f"Brutto: {format_money(brutto)}  |  Netto: {format_money(netto)}"
        )

    def _save_entry(self):
        try:
            selected_date = parse_date_text(self.date_edit.text())
            hours = self._selected_hours()
            rate = parse_positive_number(self.rate_field, "Timeløn")
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig indberetning", str(error))
            return

        key = date_to_key(selected_date)
        exists = any(key in entry for entry in self.data)
        if exists:
            answer = QMessageBox.question(
                self,
                "Overskriv indberetning",
                f"Der findes allerede en indberetning for {key}. Vil du overskrive den?",
            )
            if answer != QMessageBox.Yes:
                return

        upsert_entry(selected_date, hours, rate)
        QMessageBox.information(
            self,
            "Indberetning gemt",
            f"{key} blev gemt med {format_number(hours)} timer á {format_money(rate)}.",
        )
        self.window.refresh_all()

    def _fill_history(self):
        rows = entry_rows(self.data)
        self.history_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.history_table.setItem(row_index, 0, table_item(format_date(row["dato"])))
            self.history_table.setItem(row_index, 1, table_item(format_number(row["timer"]), Qt.AlignRight | Qt.AlignVCenter))
            self.history_table.setItem(row_index, 2, table_item(format_money(row["timeløn"]), Qt.AlignRight | Qt.AlignVCenter))
            self.history_table.setItem(row_index, 3, table_item(format_money(row["brutto"]), Qt.AlignRight | Qt.AlignVCenter))


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
        content.addWidget(input_panel, 0)

        self.tabs = QTabWidget()
        self.tabs.setUsesScrollButtons(False)
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
            set_field_number(self.calc_rate_field, last_rate(self.data))
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
            "Udbetalinger",
            "Afsluttede lønperioder med løn, anden indkomst og total udbetaling.",
        )

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        table_panel, table_layout = make_panel("Afsluttede lønperioder")
        content.addWidget(table_panel, 2)
        self.payments_table = QTableWidget()
        setup_table(self.payments_table, ["Periode", "Timer", "Brutto", "Netto", "Total"])
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
        su = self.settings.get("su", 0) if has_required_settings(self.settings) else 0
        bolig = self.settings.get("boligstøtte", 0) if has_required_settings(self.settings) else 0

        for row_index, period in enumerate(self.payments):
            total = period["netto"] + su + bolig
            self.payments_table.setItem(row_index, 0, table_item(f"{month_title(period)}\n{format_period(period)}"))
            self.payments_table.setItem(row_index, 1, table_item(format_number(period["timer"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 2, table_item(format_money(period["brutto"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 3, table_item(format_money(period["netto"]), Qt.AlignRight | Qt.AlignVCenter))
            self.payments_table.setItem(row_index, 4, table_item(format_money(total), Qt.AlignRight | Qt.AlignVCenter))

        if self.payments:
            self.payments_table.resizeRowsToContents()
            self.payments_table.selectRow(0)
        else:
            self.detail_title.setText("Ingen afsluttede udbetalinger")
            self.detail_table.setRowCount(0)

    def _update_detail(self):
        selected = self.payments_table.currentRow()
        if selected < 0 or selected >= len(self.payments):
            return
        period = self.payments[selected]
        su = self.settings.get("su", 0)
        bolig = self.settings.get("boligstøtte", 0)
        total = period["netto"] + su + bolig
        avg_rate = period["brutto"] / period["timer"] if period["timer"] else None
        self.detail_title.setText(month_title(period))
        rows = [
            ("Periode", format_period(period)),
            ("Vagter", str(period["vagter"])),
            ("Timer", f"{format_number(period['timer'])} t."),
            ("Gennemsnitlig timeløn", format_money(avg_rate)),
            ("Brutto løn", format_money(period["brutto"])),
            ("AM-bidrag", f"-{format_money(period['am_bidrag'])}"),
            ("Skat", f"-{format_money(period['skat'])}"),
            ("Netto løn", format_money(period["netto"])),
            ("SU", format_money(su)),
            ("Boligstøtte", format_money(bolig)),
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
            "Nøgletal, rekorder, udvikling, arbejdsmønster og prognose.",
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(16)
        self.scroll.setWidget(self.body)
        self.root.addWidget(self.scroll, 1)

    def refresh(self):
        clear_layout(self.body_layout)
        if not self.data:
            self.body_layout.addWidget(make_message("Der er ingen løndata endnu. Opret en indberetning først."))
            self.body_layout.addStretch()
            return
        if not has_required_settings(self.settings):
            self.body_layout.addWidget(make_message("Indstillingerne mangler nøgler, så statistik kan ikke beregnes."))
            self.body_layout.addStretch()
            return

        try:
            stats = statistik._build_statistics(self.data, self.settings)
        except Exception as error:
            self.body_layout.addWidget(make_message(f"Kunne ikke beregne statistik:\n{error}"))
            self.body_layout.addStretch()
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
            format_money(shift["brutto"]),
            format_money(shift["netto"]),
        ]

    def _period_row(self, label, period):
        if period is None:
            return [label, "N/A", "N/A", "N/A", "N/A"]
        return [
            label,
            f"{month_title(period)} ({format_date(period['periode_start'])} - {format_date(period['periode_slut'])})",
            format_number(period["timer"]),
            format_money(period["brutto"]),
            format_money(period["netto"]),
        ]

    def _add_records(self, stats):
        self._add_table(
            "Rekorder",
            ["Kategori", "Dato", "Timer", "Før skat", "Efter skat"],
            [
                self._shift_row("Længste vagt", stats["records"]["longest"]),
                self._shift_row("Korteste vagt", stats["records"]["shortest"]),
                self._shift_row("Højeste dag", stats["records"]["highest_paid"]),
            ],
        )

    def _add_periods(self, stats):
        self._add_table(
            "Lønperioder",
            ["Måling", "Periode", "Timer", "Før skat", "Efter skat"],
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
                ["Estimeret total inkl. støtte", format_money(forecast["estimated_total_with_support"])],
                ["Budgetterede faste udgifter", format_money(forecast["budget_expenses"])],
                ["Estimeret rådighedsbeløb", format_money(forecast["estimated_disposable_income"])],
            ]
        self._add_table("Prognose", ["Måling", "Værdi"], rows)


class ChartsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Grafer",
            "Visuel udvikling for timer, brutto og netto pr. lønperiode.",
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(16)
        self.scroll.setWidget(self.body)
        self.root.addWidget(self.scroll, 1)

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
            self.body_layout.addWidget(panel)
        self.body_layout.addStretch()

    def refresh(self):
        periods, _ = build_periods(self.data, self.settings)
        labels = [month_title(period) for period in periods]
        if not periods:
            labels = []

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


class HistoryPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Historik",
            "Alle registrerede vagter sorteret med nyeste først. Vælg en række for at redigere eller slette.",
        )
        self.rows = []
        self.selected_original_date = None

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
        self.table = QTableWidget()
        setup_table(self.table, ["Dato", "Timer", "Timeløn", "Brutto"])
        self.table.itemSelectionChanged.connect(self._load_selected_row)
        layout.addWidget(self.table)

        edit_panel, edit_layout = make_panel("Rediger valgt vagt")
        content.addWidget(edit_panel, 1)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        edit_layout.addLayout(form)

        self.edit_date_field = make_text_input(placeholder="dd-mm-åååå")
        self.edit_hours_field = make_text_input(placeholder="fx 4,5")
        self.edit_rate_field = make_text_input(placeholder="fx 150")
        self.edit_date_field.textChanged.connect(self._update_edit_preview)
        self.edit_hours_field.textChanged.connect(self._update_edit_preview)
        self.edit_rate_field.textChanged.connect(self._update_edit_preview)
        form.addRow("Dato", self.edit_date_field)
        form.addRow("Timer", self.edit_hours_field)
        form.addRow("Timeløn", self.edit_rate_field)

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

    def refresh(self):
        self.rows = entry_rows(self.data)
        self.total_card.set_values(str(len(self.rows)), "Gemte vagter")
        self.hours_card.set_values(f"{format_number(sum(row['timer'] for row in self.rows))} t.", "Alle registreringer")
        self.gross_card.set_values(format_money(sum(row["brutto"] for row in self.rows)), "Før skat")
        self.table.setRowCount(len(self.rows))
        for row_index, row in enumerate(self.rows):
            self.table.setItem(row_index, 0, table_item(format_date(row["dato"])))
            self.table.setItem(row_index, 1, table_item(format_number(row["timer"]), Qt.AlignRight | Qt.AlignVCenter))
            self.table.setItem(row_index, 2, table_item(format_money(row["timeløn"]), Qt.AlignRight | Qt.AlignVCenter))
            self.table.setItem(row_index, 3, table_item(format_money(row["brutto"]), Qt.AlignRight | Qt.AlignVCenter))
        self.table.resizeRowsToContents()
        if self.rows:
            self.table.selectRow(0)
        else:
            self._clear_edit_fields()

    def _load_selected_row(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.rows):
            self._clear_edit_fields()
            return

        row = self.rows[selected]
        self.selected_original_date = row["dato"]
        self.edit_date_field.setText(format_date(row["dato"]))
        set_field_number(self.edit_hours_field, row["timer"])
        set_field_number(self.edit_rate_field, row["timeløn"])
        self._update_edit_preview()

    def _clear_edit_fields(self):
        self.selected_original_date = None
        self.edit_date_field.clear()
        self.edit_hours_field.clear()
        self.edit_rate_field.clear()
        self.edit_preview.setText("Vælg en vagt i tabellen.")

    def _update_edit_preview(self):
        if self.selected_original_date is None:
            return
        try:
            hours = parse_positive_number(self.edit_hours_field, "Timer")
            rate = parse_positive_number(self.edit_rate_field, "Timeløn")
            selected_date = parse_date_text(self.edit_date_field.text())
        except ValueError:
            self.edit_preview.setText("Udfyld gyldig dato, timer og timeløn.")
            return

        brutto = hours * rate
        self.edit_preview.setText(
            f"{format_date(selected_date)}: {format_number(hours)} timer á {format_money(rate)}\n"
            f"Brutto: {format_money(brutto)}"
        )

    def _save_selected_row(self):
        if self.selected_original_date is None:
            QMessageBox.information(self, "Ingen vagt valgt", "Vælg først en vagt i historiktabellen.")
            return
        try:
            selected_date = parse_date_text(self.edit_date_field.text())
            hours = parse_positive_number(self.edit_hours_field, "Timer")
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
                f"Der findes allerede en anden indberetning for {format_date(selected_date)}. Vil du overskrive den?",
            )
            if answer != QMessageBox.Yes:
                return

        upsert_entry(selected_date, hours, rate, self.selected_original_date)
        self.window.refresh_all()

    def _delete_selected_row(self):
        if self.selected_original_date is None:
            QMessageBox.information(self, "Ingen vagt valgt", "Vælg først en vagt i historiktabellen.")
            return

        answer = QMessageBox.question(
            self,
            "Slet indberetning",
            f"Vil du slette indberetningen for {format_date(self.selected_original_date)}?",
        )
        if answer != QMessageBox.Yes:
            return
        delete_entry(self.selected_original_date)
        self.window.refresh_all()


class BudgetPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Budget",
            "Planlæg faste udgifter i kategorier og sæt ønsket rådighedsbeløb for perioden.",
        )
        self.categories = []

        cards = QHBoxLayout()
        cards.setSpacing(14)
        self.root.addLayout(cards)
        self.available_card = MetricCard("Estimeret indkomst", accent="#1f8a70")
        self.budget_card = MetricCard("Faste udgifter", accent="#2563eb")
        self.remaining_card = MetricCard("Rådighedsbeløb", accent="#d97706")
        self.goal_card = MetricCard("Ønsket rådighedsbeløb", accent="#475569")
        cards.addWidget(self.available_card)
        cards.addWidget(self.budget_card)
        cards.addWidget(self.remaining_card)
        cards.addWidget(self.goal_card)

        content = QHBoxLayout()
        content.setSpacing(16)
        self.root.addLayout(content, 1)

        table_panel, table_layout = make_panel("Kategorier")
        content.addWidget(table_panel, 2)
        self.table = QTableWidget()
        setup_table(self.table, ["Kategori", "Beløb"])
        self.table.itemSelectionChanged.connect(self._load_selected_category)
        table_layout.addWidget(self.table)

        form_panel, form_layout = make_panel("Kategori og rådighedsmål")
        content.addWidget(form_panel, 1)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form_layout.addLayout(form)

        self.name_field = make_text_input(placeholder="fx Mad")
        self.amount_field = make_text_input(placeholder="fx 2500")
        self.disposable_goal_field = make_text_input(placeholder="fx 2500")
        form.addRow("Kategori", self.name_field)
        form.addRow("Beløb", self.amount_field)
        form.addRow("Ønsket rådighedsbeløb", self.disposable_goal_field)

        button_row = QHBoxLayout()
        form_layout.addLayout(button_row)
        self.save_button = QPushButton("Gem kategori")
        self.save_button.clicked.connect(self._save_category)
        button_row.addWidget(self.save_button)
        self.new_button = QPushButton("Ny")
        self.new_button.setObjectName("SecondaryButton")
        self.new_button.clicked.connect(self._clear_form)
        button_row.addWidget(self.new_button)

        delete_button = QPushButton("Slet kategori")
        delete_button.setObjectName("SecondaryButton")
        delete_button.clicked.connect(self._delete_category)
        form_layout.addWidget(delete_button)

        goal_button = QPushButton("Gem ønsket rådighed")
        goal_button.setObjectName("SecondaryButton")
        goal_button.clicked.connect(self._save_disposable_goal)
        form_layout.addWidget(goal_button)
        form_layout.addStretch()

        self.selected_index = None

    def refresh(self):
        self.categories = self._categories_from_settings()
        set_field_number(self.disposable_goal_field, ft.get_disposable_income_goal(self.settings))
        self._fill_table()
        self._update_cards()
        if self.categories:
            self.table.selectRow(0)
        else:
            self._clear_form()

    def _categories_from_settings(self):
        return ft.get_budget_categories(self.settings)

    def _forecast_income(self):
        if not has_required_settings(self.settings):
            return None
        forecast = ft.calculate_salary_forecast(self.data, self.settings)
        if forecast and forecast.get("estimated_total_with_support") is not None:
            return forecast["estimated_total_with_support"]
        else:
            summary = current_period_summary(self.data, self.settings)
            return summary["netto"] + self.settings.get("su", 0) + self.settings.get("boligstøtte", 0)

    def _budget_total(self):
        return sum(item["beløb"] for item in self.categories)

    def _update_cards(self):
        income = self._forecast_income()
        budget_total = ft.calculate_budget_expenses(self.settings)
        remaining = income - budget_total if income is not None else None
        disposable_goal = ft.get_disposable_income_goal(self.settings)

        self.available_card.set_values(format_money(income), "Løn, SU og boligstøtte")
        self.budget_card.set_values(format_money(budget_total), f"{len(self.categories)} kategorier")
        self.remaining_card.set_values(format_money(remaining), "Estimeret indkomst minus faste udgifter")
        if remaining is None:
            self.goal_card.set_values(format_money(disposable_goal), "Mangler indkomstdata")
        else:
            difference = remaining - disposable_goal
            self.goal_card.set_values(format_money(disposable_goal), f"Forskel: {signed_money(difference)}")

    def _fill_table(self):
        self.table.setRowCount(len(self.categories))
        for row_index, item in enumerate(self.categories):
            self.table.setItem(row_index, 0, table_item(item["navn"]))
            self.table.setItem(row_index, 1, table_item(format_money(item["beløb"]), Qt.AlignRight | Qt.AlignVCenter))
        self.table.resizeRowsToContents()

    def _load_selected_category(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.categories):
            return
        self.selected_index = selected
        item = self.categories[selected]
        self.name_field.setText(item["navn"])
        set_field_number(self.amount_field, item["beløb"])

    def _clear_form(self):
        self.selected_index = None
        self.name_field.clear()
        self.amount_field.clear()

    def _settings_with_budget(self):
        new_settings = dict(self.settings) if isinstance(self.settings, dict) else {}
        new_settings["budget kategorier"] = self.categories
        try:
            new_settings["ønsket rådighedsbeløb"] = parse_positive_number(
                self.disposable_goal_field,
                "Ønsket rådighedsbeløb",
                allow_zero=True,
            )
        except ValueError:
            new_settings["ønsket rådighedsbeløb"] = ft.get_disposable_income_goal(self.settings)
        return new_settings

    def _save_category(self):
        name = self.name_field.text().strip()
        if not name:
            QMessageBox.warning(self, "Ugyldig kategori", "Kategori skal have et navn.")
            return
        try:
            amount = parse_positive_number(self.amount_field, "Beløb", allow_zero=True)
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldig kategori", str(error))
            return

        item = {"navn": name, "beløb": amount}
        if self.selected_index is None:
            self.categories.append(item)
        else:
            self.categories[self.selected_index] = item
        ft.save_settings(self._settings_with_budget())
        self.window.refresh_all()

    def _delete_category(self):
        if self.selected_index is None or self.selected_index >= len(self.categories):
            QMessageBox.information(self, "Ingen kategori valgt", "Vælg først en kategori.")
            return
        del self.categories[self.selected_index]
        ft.save_settings(self._settings_with_budget())
        self.window.refresh_all()

    def _save_disposable_goal(self):
        try:
            disposable_goal = parse_positive_number(self.disposable_goal_field, "Ønsket rådighedsbeløb", allow_zero=True)
        except ValueError as error:
            QMessageBox.warning(self, "Ugyldigt rådighedsbeløb", str(error))
            return
        new_settings = self._settings_with_budget()
        new_settings["ønsket rådighedsbeløb"] = disposable_goal
        ft.save_settings(new_settings)
        self.window.refresh_all()


class SettingsPage(BasePage):
    def __init__(self, window):
        super().__init__(
            window,
            "Indstillinger",
            "Tilpas skat, støtte og lønperiodens datoer. Faste udgifter styres på Budget-siden.",
        )

        panel, layout = make_panel("Økonomi og lønperiode")
        self.root.addWidget(panel)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        layout.addLayout(form)

        self.tax_field = make_text_input(placeholder="fx 49")
        self.fradrag_field = make_text_input(placeholder="fx 0")
        self.am_field = make_text_input(placeholder="fx 8")
        self.su_field = make_text_input(placeholder="fx 9539")
        self.housing_field = make_text_input(placeholder="fx 1203")
        self.start_day_field = make_text_input(placeholder="1-31")
        self.end_day_field = make_text_input(placeholder="1-31")

        form.addRow("Skat %", self.tax_field)
        form.addRow("Fradrag", self.fradrag_field)
        form.addRow("AM-bidrag %", self.am_field)
        form.addRow("SU", self.su_field)
        form.addRow("Boligstøtte", self.housing_field)
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
            "su": 9539,
            "boligstøtte": 1203,
            "løn start": 15,
            "løn slut": 14,
        }
        set_field_number(self.tax_field, float(settings.get("skat", 0)) * 100)
        set_field_number(self.fradrag_field, float(settings.get("fradrag", 0)))
        set_field_number(self.am_field, float(settings.get("am bidrag", 0)) * 100)
        set_field_number(self.su_field, float(settings.get("su", 0)))
        set_field_number(self.housing_field, float(settings.get("boligstøtte", 0)))
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
                    "su": parse_positive_number(self.su_field, "SU", allow_zero=True),
                    "boligstøtte": parse_positive_number(self.housing_field, "Boligstøtte", allow_zero=True),
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ensure_storage()
        self.data = []
        self.settings = {}
        self.pages = []
        self.nav_buttons = []

        self.setWindowTitle(APP_NAME)
        self.resize(1220, 780)
        self.setMinimumSize(980, 650)

        root = QWidget()
        root.setObjectName("Content")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(224)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 18)
        sidebar_layout.setSpacing(8)
        layout.addWidget(sidebar)

        brand = QLabel(APP_NAME)
        brand.setObjectName("Brand")
        brand_sub = QLabel("Løn, SU og overblik")
        brand_sub.setObjectName("BrandSub")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(brand_sub)
        sidebar_layout.addSpacing(18)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self._add_page(sidebar_layout, "Overblik", DashboardPage(self))
        self._add_page(sidebar_layout, "Indberet", EntryPage(self))
        self._add_page(sidebar_layout, "Lønberegner", CalculatorPage(self))
        self._add_page(sidebar_layout, "Udbetalinger", PaymentsPage(self))
        self._add_page(sidebar_layout, "Statistik", StatisticsPage(self))
        self._add_page(sidebar_layout, "Grafer", ChartsPage(self))
        self._add_page(sidebar_layout, "Budget", BudgetPage(self))
        self._add_page(sidebar_layout, "Historik", HistoryPage(self))
        self._add_page(sidebar_layout, "Indstillinger", SettingsPage(self))

        sidebar_layout.addStretch()
        refresh_button = QPushButton("Opdater")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.clicked.connect(self.refresh_all)
        sidebar_layout.addWidget(refresh_button)

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)
        self.refresh_all()

    def _add_page(self, sidebar_layout, label, page):
        index = len(self.pages)
        button = QPushButton(label)
        button.setObjectName("NavButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, page_index=index: self.stack.setCurrentIndex(page_index))
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


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run())

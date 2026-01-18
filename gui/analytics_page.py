import os
from datetime import date, timedelta

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal

import matplotlib
if os.environ.get("DISPLAY", "") == "":
    matplotlib.use("Agg")   # Headless (Colab, server)
else:
    matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.csv_utils import (
    get_all_student_attendance_rates,
    get_daily_attendance_counts,
    get_section_comparison,
    get_attendance_data
)


class MplCanvas(FigureCanvas):
    """Matplotlib canvas widget for embedding charts"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#FFFFFF')
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setStyleSheet("background: transparent;")


class AnalyticsPage(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation Bar
        nav_bar = self.create_nav_bar()
        main_layout.addWidget(nav_bar)

        # Content with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Filter Section
        filter_section = self.create_filter_section()
        content_layout.addWidget(filter_section)

        # Charts Grid
        charts_layout = QGridLayout()
        charts_layout.setSpacing(20)

        # Pie Chart - Overall Attendance
        self.pie_chart_container = self.create_chart_container("📊 Overall Attendance Rate")
        charts_layout.addWidget(self.pie_chart_container, 0, 0)

        # Bar Chart - Daily Trends
        self.bar_chart_container = self.create_chart_container("📈 Daily Attendance (Last 7 Days)")
        charts_layout.addWidget(self.bar_chart_container, 0, 1)

        # Section Comparison
        self.section_chart_container = self.create_chart_container("🏫 Section Comparison")
        charts_layout.addWidget(self.section_chart_container, 1, 0)

        # Student Rates
        self.student_chart_container = self.create_chart_container("👥 Student Attendance Rates")
        charts_layout.addWidget(self.student_chart_container, 1, 1)

        content_layout.addLayout(charts_layout)
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)

        self.setLayout(main_layout)

    def create_nav_bar(self):
        nav = QWidget()
        nav.setFixedHeight(70)
        nav.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                border-bottom: 2px solid rgba(0, 0, 0, 0.1);
            }
        """)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(30, 0, 30, 0)
        nav_layout.setSpacing(20)

        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4A90E2;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                color: #357ABD;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 8px;
            }
        """)
        back_btn.clicked.connect(self.go_back.emit)

        logo_label = QLabel("🎓")
        logo_label.setStyleSheet("font-size: 32px; background: transparent;")

        title_label = QLabel("Analytics Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(logo_label)
        nav_layout.addWidget(title_label)
        nav_layout.addStretch()

        credits_label = QLabel("By Ayesha Asif and Alina Asif")
        credits_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7F8C8D;
                background: transparent;
                padding: 8px 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-style: italic;
            }
        """)
        nav_layout.addWidget(credits_label)

        nav.setLayout(nav_layout)
        return nav

    def create_filter_section(self):
        section = QFrame()
        section.setStyleSheet("QFrame { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        section.setFixedHeight(80)

        layout = QHBoxLayout()
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(20)

        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        self.section_filter = QComboBox()
        self.section_filter.addItems(["All Sections", "BSCS 5A", "BSCS 5B"])
        self.section_filter.setStyleSheet("""
            QComboBox {
                background: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #4A90E2;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2C3E50;
                selection-background-color: #4A90E2;
                selection-color: white;
            }
        """)

        refresh_btn = QPushButton("🔄 Refresh Charts")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5BA0F2, stop:1 #4590CD);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_charts)

        layout.addWidget(filter_label)
        layout.addWidget(self.section_filter)
        layout.addStretch()
        layout.addWidget(refresh_btn)

        section.setLayout(layout)
        return section

    def create_chart_container(self, title):
        container = QFrame()
        container.setStyleSheet("QFrame { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        container.setMinimumHeight(350)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                padding-bottom: 10px;
                border-bottom: 2px solid rgba(0, 0, 0, 0.1);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(title_label)

        container.setLayout(layout)
        return container

    def refresh_charts(self):
        """Refresh all charts with current data"""
        section_filter = self.section_filter.currentText()
        section = None if section_filter == "All Sections" else section_filter

        self.update_pie_chart()
        self.update_bar_chart(section)
        self.update_section_chart()
        self.update_student_chart()

    def update_pie_chart(self):
        """Update the overall attendance pie chart"""
        layout = self.pie_chart_container.layout()

        # Remove old chart if exists
        for i in range(layout.count() - 1, 0, -1):
            item = layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        header, data = get_attendance_data()
        if not data:
            no_data = QLabel("No attendance data available")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("font-size: 14px; color: #95A5A6; background: transparent;")
            layout.addWidget(no_data)
            return

        total_present = 0
        total_absent = 0

        for row in data:
            if len(row) > 2:
                total_present += row[2:].count("P")
                total_absent += row[2:].count("A")

        if total_present + total_absent == 0:
            no_data = QLabel("No attendance data available")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("font-size: 14px; color: #95A5A6; background: transparent;")
            layout.addWidget(no_data)
            return

        canvas = MplCanvas(self, width=4, height=3, dpi=100)
        canvas.axes.pie(
            [total_present, total_absent],
            labels=['Present', 'Absent'],
            autopct='%1.1f%%',
            colors=['#27AE60', '#E74C3C'],
            explode=(0.05, 0),
            shadow=True,
            startangle=90
        )
        canvas.axes.set_title('')
        canvas.figure.tight_layout()

        layout.addWidget(canvas)

    def update_bar_chart(self, section=None):
        """Update the daily attendance bar chart"""
        layout = self.bar_chart_container.layout()

        # Remove old chart if exists
        for i in range(layout.count() - 1, 0, -1):
            item = layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        daily_data = get_daily_attendance_counts(7, section)

        if not daily_data:
            no_data = QLabel("No attendance data available")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("font-size: 14px; color: #95A5A6; background: transparent;")
            layout.addWidget(no_data)
            return

        dates = list(daily_data.keys())
        present_counts = [daily_data[d]["present"] for d in dates]
        absent_counts = [daily_data[d]["absent"] for d in dates]

        # Shorten date labels
        short_dates = [d[5:] for d in dates]  # Remove year

        canvas = MplCanvas(self, width=4, height=3, dpi=100)

        x = range(len(dates))
        width = 0.35

        canvas.axes.bar([i - width / 2 for i in x], present_counts, width, label='Present', color='#27AE60')
        canvas.axes.bar([i + width / 2 for i in x], absent_counts, width, label='Absent', color='#E74C3C')

        canvas.axes.set_xlabel('Date')
        canvas.axes.set_ylabel('Count')
        canvas.axes.set_xticks(x)
        canvas.axes.set_xticklabels(short_dates, rotation=45, ha='right')
        canvas.axes.legend()
        canvas.axes.grid(axis='y', alpha=0.3)
        canvas.figure.tight_layout()

        layout.addWidget(canvas)

    def update_section_chart(self):
        """Update the section comparison chart"""
        layout = self.section_chart_container.layout()

        # Remove old chart if exists
        for i in range(layout.count() - 1, 0, -1):
            item = layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        section_data = get_section_comparison()

        if not section_data:
            no_data = QLabel("No section data available\n\nMark attendance for different sections to see comparison")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setWordWrap(True)
            no_data.setStyleSheet("font-size: 14px; color: #95A5A6; background: transparent;")
            layout.addWidget(no_data)
            return

        sections = list(section_data.keys())
        rates = []

        for section in sections:
            stats = section_data[section]
            rate = (stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0
            rates.append(rate)

        canvas = MplCanvas(self, width=4, height=3, dpi=100)

        colors = ['#4A90E2', '#FF8C42', '#27AE60', '#9B59B6', '#E74C3C']
        bars = canvas.axes.bar(sections, rates, color=colors[:len(sections)])

        canvas.axes.set_ylabel('Attendance Rate (%)')
        canvas.axes.set_ylim(0, 100)
        canvas.axes.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            canvas.axes.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)

        canvas.figure.tight_layout()
        layout.addWidget(canvas)

    def update_student_chart(self):
        """Update the student attendance rates chart"""
        layout = self.student_chart_container.layout()

        # Remove old chart if exists
        for i in range(layout.count() - 1, 0, -1):
            item = layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        rates = get_all_student_attendance_rates()

        if not rates:
            no_data = QLabel("No student data available")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("font-size: 14px; color: #95A5A6; background: transparent;")
            layout.addWidget(no_data)
            return

        # Sort by rate
        sorted_students = sorted(rates.items(), key=lambda x: x[1], reverse=True)
        students = [s[0][:15] + '...' if len(s[0]) > 15 else s[0] for s in sorted_students[:10]]  # Top 10
        student_rates = [s[1] for s in sorted_students[:10]]

        canvas = MplCanvas(self, width=4, height=3, dpi=100)

        # Color bars based on attendance threshold
        colors = ['#27AE60' if r >= 75 else '#E74C3C' for r in student_rates]

        bars = canvas.axes.barh(students, student_rates, color=colors)
        canvas.axes.set_xlabel('Attendance Rate (%)')
        canvas.axes.set_xlim(0, 100)
        canvas.axes.invert_yaxis()  # Top student on top
        canvas.axes.axvline(x=75, color='#FF8C42', linestyle='--', label='75% Threshold')
        canvas.axes.legend(loc='lower right')
        canvas.axes.grid(axis='x', alpha=0.3)

        canvas.figure.tight_layout()
        layout.addWidget(canvas)

    def showEvent(self, event):
        """Refresh charts when page is shown"""
        super().showEvent(event)
        self.refresh_charts()


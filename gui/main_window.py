import os
import pickle
import csv
from datetime import date

from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QHBoxLayout, QGridLayout, QFrame, QStackedWidget, QDialog,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from gui.enroll_page import EnrollPage
from gui.attendance_page import AttendancePage
from gui.analytics_page import AnalyticsPage
from gui.reports_page import ReportsPage
from utils.csv_utils import (
    get_low_attendance_students
)


def show_message(parent, title, message, msg_type="info"):
    """Show a styled message box with white background"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)

    if msg_type == "info":
        msg.setIcon(QMessageBox.Information)
    elif msg_type == "warning":
        msg.setIcon(QMessageBox.Warning)
    elif msg_type == "error":
        msg.setIcon(QMessageBox.Critical)
    elif msg_type == "success":
        msg.setIcon(QMessageBox.Information)

    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: #2C3E50;
            font-size: 14px;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-width: 300px;
            padding: 10px;
        }
        QMessageBox QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 25px;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background-color: #357ABD;
        }
        QMessageBox QPushButton:pressed {
            background-color: #2A6A9D;
        }
    """)

    msg.exec_()


class SectionDialog(QDialog):
    """Dialog for selecting section before marking attendance"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_section = None
        self.setWindowTitle("Select Section")
        self.setFixedSize(450, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)

        # Header icon with background
        icon_container = QWidget()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 40px;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon = QLabel("📚")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px; background: transparent;")
        icon_layout.addWidget(icon)

        # Center the icon container
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_container)
        icon_row.addStretch()
        layout.addLayout(icon_row)
        layout.addSpacing(15)

        title = QLabel("Select Section")
        title.setAlignment(Qt.AlignCenter)
        layout.addSpacing(15)
        title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        subtitle = QLabel("Choose which section's attendance to mark")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7F8C8D;
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        # Section Buttons
        btn_5a = QPushButton("BSCS 5A")
        btn_5a.setFixedHeight(65)
        btn_5a.setCursor(Qt.PointingHandCursor)
        btn_5a.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5BA0F2, stop:1 #4590CD);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #357ABD, stop:1 #2A6A9D);
            }
        """)
        btn_5a.clicked.connect(lambda: self.select_section("BSCS 5A"))

        btn_5b = QPushButton("BSCS 5B")
        btn_5b.setFixedHeight(65)
        btn_5b.setCursor(Qt.PointingHandCursor)
        btn_5b.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF8C42, stop:1 #FF6B35);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF9C52, stop:1 #FF7B45);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B35, stop:1 #E55A25);
            }
        """)
        btn_5b.clicked.connect(lambda: self.select_section("BSCS 5B"))

        layout.addWidget(btn_5a)
        layout.addSpacing(15)
        layout.addWidget(btn_5b)
        layout.addSpacing(20)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F8F9FA;
                color: #7F8C8D;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                font-size: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #E8E9EA;
                border-color: #BDC3C7;
                color: #2C3E50;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        layout.addWidget(cancel_btn)
        layout.addStretch()
        self.setLayout(layout)

    def select_section(self, section):
        self.selected_section = section
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Attendance Management System")
        self.setGeometry(50, 30, 1500, 900)
        self.setMinimumSize(1400, 850)
        self.showMaximized()

        # Modern gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFE5B4, stop:1 #FFB6C1);
            }
        """)

        # Stacked widget for page navigation
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        # Create pages
        self.dashboard_page = self.create_dashboard_page()
        self.enroll_page = EnrollPage()
        self.attendance_page = AttendancePage()
        self.analytics_page = AnalyticsPage()
        self.reports_page = ReportsPage()

        # Connect signals
        self.enroll_page.go_back.connect(self.go_to_dashboard)
        self.attendance_page.go_back.connect(self.go_to_dashboard)
        self.analytics_page.go_back.connect(self.go_to_dashboard)
        self.reports_page.go_back.connect(self.go_to_dashboard)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.enroll_page)
        self.stacked_widget.addWidget(self.attendance_page)
        self.stacked_widget.addWidget(self.analytics_page)
        self.stacked_widget.addWidget(self.reports_page)

        self.setCentralWidget(self.stacked_widget)

        # Refresh timer for stats
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_statistics)
        self.refresh_timer.start(5000)

        # Initial stats update
        self.update_statistics()

    # ==================== NAVIGATION ====================
    def go_to_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_statistics()

    def go_to_enroll(self):
        self.enroll_page.reset_form()
        self.stacked_widget.setCurrentIndex(1)

    def go_to_attendance(self):
        # Show section selection dialog
        dialog = SectionDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_section:
            self.attendance_page.set_section(dialog.selected_section)
            self.attendance_page.reset_form()
            self.stacked_widget.setCurrentIndex(2)

    def go_to_analytics(self):
        self.stacked_widget.setCurrentIndex(3)

    def go_to_reports(self):
        self.stacked_widget.setCurrentIndex(4)

    # ==================== DASHBOARD PAGE ====================
    def create_dashboard_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Navigation Bar
        nav_bar = self.create_nav_bar()
        main_layout.addWidget(nav_bar)

        # Main Content Area
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # Left Sidebar - Quick Actions
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)

        # Main Dashboard Area
        dashboard = self.create_dashboard()
        content_layout.addWidget(dashboard, 3)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        page.setLayout(main_layout)
        return page

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

        logo_label = QLabel("🎓")
        logo_label.setStyleSheet("font-size: 32px; background: transparent;")

        title_label = QLabel("AI Attendance Management")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        nav_layout.addWidget(logo_label)
        nav_layout.addWidget(title_label)
        nav_layout.addStretch()

        # Low attendance alert indicator
        self.alert_label = QLabel("")
        self.alert_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #E74C3C;
                background: rgba(231, 76, 60, 0.1);
                padding: 8px 15px;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
        """)
        self.alert_label.setVisible(False)
        nav_layout.addWidget(self.alert_label)

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

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(350)
        sidebar.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(25, 25, 25, 25)
        sidebar_layout.setSpacing(15)

        section_title = QLabel("Quick Actions")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
                background: transparent;
                padding-bottom: 10px;
                border-bottom: 2px solid rgba(0, 0, 0, 0.1);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        sidebar_layout.addWidget(section_title)

        # Enroll Button
        enroll_btn = QPushButton("👤  Enroll New Student")
        enroll_btn.setFixedHeight(70)
        enroll_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5BA0F2, stop:1 #4590CD);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #357ABD, stop:1 #2A6A9D);
            }
        """)
        enroll_btn.clicked.connect(self.go_to_enroll)

        # Attendance Button
        attendance_btn = QPushButton("📸  Mark Attendance")
        attendance_btn.setFixedHeight(70)
        attendance_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF8C42, stop:1 #FF6B35);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF9C52, stop:1 #FF7B45);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B35, stop:1 #E55A25);
            }
        """)
        attendance_btn.clicked.connect(self.go_to_attendance)

        # Analytics Button
        analytics_btn = QPushButton("📊  View Analytics")
        analytics_btn.setFixedHeight(70)
        analytics_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9B59B6, stop:1 #8E44AD);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A569C6, stop:1 #9E54BD);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8E44AD, stop:1 #7E349D);
            }
        """)
        analytics_btn.clicked.connect(self.go_to_analytics)

        # Reports Button
        reports_btn = QPushButton("📄  Export Reports")
        reports_btn.setFixedHeight(70)
        reports_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27AE60, stop:1 #219A52);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2ECC71, stop:1 #27AE60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #219A52, stop:1 #1A8A42);
            }
        """)
        reports_btn.clicked.connect(self.go_to_reports)

        sidebar_layout.addWidget(enroll_btn)
        sidebar_layout.addWidget(attendance_btn)
        sidebar_layout.addWidget(analytics_btn)
        sidebar_layout.addWidget(reports_btn)
        sidebar_layout.addStretch()

        # Exit Button
        exit_btn = QPushButton("❌  Exit Application")
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B6B, stop:1 #EE5A6F);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF7B7B, stop:1 #FF6A7F);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EE5A6F, stop:1 #DD4A5F);
            }
        """)
        exit_btn.clicked.connect(self.close)

        sidebar_layout.addWidget(exit_btn)
        sidebar.setLayout(sidebar_layout)
        return sidebar

    def create_dashboard(self):
        dashboard = QWidget()
        dashboard.setStyleSheet("background: transparent;")

        dashboard_layout = QVBoxLayout()
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(20)

        stats_row = self.create_stats_cards()
        dashboard_layout.addWidget(stats_row)

        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        left_content = self.create_students_list()
        content_row.addWidget(left_content, 1)

        right_content = self.create_info_section()
        content_row.addWidget(right_content, 1)

        dashboard_layout.addLayout(content_row, 1)
        dashboard.setLayout(dashboard_layout)
        return dashboard

    def create_stats_cards(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0)

        self.total_students_card = self.create_stat_card(
            "👥", "Total Students", "0", "#4A90E2")
        self.today_attendance_card = self.create_stat_card(
            "📊", "Today's Attendance", "0", "#FF8C42")
        self.total_records_card = self.create_stat_card(
            "📝", "Total Records", "0", "#27AE60")
        self.low_attendance_card = self.create_stat_card(
            "⚠️", "Low Attendance", "0", "#E74C3C")

        grid.addWidget(self.total_students_card, 0, 0)
        grid.addWidget(self.today_attendance_card, 0, 1)
        grid.addWidget(self.total_records_card, 0, 2)
        grid.addWidget(self.low_attendance_card, 0, 3)

        container.setLayout(grid)
        return container

    def create_stat_card(self, icon, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
            }}
        """)
        card.setFixedHeight(140)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            f"font-size: 28px; background: transparent; color: {color};")

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 13px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        header.addWidget(icon_label)
        header.addStretch()
        header.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 32px; font-weight: bold; color: {color}; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        value_label.setAlignment(Qt.AlignLeft)

        layout.addLayout(header)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def create_students_list(self):
        section = QWidget()
        section.setStyleSheet(
            "QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("👥 Enrolled Students")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2C3E50; background: transparent; padding-bottom: 10px; border-bottom: 2px solid rgba(0, 0, 0, 0.1); font-family: 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(title)

        # Scroll area for students list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F8F9FA;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDC3C7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95A5A6;
            }
        """)

        self.students_container = QWidget()
        self.students_container.setStyleSheet("background: transparent;")
        self.students_layout = QVBoxLayout()
        self.students_layout.setContentsMargins(0, 0, 0, 0)
        self.students_layout.setSpacing(10)
        self.students_container.setLayout(self.students_layout)

        scroll_area.setWidget(self.students_container)
        layout.addWidget(scroll_area, 1)
        section.setLayout(layout)
        return section

    def create_info_section(self):
        section = QWidget()
        section.setStyleSheet(
            "QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("ℹ️ System Information")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2C3E50; background: transparent; padding-bottom: 10px; border-bottom: 2px solid rgba(0, 0, 0, 0.1); font-family: 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(title)

        info_items = [
            ("🎯", "Face Recognition", "Powered by YOLO & FaceNet"),
            ("⚡", "Real-time Processing", "Fast and accurate detection"),
            ("🔒", "Secure Database", "Encrypted face embeddings"),
            ("📱", "Easy Management", "Simple enrollment process"),
            ("📊", "Analytics Dashboard", "View detailed statistics"),
            ("📄", "PDF Reports", "Export attendance reports"),
        ]

        for icon, label, desc in info_items:
            item = QHBoxLayout()
            item.setSpacing(15)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet(
                "font-size: 24px; background: transparent;")
            icon_label.setFixedWidth(40)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(3)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

            desc_widget = QLabel(desc)
            desc_widget.setStyleSheet(
                "font-size: 13px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

            text_layout.addWidget(label_widget)
            text_layout.addWidget(desc_widget)

            item.addWidget(icon_label)
            item.addLayout(text_layout)
            item.addStretch()

            layout.addLayout(item)

        layout.addStretch()
        section.setLayout(layout)
        return section

    # ==================== STATISTICS ====================
    def update_statistics(self):
        total_students = self.get_total_students()
        self.update_stat_card(self.total_students_card, str(total_students))

        today_count = self.get_today_attendance()
        self.update_stat_card(self.today_attendance_card, str(today_count))

        total_records = self.get_total_records()
        self.update_stat_card(self.total_records_card, str(total_records))

        # Low attendance count
        low_students = get_low_attendance_students(75.0)
        low_count = len(low_students)
        self.update_stat_card(self.low_attendance_card, str(low_count))

        # Update alert indicator
        if low_count > 0:
            self.alert_label.setText(f"⚠️ {low_count} students below 75%")
            self.alert_label.setVisible(True)
        else:
            self.alert_label.setVisible(False)

        self.update_students_list()

    def update_stat_card(self, card, value):
        layout = card.layout()
        if layout and layout.count() > 1:
            value_label = layout.itemAt(1).widget()
            if value_label:
                value_label.setText(value)

    def get_total_students(self):
        try:
            if os.path.exists("face_db.pkl"):
                with open("face_db.pkl", "rb") as f:
                    face_db = pickle.load(f)
                return len(face_db)
        except:
            pass
        return 0

    def get_today_attendance(self):
        try:
            today = str(date.today())
            if os.path.exists("data/attendance.csv"):
                with open("data/attendance.csv", "r") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) > 1:
                        header = rows[0]
                        # Check if Section column exists
                        has_section = len(
                            header) > 1 and header[1] == "Section"
                        start_idx = 2 if has_section else 1

                        count = 0
                        for row in rows[1:]:
                            if row[0] == today:
                                count += row[start_idx:].count(
                                    "P") if len(row) > start_idx else 0
                        return count
        except:
            pass
        return 0

    def get_total_records(self):
        try:
            if os.path.exists("data/attendance.csv"):
                with open("data/attendance.csv", "r") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    return max(0, len(rows) - 1)
        except:
            pass
        return 0

    def update_students_list(self):
        if not hasattr(self, 'students_layout'):
            return

        layout = self.students_layout

        # Clear existing items
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            if os.path.exists("face_db.pkl"):
                with open("face_db.pkl", "rb") as f:
                    face_db = pickle.load(f)

                students = list(face_db.keys())

                if not students:
                    no_data = QLabel("No students enrolled yet")
                    no_data.setAlignment(Qt.AlignCenter)
                    no_data.setStyleSheet(
                        "font-size: 14px; color: #95A5A6; background: transparent; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif;")
                    layout.addWidget(no_data)
                    return

                for student in sorted(students):
                    student_frame = QFrame()
                    student_frame.setStyleSheet("""
                        QFrame {
                            background: rgba(74, 144, 226, 0.1);
                            border-radius: 10px;
                            border-left: 4px solid #4A90E2;
                        }
                    """)

                    frame_layout = QHBoxLayout()
                    frame_layout.setContentsMargins(15, 12, 15, 12)

                    student_name = QLabel(f"👤 {student}")
                    student_name.setStyleSheet("""
                        QLabel {
                            font-size: 15px;
                            font-weight: bold;
                            color: #2C3E50;
                            background: transparent;
                            font-family: 'Segoe UI', Arial, sans-serif;
                        }
                    """)

                    frame_layout.addWidget(student_name)
                    frame_layout.addStretch()

                    student_frame.setLayout(frame_layout)
                    layout.addWidget(student_frame)

                # Add stretch at the end
                layout.addStretch()
            else:
                no_data = QLabel("No students enrolled yet")
                no_data.setAlignment(Qt.AlignCenter)
                no_data.setStyleSheet(
                    "font-size: 14px; color: #95A5A6; background: transparent; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif;")
                layout.addWidget(no_data)
        except Exception as e:
            no_data = QLabel(f"Error loading students: {str(e)}")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet(
                "font-size: 14px; color: #E74C3C; background: transparent; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif;")
            layout.addWidget(no_data)

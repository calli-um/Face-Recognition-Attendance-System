import os
from datetime import date, datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QFrame, QDateEdit, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate

from fpdf import FPDF

from utils.csv_utils import (
    get_attendance_by_date_range,
    get_all_student_attendance_rates,
    get_students_list,
    get_low_attendance_students
)


def styled_message(parent, title, message, msg_type="info"):
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
    """)

    msg.exec_()


class AttendanceReport(FPDF):
    """Custom PDF class for attendance reports"""

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AI Attendance Management System', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


class ReportsPage(QWidget):
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
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # Left Panel - Report Options
        left_panel = self.create_options_panel()
        content_layout.addWidget(left_panel)

        # Right Panel - Preview
        right_panel = self.create_preview_panel()
        content_layout.addWidget(right_panel, 1)

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

        title_label = QLabel("Export Reports")
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

    def create_options_panel(self):
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        panel.setFixedWidth(400)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")

        title = QLabel("Generate Report")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        subtitle = QLabel("Configure report settings and export to PDF")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "font-size: 14px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        # Report Type
        type_label = QLabel("Report Type")
        type_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        self.report_type = QComboBox()
        self.report_type.addItems([
            "📊 Full Attendance Report",
            "📈 Student-wise Summary",
            "⚠️ Low Attendance Alert Report",
            "📅 Date Range Report"
        ])
        self.report_type.setStyleSheet("""
            QComboBox {
                background: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
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

        layout.addWidget(type_label)
        layout.addWidget(self.report_type)

        # Section Filter
        section_label = QLabel("Section")
        section_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        self.section_filter = QComboBox()
        self.section_filter.addItems(["All Sections", "BSCS 5A", "BSCS 5B"])
        self.section_filter.setStyleSheet("""
            QComboBox {
                background: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
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

        layout.addWidget(section_label)
        layout.addWidget(self.section_filter)

        # Date Range
        date_label = QLabel("Date Range")
        date_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDateEdit:hover {
                border: 2px solid #4A90E2;
            }
        """)

        to_label = QLabel("to")
        to_label.setStyleSheet(
            "font-size: 13px; color: #7F8C8D; background: transparent;")

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDateEdit:hover {
                border: 2px solid #4A90E2;
            }
        """)

        date_layout.addWidget(self.start_date)
        date_layout.addWidget(to_label)
        date_layout.addWidget(self.end_date)

        layout.addWidget(date_label)
        layout.addLayout(date_layout)
        layout.addSpacing(10)

        # Quick Date Presets
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(10)

        today_btn = QPushButton("Today")
        today_btn.setStyleSheet(self.get_preset_btn_style())
        today_btn.clicked.connect(lambda: self.set_date_preset(0))

        week_btn = QPushButton("This Week")
        week_btn.setStyleSheet(self.get_preset_btn_style())
        week_btn.clicked.connect(lambda: self.set_date_preset(7))

        month_btn = QPushButton("This Month")
        month_btn.setStyleSheet(self.get_preset_btn_style())
        month_btn.clicked.connect(lambda: self.set_date_preset(30))

        preset_layout.addWidget(today_btn)
        preset_layout.addWidget(week_btn)
        preset_layout.addWidget(month_btn)

        layout.addLayout(preset_layout)
        layout.addStretch()

        # Buttons
        preview_btn = QPushButton("👁️  Preview Report")
        preview_btn.setFixedHeight(50)
        preview_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9B59B6, stop:1 #8E44AD);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A569C6, stop:1 #9E54BD);
            }
        """)
        preview_btn.clicked.connect(self.preview_report)

        export_btn = QPushButton("📄  Export to PDF")
        export_btn.setFixedHeight(55)
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27AE60, stop:1 #219A52);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ECC71, stop:1 #27AE60);
            }
        """)
        export_btn.clicked.connect(self.export_pdf)

        layout.addWidget(preview_btn)
        layout.addWidget(export_btn)

        panel.setLayout(layout)
        return panel

    def create_preview_panel(self):
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        preview_title = QLabel("📋 Report Preview")
        preview_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2C3E50; background: transparent; padding-bottom: 10px; border-bottom: 2px solid rgba(0, 0, 0, 0.1); font-family: 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(preview_title)

        # Status Label
        self.preview_status = QLabel(
            "Configure report options and click 'Preview Report'")
        self.preview_status.setAlignment(Qt.AlignCenter)
        self.preview_status.setWordWrap(True)
        self.preview_status.setStyleSheet(
            "font-size: 14px; color: #95A5A6; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        # Table for preview
        self.preview_table = QTableWidget()
        self.preview_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #E0E0E0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QHeaderView::section {
                background-color: #4A90E2;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        self.preview_table.setVisible(False)

        layout.addWidget(self.preview_status)
        layout.addWidget(self.preview_table, 1)

        panel.setLayout(layout)
        return panel

    def get_preset_btn_style(self):
        return """
            QPushButton {
                background: #F8F9FA;
                color: #2C3E50;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #E8E9EA;
                border: 1px solid #4A90E2;
            }
        """

    def set_date_preset(self, days):
        today = QDate.currentDate()
        if days == 0:
            self.start_date.setDate(today)
        else:
            self.start_date.setDate(today.addDays(-days))
        self.end_date.setDate(today)

    def preview_report(self):
        """Generate preview of the report"""
        report_type = self.report_type.currentIndex()
        section = self.section_filter.currentText()
        section = None if section == "All Sections" else section

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        if report_type == 0:  # Full Attendance Report
            self.preview_full_report(section, start, end)
        elif report_type == 1:  # Student-wise Summary
            self.preview_student_summary()
        elif report_type == 2:  # Low Attendance Alert
            self.preview_low_attendance()
        elif report_type == 3:  # Date Range Report
            self.preview_date_range(section, start, end)

    def preview_full_report(self, section, start, end):
        header, data = get_attendance_by_date_range(start, end, section)

        if not data:
            self.preview_status.setText(
                "No attendance data available for the selected criteria")
            self.preview_status.setVisible(True)
            self.preview_table.setVisible(False)
            return

        self.preview_status.setVisible(False)
        self.preview_table.setVisible(True)

        # Setup table
        self.preview_table.setRowCount(len(data))
        self.preview_table.setColumnCount(len(header))
        self.preview_table.setHorizontalHeaderLabels(header)

        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if col_idx > 1:  # Attendance columns
                    if value == "P":
                        item.setBackground(Qt.green)
                    elif value == "A":
                        item.setBackground(Qt.red)
                self.preview_table.setItem(row_idx, col_idx, item)

        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def preview_student_summary(self):
        rates = get_all_student_attendance_rates()

        if not rates:
            self.preview_status.setText("No student data available")
            self.preview_status.setVisible(True)
            self.preview_table.setVisible(False)
            return

        self.preview_status.setVisible(False)
        self.preview_table.setVisible(True)

        sorted_rates = sorted(rates.items(), key=lambda x: x[1], reverse=True)

        self.preview_table.setRowCount(len(sorted_rates))
        self.preview_table.setColumnCount(3)
        self.preview_table.setHorizontalHeaderLabels(
            ["Student Name", "Attendance Rate", "Status"])

        for row_idx, (student, rate) in enumerate(sorted_rates):
            self.preview_table.setItem(row_idx, 0, QTableWidgetItem(student))
            self.preview_table.setItem(
                row_idx, 1, QTableWidgetItem(f"{rate:.1f}%"))

            status = "✅ Good" if rate >= 75 else "⚠️ Low"
            status_item = QTableWidgetItem(status)
            if rate < 75:
                status_item.setBackground(Qt.yellow)
            self.preview_table.setItem(row_idx, 2, status_item)

        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def preview_low_attendance(self):
        low_students = get_low_attendance_students(75.0)

        if not low_students:
            self.preview_status.setText(
                "✅ Great! No students with low attendance (below 75%)")
            self.preview_status.setVisible(True)
            self.preview_table.setVisible(False)
            return

        self.preview_status.setVisible(False)
        self.preview_table.setVisible(True)

        sorted_students = sorted(low_students.items(), key=lambda x: x[1])

        self.preview_table.setRowCount(len(sorted_students))
        self.preview_table.setColumnCount(3)
        self.preview_table.setHorizontalHeaderLabels(
            ["Student Name", "Attendance Rate", "Alert Level"])

        for row_idx, (student, rate) in enumerate(sorted_students):
            self.preview_table.setItem(row_idx, 0, QTableWidgetItem(student))
            self.preview_table.setItem(
                row_idx, 1, QTableWidgetItem(f"{rate:.1f}%"))

            if rate < 50:
                alert = "🔴 Critical"
            elif rate < 65:
                alert = "🟠 Warning"
            else:
                alert = "🟡 Attention"

            alert_item = QTableWidgetItem(alert)
            if rate < 50:
                alert_item.setBackground(Qt.red)
            elif rate < 65:
                alert_item.setBackground(Qt.yellow)
            self.preview_table.setItem(row_idx, 2, alert_item)

        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def preview_date_range(self, section, start, end):
        self.preview_full_report(section, start, end)

    def export_pdf(self):
        """Export the report to PDF"""
        report_type = self.report_type.currentIndex()
        section = self.section_filter.currentText()
        section_filter = None if section == "All Sections" else section

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        # Get file path
        default_name = f"attendance_report_{date.today()}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", default_name, "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            pdf = AttendanceReport()
            pdf.alias_nb_pages()
            pdf.add_page()

            # Report Title
            report_titles = [
                "Full Attendance Report",
                "Student-wise Attendance Summary",
                "Low Attendance Alert Report",
                "Date Range Attendance Report"
            ]

            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, report_titles[report_type], 0, 1, 'C')
            pdf.ln(5)

            # Report Info
            pdf.set_font('Arial', '', 10)
            pdf.cell(
                0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
            pdf.cell(0, 6, f"Section: {section}", 0, 1)
            pdf.cell(0, 6, f"Date Range: {start} to {end}", 0, 1)
            pdf.ln(10)

            if report_type == 0 or report_type == 3:  # Full/Date Range Report
                self.export_full_report(pdf, section_filter, start, end)
            elif report_type == 1:  # Student Summary
                self.export_student_summary(pdf)
            elif report_type == 2:  # Low Attendance
                self.export_low_attendance(pdf)

            pdf.output(file_path)
            styled_message(
                self, "Success", f"Report exported successfully!\n\nSaved to:\n{file_path}", "info")

        except Exception as e:
            styled_message(
                self, "Error", f"Failed to export PDF:\n{str(e)}", "warning")

    def export_full_report(self, pdf, section, start, end):
        header, data = get_attendance_by_date_range(start, end, section)

        if not data:
            pdf.cell(0, 10, "No attendance data available", 0, 1, 'C')
            return

        # Table header
        pdf.set_font('Arial', 'B', 9)
        col_width = 190 / min(len(header), 8)

        # Only show first 8 columns for readability
        display_header = header[:8]
        for col in display_header:
            col_name = col[:12] + '..' if len(col) > 14 else col
            pdf.cell(col_width, 8, col_name, 1, 0, 'C')
        pdf.ln()

        # Table data
        pdf.set_font('Arial', '', 8)
        for row in data[:50]:  # Limit to 50 rows
            for col_idx, value in enumerate(row[:8]):
                val = str(value)[:12] if len(str(value)) > 12 else str(value)
                pdf.cell(col_width, 6, val, 1, 0, 'C')
            pdf.ln()

        if len(data) > 50:
            pdf.ln(5)
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 6, f"... and {len(data) - 50} more records", 0, 1, 'C')

    def export_student_summary(self, pdf):
        rates = get_all_student_attendance_rates()

        if not rates:
            pdf.cell(0, 10, "No student data available", 0, 1, 'C')
            return

        sorted_rates = sorted(rates.items(), key=lambda x: x[1], reverse=True)

        # Summary stats
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Summary Statistics", 0, 1)
        pdf.set_font('Arial', '', 10)

        total = len(rates)
        above_75 = sum(1 for _, r in rates.items() if r >= 75)
        below_75 = total - above_75
        avg_rate = sum(rates.values()) / total if total > 0 else 0

        pdf.cell(0, 6, f"Total Students: {total}", 0, 1)
        pdf.cell(0, 6, f"Average Attendance: {avg_rate:.1f}%", 0, 1)
        pdf.cell(0, 6, f"Students >= 75%: {above_75}", 0, 1)
        pdf.cell(0, 6, f"Students < 75%: {below_75}", 0, 1)
        pdf.ln(10)

        # Table
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(100, 8, "Student Name", 1, 0, 'C')
        pdf.cell(45, 8, "Attendance %", 1, 0, 'C')
        pdf.cell(45, 8, "Status", 1, 1, 'C')

        pdf.set_font('Arial', '', 9)
        for student, rate in sorted_rates:
            status = "Good" if rate >= 75 else "Low"
            student_name = student[:30] + \
                '..' if len(student) > 32 else student
            pdf.cell(100, 6, student_name, 1, 0)
            pdf.cell(45, 6, f"{rate:.1f}%", 1, 0, 'C')
            pdf.cell(45, 6, status, 1, 1, 'C')

    def export_low_attendance(self, pdf):
        low_students = get_low_attendance_students(75.0)

        if not low_students:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "No students with low attendance!", 0, 1, 'C')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, "All students have attendance rate >= 75%", 0, 1, 'C')
            return

        sorted_students = sorted(low_students.items(), key=lambda x: x[1])

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(
            0, 8, f"Students with Low Attendance ({len(low_students)} students)", 0, 1)
        pdf.ln(5)

        # Table
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(100, 8, "Student Name", 1, 0, 'C')
        pdf.cell(45, 8, "Attendance %", 1, 0, 'C')
        pdf.cell(45, 8, "Alert Level", 1, 1, 'C')

        pdf.set_font('Arial', '', 9)
        for student, rate in sorted_students:
            if rate < 50:
                alert = "Critical"
            elif rate < 65:
                alert = "Warning"
            else:
                alert = "Attention"

            student_name = student[:30] + \
                '..' if len(student) > 32 else student
            pdf.cell(100, 6, student_name, 1, 0)
            pdf.cell(45, 6, f"{rate:.1f}%", 1, 0, 'C')
            pdf.cell(45, 6, alert, 1, 1, 'C')

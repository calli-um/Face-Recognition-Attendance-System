import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Comprehensive global stylesheet for ALL dialogs to have white backgrounds
    app.setStyleSheet("""
        /* ===== BASE DIALOG STYLING ===== */
        QDialog {
            background-color: white;
            color: #2C3E50;
        }
        QDialog * {
            background-color: transparent;
            color: #2C3E50;
        }
        QDialog QWidget {
            background-color: transparent;
        }
        QDialog QFrame {
            background-color: transparent;
        }
        QDialog QLabel {
            background-color: transparent;
            color: #2C3E50;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QDialog QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QDialog QPushButton:hover {
            background-color: #357ABD;
        }
        QDialog QPushButton:pressed {
            background-color: #2A6A9D;
        }
        
        /* ===== QMESSAGEBOX STYLING ===== */
        QMessageBox {
            background-color: white;
            color: #2C3E50;
        }
        QMessageBox QWidget {
            background-color: white;
        }
        QMessageBox QLabel {
            color: #2C3E50;
            background-color: transparent;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            min-width: 300px;
        }
        QMessageBox QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-size: 13px;
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
        QMessageBox QDialogButtonBox {
            background-color: transparent;
        }
        
        /* ===== QFILEDIALOG STYLING ===== */
        QFileDialog {
            background-color: white;
            color: #2C3E50;
        }
        QFileDialog * {
            background-color: white;
            color: #2C3E50;
        }
        QFileDialog QWidget {
            background-color: white;
            color: #2C3E50;
        }
        QFileDialog QFrame {
            background-color: white;
        }
        QFileDialog QLabel {
            color: #2C3E50;
            background-color: transparent;
        }
        QFileDialog QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QFileDialog QPushButton:hover {
            background-color: #357ABD;
        }
        QFileDialog QLineEdit {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 8px;
            selection-background-color: #4A90E2;
            selection-color: white;
        }
        QFileDialog QTreeView {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            selection-background-color: #4A90E2;
            selection-color: white;
        }
        QFileDialog QTreeView::item {
            color: #2C3E50;
            background-color: white;
        }
        QFileDialog QTreeView::item:hover {
            background-color: #F0F0F0;
        }
        QFileDialog QTreeView::item:selected {
            background-color: #4A90E2;
            color: white;
        }
        QFileDialog QListView {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
        }
        QFileDialog QListView::item {
            color: #2C3E50;
            background-color: white;
        }
        QFileDialog QListView::item:hover {
            background-color: #F0F0F0;
        }
        QFileDialog QListView::item:selected {
            background-color: #4A90E2;
            color: white;
        }
        QFileDialog QComboBox {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QFileDialog QComboBox::drop-down {
            background-color: white;
            border: none;
        }
        QFileDialog QComboBox QAbstractItemView {
            background-color: white;
            color: #2C3E50;
            selection-background-color: #4A90E2;
            selection-color: white;
        }
        QFileDialog QHeaderView {
            background-color: white;
        }
        QFileDialog QHeaderView::section {
            background-color: #F8F9FA;
            color: #2C3E50;
            border: none;
            border-right: 1px solid #E0E0E0;
            padding: 6px;
        }
        QFileDialog QScrollBar:vertical {
            background-color: #F8F9FA;
            width: 12px;
            border: none;
        }
        QFileDialog QScrollBar::handle:vertical {
            background-color: #BDC3C7;
            border-radius: 6px;
            min-height: 20px;
        }
        QFileDialog QScrollBar:horizontal {
            background-color: #F8F9FA;
            height: 12px;
            border: none;
        }
        QFileDialog QScrollBar::handle:horizontal {
            background-color: #BDC3C7;
            border-radius: 6px;
            min-width: 20px;
        }
        QFileDialog QToolButton {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 4px;
        }
        QFileDialog QToolButton:hover {
            background-color: #F0F0F0;
        }
        QFileDialog QSplitter {
            background-color: white;
        }
        QFileDialog QSplitter::handle {
            background-color: #E0E0E0;
        }
        
        /* ===== QINPUTDIALOG STYLING ===== */
        QInputDialog {
            background-color: white;
            color: #2C3E50;
        }
        QInputDialog QWidget {
            background-color: white;
        }
        QInputDialog QLabel {
            color: #2C3E50;
            background-color: transparent;
        }
        QInputDialog QLineEdit {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 6px;
        }
        QInputDialog QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        /* ===== QCOLORDIALOG STYLING ===== */
        QColorDialog {
            background-color: white;
        }
        QColorDialog QWidget {
            background-color: white;
            color: #2C3E50;
        }
        
        /* ===== QFONTDIALOG STYLING ===== */
        QFontDialog {
            background-color: white;
        }
        QFontDialog QWidget {
            background-color: white;
            color: #2C3E50;
        }
        
        /* ===== CALENDAR WIDGET ===== */
        QCalendarWidget {
            background-color: white;
        }
        QCalendarWidget QWidget {
            background-color: white;
            color: #2C3E50;
        }
        QCalendarWidget QToolButton {
            background-color: white;
            color: #2C3E50;
            border: none;
        }
        QCalendarWidget QToolButton:hover {
            background-color: #F0F0F0;
        }
        QCalendarWidget QMenu {
            background-color: white;
            color: #2C3E50;
        }
        QCalendarWidget QSpinBox {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
        }
        QCalendarWidget QTableView {
            background-color: white;
            color: #2C3E50;
            selection-background-color: #4A90E2;
            selection-color: white;
        }
        QCalendarWidget QAbstractItemView:enabled {
            background-color: white;
            color: #2C3E50;
        }
        QCalendarWidget QAbstractItemView:disabled {
            background-color: #F8F9FA;
            color: #95A5A6;
        }
        
        /* ===== MENU STYLING ===== */
        QMenu {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
        }
        QMenu::item {
            background-color: transparent;
            color: #2C3E50;
            padding: 6px 20px;
        }
        QMenu::item:selected {
            background-color: #4A90E2;
            color: white;
        }
        
        /* ===== TOOLTIP STYLING ===== */
        QToolTip {
            background-color: white;
            color: #2C3E50;
            border: 1px solid #E0E0E0;
            padding: 4px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

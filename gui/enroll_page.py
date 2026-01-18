import os
import cv2
import pickle
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QMessageBox, QProgressBar, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from utils.face_utils import extract_embedding
from utils.csv_utils import add_student_column


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


class EnrollPage(QWidget):
    # Signal to notify when to go back to dashboard
    go_back = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.images = []
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation Bar
        nav_bar = self.create_nav_bar()
        main_layout.addWidget(nav_bar)
        
        # Content
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Left Panel - Form
        left_panel = self.create_form_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Right Panel - Image Preview
        right_panel = self.create_preview_panel()
        content_layout.addWidget(right_panel, 3)
        
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
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
        
        title_label = QLabel("Enroll New Student")
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
    
    def create_form_panel(self):
        panel = QWidget()
        panel.setStyleSheet("QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        icon_label = QLabel("👤")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        
        title = QLabel("Student Information")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        
        subtitle = QLabel("Enter student details and select 10 face images")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        
        # Name Input
        name_label = QLabel("Full Name")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter student's full name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: white;
            }
        """)
        
        # SAP ID Input
        sap_label = QLabel("SAP ID")
        sap_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        
        self.sap_input = QLineEdit()
        self.sap_input.setPlaceholderText("Enter student's SAP ID")
        self.sap_input.setStyleSheet("""
            QLineEdit {
                background-color: #F8F9FA;
                color: #2C3E50;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
                background-color: white;
            }
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(sap_label)
        layout.addWidget(self.sap_input)
        layout.addSpacing(10)
        
        # Image Selection
        self.image_status = QLabel("📷 No images selected")
        self.image_status.setAlignment(Qt.AlignCenter)
        self.image_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; padding: 15px;")
        
        self.select_btn = QPushButton("📁  Select 10 Images")
        self.select_btn.setFixedHeight(50)
        self.select_btn.setStyleSheet("""
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
        self.select_btn.clicked.connect(self.select_images)
        
        layout.addWidget(self.image_status)
        layout.addWidget(self.select_btn)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E0E0E0;
                border-radius: 8px;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #357ABD);
                border-radius: 8px;
            }
        """)
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Submit Button
        self.submit_btn = QPushButton("✅  Enroll Student")
        self.submit_btn.setFixedHeight(55)
        self.submit_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.submit_btn.clicked.connect(self.process_enrollment)
        
        layout.addWidget(self.submit_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_preview_panel(self):
        panel = QWidget()
        panel.setStyleSheet("QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        preview_title = QLabel("📷 Image Preview")
        preview_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50; background: transparent; padding-bottom: 10px; border-bottom: 2px solid rgba(0, 0, 0, 0.1); font-family: 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(preview_title)
        
        # Scroll area for image grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.image_grid = QWidget()
        self.image_grid.setStyleSheet("background: transparent;")
        self.image_grid_layout = QGridLayout()
        self.image_grid_layout.setSpacing(10)
        self.image_grid.setLayout(self.image_grid_layout)
        
        # Placeholder
        self.placeholder = QLabel("Selected images will appear here\n\nClick 'Select 10 Images' to choose photos")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("font-size: 16px; color: #95A5A6; background: #F8F9FA; border-radius: 10px; padding: 60px; font-family: 'Segoe UI', Arial, sans-serif;")
        self.image_grid_layout.addWidget(self.placeholder, 0, 0, 1, 2)
        
        scroll_area.setWidget(self.image_grid)
        layout.addWidget(scroll_area)
        
        panel.setLayout(layout)
        return panel
    
    def reset_form(self):
        """Reset all form fields"""
        self.name_input.clear()
        self.sap_input.clear()
        self.images = []
        self.image_status.setText("📷 No images selected")
        self.image_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; padding: 15px;")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("")
        self.submit_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        
        # Clear image grid
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.placeholder = QLabel("Selected images will appear here\n\nClick 'Select 10 Images' to choose photos")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("font-size: 16px; color: #95A5A6; background: #F8F9FA; border-radius: 10px; padding: 60px; font-family: 'Segoe UI', Arial, sans-serif;")
        self.image_grid_layout.addWidget(self.placeholder, 0, 0, 1, 2)
    
    def select_images(self):
        images, _ = QFileDialog.getOpenFileNames(
            self, "Select 10 Face Images", "", "Images (*.jpg *.png *.jpeg)"
        )
        
        if not images:
            return
        
        self.images = images
        
        if len(images) == 10:
            self.image_status.setText(f"✅ {len(images)} images selected")
            self.image_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; padding: 15px;")
        else:
            self.image_status.setText(f"⚠️ {len(images)} images (need exactly 10)")
            self.image_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #E74C3C; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; padding: 15px;")
        
        # Clear existing thumbnails
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add thumbnails
        for i, img_path in enumerate(images[:10]):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setStyleSheet("background: #F8F9FA; border-radius: 8px; padding: 5px;")
                
                row = i // 2
                col = i % 2
                self.image_grid_layout.addWidget(img_label, row, col)
        
        if len(images) != 10:
            styled_message(self, "Invalid Selection", f"Please select exactly 10 images. You selected {len(images)}.", "warning")
    
    def process_enrollment(self):
        name = self.name_input.text().strip()
        sap = self.sap_input.text().strip()
        
        if not name:
            styled_message(self, "Missing Information", "Please enter the student's name.", "warning")
            self.name_input.setFocus()
            return
        
        if not sap:
            styled_message(self, "Missing Information", "Please enter the student's SAP ID.", "warning")
            self.sap_input.setFocus()
            return
        
        if len(self.images) != 10:
            styled_message(self, "Missing Images", "Please select exactly 10 face images.", "warning")
            return
        
        folder_name = f"{name} ({sap})"
        student_path = os.path.join("dataset", folder_name)
        
        if os.path.exists(student_path):
            styled_message(self, "Student Exists", "A student with this name and SAP ID already exists.", "warning")
            return
        
        self.submit_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing images...")
        
        from PyQt5.QtWidgets import QApplication
        
        os.makedirs(student_path)
        embeddings = []
        
        for i, img_path in enumerate(self.images):
            self.progress_bar.setValue((i + 1) * 10)
            self.status_label.setText(f"Processing image {i + 1} of 10...")
            QApplication.processEvents()
            
            img = cv2.imread(img_path)
            emb = extract_embedding(img)
            if emb is None:
                import shutil
                shutil.rmtree(student_path)
                self.progress_bar.setVisible(False)
                self.status_label.setText("")
                self.submit_btn.setEnabled(True)
                self.select_btn.setEnabled(True)
                styled_message(self, "Face Detection Error",
                                    f"Could not detect a face in image {i + 1}.\nPlease ensure all images contain clear, visible faces.", "warning")
                return
            embeddings.append(emb)
        
        self.status_label.setText("Creating face embeddings...")
        QApplication.processEvents()
        
        mean_embedding = np.mean(embeddings, axis=0)
        
        self.status_label.setText("Saving images...")
        QApplication.processEvents()
        
        for img_path in self.images:
            cv2.imwrite(os.path.join(student_path, os.path.basename(img_path)), cv2.imread(img_path))
        
        self.status_label.setText("Updating database...")
        QApplication.processEvents()
        
        db_path = "face_db.pkl"
        face_db = {}
        
        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                face_db = pickle.load(f)
        
        face_db[folder_name] = [mean_embedding]
        
        with open(db_path, "wb") as f:
            pickle.dump(face_db, f)
        
        add_student_column(folder_name)
        
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Enrollment complete!")
        
        styled_message(self, "Success",
                                f"Student '{name}' has been enrolled successfully!\n\nSAP ID: {sap}\nImages processed: 10", "info")
        
        self.go_back.emit()


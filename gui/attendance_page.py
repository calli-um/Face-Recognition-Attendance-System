import os
import cv2
import pickle
import logging
from datetime import date

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

from utils.face_utils import recognize_face, preprocess_face, THRESHOLD
from utils.csv_utils import mark_attendance

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('attendance_debug.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)


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


# Lazy load heavy models
_yolo_model = None
_facenet_model = None


def get_yolo():
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        _yolo_model = YOLO("model.pt")
    return _yolo_model


def get_facenet():
    global _facenet_model
    if _facenet_model is None:
        from keras_facenet import FaceNet
        _facenet_model = FaceNet()
    return _facenet_model


class AttendancePage(QWidget):
    # Signal to notify when to go back to dashboard
    go_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.current_section = "Unknown"  # Default section
        # Use the SAME models from face_utils to ensure consistent embeddings!
        # This is critical - enrollment uses face_utils.embedder, so we must too
        from utils.face_utils import yolo, embedder
        self.yolo = yolo
        self.embedder = embedder
        self.setup_ui()

    def set_section(self, section):
        """Set the section for attendance marking"""
        self.current_section = section
        self.section_label.setText(f"📚 Section: {section}")
        self.section_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #4A90E2;
                background: rgba(74, 144, 226, 0.1);
                padding: 10px 20px;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

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

        # Left Panel - Controls
        left_panel = self.create_controls_panel()
        content_layout.addWidget(left_panel)

        # Right Panel - Preview
        right_panel = self.create_preview_panel()
        content_layout.addWidget(right_panel, 1)

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

        title_label = QLabel("Mark Attendance")
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

    def create_controls_panel(self):
        panel = QWidget()
        panel.setStyleSheet(
            "QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")
        panel.setFixedWidth(400)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        icon_label = QLabel("📸")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")

        title = QLabel("Process Attendance")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        subtitle = QLabel(
            "Upload a classroom image to automatically detect and recognize students")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "font-size: 14px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        # Section Label
        self.section_label = QLabel("📚 Section: Not Selected")
        self.section_label.setAlignment(Qt.AlignCenter)
        self.section_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #7F8C8D;
                background: rgba(127, 140, 141, 0.1);
                padding: 10px 20px;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.section_label)
        layout.addSpacing(20)

        self.select_btn = QPushButton("📁  Select Classroom Image")
        self.select_btn.setFixedHeight(60)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C42, stop:1 #FF6B35);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF9C52, stop:1 #FF7B45);
            }
            QPushButton:disabled {
                background: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.select_btn.clicked.connect(self.process_attendance)

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C42, stop:1 #FF6B35);
                border-radius: 8px;
            }
        """)
        self.progress_bar.setVisible(False)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            "font-size: 14px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()

        # Results Section
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet(
            "QFrame { background: #F0FFF0; border-radius: 10px; }")
        self.results_frame.setVisible(False)

        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(10)

        self.results_title = QLabel("📊 Results")
        self.results_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #27AE60; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        self.results_count = QLabel("")
        self.results_count.setStyleSheet(
            "font-size: 14px; color: #2C3E50; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        self.results_list = QLabel("")
        self.results_list.setWordWrap(True)
        self.results_list.setStyleSheet(
            "font-size: 13px; color: #7F8C8D; background: transparent; font-family: 'Segoe UI', Arial, sans-serif;")

        results_layout.addWidget(self.results_title)
        results_layout.addWidget(self.results_count)
        results_layout.addWidget(self.results_list)

        self.results_frame.setLayout(results_layout)
        layout.addWidget(self.results_frame)

        panel.setLayout(layout)
        return panel

    def create_preview_panel(self):
        panel = QWidget()
        panel.setStyleSheet(
            "QWidget { background: rgba(255, 255, 255, 0.95); border-radius: 15px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        preview_title = QLabel("🖼️ Image Preview")
        preview_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2C3E50; background: transparent; padding-bottom: 10px; border-bottom: 2px solid rgba(0, 0, 0, 0.1); font-family: 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(preview_title)

        self.preview_label = QLabel(
            "Select an image to see preview here\n\nProcessed image with detected faces will be displayed")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            "font-size: 16px; color: #95A5A6; background: #F8F9FA; border-radius: 10px; padding: 100px; font-family: 'Segoe UI', Arial, sans-serif;")
        self.preview_label.setMinimumHeight(400)

        layout.addWidget(self.preview_label, 1)

        panel.setLayout(layout)
        return panel

    def reset_form(self):
        """Reset all form fields"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("")
        self.results_frame.setVisible(False)
        self.select_btn.setEnabled(True)
        self.select_btn.setText("📁  Select Classroom Image")
        self.preview_label.setText(
            "Select an image to see preview here\n\nProcessed image with detected faces will be displayed")
        self.preview_label.setStyleSheet(
            "font-size: 16px; color: #95A5A6; background: #F8F9FA; border-radius: 10px; padding: 100px; font-family: 'Segoe UI', Arial, sans-serif;")

    def process_attendance(self):
        img_path, _ = QFileDialog.getOpenFileName(
            self, "Select Classroom Image", "", "Images (*.jpg *.png *.jpeg)"
        )
        if not img_path:
            return

        self.results_frame.setVisible(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Loading face database...")

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            with open("face_db.pkl", "rb") as f:
                face_db = pickle.load(f)
            logger.info("=" * 60)
            logger.info("FACE DATABASE LOADED")
            logger.info(f"Number of enrolled students: {len(face_db)}")
            for name, embeddings in face_db.items():
                logger.info(f"  - {name}: {len(embeddings)} embedding(s)")
                if embeddings:
                    logger.debug(f"    Embedding shape: {embeddings[0].shape}")
                    logger.debug(
                        f"    Embedding sample: {embeddings[0][:5]}...")
            logger.info("=" * 60)
        except FileNotFoundError:
            logger.error("face_db.pkl not found!")
            self.progress_bar.setVisible(False)
            self.status_label.setText("")
            self.select_btn.setEnabled(True)
            styled_message(
                self, "Error", "No students enrolled yet. Please enroll students first.", "warning")
            return

        self.progress_bar.setValue(20)
        self.status_label.setText("Reading image...")
        QApplication.processEvents()

        img = cv2.imread(img_path)
        logger.info(f"Image loaded: {img_path}, shape: {img.shape}")
        present_students = set()

        self.progress_bar.setValue(40)
        self.status_label.setText("Detecting faces...")
        QApplication.processEvents()

        # Run YOLO detection (exactly like old code)
        logger.info(f"Running YOLO detection with model: {self.yolo}")
        logger.info(f"Embedder being used: {self.embedder}")

        # Check if we're using the same embedder as face_utils
        from utils.face_utils import embedder as face_utils_embedder
        logger.info(f"Attendance embedder ID: {id(self.embedder)}")
        logger.info(f"face_utils embedder ID: {id(face_utils_embedder)}")
        logger.info(f"Same embedder? {self.embedder is face_utils_embedder}")
        results = self.yolo(img, verbose=False)

        self.progress_bar.setValue(50)

        # Count faces first to check if any detected
        total_faces = sum(
            len(r.boxes) if r.boxes is not None else 0 for r in results)
        logger.info(f"YOLO detected {total_faces} faces")

        if total_faces == 0:
            self.progress_bar.setVisible(False)
            self.status_label.setText("")
            self.select_btn.setEnabled(True)
            styled_message(
                self, "Error", "No faces detected in the image. Please try a different image.", "warning")
            return

        self.status_label.setText(
            f"Processing {total_faces} detected faces...")
        QApplication.processEvents()

        # Process faces exactly like old code
        recognized_count = 0
        face_index = 0
        logger.info(f"Recognition THRESHOLD: {THRESHOLD}")
        logger.info("-" * 60)

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                face_index += 1
                try:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    logger.debug(
                        f"Face {face_index}: bbox=({x1},{y1},{x2},{y2})")

                    face = img[y1:y2, x1:x2]
                    if face.size == 0:
                        logger.warning(
                            f"Face {face_index}: Empty face region, skipping")
                        continue

                    # Process face exactly like old code
                    face = preprocess_face(face)
                    logger.debug(
                        f"Face {face_index}: Preprocessed shape: {face.shape}")

                    emb = self.embedder.embeddings([face])[0]
                    logger.debug(
                        f"Face {face_index}: Embedding shape: {emb.shape}")
                    logger.debug(
                        f"Face {face_index}: Embedding sample: {emb[:5]}...")

                    # Use verbose mode for first 3 faces to see all distances
                    verbose = (face_index <= 3)
                    if verbose:
                        logger.info(f"Face {face_index}: Detailed comparison:")
                    name, dist = recognize_face(emb, face_db, verbose=verbose)
                    logger.info(
                        f"Face {face_index}: RESULT -> name='{name}', distance={dist:.4f}, threshold={THRESHOLD}")

                    if name != "Unknown":
                        present_students.add(name)
                        recognized_count += 1
                        logger.info(
                            f"Face {face_index}: ✓ RECOGNIZED as '{name}'")
                    else:
                        logger.info(
                            f"Face {face_index}: ✗ Unknown (distance {dist:.4f} > threshold {THRESHOLD})")

                    label = f"{name} ({dist:.2f})"
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    cv2.putText(img, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                except Exception as e:
                    # Log error but continue processing
                    logger.error(f"Face {face_index}: Error processing - {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

        logger.info("-" * 60)
        logger.info(
            f"FINAL RESULTS: {recognized_count} recognized out of {total_faces} faces")
        logger.info(f"Present students: {present_students}")
        logger.info("=" * 60)

        # Update progress after processing all faces
        self.progress_bar.setValue(90)
        QApplication.processEvents()

        self.progress_bar.setValue(95)
        self.status_label.setText("Saving attendance records...")
        QApplication.processEvents()

        # Try to mark attendance with section and error handling
        try:
            mark_attendance(present_students, self.current_section)
        except PermissionError:
            styled_message(self, "File Access Error",
                           "Cannot save attendance - the CSV file is currently open in another program.\n\n"
                           "Please close the file (e.g., in Excel) and try again.", "warning")
            self.progress_bar.setVisible(False)
            self.status_label.setText("")
            self.select_btn.setEnabled(True)
            return

        os.makedirs("attendance_images", exist_ok=True)
        output_path = f"attendance_images/{date.today()}_{self.current_section.replace(' ', '_')}.jpg"
        cv2.imwrite(output_path, img)

        # Update preview
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(img_rgb.data, w, h, bytes_per_line,
                       QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        preview_size = self.preview_label.size()
        scaled = pixmap.scaled(preview_size.width(
        ) - 40, preview_size.height() - 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.preview_label.setStyleSheet(
            "background: transparent; padding: 10px;")

        self.progress_bar.setValue(100)
        self.status_label.setText(
            f"✅ Attendance marked for {self.current_section}!")

        self.results_frame.setVisible(True)
        self.results_count.setText(
            f"Detected: {total_faces} faces | Recognized: {len(present_students)} students")

        if present_students:
            self.results_list.setText(
                f"Present: {', '.join(sorted(present_students))}")
        else:
            self.results_list.setText("No enrolled students recognized.")

        self.select_btn.setEnabled(True)
        self.select_btn.setText("📁  Process Another Image")

        styled_message(self, "Attendance Marked",
                       f"Attendance marked successfully for {self.current_section}!\n\nFaces detected: {total_faces}\nStudents recognized: {len(present_students)}\n\nImage saved to:\n{output_path}", "info")

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class ModernProgressDialog(QDialog):
    def __init__(self, message="Loading...", parent=None, max_value=0):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setFixedSize(400, 100)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold; color: black;")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setFixedHeight(20)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QProgressBar {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QProgressBar::chunk {
                background-color: #66b3ff;
                border-radius: 10px;
            }
        """)

        if max_value > 0:
            self.progress.setRange(0, max_value)
        else:
            self.progress.setRange(0, 0)  # indeterminate

    def update_progress(self, value, text=None):
        if text:
            self.label.setText(text)
        self.progress.setValue(value)


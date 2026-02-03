import sys
import DataLoaderThread as dl
from ProgressBar import ModernProgressDialog
import table_utils_functions as tu
from MenuBar import MenuBar
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget,
    QVBoxLayout, QWidget, QDialog, QLabel, QPushButton, QFileDialog
)
from MainWindow_ui import Ui_MainWindow


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.clear_csv_action = QAction("Clear table", self)
        self.add_csv_action = QAction("Add data", self)

        self.df = None
        self.width_thread = None
        self.loader_thread = None
        self.progress_dialog = None
        self.menu_bar = None
        self.current_row = 0

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Data Viewer and Analytics v1.0")
        self.setMinimumSize(600, 400)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Table
        self.table = QTableWidget()
        self.setStyleSheet("""
            QTableWidget{
                background-color: rgb(240,240,240);
                color: black;
                gridline-color: gray;
                font-size: 10pt;
            }           
        """)

        self.layout.addWidget(self.table)

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

    # ERROR
    def on_error(self, message):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        dialog = QDialog(self)
        dialog.setWindowTitle("Error")

        layout = QVBoxLayout(dialog)
        label = QLabel(f"Failed to load file:\n{message}")
        layout.addWidget(label)

        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.exec()

    # DATA LOADED
    def on_data_loaded(self, df):
        self.df = df
        self.current_row = 0

        self.table.clearContents()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: bold; font-size: 10pt; }"
        )
        self.table.verticalHeader().setStyleSheet(
            "QHeaderView::section { font-weight: bold; }"
        )

        self.clear_csv_action.setEnabled(True)
        QTimer.singleShot(0, self.insert_next_rows)

    # INSERT ROWS ASYNC
    def insert_next_rows(self):
        done = tu.populate_table_chunk(self.table, self.df, self.current_row)
        self.current_row += 30

        if done:
            self.progress_dialog.label.setText("Adjusting column widths...")
            QTimer.singleShot(50, self.finish_loading)
            return

        QTimer.singleShot(20, self.insert_next_rows)

    # COLUMN WIDTHS
    def finish_loading(self):
        font_metrics = self.table.fontMetrics()
        total_cols = self.df.shape[1]

        self.progress_dialog.progress.setRange(0, total_cols)

        self.width_thread = tu.ColumnWidthThread(self.df, font_metrics)
        self.width_thread.width_progress.connect(self.on_width_progress)
        self.width_thread.widths_computed.connect(self.apply_column_widths)
        self.width_thread.start()

    def on_width_progress(self, value, total):
        self.progress_dialog.update_progress(
            value,
            f"Adjusting column widths... ({value}/{total})"
        )

    def apply_column_widths(self, widths):
        for col, width in enumerate(widths):
            self.table.setColumnWidth(col, width)

        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    # SELECT FILE
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV/Excel File",
            "",
            "CSV/Excel Files (*.csv *.xlsx *.xls)"
        )

        if not file_name:
            return

        self.progress_dialog = ModernProgressDialog("Loading data...", self)
        self.progress_dialog.show()

        self.loader_thread = dl.DataLoaderThread(file_name)
        self.loader_thread.data_loaded.connect(self.on_data_loaded)
        self.loader_thread.error_occurred.connect(self.on_error)
        self.loader_thread.start()

    # CLEAR TABLE
    def clear_csv(self):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.clear_csv_action.setEnabled(False)

# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
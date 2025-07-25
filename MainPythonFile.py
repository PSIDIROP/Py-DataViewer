import sys
import data_loader_functions as dl
import table_utils_functions as tu
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidget,
    QVBoxLayout, QWidget, QProgressDialog
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
        self.current_row = 0

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Data Viewer and Calculator")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #e0f7fa;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.table = QTableWidget()
        self.table.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.layout.addWidget(self.table)

        self.create_menu()
        self.menuBar().setStyleSheet("background-color: #66b3ff;")

    def create_menu(self):
        file_menu = self.menuBar().addMenu("File")

        self.add_csv_action.triggered.connect(self.select_file)
        file_menu.addAction(self.add_csv_action)

        self.clear_csv_action.setEnabled(False)
        self.clear_csv_action.triggered.connect(self.clear_csv)
        file_menu.addAction(self.clear_csv_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV/Excel File", "", "CSV/Excel Files (*.csv *.xlsx *.xls)")
        if file_name:
            self.progress_dialog = QProgressDialog("Loading data...", None, 0, 0, self)
            self.progress_dialog.setWindowTitle("Please Wait")
            self.progress_dialog.setWindowModality(Qt.ApplicationModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.show()

            self.loader_thread = dl.DataLoaderThread(file_name)
            self.loader_thread.data_loaded.connect(self.on_data_loaded)
            self.loader_thread.error_occurred.connect(self.on_error)
            self.loader_thread.start()

    def on_data_loaded(self, df):
        self.df = df
        self.current_row = 0

        self.table.clearContents()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { font-weight: bold; font-size: 10pt; }")
        self.clear_csv_action.setEnabled(True)
        self.table.setSortingEnabled(True)

        QTimer.singleShot(0, self.insert_next_rows)

    # inserting rows asynchronously, by ColumnWidthThread
    def insert_next_rows(self):
        if tu.populate_table_chunk(self.table, self.df, self.current_row):
            if self.progress_dialog:
                self.progress_dialog.setLabelText("Adjusting column widths...")
                QTimer.singleShot(50, self.finish_loading)
            return

        self.current_row += 30
        QTimer.singleShot(30, self.insert_next_rows)

    # widths data, from ColumnWidthThread actions
    def apply_column_widths(self, widths):
        for col, width in enumerate(widths):
            self.table.setColumnWidth(col, width)
        if self.progress_dialog:
            self.progress_dialog.close()

    # after finish loading data to table, apply calculated (from Thread) widths
    def finish_loading(self):
        font_metrics = self.table.fontMetrics()
        self.width_thread = tu.ColumnWidthThread(self.df, font_metrics)
        self.width_thread.widths_computed.connect(self.apply_column_widths)
        self.width_thread.start()

    # Error loading data from file
    def on_error(self, message):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{message}")

    # Menu action
    def clear_csv(self):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.clear_csv_action.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
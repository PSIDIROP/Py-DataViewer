from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction


class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main = main_window   # reference στο MyApp

        self.create_menu()

    def create_menu(self):
        file_menu = self.addMenu("File")

        # Add Data
        self.main.add_csv_action = QAction("Add data", self)
        self.main.add_csv_action.triggered.connect(self.main.select_file)
        file_menu.addAction(self.main.add_csv_action)

        # Clear Table
        self.main.clear_csv_action = QAction("Clear table", self)
        self.main.clear_csv_action.setEnabled(False)
        self.main.clear_csv_action.triggered.connect(self.main.clear_csv)
        file_menu.addAction(self.main.clear_csv_action)

        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.main.close)
        file_menu.addAction(exit_action)
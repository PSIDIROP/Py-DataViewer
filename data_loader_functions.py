import os
import pandas as pd
from PySide6.QtCore import QThread, Signal


class DataLoaderThread(QThread):
    data_loaded = Signal(pd.DataFrame)
    error_occurred = Signal(str)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        try:
            ext = os.path.splitext(self.file_name)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(self.file_name)
            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(self.file_name)
            else:
                self.error_occurred.emit("Unsupported file format.")
                return
            self.data_loaded.emit(df)
        except Exception as e:
            self.error_occurred.emit(str(e))

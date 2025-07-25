from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt, QThread, Signal

class ColumnWidthThread(QThread):
    widths_computed = Signal(list)

    def __init__(self, df, font_metrics):
        super().__init__()
        self.df = df
        self.font_metrics = font_metrics

    def run(self):
        widths = []
        for col in range(self.df.shape[1]):
            max_width = self.font_metrics.horizontalAdvance(str(self.df.columns[col]) + "               ")
            for row in range(self.df.shape[0]):
                cell_text = str(self.df.iat[row, col])
                cell_width = self.font_metrics.horizontalAdvance(cell_text + "               ")
                max_width = max(max_width, cell_width)
            widths.append(max_width)
        self.widths_computed.emit(widths)

def adjust_column_widths(table, df):
    font_metrics = table.fontMetrics()
    for col, col_name in enumerate(df.columns):
        max_width = font_metrics.horizontalAdvance(col_name + "               ")
        for row in range(df.shape[0]):
            cell_text = str(df.iat[row, col])
            max_width = max(max_width, font_metrics.horizontalAdvance(cell_text + "               "))
        table.setColumnWidth(col, max_width)

def populate_table_chunk(table, df, start_row, rows_per_chunk=30):
    current_row = start_row
    total_rows = len(df)

    for _ in range(rows_per_chunk):
        if current_row >= total_rows:
            break
        for col, _ in enumerate(df.columns):
            value = str(df.iat[current_row, col])
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(current_row, col, item)
        current_row += 1

    return current_row >= total_rows
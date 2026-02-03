from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt, QThread, Signal

# Column Width Calculation Thread
class ColumnWidthThread(QThread):
    width_progress = Signal(int, int)   # current column, total columns
    widths_computed = Signal(list)

    def __init__(self, df, font_metrics):
        super().__init__()
        self.df = df
        self.font_metrics = font_metrics

    def run(self):
        widths = []
        total_cols = self.df.shape[1]

        for col in range(total_cols):
            # Header width
            max_width = self.font_metrics.horizontalAdvance(str(self.df.columns[col]))

            # Cell widths
            for row in range(self.df.shape[0]):
                cell_text = str(self.df.iat[row, col])
                cell_width = self.font_metrics.horizontalAdvance(cell_text)
                max_width = max(max_width, cell_width)

            max_width += 20  # padding
            widths.append(max_width)

            # Emit progress
            self.width_progress.emit(col + 1, total_cols)

        self.widths_computed.emit(widths)

# Populate table chunk by chunk
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
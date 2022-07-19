from turtle import pen
from visualization.pdw.capsulation.cell import Cell
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import numpy as np

from visualization.visualizationparams import DataPacket

class Capsulator(QObject):
    cell_count_v = 100
    cell_count_h = 400
    capsulated_data_is_reaady = pyqtSignal(DataPacket)
    def __init__(self):
        super(Capsulator, self).__init__()
        self.map = []
        for i in range(self.cell_count_h+1):
            row_list = []
            for j in range(self.cell_count_v+1):
                cell = Cell(i, j)
                row_list.append(cell)
            self.map.append(row_list)

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()
            
    def clear(self):
        self.map.clear()

    def feed(self, data_packet):
        if len(data_packet.key) != 0 and len(data_packet.data) != 0:
            min_time = min(data_packet.key)
            max_time = max(data_packet.key)
            min_data = min(data_packet.data)
            max_data = max(data_packet.data)

            time_length = max_time - min_time
            
            if max_time == min_time:
                time_length = min_time

            data_length = max_data - min_data

            if max_data == min_data:
                data_length = min_data

            time_resolution = time_length/self.cell_count_h
            data_resolution = data_length/self.cell_count_v

            for x, y in zip(data_packet.key, data_packet.data):
                min_row_indx =(min_time / time_resolution).astype(np.int)
                min_col_indx = (min_data / data_resolution).astype(np.int)
                row = (x / time_resolution).astype(np.int)
                col = (y / data_resolution).astype(np.int)
                modified_row = row - min_row_indx
                modified_col = col - min_col_indx
                current_cell = self.map[modified_row][modified_col]
                current_cell.x_start = row * time_resolution
                current_cell.x_end = (row+1) * time_resolution
                current_cell.y_start = col * data_resolution
                current_cell.y_end = (col+1) * data_resolution
                current_cell.feed()

            final_data_key = []
            final_data_val = []

            for row  in self.map:
                for item in row:
                    if item.is_trigged:
                        key, val = item.output()
                        final_data_key.append(key)
                        final_data_val.append(val)

            final_data = DataPacket()
            final_data.id = data_packet.id
            final_data.key = np.array(final_data_key)
            final_data.data = np.array(final_data_val)
            self.capsulated_data_is_reaady.emit(final_data)
    
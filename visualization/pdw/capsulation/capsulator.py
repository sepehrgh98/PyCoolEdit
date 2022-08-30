from tarfile import FIFOTYPE
from time import time
from turtle import pen
from visualization.pdw.capsulation.cell import Cell
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QElapsedTimer
import numpy as np
from multiprocessing import Pool
from functools import partial


from visualization.visualizationparams import DataPacket

def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def do_compression(val, key, cell_count_h, cell_count_v):

    map = []
    final_data_key = []
    final_data_val = []

    if len(key) != 0 and len(val[1]) != 0:
        data_val = val[1]
        min_time = min(key)
        max_time = max(key)
        min_data = min(data_val)
        max_data = max(data_val)

        time_length = max_time - min_time

        if max_time == min_time:
            time_length = min_time

        data_length = max_data - min_data

        if max_data == min_data:
            data_length = min_data

        time_resolution = time_length/cell_count_h
        data_resolution = data_length/cell_count_v

        for i in range(cell_count_h+1):
            row_list = []
            for j in range(cell_count_v+1):
                cell = Cell(i, j)
                cell.x_start = j * time_resolution
                cell.x_end = (j+1) * time_resolution
                cell.y_start = i * data_resolution
                cell.y_end = (i+1) * data_resolution
                row_list.append(cell)
            map.append(row_list)

        timer = QElapsedTimer()
        timer.start()
        for x, y in zip(key, data_val):
            min_row_indx =(min_time / time_resolution).astype(np.int)
            min_col_indx = (min_data / data_resolution).astype(np.int)
            row = (x / time_resolution).astype(np.int)
            col = (y / data_resolution).astype(np.int)
            modified_row = row - min_row_indx
            modified_col = col - min_col_indx
            current_cell = map[modified_row][modified_col]
            if not current_cell.is_trigged:
                current_cell.feed()
                key, val = current_cell.output()
                final_data_key.append(row)
                final_data_val.append(col)

    print(timer.elapsed())

    final_data = DataPacket()
    final_data.key = np.array(final_data_key)
    final_data.data = np.array(final_data_val)
    return final_data



class Capsulator(QObject):
    cell_count_v = 100
    cell_count_h = 400
    capsulated_data_is_reaady = pyqtSignal(DataPacket)
    def __init__(self):
        super(Capsulator, self).__init__()


        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()
            
    def clear(self):
        self.map.clear()

    def feed(self, data_dict):
        Toa = data_dict['TOA']
        data_dict.pop('TOA')
        data_dict.pop('CW')
        items = list(data_dict.items())
        pool = Pool(processes=5)
        for i, output in enumerate(pool.imap(partial(do_compression, key=Toa, cell_count_h=self.cell_count_h, cell_count_v=self.cell_count_v), items), 1):
            output.id = i
            # self.capsulated_data_is_reaady.emit(output)

    
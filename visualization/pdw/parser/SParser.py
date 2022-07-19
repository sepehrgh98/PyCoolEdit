from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
import numpy as np
from joblib import Parallel, delayed, cpu_count
from tqdm import tqdm


def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class SParser(QObject):
    columns_defined = pyqtSignal(list)
    data_packet_is_ready = pyqtSignal(dict)
    def __init__(self) -> None:
        super(SParser, self).__init__()
        self.columns = []
        self.initilize_data = True
        self.parsed_data = {}
        self.progress = 0
        self.raw_data = []

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(list, bool, float)
    def prepare_data(self, data_list, eof, file_total_size):
        self._set_columns(data_list)
        self.parse(data_list)
        # self.progress = self.progress + (len(data_list)/file_total_size)
        # print(self.progress*100, len(data_list), file_total_size)
        self.raw_data.append(data_list)
        if eof :
            self.calculate_rri()
            self.data_packet_is_ready.emit(self.parsed_data)
            # self.progress = 0

    
    @pyqtSlot(tuple, tuple)
    def prepare_requested_data(self, time_range, value_range):
        if time_range == (-1, -1) and value_range == (-1, -1):
            first_x_index = 0
            last_x_index = len(self.parsed_data['TOA']) - 1
        else:
            first_x_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[0])
            last_x_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[1])
        requested_data = dict()
        for key, val in self.parsed_data.items():
            requested_data[key] = val[first_x_index:last_x_index]
        self.data_packet_is_ready.emit(requested_data)


    def _set_columns(self, data_list):
        if not self.columns:
            if self._has_columns(data_list):
                self.columns = data_list[0].split("\n")[0].split()[1:]
                self.columns.append('RRI')
                self.columns.append('RRF')
                self.columns_defined.emit(self.columns)
            else:
                print("ERORRRRRRR!")

    def _has_columns(self, received_data) -> bool:
        first_line = received_data[0]
        if first_line[0] != "%":
            return False
        return True

    def parse(self, data_list):
        if self.initilize_data:
            self._init_data()
            self.initilize_data = False 
        for line in data_list[2:]:
            cols = line.split()
            for i in range(len(cols)):
                col_name = self.columns[i]
                self.parsed_data[col_name] = np.append(self.parsed_data[col_name], [float(cols[i])])

    def _init_data(self) -> None:
        for column in self.columns:
            self.parsed_data[column] = np.ndarray(0)

    def calculate_rri(self):
        time_data = self.parsed_data['TOA']
        RRI = []
        RRF = []
        for i in range(len(time_data)-1):
            diff = time_data[i+1] - time_data[i]
            RRI.append(diff)
            RRF.append(1000000/diff)
            if i == len(time_data)-2:
                RRI.append(RRI[-1])
                RRF.append(1000000/RRI[-1])
        self.parsed_data['RRI'] = RRI
        self.parsed_data['RRF'] = RRF


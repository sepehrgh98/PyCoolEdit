from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
from visualization.visualizationparams import SignalDataPacket
from visualization.Signal.mhdll import MHDatReader
from visualization.Signal.mhreaderv2 import readFile
import os
import numpy as np
def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

class SignalController(QObject):
    data_packet_is_ready = pyqtSignal(list)

    def __init__(self):
        super(SignalController, self).__init__()
        # variables
        self.sampling_rate = 1000000
        self.file_info = {}
        self.total_range = ()
        self.key_data = []

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(dict, tuple)
    def on_info_received(self, file_info, data_range):
        self.file_info = file_info
        self.total_range = data_range
        # for i in range(int((os.path.getsize(self.file_info["file"])/2)/self.file_info["channels"])):
        #     self.key_data.append(i)
        self.get_data(self.total_range)


    @pyqtSlot(tuple)
    def get_data(self, data_range):
        if data_range:
            start_range = round(data_range[0])
            end_range = round(data_range[1])
        else:
            start_range = 0
            end_range = (os.path.getsize(self.file_info["file"])/2)/self.file_info["channels"]
        res = readFile(self.file_info["file"], start_range, end_range, self.file_info["channels"], self.sampling_rate)
        data_list = []
        key_data = []
        data_point = start_range
        for i in range(start_range, start_range+len(res[0])):
            key_data.append(i)
            data_point += self.sampling_rate
        channel_count = 1
        # start_index = find_nearest_value_indx(self.key_data, start_range)
        # end_index = find_nearest_value_indx(self.key_data, end_range)
        # key_data = self.key_data[start_index:end_index]
        for ch in res:
            final_data = SignalDataPacket()
            final_data.id = channel_count
            final_data.key = key_data
            final_data.data = ch
            data_list.append(final_data)
        self.data_packet_is_ready.emit(data_list)

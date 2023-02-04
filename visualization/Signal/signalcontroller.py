from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
from visualization.visualizationparams import SignalDataPacket
from visualization.Signal.readFile_final import Read_file
import os
import numpy as np
def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

class SignalController(QObject):
    data_packet_is_ready = pyqtSignal(list)
    range_requested = pyqtSignal(int , int, int, int) # start, stop , NOF channels , rate
    def __init__(self):
        super(SignalController, self).__init__()
        # module
        self.signal_reader = None

        # variables
        self.sampling_rate = 1000000
        self.file_info = {}
        self.total_range = ()
        self.key_data = []

        # moving to thread
        self.objThread = QThread(self)
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(dict, tuple)
    def on_info_received(self, file_info, data_range):
        self.clear()
        self.file_info = file_info
        self.total_range = data_range
        self.signal_reader = Read_file(self.file_info["file"])
        self.range_requested.connect(self.signal_reader.fileReader)
        self.signal_reader.data_is_ready.connect(self.prepare_packet)
        self.get_data(self.total_range)



    @pyqtSlot(tuple)
    def get_data(self, data_range):
        if not self.signal_reader:
            return

        if data_range:
            start_range = int(round(data_range[0]))
            end_range = int(round(data_range[1]))
        else:
            start_range = 0
            end_range = int((os.path.getsize(self.file_info["file"])/2)/self.file_info["channels"])

        self.range_requested.emit(start_range, end_range, self.file_info["channels"], self.sampling_rate)


    @pyqtSlot(list)
    def prepare_packet(self, data_list):
        final_list = []
        key_data = data_list[-1]
        channel_list = data_list[:-1]
        channel_count = 1
        for ch in channel_list:
            final_data = SignalDataPacket()
            final_data.id = channel_count
            final_data.key = key_data
            final_data.data = ch
            final_list.append(final_data)
        self.data_packet_is_ready.emit(final_list)

    def clear(self):
        self.signal_reader = None
        self.file_info = {}
        self.total_range = ()
        self.key_data = []

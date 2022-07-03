from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from visualization.Signal.mhfilereader import MHDatReader
from visualization.visualizationparams import SignalDataPacket


class SignalController(QObject):
    data_packet_is_ready = pyqtSignal(list)

    def __init__(self):
        super(SignalController, self).__init__()
        # variables
        self.sampling_rate = 10000

    @pyqtSlot(dict, tuple)
    def get_data(self, file_info, data_range):
        mhd = MHDatReader(file_info["file"], file_info["channels"])
        if data_range:
            start_range = data_range[0]
            end_range = data_range[1]
        else:
            start_range = 0
            end_range = 100000000
            print(mhd.get_file_total_size())
            # end_range = mhd.get_file_total_size()-10
        res = mhd.get(start_range, end_range, self.sampling_rate)
        data_list = []
        key_data = []
        data_point = start_range
        for _ in range(len(res[0])):
            key_data.append(data_point)
            data_point += self.sampling_rate
        channel_count = 1
        for ch in res:
            final_data = SignalDataPacket()
            final_data.id = channel_count
            final_data.key = key_data
            final_data.data = ch
            data_list.append(final_data)
        self.data_packet_is_ready.emit(data_list)

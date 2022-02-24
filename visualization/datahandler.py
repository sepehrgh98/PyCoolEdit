from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from parser.create_parser import DataParser
from reader.create_reader import DataCreator
from visualizationparams import DataPacket


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket)

    def __init__(self):
        super(DataHandler, self).__init__()
        self.reader = DataCreator()
        self.file_path_changed.connect(self.reader.set_file_path)
        self.parser = DataParser()
        # self.reader.reading_batch_file_is_ready.connect(self.parser.set_data)
        self.parser.data_is_ready.connect(self.packetize_data)

    @pyqtSlot(dict)
    def packetize_data(self, data):
        final_data = DataPacket()
        # final_data.data = data.value
        self.final_data_is_ready.emit(final_data)


@pyqtSlot(str)
def set_file_path(self, file_path):
    self.file_path_changed.emit(file_path)

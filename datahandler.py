from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from parser.dataparser import DataParser
from reader.create_reader import DataCreator
from visualizationparams import DataPacket


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket)
    columns_defined = pyqtSignal(dict)

    def __init__(self):
        super(DataHandler, self).__init__()
        self.reader = DataCreator()
        self.file_path_changed.connect(self.reader.set_file_path)
        self.parser = DataParser()
        self.reader.reading_batch_file_is_ready.connect(self.parser.set_data)
        self.parser.columns_defined.connect(self.define_columns)
        self.parser.data_is_ready.connect(self.packetize_data)
        self.columns = dict()

    @pyqtSlot(list)
    def define_columns(self, columns):
        cols = dict()
        for i in range(len(columns)):
            cols[i] = columns[i]
        self.columns_defined.emit(columns)

    @pyqtSlot(dict)
    def packetize_data(self, data):
        # datas = []
        for name, val in data:
            final_data = DataPacket()
            final_data.data = val
            final_data.key = name
            final_data.id = list(data.keys())[list(data.values()).index(name)]
            print(final_data)
            self.final_data_is_ready.emit(final_data)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)

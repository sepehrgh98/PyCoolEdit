from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from visualization.parser.dataparser import DataParser
from visualization.reader.create_reader import DataCreator
from visualization.visualizationparams import DataPacket


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket)
    columns_defined = pyqtSignal(dict)

    def __init__(self):
        super(DataHandler, self).__init__()
        self.reader = DataCreator(1000)
        self.file_path_changed.connect(self.reader.set_file_path)
        self.parser = DataParser()
        self.reader.reading_batch_file_is_ready.connect(self.parser.set_data)
        self.parser.columns_defined.connect(self.define_columns)
        self.parser.data_is_ready.connect(self.packetize_data)
        self.columns = dict()

    @pyqtSlot(list)
    def define_columns(self, columns):
        cols = dict()
        for i in range(1, len(columns)):
            cols[i] = columns[i]
        self.columns = cols
        # print("collls: ", self.columns)
        self.columns_defined.emit(cols)

    @pyqtSlot(dict)
    def packetize_data(self, data):
        for name, val in data.items():
            if name != "TOA":
                final_data = DataPacket()
                final_data.data = val
                final_data.key = data['TOA']
                final_data.id = list(self.columns.keys())[list(self.columns.values()).index(name)]
                # print(final_data)
                self.final_data_is_ready.emit(final_data)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)

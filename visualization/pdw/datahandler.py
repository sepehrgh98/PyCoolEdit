from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
from visualization.pdw.parser.SParser import SParser
from visualization.pdw.reader.SReader import SReader
from visualization.visualizationparams import ChannelUnit, DataPacket
from visualization.pdw.capsulation.capsulator import Capsulator
import numpy as np

class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket)
    columns_defined = pyqtSignal(dict)
    dataRequest = pyqtSignal(tuple, tuple)  # time Range & value Range

    def __init__(self):
        super(DataHandler, self).__init__()

        # majules
        self.reader = SReader()
        self.parser = SParser()

        # connections
        self.file_path_changed.connect(self.reader.set_file_path)
        # self.reader.reading_batch_file_is_ready.connect(self.parser.set_data)
        # self.reader.batch_is_ready.connect(self.parser.set_data)
        self.reader.batch_is_ready.connect(self.parser.prepare_data)
        self.parser.columns_defined.connect(self.define_columns)
        self.parser.data_packet_is_ready.connect(self.packetize_data)
        # self.capsulator.capsulated_data_is_reaady.connect(self.final_data_is_ready)
        self.dataRequest.connect(self.parser.prepare_requested_data)
        

        # variables
        self.columns = dict()
        self.capsulators = []

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(list)
    def define_columns(self, columns):
        columns.remove("CW")
        for i in range(1, len(columns)):
            self.columns[i] = columns[i]
        self.columns_defined.emit(self.columns)

    @pyqtSlot(dict)
    def packetize_data(self, data):
        for name, val in data.items():
            if name != "TOA" and name != "CW":
                final_data = DataPacket()
                final_data.data = val
                final_data.key = data['TOA']
                final_data.id = list(self.columns.values()).index(name) + 1
                capsulator = Capsulator()
                capsulator.capsulated_data_is_reaady.connect(self.final_data_is_ready)
                self.capsulators.append(capsulator)
                # capsulator.feed(final_data)
                self.final_data_is_ready.emit(final_data)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)




        

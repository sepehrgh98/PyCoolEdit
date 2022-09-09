from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread, QElapsedTimer
from visualization.pdw.parser.SParser import SParser
from visualization.pdw.reader.SReader import SReader
from visualization.visualizationparams import ChannelUnit, DataPacket
from visualization.pdw.capsulation.capsulator import Capsulator
from visualization.visualizationparams import Channel_id_to_name
import time


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket)
    columns_defined = pyqtSignal(dict)
    selectDataRequested = pyqtSignal(str, tuple, tuple)  # time Range & value range
    deleteSelectedRequested = pyqtSignal(list) # list of tuples 
    progress_is_ready = pyqtSignal(dict)
    clearRequested = pyqtSignal()
    lineCursorDataRequested = pyqtSignal(float)
    markerLineResultIsReady = pyqtSignal(dict)
    pointMarkerDataRequested = pyqtSignal(str, tuple)
    dataIsReadyForCapsulation = pyqtSignal(dict)
    pointMarkerResultIsReady = pyqtSignal(tuple)
    totalSizeIsReady = pyqtSignal(int)


    def __init__(self):
        super(DataHandler, self).__init__()

        # majules
        self.reader = SReader()
        self.parser = SParser()
        self.capsulator = Capsulator()

        # connections
        self.file_path_changed.connect(self.reader.set_file_path)
        self.selectDataRequested.connect(self.capsulator.prepare_requested_select_data)
        # self.deleteSelectedRequested.connect(self.parser.on_delete_selected_req)
        self.clearRequested.connect(self.reader.clear)
        self.clearRequested.connect(self.parser.clear)
        self.clearRequested.connect(self.capsulator.clear)
        self.lineCursorDataRequested.connect(self.capsulator.single_row_req)
        self.pointMarkerDataRequested.connect(self.capsulator.single_data_req)
        self.dataIsReadyForCapsulation.connect(self.capsulator.feed)

        self.reader.batch_is_ready.connect(self.parser.prepare_data)
        self.reader.progress_is_ready.connect(self.progress_is_ready)

        self.parser.columns_defined.connect(self.define_columns)
        self.parser.data_packet_is_ready.connect(self.packetize_data_cap_mod)
        self.parser.progress_is_ready.connect(self.progress_is_ready)
        self.parser.totalSizeIsReady.connect(self.totalSizeIsReady)

        # self.capsulator.capsulated_data_is_reaady.connect(self.final_data_is_ready)
        self.capsulator.capsulated_data_is_reaady.connect(self.send_capsulated_data)
        self.capsulator.markerLineResultIsReady.connect(self.markerLineResultIsReady)
        self.capsulator.pointMarkerResultIsReady.connect(self.pointMarkerResultIsReady)
        self.capsulator.progress_is_ready.connect(self.progress_is_ready)


        self.timer = QElapsedTimer()
        self.timer.start()
        

        # variables
        self.columns = dict()

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(dict)
    def define_columns(self, columns):
        if "CW" in columns:
            columns.pop("CW")
        if "No." in columns:
            columns.pop("No.")
        for i in range(1, len(columns.keys())):
            channel = list(columns.keys())[i]
            unit = list(columns.values())[i]
            self.columns[i] = (channel,unit)
        self.columns_defined.emit(self.columns)

    @pyqtSlot(dict)
    def packetize_data_cap_mod(self, data):
        self.dataIsReadyForCapsulation.emit(data)
    
    @pyqtSlot(dict)
    def send_capsulated_data(self, data_pack):
        for name, pack in data_pack.items():
            self.final_data_is_ready.emit(pack)

    @pyqtSlot(dict)
    def packetize_data(self, data):
        for name, val in data.items():
            if name != "TOA" and name != "CW":
                final_data = DataPacket()
                final_data.data = val
                final_data.key = data['TOA']
                myval = list(self.columns.values())
                final_data.id = [myval.index(item)+ 1 for item in myval if item[0] == name][0]
                Channel_id_to_name[final_data.id] = name
                self.final_data_is_ready.emit(final_data)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)
    
    @pyqtSlot()
    def clear(self):
        self.columns = dict()
        # self.capsulators = []
        self.clearRequested.emit()



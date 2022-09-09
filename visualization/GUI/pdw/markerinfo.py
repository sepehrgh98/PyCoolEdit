import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from visualization.visualizationparams import Channel_id_to_name

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'markerinfoui.ui'))[0]

class MarkerInfo(QWidget, Form):
    def __init__(self):
        super(MarkerInfo, self).__init__()
        self.setupUi(self)
        self.lineEdit_list = []


    def setup_channels(self, header):
        for key, val in header.items():
            label = QLabel(self.markerInfoGroupBox)
            label.setText(str(val[0])+': ')
            lineEdit = QLineEdit(self.markerInfoGroupBox)
            lineEdit.setReadOnly(True)
            self.lineEdit_list.append((key,lineEdit))
            self.markerInfoLayout.addRow(label, lineEdit)

    @pyqtSlot(dict)
    def feed(self, data_packet):
        for lineEdit in self.lineEdit_list:
            ch_name = Channel_id_to_name[lineEdit[0]]
            val = data_packet[ch_name]
            lineEdit[1].setText(str(round(val,2)))

    @pyqtSlot(tuple)
    def feed_point_marker(self, data):
        self.timeLineEdit.setText(str(round(data[0],2)))
        self.valLineEdit.setText(str(round(data[1],2)))

    def clear(self):
        for i in reversed(range(self.markerInfoLayout.count())): 
            self.markerInfoLayout.itemAt(i).widget().setParent(None)
        self.lineEdit_list.clear()
        self.timeLineEdit.setText(" ")
        self.valLineEdit.setText(" ")

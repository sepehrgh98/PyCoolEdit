import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'signal', 'signalinformationui.ui'))[0]


class SignalInformationForm(QWidget, Form):
    file_info_is_ready = pyqtSignal(dict)

    def __init__(self):
        super(QWidget, self).__init__()
        self.setupUi(self)

        self.applyBtn.clicked.connect(self.applyBtn_clicked)

    def applyBtn_clicked(self):
        number_of_channels = int(self.channelNumberComboBox.currentText())
        data_sign = self.dataSignComboBox.currentText()
        file_info = {"number_of_channels": number_of_channels, "data_sign": data_sign}
        self.file_info_is_ready.emit(file_info)
        self.close()

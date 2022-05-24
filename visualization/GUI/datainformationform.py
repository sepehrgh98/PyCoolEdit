import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'datainformationbox.ui'))[0]


class DataInformationForm(QWidget, Form):

    def __init__(self):
        super(DataInformationForm, self).__init__()
        self.setupUi(self)
        self.fileNameLabel.setStyleSheet('color: red')
        self.totalDataNumberLabel.setStyleSheet('color: red')
        self.selectedDataNumberLabel.setStyleSheet('color: red')

    @pyqtSlot(str)
    def set_file_name(self, path):
        self.fileNameLabel.setText(os.path.basename(path))

    @pyqtSlot(int)
    def set_total_data_size(self, size):
        self.totalDataNumberLabel.setText(str(size))

    @pyqtSlot(int)
    def set_select_data_size(self, size):
        self.selectedDataNumberLabel.setText(str(size))

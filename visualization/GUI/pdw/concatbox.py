from operator import concat
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox
from PyQt5.QtCore import pyqtSignal

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'concatboxui.ui'))[0]


class ConcatBox(QWidget, Form):
    concatListIsReady = pyqtSignal(list)
    def __init__(self):
        super(ConcatBox, self).__init__()
        self.setupUi(self)
        self.applyBtn.clicked.connect(self.handle_concatination)
        self.channels = []

    def setup_channel(self, header):
        for id, name in header.items():
            ch_label = QLabel(self.concatGroupBox)
            ch_label.setText(name)
            self.channel_checkBox = QCheckBox(self.concatGroupBox)
            self.channel_checkBox.setAccessibleName(str(id))
            self.channels.append(self.channel_checkBox)
            self.concatBoxLayout.addRow(ch_label, self.channel_checkBox)

    def handle_concatination(self):
        concat_list = []
        for ch in self.channels:
            if ch.isChecked():
                concat_list.append(ch.accessibleName())
        self.concatListIsReady.emit(concat_list)





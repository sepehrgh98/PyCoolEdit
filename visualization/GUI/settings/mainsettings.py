import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from visualization.visualizationparams import ShowPolicy

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'settings', 'mainsettingsui.ui'))[0]

class MainSettings(QWidget, Form):
    showPolicyChanged = pyqtSignal(ShowPolicy)
    def __init__(self):
        super(MainSettings, self).__init__()
        self.setupUi(self)
        self.scrollRadioButton.toggled.connect(self.on_ShowPolicy_checked)
        self.nonScrollRadioButton.toggled.connect(self.on_ShowPolicy_checked)

    def on_ShowPolicy_checked(self, _):
        rbtn = self.sender()
        if rbtn.isChecked() == True:
            if self.scrollRadioButton == rbtn:
                self.showPolicyChanged.emit(ShowPolicy.scroll)
            else:
                self.showPolicyChanged.emit(ShowPolicy.non_scroll)

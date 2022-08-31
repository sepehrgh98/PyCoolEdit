import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from visualization.visualizationparams import ShowPolicy, PlotType

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'settings', 'mainsettingsui.ui'))[0]

class MainSettings(QWidget, Form):
    showPolicyChanged = pyqtSignal(ShowPolicy)
    showOmniDfChanged = pyqtSignal(PlotType)
    def __init__(self):
        super(MainSettings, self).__init__()
        self.setupUi(self)
        self.scrollRadioButton.toggled.connect(self.on_ShowPolicy_checked)
        self.nonScrollRadioButton.toggled.connect(self.on_ShowPolicy_checked)
        # self.pointShowRadioButton.toggled.connect(self.on_OmniDf_show_checked)
        # self.stemShowRadioButton.toggled.connect(self.on_OmniDf_show_checked)


    def on_ShowPolicy_checked(self, _):
        rbtn = self.sender()
        if rbtn.isChecked() == True:
            if self.scrollRadioButton == rbtn:
                self.showPolicyChanged.emit(ShowPolicy.scroll)
            elif self.nonScrollRadioButton == rbtn:
                self.showPolicyChanged.emit(ShowPolicy.non_scroll)

    def on_OmniDf_show_checked(self, _):
        rbtn = self.sender()
        if rbtn.isChecked() == True:
            if self.pointShowRadioButton == rbtn:
                self.showOmniDfChanged.emit(PlotType.point)
            elif self.stemShowRadioButton:
                self.showOmniDfChanged.emit(PlotType.stem)

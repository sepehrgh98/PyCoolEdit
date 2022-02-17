from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from GUI.PDWInformationBox import PDWInformationBoxForm
from GUI.PDWTools import PDWToolsForm
import os

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'PDWUi.ui'))[0]

class PDWForm(QMainWindow, Form):
    def __init__(self):
        super(PDWForm, self).__init__()
        self.setupUi(self)

        self.infBoxWidget = PDWInformationBoxForm()
        self.toolsWidget = PDWToolsForm()
        self.rightFrameLayout.addWidget(self.toolsWidget)
        self.rightFrameLayout.addWidget(self.infBoxWidget)
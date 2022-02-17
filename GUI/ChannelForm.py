from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
import os

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'ChannelUi.ui'))[0]


class ChannelForm(QWidget, Form):
    def __init__(self):
        super(ChannelForm, self).__init__()
        self.setupUi(self)

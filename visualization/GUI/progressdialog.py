from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot
import os
from PyQt5 import uic

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'progressdialogform.ui'))[0]


class ProgressDialog(QDialog, Form):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setupUi(self)

    @pyqtSlot(dict)
    def feed(self, progress):
        for id, val in progress.items():
            if id == 0 :
                self.readingProgressBar.setValue(val)
            elif id == 1 :
                self.parsingProgressBar.setValue(val)
            elif id == 2 : 
                self.visualizingProgressBar.setValue(val)

        



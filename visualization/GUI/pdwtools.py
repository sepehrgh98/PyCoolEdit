import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QFileDialog

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'pdwtools.ui'))[0]


class PDWToolsForm(QWidget, Form):
    # signals
    filePathChanged = pyqtSignal(str)

    def __init__(self):
        super(PDWToolsForm, self).__init__()
        self.setupUi(self)

        # connections
        self.selectFileBtn.clicked.connect(self.getFilePath)
        self.filePathLineEdit.textChanged.connect(self.setFilePath)

    def getFilePath(self):
        filePath = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.txt);")[0]
        self.filePathLineEdit.setText(filePath)

    def setFilePath(self, text):
        self.filePathChanged.emit(text)

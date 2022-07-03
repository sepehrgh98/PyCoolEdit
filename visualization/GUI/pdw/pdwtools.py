import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QFileDialog

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'pdwtools.ui'))[0]


class PDWToolsForm(QWidget, Form):
    # signals
    filePathChanged = pyqtSignal(str)
    # dataRequested = pyqtSignal()
    selectBtnPressed = pyqtSignal(bool)
    radarRequested = pyqtSignal()

    def __init__(self):
        super(PDWToolsForm, self).__init__()
        self.setupUi(self)

        # variables
        self.file_path = None

        # configs
        self.selectFileBtn.setToolTip('Select Pdw File')
        self.showDataBtn.setToolTip('Show Data')
        self.newRadarBtn.setToolTip('New Radar')
        self.selectBtn.setToolTip('Select Data')
        self.selectAllBtn.setToolTip('Select All Data')
        self.clearBtn.setToolTip('Clear All Channels')

        # connections
        self.selectFileBtn.clicked.connect(self.get_file_path)
        self.selectBtn.clicked.connect(self.selectBtnPressed)
        self.newRadarBtn.clicked.connect(self.radarRequested)

    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.txt);")[0]
        if self.file_path != new_path:
            self.file_path = new_path
            self.filePathChanged.emit(self.file_path)

    def set_file_path(self, text):
        self.filePathChanged.emit(text)

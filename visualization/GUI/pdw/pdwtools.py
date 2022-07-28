import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QButtonGroup, QLabel
from PyQt5.QtGui import QPixmap
from visualization.GUI.pdw.concatbox import ConcatBox

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'pdwtools.ui'))[0]


class PDWToolsForm(QWidget, Form):
    # signals
    filePathChanged = pyqtSignal(str)
    zoomRequested = pyqtSignal(bool)
    panRequested = pyqtSignal(bool)
    selectBtnPressed = pyqtSignal(bool)
    radarRequested = pyqtSignal()
    resetInteractionsRequested = pyqtSignal()
    selectAllRequested = pyqtSignal()
    concatListIsReady = pyqtSignal(list)

    def __init__(self):
        super(PDWToolsForm, self).__init__()
        self.setupUi(self)

        # # icon
        # icon_label = QLabel(self.iconWidget)
        # icon_path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'icons', 'main.png')
        # icon_label.setScaledContents(True)
        # icon_label.setPixmap(QPixmap(icon_path).scaled(200,200,Qt.AspectRatioMode.KeepAspectRatio))
        # icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        # self.iconWidgetLayout.addWidget(icon_label)

        # widgets
        self.concat_box = ConcatBox()


        # variables
        self.file_path = None

        # configs
        self.selectFileBtn.setToolTip('Select Pdw File')
        self.newRadarBtn.setToolTip('New Radar')
        self.selectBtn.setToolTip('Select Data')
        self.selectAllBtn.setToolTip('Select All Data')
        self.clearBtn.setToolTip('Clear All Channels')

        # connections
        self.selectFileBtn.clicked.connect(self.get_file_path)
        self.selectBtn.clicked.connect(self.selectBtnPressed)
        self.selectAllBtn.clicked.connect(self.selectAllRequested)
        self.zoomBtn.clicked.connect(self.zoomRequested)
        self.dragBtn.clicked.connect(self.panRequested)
        self.newRadarBtn.clicked.connect(self.radarRequested)
        self.resetBtn.clicked.connect(self.resetInteractionsRequested)
        self.concatChannelsBtn.clicked.connect(self.show_concat_box)
        self.concat_box.concatListIsReady.connect(self.concatListIsReady)

        # group Btn
        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.selectBtn)
        self.btn_grp.addButton(self.zoomBtn)
        self.btn_grp.addButton(self.dragBtn)

    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter="Text files (*.txt);")[0]
        if new_path and self.file_path != new_path:
            self.file_path = new_path
            self.filePathChanged.emit(self.file_path)

    def set_file_path(self, text):
        self.filePathChanged.emit(text)

    def show_concat_box(self):
        self.concat_box.show()

    def setup_channel(self, header):
        self.concat_box.setup_channel(header)

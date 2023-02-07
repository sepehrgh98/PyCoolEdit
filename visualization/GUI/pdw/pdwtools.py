import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QFileDialog, QButtonGroup, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from visualization.GUI.pdw.concatbox import ConcatBox

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'pdwtools.ui'))[0]


class PDWToolsForm(QWidget, Form):
    # signals
    filePathChanged = pyqtSignal(str)
    zoomRequested = pyqtSignal(bool)
    panRequested = pyqtSignal(bool)
    selectBtnPressed = pyqtSignal(bool)
    radarRequested = pyqtSignal()
    resetZoomRequested = pyqtSignal()
    selectAllRequested = pyqtSignal()
    concatListIsReady = pyqtSignal(list)
    deselectAllRequested = pyqtSignal()
    clearRequested = pyqtSignal()
    exportRequested = pyqtSignal()
    deleteSelectedRequested = pyqtSignal()
    showNormalizeRequested = pyqtSignal()
    forwardZoomRequested = pyqtSignal()
    backeardZoomRequested = pyqtSignal()
    lineMarkerRequested = pyqtSignal(bool)
    pointMarkerRequested = pyqtSignal(bool)


    def __init__(self):
        super(PDWToolsForm, self).__init__()
        self.setupUi(self)

        # widgets
        self.concat_box = ConcatBox()
        


        # variables
        self.file_path = None

        # configs
        self.fileNameLabel.setStyleSheet('color: red')
        self.totalDataNumberLabel.setStyleSheet('color: red')
        # self.dragBtn.setToolTip('Pan charts in every directions')
        self.zoomBtn.setToolTip('Rectangular zoom')
        self.backwardZoomBtn.setToolTip('Previous zoom range')
        self.forwardZoomBtn.setToolTip('Next zoom range')
        self.selectBtn.setToolTip('Select Data')
        self.selectAllBtn.setToolTip('Select All Data')
        self.deleteBtn.setToolTip('Clear selected area')
        self.unselectBtn.setToolTip('Unselect all selected areas')
        self.pointCursorBtn.setToolTip('Point marker')
        self.lineMarkerBtn.setToolTip('Line marker')
        self.resetBtn.setToolTip('Reset to home range')

        self.selectFileBtn.setToolTip('Select Pdw File')
        self.newRadarBtn.setToolTip('New Radar')
        self.noralizeBtn.setToolTip('Show normalized data')
        self.exportBtn.setToolTip('Export selected data')

        # connections
        # self.selectFileBtn.clicked.connect(self.get_file_path)
        self.selectBtn.clicked.connect(self.selectBtnPressed)
        self.selectAllBtn.clicked.connect(self.selectAllRequested)
        self.zoomBtn.clicked.connect(self.zoomRequested)
        self.newRadarBtn.clicked.connect(self.radarRequested)
        self.resetBtn.clicked.connect(self.resetZoomRequested)
        self.unselectBtn.clicked.connect(self.deselectAllRequested)
        self.exportBtn.clicked.connect(self.exportRequested)
        self.deleteBtn.clicked.connect(self.deleteSelectedRequested)
        self.noralizeBtn.clicked.connect(self.showNormalizeRequested)
        self.forwardZoomBtn.clicked.connect(self.forwardZoomRequested)
        self.backwardZoomBtn.clicked.connect(self.backeardZoomRequested)
        self.lineMarkerBtn.clicked.connect(self.lineMarkerRequested)
        self.pointCursorBtn.clicked.connect(self.pointMarkerRequested)
        self.concat_box.concatListIsReady.connect(self.concatListIsReady)

        # group Btn
        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.selectBtn)
        self.btn_grp.addButton(self.zoomBtn)

        self.zoomBtn.setIcon(QIcon('visualization/Resources/icons/zoom.png'))
        self.backwardZoomBtn.setIcon(QIcon('visualization/Resources/icons/backward.png'))
        self.forwardZoomBtn.setIcon(QIcon('visualization/Resources/icons/forward.png'))
        self.selectBtn.setIcon(QIcon('visualization/Resources/icons/select.png'))
        self.selectAllBtn.setIcon(QIcon('visualization/Resources/icons/select_all.png'))
        self.deleteBtn.setIcon(QIcon('visualization/Resources/icons/delete.png'))
        self.unselectBtn.setIcon(QIcon('visualization/Resources/icons/deselect.png'))
        self.pointCursorBtn.setIcon(QIcon('visualization/Resources/icons/pointmarker.png'))
        self.lineMarkerBtn.setIcon(QIcon('visualization/Resources/icons/linemarker.png'))
        self.resetBtn.setIcon(QIcon('visualization/Resources/icons/Home.png'))
        self.selectFileBtn.setIcon(QIcon('visualization/Resources/icons/openfile.png'))
        self.newRadarBtn.setIcon(QIcon('visualization/Resources/icons/radar.png'))
        self.noralizeBtn.setIcon(QIcon('visualization/Resources/icons/normilize.png'))
        self.exportBtn.setIcon(QIcon('visualization/Resources/icons/export.png'))

    def get_file_path(self):
        self.clearRequested.emit()
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

    @pyqtSlot(str)
    def set_file_name(self, path):
        self.fileNameLabel.setText(os.path.basename(path))

    @pyqtSlot(int)
    def set_total_data_size(self, size):
        self.totalDataNumberLabel.setText(str(size))


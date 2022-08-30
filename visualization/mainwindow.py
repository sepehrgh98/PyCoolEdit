from PyQt5.QtWidgets import QMainWindow
import os
from PyQt5 import uic
from visualization.GUI.pdw.pdwform import PDWForm
from visualization.GUI.signal.signalform import SignalForm
from visualization.Signal.signalcontroller import SignalController
from visualization.pdw.datahandler import DataHandler
from visualization.GUI.settings.mainsettings import MainSettings

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'mainform.ui'))[0]


class MainWindow(QMainWindow, Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle('Offline')

        # setup module
        self.pdw_form = PDWForm()
        self.data_handler = DataHandler()
        self.signal_form = SignalForm()
        self.signal_controller = SignalController()
        self.mainsettings = MainSettings()
        self.pdwLayout.addWidget(self.pdw_form)
        self.signalLayout.addWidget(self.signal_form)
        self.MainSettingsLayout.addWidget(self.mainsettings)

        # setup connections
        # pdw form
        self.pdw_form.filePathChanged.connect(self.data_handler.set_file_path)
        self.pdw_form.clearRequested.connect(self.data_handler.clear)
        self.pdw_form.selectDataRequested.connect(self.data_handler.selectDataRequested)
        self.pdw_form.deleteSelectedRequested.connect(self.data_handler.deleteSelectedRequested)

        # data handler
        self.data_handler.columns_defined.connect(self.pdw_form.setup_channels)
        self.data_handler.final_data_is_ready.connect(self.pdw_form.feed)
        self.data_handler.progress_is_ready.connect(self.pdw_form.feed_progressbar)

        # signal form
        self.signal_form.request_data.connect(self.signal_controller.get_data)

        # signal controller
        self.signal_controller.data_packet_is_ready.connect(self.signal_form.feed)

        # settings
        self.mainsettings.showPolicyChanged.connect(self.pdw_form.showPolicyChanged)
        

        # show project
        self.showMaximized()

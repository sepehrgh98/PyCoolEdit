from PyQt5.QtWidgets import QMainWindow
import os
from PyQt5 import uic
from visualization.GUI.pdw.pdwform import PDWForm
from visualization.pdw.datahandler import DataHandler

Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'mainform.ui'))[0]


class MainWindow(QMainWindow, Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pdw_form = PDWForm()
        self.data_handler = DataHandler()
        self.pdw_form.filePathChanged.connect(self.data_handler.set_file_path)
        self.data_handler.columns_defined.connect(self.pdw_form.setup_channels)
        self.data_handler.final_data_is_ready.connect(self.pdw_form.feed)
        self.pdwLayout.addWidget(self.pdw_form)

        self.pdw_form.dataRequested.connect(self.data_handler.dataRequest)
        self.show()

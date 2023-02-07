import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QFileDialog
from visualization.pdw.export.PDWTextExport import PDWTextExport
from visualization.pdw.export.PDWHtmlExport import PDWHtmlExport
from visualization.pdw.export.PDWCsvExport import PDWCsvExport
from visualization.visualizationparams import Channel_id_to_name
import numpy as np


Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'pdw', 'exportWindowui.ui'))[0]


class PDWExprtWindow(QWidget, Form):
    def __init__(self):
        super(PDWExprtWindow, self).__init__()
        self.setupUi(self)
        self.browsBtn.clicked.connect(self.get_file_path)
        self.exportBtn.clicked.connect(self.do_export)
        self.selected_data = {}
        self.type = None

    def get_file_path(self):
        self.type = self.exportTypeComboBox.currentText()
        new_path = QFileDialog.getSaveFileName(self, "Save audio file", filter="OUTPUT(*." + self.type + ")")[0]
        self.pathLineEdit.setText(new_path)

    def feed(self, packet):
        self.selected_data = {}
        for id, data in packet.items():
            if not 'TOA' in self.selected_data:
                self.selected_data['TOA'] = data.key
            self.selected_data[Channel_id_to_name[id]] = data.data
       
        
    def do_export(self):
        exporter = None
        new_path = self.pathLineEdit.text()
        if self.type == 'txt':
            exporter = PDWTextExport(new_path)
        elif self.type == 'html':
            exporter = PDWHtmlExport(new_path)
        elif self.type == 'csv':
            exporter = PDWCsvExport(new_path)
        exporter.feed(self.selected_data)
        self.close()




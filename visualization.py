import sys

from PyQt5.QtWidgets import QApplication

from GUI.pdwform import PDWForm
from datahandler import DataHandler


class Visualization(QApplication):
    def __init__(self):
        super(Visualization, self).__init__([])
        self.pdw_form = PDWForm()
        self.data_handler = DataHandler()
        self.pdw_form.filePathChanged.connect(self.data_handler.set_file_path)
        self.data_handler.final_data_is_ready.connect(self.pdw_form.feed)
        self.pdw_form.show()


if __name__ == '__main__':
    # app = QApplication([])
    v = Visualization()
    # v = PDWForm()
    # pdwForm.show()
    sys.exit(v.exec_())

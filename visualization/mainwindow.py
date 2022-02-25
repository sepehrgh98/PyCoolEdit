from PyQt5.QtWidgets import QMainWindow
from GUI.pdwform import PDWForm


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pdw_form = PDWForm()
        # self.data_handler = DataHandler()
        # self.pdw_form.filePathChanged.connect(self.data_handler.set_file_path)
        # self.data_handler.final_data_is_ready.connect(self.pdw_form.feed)
        self.pdw_form.show()




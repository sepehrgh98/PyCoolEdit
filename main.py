from GUI.PDWForm import PDWForm
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication([])
    pdwForm = PDWForm()
    pdwForm.show()
    sys.exit(app.exec_())


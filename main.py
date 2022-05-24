import sys
from PyQt5.QtWidgets import QApplication
from visualization.mainwindow import MainWindow
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("AUT")
    app.setApplicationName("Visualization")
    app.setApplicationDisplayName("Visualization")
    path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'style.qss')
    with open(path, "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    p = MainWindow()
    sys.exit(app.exec_())

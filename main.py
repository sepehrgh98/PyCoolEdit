import sys
from PyQt5.QtWidgets import QApplication
from visualization.mainwindow import MainWindow
import os
from PyQt5.QtGui import QIcon

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("AUT")
    app.setApplicationName("Offline")
    app.setApplicationDisplayName("Offline")
    icon_path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'icons', 'main.png')
    app.setWindowIcon(QIcon(icon_path))
    path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'Obit.qss')
    with open(path, "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    p = MainWindow()
    sys.exit(app.exec_())

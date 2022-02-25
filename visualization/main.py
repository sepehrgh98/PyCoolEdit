import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow
from PyQt5.QtCore import QFile, QIODevice, QVariant
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("AUT")
    app.setApplicationName("Visualization")
    app.setApplicationDisplayName("Visualization")
    path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'style.css')
    print(path)
    styleFile = QFile(path)
    styleFile.open(QIODevice.ReadOnly)
    if styleFile.isOpen():
        print("is")
        app.setStyleSheet(str(QVariant(styleFile.readAll())))
    styleFile.close()

    p = MainWindow()
    sys.exit(app.exec_())

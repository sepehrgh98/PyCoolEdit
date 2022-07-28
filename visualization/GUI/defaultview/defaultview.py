import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt


Form = uic.loadUiType(os.path.join(os.getcwd(), 'visualization', 'GUI', 'defaultview', 'defaultview.ui'))[0]


class DefaultView(QWidget, Form):
    filePathChanged = pyqtSignal(str)

    def __init__(self,icon_path, text, filter = "Text files (*.txt);"):
        super(DefaultView, self).__init__()
        self.setupUi(self)
        self.filter = filter
        # icon
        icon_label = QLabel(self.iconWidget)
        # icon_path = os.path.join(os.getcwd(), 'visualization', 'Resources', 'icons', 'main.png')
        icon_label.setScaledContents(True)
        icon_label.setPixmap(QPixmap(icon_path).scaled(200,200,Qt.AspectRatioMode.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        self.iconLayout.addWidget(icon_label)
        self.label.setText(text)

        # add file
        self.commandLinkButton.clicked.connect(self.get_file_path)

        # variables
        self.file_path = ""

    def get_file_path(self):
        new_path = QFileDialog.getOpenFileName(self, "Open File", filter=self.filter)[0]
        if new_path and self.file_path != new_path:
            self.file_path = new_path
            self.filePathChanged.emit(self.file_path)
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\sepeh\Desktop\Visualization\visualization\GUI\pdw\datainformationbox.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dataInformationBox(object):
    def setupUi(self, dataInformationBox):
        dataInformationBox.setObjectName("dataInformationBox")
        dataInformationBox.resize(800, 29)
        dataInformationBox.setMinimumSize(QtCore.QSize(800, 0))
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(dataInformationBox)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox = QtWidgets.QGroupBox(dataInformationBox)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_3 = QtWidgets.QWidget(self.groupBox)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.widget_3)
        self.label_3.setMaximumSize(QtCore.QSize(40, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.totalDataNumberLabel = QtWidgets.QLabel(self.widget_3)
        self.totalDataNumberLabel.setText("")
        self.totalDataNumberLabel.setObjectName("totalDataNumberLabel")
        self.horizontalLayout_3.addWidget(self.totalDataNumberLabel)
        self.horizontalLayout.addWidget(self.widget_3)
        self.widget_2 = QtWidgets.QWidget(self.groupBox)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.widget_2)
        self.label_5.setMinimumSize(QtCore.QSize(0, 0))
        self.label_5.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.selectedDataNumberLabel = QtWidgets.QLabel(self.widget_2)
        self.selectedDataNumberLabel.setObjectName("selectedDataNumberLabel")
        self.horizontalLayout_4.addWidget(self.selectedDataNumberLabel)
        self.horizontalLayout.addWidget(self.widget_2)
        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fileNameLabel = QtWidgets.QLabel(self.widget)
        self.fileNameLabel.setText("")
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.horizontalLayout_2.addWidget(self.fileNameLabel)
        self.horizontalLayout.addWidget(self.widget)
        self.horizontalLayout_5.addWidget(self.groupBox)

        self.retranslateUi(dataInformationBox)
        QtCore.QMetaObject.connectSlotsByName(dataInformationBox)

    def retranslateUi(self, dataInformationBox):
        _translate = QtCore.QCoreApplication.translate
        dataInformationBox.setWindowTitle(_translate("dataInformationBox", "Form"))
        self.label_3.setText(_translate("dataInformationBox", "Total:"))
        self.label_5.setText(_translate("dataInformationBox", "Selected:"))
        self.selectedDataNumberLabel.setText(_translate("dataInformationBox", "0"))

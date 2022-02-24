from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, QDateTime
import os

Form = uic.loadUiType(os.path.join(os.getcwd(), 'GUI', 'pdwinformationbox.ui'))[0]


class PDWInformationBoxForm(QWidget, Form):
    def __init__(self):
        super(PDWInformationBoxForm, self).__init__()
        self.setupUi(self)

    @pyqtSlot(str)
    def setSite(self, site):
        self.siteLabel.setText(site)

    @pyqtSlot(QDateTime)
    def setDate(self, date):
        self.dateLabel.setText(date.toString('yyyy/MM/dd , hh:mm:ss'))

    @pyqtSlot(QDateTime)
    def setTime(self, time):
        self.timeLabel.setText(time.toString('hh:mm:ss'))

    @pyqtSlot('qint64')
    def setFrequency(self, freq):
        self.frequencyLabel.setText(str(freq))

    @pyqtSlot('double')
    def setOmniGain(self, omni):
        self.omniGainLabel.setText(str(omni))

    @pyqtSlot('double')
    def setAOAOffset(self, aoa):
        self.aoaOffsetLabel.setText(str(aoa))

    @pyqtSlot('double')
    def setIFFilter(self, ifFilter):
        self.ifFilterLabel.setText(str(ifFilter))

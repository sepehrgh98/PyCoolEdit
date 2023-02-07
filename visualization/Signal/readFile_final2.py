import os
import sys
import time
import numpy as np
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class Read_file(QObject):
    data_is_ready = pyqtSignal(list)
    
    def __init__(self, file_path):
        super(Read_file, self).__init__()
        self.file = file_path
    
    def fileOpen(self):
        with open(self.file, 'rb') as file:
            self.data = file.read()
    
    def fileReader(self, a, b, channels, N):
        self.start = a
        self.end = b
        self.sampleRate = N
        self.channels = channels
        if self.sampleRate > self.end - self.start + 1:
            self.sampleRate = self.end - self.start + 1
        idx = np.round(np.linspace(self.start, self.end, self.sampleRate)).astype(int)
        if self.channels==1:
            self.res = [[int.from_bytes(self.data[2*i:2*i+2], "little", signed="True") for i in idx]]
        else:
            self.res = [[int.from_bytes(self.data[4*i:4*i+2], "little", signed="True") for i in idx], [int.from_bytes(self.data[4*i+2:4*i+4], "little", signed="True") for i in idx]]

        self.res.append(idx.tolist())
        self.data_is_ready.emit(self.res)
    


if __name__ == "__main__":
    file_path = os.path.join(os.getcwd(), "visualization", "Signal", "IF1 2724 161652.dat")
    file = Read_file(file_path)
    tic = time.time()
    file.fileOpen()

    signal = file.fileReader(0, 10000000, 2, 500000)
    toc = time.time() - tic
    print(toc)
    print(len(signal))
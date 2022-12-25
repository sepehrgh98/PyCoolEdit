import os
import sys
import time
import numpy as np

class Read_file:
    def __init__(self, file_path):
        with open(file_path, 'rb') as file:
            self.data = file.read()
            self.num = int(len(self.data)/2)
            # self.signal = [int.from_bytes(self.data[2*i:2*i+2], "little", signed="True") for i in range(self.num)]
    
    def fileReader(self, a, b, channels, N):
        self.start = a
        self.end = b
        self.sampleRate = N
        self.channels = channels
        if self.sampleRate > self.end - self.start + 1:
            self.sampleRate = self.end - self.start + 1
        idx = np.round(np.linspace(self.start, self.end, self.sampleRate)).astype(int)
        if self.channels==1:
            self.data = [[int.from_bytes(self.data[2*i:2*i+2], "little", signed="True") for i in idx]]
        else:
            self.data = [[int.from_bytes(self.data[4*i:4*i+2], "little", signed="True") for i in idx], [int.from_bytes(self.data[4*i+2:4*i+4], "little", signed="True") for i in idx]]

        self.data.append(idx.tolist())
        return self.data
    


if __name__ == "__main__":
    file_path = os.path.join(os.getcwd(), "visualization", "visualization","Signal", "IF1 2724 161652.dat")
    file = Read_file(file_path)
    tic = time.time()

    signal = file.fileReader(0, 20, 1, 10)
    toc = time.time() - tic
    print(toc)
    print(signal)

from signal import signal
from unicodedata import decimal
import matplotlib.pyplot as plt
import numpy as np
import os
import struct


def readFile_M(file_path, a, b, channels, N):
    with open(file_path, 'rb') as file:
        counter = 0
        signal = []
        for i in range(b-a):
            file.seek(a+ i*2*channels)
            num = file.read(2*channels)
            # for j in range(channels):
            #     print(j)
            #     signal.append(int.from_bytes(num[j*2:2+j], "little", signed="True"))
            if channels == 1:
                signal.append(int.from_bytes(num, "little", signed="True"))
            else:
                signal.append(int.from_bytes(num[0:2], "little", signed="True"))
                signal.append(int.from_bytes(num[2:4], "little", signed="True"))

        ch1 = []
        ch2 = []   
        if len(signal) != (b-a):
            for k in range(len(signal)):
                if k % 2:
                    ch2.append(signal[k])
                else:
                    ch1.append(signal[k])
            signal = [ch1, ch2]
    return signal
                        
                



def readFile(file_path, a, b, channels, N):
    with open(file_path, 'rb') as file:
        data = []
        signal = []
        #Sampling when data size is significant, otherwise whole data is consider
        # if (a-b) > 1000000:
        #     delta = int((b - a)/N)
        # else:
        #     delta = 1
        #     N = b - a
        delta = int((b - a)/N)
        for i in range(N):
            # Go to the appropriate byte position regarding reading 2 bytes for a mono signal and read 4 bytes for a stereo signal 
            file.seek(a+ i*2*channels*delta)
            num = file.read(2*channels)
            
            # Consider every 2bytes a number with a sign
            if channels == 1:
                data.append(int.from_bytes(num, "little", signed="True"))
            else:
                data.append(int.from_bytes(num[0:2], "little", signed="True"))
                data.append(int.from_bytes(num[2:4], "little", signed="True"))
        
        ch1 = []
        ch2 = []   
        
        if channels==2:
            for k in range(len(data)):
                if k % 2:
                    ch2.append(data[k])
                else:
                    ch1.append(data[k])
            signal = [ch1, ch2]
        else:
            signal = [data]
    return signal

if __name__ == '__main__':
    filename = 'IF1 2724 161652.DAT'
    channels = 2
    a, b = 0, 100000000
    # file_path = os.path.join(os.getcwd(), "sterio", "Barker 13 (1).dat")
    file_path = os.path.join(os.getcwd(), "visualization", "Signal", "IF1 2724 161652.dat")
    data_mono = readFile(file_path, 0, 100000, 1, 50000)
    print(len(data_mono), type(data_mono[0]))
    data_stereo = readFile(file_path, 0, 100000, 2, 50000)
    print(len(data_stereo), type(data_stereo[0]), type(data_stereo[1]))

    
  
    # plt.subplot(2, 1, 1)
    # plt.plot(data_M[0])
    # plt.subplot(2, 1, 2)
    # plt.plot(data_M[1])
    # plt.show()
    
    

    



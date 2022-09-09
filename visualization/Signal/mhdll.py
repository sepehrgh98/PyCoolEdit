import numpy.ctypeslib as ctl
import numpy as np
import ctypes
from numpy.ctypeslib import ndpointer, as_array
from time import time

class MHDatReader:
    def __init__(self, filename, dll_path, channels=2):
        self.filename = filename
        self.dll_path = dll_path 
        self.channels = channels 
        self.lib = ctypes.CDLL(dll_path)
        self.getSize = self.lib.getSize
        self.getData = self.lib.getData
    
    def get(self, a, b, n):
        self.getData.restype = ndpointer(ctypes.c_int, shape=(n,))
        res = self.getData(self.filename.encode('UTF-8'), a, b, n, self.channels)
        data = [res[i::self.channels] for i in range(self.channels)]
        return data


if __name__ == '__main__':
    # mhreader = MHDatReader("IF1 2724 161652.DAT", 'ver2.dll', 2)
    mhreader = MHDatReader("IF1 2724 161652.DAT", 'drkh.dll', 2)
    t0 = time()
    res = mhreader.get(0, 100000000, 50000)
    t1 = time()
    print(f'Took {t1-t0} seconds...')
    print(len(res), res[0].shape)
    # print(mhreader.getSize(b"IF1 2724 161652.DAT"))

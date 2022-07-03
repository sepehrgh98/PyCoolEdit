import mmap
import struct
import numpy as np
from glob import glob
from time import time


##  mm.read(a); mm.read(n) was slower than mm[a:a+n]...


class MHDatReader(mmap.mmap):
    def __init__(self, filename, channels, big_ending=True, singed=True):
        self.channels = channels
        self.big_ending = big_ending
        self.singed = singed
        self.raw_length = len(self)
        self.length = int(self.raw_length / 2 / self.channels)

        # self.arr = self[::]
        # format = ">" if self.big_ending else "<"
        # if self.singed:
        #     format += "h" * (len(self.arr) // 2)
        # else:
        #     format += "H" * (len(self.arr) // 2)
        # self.arr = struct.unpack(format, self.arr)
        # print("Object created with length:", len(self.arr))

    def __new__(cls, filename, *args, **kwargs):
        file = open(filename, "rb")
        return super().__new__(cls, file.fileno(), 0, access=mmap.ACCESS_READ)

    def get(self, a, b, n=10, algorithm="simple"):
        intervals = np.linspace(a, b, n, dtype=int)
        delta = intervals[1] - intervals[0]
        
        format = ">" if self.big_ending else "<"
        if self.singed:
            format += "h"
        else:
            format += "H"

        arr = [[] for _ in range(self.channels)]
        ##  Simple algorithm...
        if algorithm == "simple":
            for point in intervals:
                for ch in range(self.channels):
                    arr[ch].append(
                        self[
                        point * 2 * self.channels
                        + ch * 2: point * 2 * self.channels
                                  + ch * 2
                                  + 2
                        ]
                    )

        res = [[] for _ in range(self.channels)]
        for ch in range(self.channels):
            for i in range(n):
                res[ch].append(struct.unpack(format, arr[ch][i])[0])
        return res

    def get_file_total_size(self):
        return len(self)


if __name__ == "__main__":
    files = glob("*.dat")

    n = 10
    index = 0
    length = 10000000

    mhd = MHDatReader(files[0], 2)
    res = mhd.get(index, index + length, n)
    print("Testing simple algorithm...")
    times = []
    for i in range(10):
        t0 = time()
        channels = mhd.get(index, index + length, n)
        t1 = time()
        times.append(t1 - t0)
        print(f"No {i}: It took ", t1 - t0)

    print("In average: ", sum(times) / len(times))

    # start = 0
    # end = 2
    # arr = mhd[start * 2 * 2 : end * 2 * 2]  ##  2 channels, 2 bytes per sample
    # values = [c for c in arr]
    # channels = mhd.get(start, end)
    # print(channels)
    # print(values[0] << 8 | values[1])

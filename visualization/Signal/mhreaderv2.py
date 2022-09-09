import numpy as np 
from time import time
import matplotlib.pyplot as plt
import os

def measureTime(func):
    def timer(*args):
        t0 = time()
        res = func(*args)
        t1 = time()
        print(f'Took {t1 - t0} seconds!')
        return res 
    return timer

# @measureTime
def readFile(filename, a, b, channels, N):
    delta = int((b - a) / N)
    ##  To check if there is sufficient points in the interval...
    ##  Otherwise, just pick how many points possible...
    if not delta:
        delta = 1
        N = int(b - a)

    content = []
    with open(filename, 'rb') as file:
        for t in range(N):
            ##  Go to the appropriate byte position which is (a + t) * channels * 2...
            file.seek((a + t) * delta * 2)
            ##  Read bytes (length = channels * 2)...
            ch = file.read(channels * 2)
            ##  Convert bytes into integers...
            ch_int = [ch[2*i] + ch[2*i+1] * 256 for i in range(channels)]
            content.extend(ch_int)

    arr = np.array(content, dtype=np.int16)
    result = [arr[i::channels] for i in range(channels)]
    return result


if __name__ == '__main__':
    filename = 'IF1 2724 161652.DAT'
    # filename = 'IF1 9800 174849.DAT'
    size = os.path.getsize(filename)
    channels = 1
    N = 50000
    a, b = 0, size//2 - 1
    res = readFile(filename, a, b, channels, N)
    x, y = np.array(range(len(res[0]))), res[0]
    # x_new = np.linspace(x.min(), x.max(),2500)
    # print(res[1][28])  ##  To access 2nd channel, point no 28
    print(res)
    print(f'Size: {size}')
    # f = interp1d(x, y, kind='quadratic')
    # y_smooth=f(x_new)
    plt.figure()
    plt.plot(res[0], 'r')
    plt.ylim((-10000, 10000))
    # plt.plot(x_new, y_smooth)
    plt.show()
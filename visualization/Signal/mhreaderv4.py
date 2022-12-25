import numpy as np
import os
import time

def readFile_old(file_path, a, b, channels, N): 
    with open(file_path, 'rb') as file: 
        delta = int((b - a + 1)/N)
        if N > (b - a + 1):
            N = b - a + 1
            delta = 1
        
        if channels == 1: 
            return [[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(2*a + i*2*delta) or True]] 
        else: # channels == 2 
            return [[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta) or True], 
                    [int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta+2) or True]]


def readFile_new(file_path, a, b, channels, N): 
    with open(file_path, 'rb') as file: 
        if N > b - a + 1:
            N = b - a + 1
        idx = np.round(np.linspace(a, b, N)).astype(int)
        print(idx)
              
        delta = [0] + [(idx[i+1] - idx[i]) for i in range(N-1) if True]

        if channels == 1: 
            return [[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(2*a + i*2*(delta[i])) or True]] 
        else: # channels == 2 
            return [[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta[i]) or True], 
                    [int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta[i]+2) or True]]


if __name__ == '__main__':
    
    
    file_path = os.path.join(os.getcwd(), "visualization", "visualization", "Signal", "IF1 2724 161652.dat")
   
    start = time.time()
    data_new = readFile_new(file_path, 0, 10000000, 1, 1000000)
    # print(data_new)

    end = time.time()
    print(start-end)

    # start = time.time()
    data_old = readFile_old(file_path, 0, 100000000, 1, 1000000)
    # print(data_old)

    # end = time.time()
    # print(start -  end)

    

    
    

    



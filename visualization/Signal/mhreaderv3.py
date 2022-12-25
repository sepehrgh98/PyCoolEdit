import os
from multiprocessing import Process, Pipe
from signal import signal
import numpy as np
import time


def readFile(file_path, a, b, channels, N, process_num):

    length = int(np.ceil((b - a + 1)/process_num))
    
    processes = []
    processes_conns = []
    last_index = b

    if N % process_num >= (process_num/2):
        N = N + (process_num - (N % process_num))
    else:
        N = N - (N % process_num)
    
    N_per_process = int(N/process_num)
    signal = []
    ch1 = []
    ch2 = []
    data = []
    index = []
    for i in range(process_num):
        conn1, conn2 = Pipe()
        p = Process(target=readFile_process, args=(conn1, file_path, a + i*length,  a + i*length + (length-1), channels, N_per_process,last_index,))
        processes.append(p)
        processes_conns.append((conn1, conn2))
        # p.start()
        # print(conn2.recv())
        # p.join()
    for p in processes:
        p.start()
    for conns in processes_conns:
        signal = signal + conns[1].recv()
        
    for p in processes:
       p.join()
    if channels == 1:
        for i in range(len(signal)):
            if i%2==0:
                data = data + signal[i]
            else: 
                index = index + signal[i]
        return[data, index]
    else:
        counter = 0
        for i in range(len(signal)):
            if counter==3:
                counter=0
            if counter==0:
                ch1 = ch1 + signal[i]
            elif counter==1:
                ch2 = ch2 + signal[i]
            elif counter==2:
                index = index + signal[i]
            counter = counter + 1
        return[ch1, ch2, index]

def readFile_process(connection, file_path, a, b, channels, N, endIndex):
    with open(file_path, 'rb') as file:
        if b > endIndex:
            b = endIndex

        if N > b - a + 1:
            N = b - a + 1
        idx = np.round(np.linspace(a, b, N)).astype(int)
        delta = [0] + [(idx[i+1] - idx[i]) for i in range(N-1) if True]
        
        
        
        if channels == 1:
            connection.send([[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(2*a + i*2*(delta[i])) or True], idx.tolist()])
            connection.close()
        else:
            connection.send([[int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta[i]) or True],
                            [int.from_bytes(file.read(2), "little", signed="True") for i in range(N) if file.seek(4*a + i*4*delta[i]+2) or True], idx.tolist()])
            connection.close()
       
if __name__ == '__main__':
    
    file_path = os.path.join(os.getcwd(), "visualization", "visualization", "Signal", "IF1 2724 161652.DAT")
    start = time.time()
    data_mono = readFile(file_path, 0, 10, 2, 8, 4)
    end = time.time()
    print(data_mono)

    
    

    



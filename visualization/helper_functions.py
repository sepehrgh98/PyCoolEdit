import numpy as np

def find_nearest_value_indx(array, value):
    if not len(array) :
        return
    if len(array) == 1:
        idx = 0
    else:
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
    return idx

def format_e(n):
    if len(str(int(float(n)))) > 3 :
        a = '%E' % n
        return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
    return n
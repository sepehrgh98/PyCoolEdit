from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
import numpy as np
from multiprocessing import Pool
from functools import partial
from visualization.visualizationparams import ProgressType
from visualization.visualizationparams import ChannelUnit
from string import digits
from visualization.visualizationparams import TimeCoef
import re


def find_nearest_value_indx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def parse(data_list, cols):
    parsed_data = {}
    for column in cols:
        parsed_data[column] = np.ndarray(0)
    for line in data_list[2:]:
        cols_line = line.split()
        for i in range(len(cols_line)):
            try:
                col_name = cols[i]
                parsed_data[col_name] = np.append(parsed_data[col_name], [float(cols_line[i])])
            except:
                pass
    return parsed_data

def cut_data(data, f_inx, l_inx):
    part1 = data[0:f_inx+1]
    part2 = data[l_inx:]
    return np.concatenate([part1, part2])

class SParser(QObject):
    columns_defined = pyqtSignal(dict)
    data_packet_is_ready = pyqtSignal(dict)
    progress_is_ready = pyqtSignal(dict)
    markerLineResultIsReady = pyqtSignal(dict)
    totalSizeIsReady = pyqtSignal(int)
    
    def __init__(self) -> None:
        super(SParser, self).__init__()
        self.columns = []
        self.initilize_data = True
        self.parsed_data = {}
        self.progress = 0
        self.raw_data = []
        self.time_coef = 1
        self.total_size = 0
        self.is_columns_defined = False

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(list, bool, float)
    def prepare_data(self, data_list, eof, number_of_batches):
        self._set_columns(data_list)
        self.raw_data.append(data_list)
        if eof :
            if self.initilize_data:
                self._init_data()
                self.initilize_data = False 

            pool = Pool(processes=5)
            for i, output in enumerate(pool.imap(partial(parse, cols=self.columns), self.raw_data), 1):
                for name, val in output.items():
                    self.parsed_data[name] = np.append(self.parsed_data[name], val)
                    self.total_size += len(val)
                self.progress_is_ready.emit({ProgressType.parser: 1 if (i/number_of_batches)>=1 else i/number_of_batches})
            self.calculate_rri()
            self.totalSizeIsReady.emit(len(self.parsed_data['TOA']))
            self.data_packet_is_ready.emit(self.parsed_data)

    
    @pyqtSlot(str, tuple, tuple)
    def prepare_requested_select_data(self,ch_name, time_range, value_range):

        if time_range == (-1,) :
            first_x_index = 0
            last_x_index = len(self.parsed_data['TOA']) - 1
        else:
            first_x_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[0])
            last_x_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[1])

        if value_range == (-1,):
            min_val = min(self.parsed_data[ch_name])
            max_val = max(self.parsed_data[ch_name])
            value_range = (min_val, max_val)

            
        requested_data = dict()
        req_time = (self.parsed_data['TOA'])[first_x_index:last_x_index]
        req_val = (self.parsed_data[ch_name])[first_x_index:last_x_index]
        y_x_filtered = []
        outout_index = []
        for key, val in zip(req_time, req_val):
            if val >= value_range[0] and val <= value_range[1]:
                y_x_filtered.append(val)
                outout_index.append(list(self.parsed_data['TOA']).index(key))


        requested_data[ch_name] = y_x_filtered

        for key, val in self.parsed_data.items():
            if key != ch_name:
                new_val = [val[ind] for ind in outout_index]
                requested_data[key] = new_val


        self.data_packet_is_ready.emit(requested_data)


    def _set_columns(self, data_list):
        if not self.is_columns_defined:
            sentence = data_list[0].split("\n")[0]
            # repaired = re.sub(r'([^\s])\s([^\s])', r'\1_\2',a)
            repaired = re.sub('%', '', sentence)
            columns_dict = self.unit_detection(repaired.split()[:])
            self.columns = list(columns_dict.keys())
            self.columns.append('RRI')
            self.columns.append('RRF')
            columns_dict['RRI'] = ChannelUnit['RRI']
            columns_dict['RRF'] = ChannelUnit['RRF']
            self.set_time_coefficient(columns_dict['TOA'])
            self.columns_defined.emit(columns_dict)
            self.is_columns_defined = True


    def _init_data(self) -> None:
        for column in self.columns:
            self.parsed_data[column] = np.ndarray(0)

    def calculate_rri(self):
        time_data = self.parsed_data['TOA']
        RRI = []
        RRF = []
        for i in range(len(time_data)-1):
            # diff = (time_data[i+1] - time_data[i])*self.time_coef
            diff = (time_data[i+1] - time_data[i])
            RRI.append(diff)
            RRF.append(1000000/diff)
            if i == len(time_data)-2:
                RRI.append(RRI[-1])
                RRF.append(1000000/RRI[-1])
        self.parsed_data['RRI'] = RRI
        self.parsed_data['RRF'] = RRF

    def clear(self):
        self.columns = []
        self.initilize_data = True
        self.parsed_data = {}
        self.progress = 0
        self.raw_data = []
        self.is_columns_defined = False
    
    def unit_detection(self, channel_list):
        columns = {}
        unit = ''
        for received_name in channel_list:
            if "(" in received_name or ")" in received_name:
                mylist = received_name.split("(")
                name = mylist[0]
                unit = mylist[1].split(")")[0]
            else:
                name = received_name
                try:
                    unit = ChannelUnit[name.translate(name.maketrans('', '', digits))] if ChannelUnit[name.translate(name.maketrans('', '', digits))] else ''
                except:
                    pass
            columns[name] = unit
        return columns

    def set_time_coefficient(self, unit):
        self.time_coef = TimeCoef[unit]

    # @pyqtSlot(list)
    # def on_delete_selected_req(self, selected_area):
    #     for time_range in selected_area:
    #         pool = Pool(processes=5)
    #         channel_val = self.parsed_data.values()
    #         key_list = list(self.parsed_data.keys())
    #         start_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[0])
    #         stop_index = find_nearest_value_indx(self.parsed_data['TOA'], time_range[1])
    #         self.parsed_data = {}
    #         for i, output in enumerate(pool.imap(partial(cut_data, f_inx=start_index, l_inx=stop_index), channel_val), 1):
    #             self.parsed_data[key_list[i-1]] = output
    #     self.data_packet_is_ready.emit(self.parsed_data)


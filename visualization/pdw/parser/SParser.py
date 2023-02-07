from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread, QElapsedTimer
import numpy as np
from multiprocessing import Pool
from functools import partial
from visualization.visualizationparams import FeedMood, ProgressType
from visualization.visualizationparams import ChannelUnit, DataPacket
from string import digits
from visualization.visualizationparams import TimeCoef
import re
from visualization.helper_functions import find_nearest_value_indx



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
    zoomed_area_is_ready = pyqtSignal(dict, FeedMood)
    selected_data_is_ready = pyqtSignal(dict, FeedMood)


    
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
        self.parse_index = 0

        # moving to thread
        self.objThread = QThread()
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    def __del__(self):
        self.objThread.quit()
        self.objThread.wait()

    @pyqtSlot(list, bool, float)
    def prepare_data(self, data_list, eof, number_of_batches):
        self._set_columns(data_list)
        if self.initilize_data:
            self._init_data()
            self.initilize_data = False
        self.raw_data.append(data_list)
        if eof :
            if self.initilize_data:
                self._init_data()
                self.initilize_data = False 

            self.timer = QElapsedTimer()
            self.timer.start()

            pool = Pool(processes=5)
            for i, output in enumerate(pool.imap(partial(parse, cols=self.columns), self.raw_data), 1):
                for name, val in output.items():
                    self.parsed_data[name] = np.append(self.parsed_data[name], val)
                    self.total_size += len(val)
                self.progress_is_ready.emit({ProgressType.parser: 1 if (i/number_of_batches)>=1 else i/number_of_batches})

            # print(self.timer.elapsed())
            self.calculate_rri()
            self.totalSizeIsReady.emit(len(self.parsed_data['TOA']))
            data_packet = self.parsed_data.copy()
            toa = data_packet['TOA']
            data_packet.pop('TOA')    
            if "CW" in data_packet:
                data_packet.pop('CW')
            if "No." in data_packet:
                data_packet.pop('No.')

            ch_counter = 0
            output_packet = {}
            for name, data in data_packet.items():
                final_data = DataPacket()
                final_data.key = np.array(toa)
                final_data.data = np.array(data)
                ch_counter += 1
                final_data.id = ch_counter
                output_packet[name] = final_data
            self.data_packet_is_ready.emit(output_packet)

    
    @pyqtSlot(str, tuple, tuple)
    def prepare_requested_zoom_data(self,ch_name, time_range, value_range):
        current_channel_time_list = (self.parsed_data['TOA'])
        current_channel_val_list = (self.parsed_data[ch_name])

        if time_range == (-1,) :
            first_x_index = 0
            last_x_index = len(current_channel_time_list) - 1
        else:
            may_first_x_index = find_nearest_value_indx(current_channel_time_list, time_range[0])
            f_ind_val = current_channel_time_list[may_first_x_index]
            f_indices = np.where(current_channel_time_list == f_ind_val)[0]
            first_x_index = f_indices[0]
            may_last_x_index = find_nearest_value_indx(current_channel_time_list, time_range[1])
            l_ind_val = current_channel_time_list[may_last_x_index]
            l_indices = np.where(current_channel_time_list == l_ind_val)[0]
            last_x_index = l_indices[-1]

        if value_range == (-1,):
            min_val = np.amin(current_channel_val_list)
            max_val = np.amax(current_channel_val_list)
            value_range = (min_val, max_val)


        req_time = current_channel_time_list[first_x_index:last_x_index+1]

        requested_data ={}
        ch_counter = 0
        for name, channel_data in self.parsed_data.items():
            req_val = channel_data[first_x_index:last_x_index+1]
            final_key = []
            final_val = []
            for key, val in zip(req_time, req_val):
                if val >= value_range[0] and val <= value_range[1]:
                    final_key.append(key)
                    final_val.append(val)
            final_pack = DataPacket()
            final_pack.key = np.array(final_key)
            final_pack.data = np.array(final_val)
            final_pack.id = ch_counter
            requested_data[name] = final_pack
            ch_counter += 1
        self.zoomed_area_is_ready.emit(requested_data, FeedMood.main_data)

   

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

   
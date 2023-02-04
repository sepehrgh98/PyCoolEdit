from ast import Return
from operator import index
import re
from select import select
from time import time
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread, QElapsedTimer
from visualization.pdw.parser.SParser import SParser
from visualization.pdw.reader.SReader import SReader
from visualization.visualizationparams import ChannelUnit, DataPacket, FeedMood
from visualization.pdw.capsulation.capsulator import Capsulator
from visualization.visualizationparams import Channel_id_to_name, DataMode
from visualization.helper_functions import find_nearest_value_indx
from visualization.pdw.pdwhistory import PDWHistory
import numpy as np


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket, FeedMood)
    zoomed_area_is_ready = pyqtSignal(DataPacket, FeedMood)
    select_areas_is_ready = pyqtSignal(DataPacket, FeedMood)
    columns_defined = pyqtSignal(dict)
    deleteSelectedRequested = pyqtSignal(list) # list of tuples 
    progress_is_ready = pyqtSignal(dict)
    clearRequested = pyqtSignal()
    lineCursorDataRequested = pyqtSignal(float)
    markerLineResultIsReady = pyqtSignal(dict)
    pointMarkerDataRequested = pyqtSignal(str, tuple)
    dataIsReadyForCapsulation = pyqtSignal(dict)
    pointMarkerResultIsReady = pyqtSignal(tuple)
    totalSizeIsReady = pyqtSignal(int)


    def __init__(self):
        super(DataHandler, self).__init__()

        # majules
        self.reader = SReader()
        self.parser = SParser()
        self.capsulator = Capsulator()

        # connections
        self.file_path_changed.connect(self.reader.set_file_path)
        self.clearRequested.connect(self.reader.clear)
        self.clearRequested.connect(self.parser.clear)
        self.clearRequested.connect(self.capsulator.clear)
        self.lineCursorDataRequested.connect(self.capsulator.single_row_req)
        self.pointMarkerDataRequested.connect(self.capsulator.single_data_req)
        self.dataIsReadyForCapsulation.connect(self.capsulator.feed)

        self.reader.batch_is_ready.connect(self.parser.prepare_data)
        self.reader.progress_is_ready.connect(self.progress_is_ready)

        self.parser.columns_defined.connect(self.define_columns)
        self.parser.data_packet_is_ready.connect(self.on_main_data_recieved)
        self.parser.progress_is_ready.connect(self.progress_is_ready)
        self.parser.totalSizeIsReady.connect(self.totalSizeIsReady)


        self.capsulator.capsulated_data_is_reaady.connect(self.on_capsulated_data_recieved)        
        self.capsulator.markerLineResultIsReady.connect(self.markerLineResultIsReady)
        self.capsulator.pointMarkerResultIsReady.connect(self.pointMarkerResultIsReady)
        self.capsulator.progress_is_ready.connect(self.progress_is_ready)


        self.timer = QElapsedTimer()
        self.timer.start()
        

        # variables
        self.columns = dict()
        self.normal_data = {}
        self.full_time_duration = 0
        self.capsulated_data = None
        # self.select_areas = {} # {(time_range, val_range) : ((capsul_data,cap_indexes) , (main_data, main_indexes))}
        self.select_areas = {} # {data_type : DataPack(index)}
        self.select_areas[DataMode.normal] = dict()
        self.select_areas[DataMode.capsulated] = dict()
        self.history = []
        self.current_hist = None
        # self.currnet_showing_index = -1


        # moving to thread
        self.objThread = QThread(self)
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    @pyqtSlot(dict)
    def define_columns(self, columns):
        if "CW" in columns:
            columns.pop("CW")
        if "No." in columns:
            columns.pop("No.")
        for i in range(1, len(columns.keys())):
            channel = list(columns.keys())[i]
            unit = list(columns.values())[i]
            self.columns[i] = (channel,unit)
        self.columns_defined.emit(self.columns)

    @pyqtSlot(dict)
    def on_main_data_recieved(self, data):
        self.normal_data = data
        time_data = (list(data.values())[0]).key
        self.full_time_duration = time_data[-1] - time_data[0]
        self.dataIsReadyForCapsulation.emit(data)

    @pyqtSlot(dict, FeedMood)
    def on_capsulated_data_recieved(self, data_pack, mood):
        self.capsulated_data = data_pack

        hist_obj = PDWHistory(DataMode.capsulated)
        hist_obj.data = data_pack 
        self.history.append(hist_obj)

        self.current_hist = hist_obj
        self.to_plot(data_pack, FeedMood.main_data)


    def to_plot(self, data, mode):
        if data :
            for name, pack in data.items():
                self.final_data_is_ready.emit(pack, mode)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)

    @pyqtSlot(str, tuple, tuple)
    def on_zoom_requested(self,ch_name, time_range, value_range):
        if self.is_normal_data_needed(time_range):
            working_data = self.normal_data
            data_mode = DataMode.normal
        else:
            working_data = self.capsulated_data
            data_mode = DataMode.capsulated

        output = self.search_in_data(working_data,ch_name, time_range, value_range, data_mode)
        if not output:
            return
        
        new_data, new_data_indexes = output
        self.to_plot(new_data, FeedMood.zoom)

        hist_obj = PDWHistory(data_mode)
        hist_obj.data = new_data 
        hist_obj.time_range = time_range
        hist_obj.val_range = value_range
        self.current_hist = hist_obj
        self.history.append(hist_obj)


    @pyqtSlot(str, tuple, tuple)
    def on_select_req(self,ch_name, time_range, value_range):
        if ch_name == "":
            ch_name = (list(self.columns.values())[0])[0]

        
        if self.current_hist.data_mode == DataMode.capsulated:
            working_data = self.capsulated_data
            backup_data = self.normal_data
            backup_hist_mode = DataMode.normal
        elif self.current_hist.data_mode == DataMode.normal:
            working_data = self.normal_data
            backup_data = self.capsulated_data
            backup_hist_mode = DataMode.capsulated

         
        selected_output = self.search_in_data(working_data,ch_name, time_range, value_range, self.current_hist.data_mode)
        if not selected_output:
            return
        new_data, new_data_indexes = selected_output
        self.to_plot(new_data, FeedMood.select)

        backup_output = self.search_in_data(backup_data,ch_name, time_range, value_range, backup_hist_mode)
        if not backup_output:
            return
        backup_select_region, backup_select_region_indexes = backup_output


        for hist in self.history:
            if hist.data_mode == self.current_hist.data_mode:
                reg =  new_data
                idxs = new_data_indexes
            else:
                reg = backup_select_region
                idxs = backup_select_region_indexes

            hist.add_selected(reg,idxs)

        if hist.data_mode == self.current_hist.data_mode:
            workig_index = new_data_indexes
        else:
            workig_index = backup_select_region_indexes

        if self.current_hist.data_mode in self.select_areas.keys(): 
            selected_data = self.select_areas[self.current_hist.data_mode]
            for name , indexes in workig_index.items():
                if name not in selected_data.keys():
                    selected_data[name] = set() 
                selected_data[name].update(indexes)




    def is_normal_data_needed(self,time_range):
        diff = time_range[1] - time_range[0]
        percentage = diff / self.full_time_duration
        if percentage > 0.5:
            return False
        else:
            return True

    def search_in_data(self, working_data, ch_name, time_range, value_range, type=DataMode.normal):
        current_channel_time_list = (working_data[ch_name]).key
        current_channel_val_list = (working_data[ch_name]).data

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


        if first_x_index == last_x_index:
            return

        result_pack = {}
        result_pack_index = {}
        needed_indexes = [x for x in range(first_x_index, last_x_index+1)]

        if type == DataMode.normal:
            final_indexes = []
            final_key = []
            for idx in needed_indexes:
                candidate_val = current_channel_val_list[idx]
                if candidate_val > value_range[0] and candidate_val < value_range[1]:
                    final_indexes.append(idx)
                    final_key.append(current_channel_time_list[idx])

            result_pack = {}
            result_pack_index = {}
            for name, pack in working_data.items():
                final_pack = DataPacket()
                final_pack.key = final_key
                final_pack.data = np.array([pack.data[ix] for ix in final_indexes])
                final_pack.id = pack.id
                result_pack[name] = final_pack
                result_pack_index[name] = final_indexes
        else:
            final_indexes = []
            final_key = []
            final_val = []
            for idx in needed_indexes:
                candidate_val = current_channel_val_list[idx]
                if candidate_val > value_range[0] and candidate_val < value_range[1]:
                    final_indexes.append(idx)
                    final_key.append(current_channel_time_list[idx])
                    final_val.append(current_channel_val_list[idx])
        
            if len(final_key) == 0:
                return

            outout_key =list(set(final_key))

            for name, pack in working_data.items():
                required_key = []
                required_val = []
                indexes = []
                for time in outout_key:
                    idxs = np.where(pack.key == time)
                    indexes.extend(idxs[0])
                    if name != ch_name:
                        required_key.extend([pack.key[ix] for ix in idxs[0]])
                        required_val.extend([pack.data[ix] for ix in idxs[0]])
                    else:
                        required_key = final_key
                        required_val = final_val
                final_pack = DataPacket()
                final_pack.key = np.array(required_key)
                final_pack.data = np.array(required_val)
                final_pack.id = pack.id
                result_pack[name] = final_pack
                result_pack_index[name] = indexes

        return result_pack, result_pack_index


    @pyqtSlot()
    def on_forward_zoom_req(self):
        req_index = self.current_hist.index +1
        if req_index < len(self.history):
            data_obj = self.history[req_index]
            self.to_plot(data_obj.data, FeedMood.zoom)
            self.to_plot(data_obj.selected_area, FeedMood.select)
            self.current_hist = data_obj

    @pyqtSlot()
    def on_backward_zoom_req(self):
        req_index = self.current_hist.index - 1
        if req_index >= 0 :
            data_obj = self.history[req_index]
            self.to_plot(data_obj.data, FeedMood.zoom)
            self.to_plot(data_obj.selected_area, FeedMood.select)
            self.current_hist = data_obj
            if self.current_hist.index == 0:
                original_data  = self.history[0]
                self.history.clear()
                self.history.append(original_data)

        

    def reset_zoom(self):
        # self.currnet_showing_index = 0
        original_data  = self.history[0]
        self.to_plot(original_data.data, FeedMood.zoom)
        # self.to_add_selected_area(original_data, PDWHistory.history_index)
        self.history.clear()
        self.history.append(original_data)

    @pyqtSlot()
    def clear(self):
        self.columns = dict()
        self.history.clear()
        self.select_areas.clear()
        self.clearRequested.emit()
        self.select_areas[DataMode.normal] = dict()
        self.select_areas[DataMode.capsulated] = dict()

    
    @pyqtSlot(tuple)
    def unselect_special_area(self, area):
        for seleted in self.select_areas.keys():
            if seleted == DataMode.normal:
                current_channel_time_list = (list(self.normal_data.values())[0]).key
            elif seleted == DataMode.capsulated:
                current_channel_time_list = (list(self.capsulated_data.values())[0]).key

        may_first_x_index = find_nearest_value_indx(current_channel_time_list, area[0])
        f_ind_val = current_channel_time_list[may_first_x_index]
        f_indices = np.where(current_channel_time_list == f_ind_val)[0]
        first_x_index = f_indices[0]
        may_last_x_index = find_nearest_value_indx(current_channel_time_list, area[1])
        l_ind_val = current_channel_time_list[may_last_x_index]
        l_indices = np.where(current_channel_time_list == l_ind_val)[0]
        last_x_index = l_indices[-1]

        indexes = [i for i in range(first_x_index, last_x_index+1)]

        for name, pack in self.select_areas[seleted].items():
            for idx in indexes:
                if idx in pack:
                    pack.remove(idx) 


    @pyqtSlot()
    def unselect_all(self):
        if len(self.history) == 1:
            self.select_areas.clear()
            self.history[0].selected_area.clear()
        


    @pyqtSlot()
    def on_delete_selected_req(self):

        for mode, selected_data in self.select_areas.items():
            for name, idx in selected_data.items():
                idx = list(idx)
                if mode == DataMode.normal:
                    self.normal_data[name].key = np.delete(self.normal_data[name].key, idx)
                    self.normal_data[name].data = np.delete(self.normal_data[name].data, idx)
                else:
                    self.capsulated_data[name].key = np.delete(self.capsulated_data[name].key, idx)
                    self.capsulated_data[name].data = np.delete(self.capsulated_data[name].data, idx)
                    

        self.history.clear()

        hist_obj = PDWHistory(DataMode.capsulated)
        hist_obj.data = self.capsulated_data 
        self.history.append(hist_obj)

        self.to_plot(self.capsulated_data , FeedMood.main_data)



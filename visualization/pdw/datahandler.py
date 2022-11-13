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
from visualization.visualizationparams import Channel_id_to_name
from visualization.helper_functions import find_nearest_value_indx
from visualization.pdw.pdwhistory import PDWHistory
import numpy as np


class DataHandler(QObject):
    file_path_changed = pyqtSignal(str)
    final_data_is_ready = pyqtSignal(DataPacket, FeedMood)
    zoomed_area_is_ready = pyqtSignal(DataPacket, FeedMood)
    select_areas_is_ready = pyqtSignal(DataPacket, FeedMood)
    columns_defined = pyqtSignal(dict)
    # selectDataRequested = pyqtSignal(str, tuple, tuple)  # time Range & value range
    deleteSelectedRequested = pyqtSignal(list) # list of tuples 
    progress_is_ready = pyqtSignal(dict)
    clearRequested = pyqtSignal()
    lineCursorDataRequested = pyqtSignal(float)
    markerLineResultIsReady = pyqtSignal(dict)
    pointMarkerDataRequested = pyqtSignal(str, tuple)
    dataIsReadyForCapsulation = pyqtSignal(dict)
    pointMarkerResultIsReady = pyqtSignal(tuple)
    totalSizeIsReady = pyqtSignal(int)
    # zoom_requested = pyqtSignal(str,tuple,tuple)



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
        self.parser.data_packet_is_ready.connect(self.packetize_data_cap_mod)
        self.parser.progress_is_ready.connect(self.progress_is_ready)
        self.parser.totalSizeIsReady.connect(self.totalSizeIsReady)


        self.capsulator.capsulated_data_is_reaady.connect(self.send_capsulated_data)        
        self.capsulator.markerLineResultIsReady.connect(self.markerLineResultIsReady)
        self.capsulator.pointMarkerResultIsReady.connect(self.pointMarkerResultIsReady)
        self.capsulator.progress_is_ready.connect(self.progress_is_ready)


        self.timer = QElapsedTimer()
        self.timer.start()
        

        # variables
        self.columns = dict()
        self.main_data = {}
        self.capsulated_data = None
        self.select_areas = {} # {(time_range, val_range) : ((capsul_data,cap_indexes) , (main_data, main_indexes))}
        self.history = []
        self.currnet_showing_index = -1


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
    def packetize_data_cap_mod(self, data):
        self.main_data = data
        self.dataIsReadyForCapsulation.emit(data)
    
    @pyqtSlot(dict, FeedMood)
    def send_capsulated_data(self, data_pack, mood):
        self.capsulated_data = data_pack

        hist_obj = PDWHistory(True)
        hist_obj.data = data_pack 
        self.history.append(hist_obj)

        self.currnet_showing_index += 1
        self.to_plot(data_pack, FeedMood.main_data)


    @pyqtSlot(str, tuple, tuple)
    def on_zoom_requested(self,ch_name, time_range, value_range):
        new_data, new_data_indexes = self.search_in_maindata(self.main_data,ch_name, time_range, value_range)
        self.to_plot(new_data, FeedMood.zoom)
        self.currnet_showing_index += 1
        
        hist_obj = PDWHistory()
        hist_obj.data = new_data 
        hist_obj.time_range = time_range
        hist_obj.val_range = value_range
        self.history.append(hist_obj)

        self.to_add_selected_area(hist_obj, self.currnet_showing_index)


    @pyqtSlot(dict)
    def packetize_data(self, data):
        for name, val in data.items():
            if name != "TOA" and name != "CW":
                final_data = DataPacket()
                final_data.data = val
                final_data.key = data['TOA']
                myval = list(self.columns.values())
                final_data.id = [myval.index(item)+ 1 for item in myval if item[0] == name][0]
                Channel_id_to_name[final_data.id] = name
                self.final_data_is_ready.emit(final_data)

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path_changed.emit(file_path)
    
    @pyqtSlot()
    def clear(self):
        self.columns = dict()
        self.history.clear()
        self.select_areas.clear()
        self.clearRequested.emit()

    @pyqtSlot()
    def reset_zoom(self):
        self.currnet_showing_index = 0
        original_data  = self.history[0]
        self.to_plot(original_data.data, FeedMood.zoom)
        self.to_add_selected_area(original_data, self.currnet_showing_index)
        self.history.clear()
        self.history.append(original_data)

    @pyqtSlot()
    def on_forward_zoom_req(self):
        req_index = self.currnet_showing_index +1
        if req_index < len(self.history):
            data_obj = self.history[req_index]
            self.to_plot(data_obj.data, FeedMood.zoom)
            self.to_add_selected_area(data_obj, req_index)

            self.currnet_showing_index += 1


    @pyqtSlot()
    def on_backward_zoom_req(self):
        req_index = self.currnet_showing_index - 1
        if req_index >= 0 :
            data_obj = self.history[req_index]
            self.to_plot(data_obj.data, FeedMood.zoom)
            self.to_add_selected_area(data_obj, req_index)
            self.currnet_showing_index -= 1
            if self.currnet_showing_index == 0:
                original_data  = self.history[0]
                self.history.clear()
                self.history.append(original_data)

    @pyqtSlot(str, tuple, tuple)
    def on_select_req(self,ch_name, time_range, value_range):
        if ch_name == "":
            ch_name = (list(self.columns.values())[0])[0]

        if self.currnet_showing_index == 0:
            used_data = self.capsulated_data
            backup_data = self.main_data
            searching_func =  self.search_in_capsulateddata
            backup_searching_func = self.search_in_maindata
        else :
            used_data = self.main_data
            backup_data = self.capsulated_data
            searching_func =  self.search_in_maindata
            backup_searching_func = self.search_in_capsulateddata


        select_region, select_region_indexes = searching_func(used_data, ch_name, time_range, value_range)
        self.to_plot(select_region, FeedMood.select)
        backup_select_region, backup_select_region_indexes = backup_searching_func(backup_data, ch_name, time_range, value_range)

        if self.currnet_showing_index == 0:
            capsulated_req = select_region
            main_reg = backup_select_region
            capsulated_req_indexes = select_region_indexes
            main_reg_indexes = backup_select_region_indexes
        else :
            capsulated_req = backup_select_region
            main_reg = select_region
            capsulated_req_indexes = backup_select_region_indexes
            main_reg_indexes = select_region_indexes

        self.select_areas[(time_range, value_range)] = ((capsulated_req,capsulated_req_indexes) , (main_reg,main_reg_indexes))
        

    def to_plot(self, data, mode):
        if data :
            for name, pack in data.items():
                self.final_data_is_ready.emit(pack, mode)

    def to_add_selected_area(self, hist_obj, req_index):
        hist_time_range = hist_obj.time_range
        hist_val_range = hist_obj.val_range
        for range, data_tuple in self.select_areas.items():
            sel_time_range = range[0]
            sel_val_range = range[1]
            cond1 = True
            cond2 = True
            if not hist_obj.is_capsulated:
                cond1 = (sel_time_range[0] >= hist_time_range[0] or sel_time_range[1] <= hist_time_range[1])
                cond2 = (sel_val_range[0] >= hist_val_range[0] or sel_val_range[1] <= hist_val_range[1])
            if cond1 and cond2:
                if req_index == 0:
                    ploting_data = (data_tuple[0])[0]
                else:
                    ploting_data = (data_tuple[1])[0]
                self.to_plot(ploting_data, FeedMood.select)

    def search_in_capsulateddata(self, working_data, ch_name, time_range, value_range):
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

        req_time = current_channel_time_list[first_x_index:last_x_index+1]
        req_val = current_channel_val_list[first_x_index:last_x_index+1]
        outout_key = []
        final_key = []
        final_val = []
        for key, val in zip(req_time, req_val):
            if val >= value_range[0] and val <= value_range[1]:
                final_key.append(key)
                final_val.append(val)


        if len(final_key) == 0:
            return

        outout_key =list(set(final_key))
        select_area = {}
        select_area_indexes = {}
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
            select_area[name] = final_pack
            select_area_indexes[name] = indexes
        return select_area, select_area_indexes


    def search_in_maindata(self, working_data, ch_name, time_range, value_range):
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

        req_time = current_channel_time_list[first_x_index:last_x_index+1]
        req_val = current_channel_val_list[first_x_index:last_x_index+1]
        # needed_indexes = [i for i in range(first_x_index,last_x_index+1)]

        # not_requiered_indexes = []
        # for key, val in zip(req_time, req_val):
        #     if val < value_range[0] and val > value_range[1]:
        #         not_requiered_indexes.extend(np.where(current_channel_time_list == key)[0])
                
        # needed_indexes = [x for x in needed_indexes if x not in not_requiered_indexes]

        needed_indexes = []
        for key, val in zip(req_time, req_val):
            if val > value_range[0] and val < value_range[1]:
                needed_indexes.extend(np.where(current_channel_time_list == key)[0])

        if len(needed_indexes) == 0:
            return

        result_pack = {}
        result_pack_index = {}
        for name, pack in working_data.items():
            final_pack = DataPacket()
            final_pack.key = np.array([pack.key[ix] for ix in needed_indexes])
            final_pack.data = np.array([pack.data[ix] for ix in needed_indexes])
            final_pack.id = pack.id
            result_pack[name] = final_pack
            result_pack_index[name] = needed_indexes
        return result_pack, result_pack_index

    @pyqtSlot(tuple)
    def unselect_special_area(self, area):
        target_key = None
        for seleted in self.select_areas.keys():
            if area == seleted[0]:
                target_key = seleted
                break
        if target_key:
            self.select_areas.pop(target_key)

    @pyqtSlot()
    def unselect_all(self):
        self.select_areas.clear()

    @pyqtSlot()
    def on_delete_selected_req(self):
        self.history.clear()
        self.currnet_showing_index = -1
        for range, data_tuple in self.select_areas.items():
            sel_cap_data_tuple = data_tuple[0]
            sel_cap_indexes = sel_cap_data_tuple[1]
            for data_packet, sel_inds in zip(self.capsulated_data.values(), sel_cap_indexes.values()):
                data_packet.key = np.delete(data_packet.key, sel_inds)
                data_packet.data = np.delete(data_packet.data, sel_inds)


        hist_obj = PDWHistory(True)
        hist_obj.data = self.capsulated_data 
        self.history.append(hist_obj)

        self.currnet_showing_index += 1
        self.to_plot(self.capsulated_data , FeedMood.main_data)

        for range, data_tuple in self.select_areas.items():
            sel_main_data_tuple = data_tuple[1]
            sel_main_indexes = sel_main_data_tuple[1]
            for data_packet, sel_inds in zip(self.main_data.values(), sel_main_indexes.values()):
                data_packet.key = np.delete(data_packet.key, sel_inds)
                data_packet.data = np.delete(data_packet.data, sel_inds)

        self.select_areas.clear()



from PyQt5.QtCore import QThread, QObject, pyqtSignal, QElapsedTimer, pyqtSlot
import numpy as np
from visualization.visualizationparams import DataPacket, Channel_id_to_name, ProgressType, FeedMood
from visualization.helper_functions import find_nearest_value_indx


# def find_nearest_value_indx(array, value):
#     array = np.asarray(array)
#     idx = (np.abs(array - value)).argmin()
#     return idx


class Capsulator(QObject):
    cell_count_v = 200
    cell_count_h = 800
    # cell_count_v = 20
    # cell_count_h = 80
    capsulated_data_is_reaady = pyqtSignal(dict, FeedMood)
    markerLineResultIsReady = pyqtSignal(dict)
    pointMarkerResultIsReady = pyqtSignal(tuple)
    progress_is_ready = pyqtSignal(dict)

    def __init__(self):
        super(Capsulator, self).__init__()
        self.capsulated_data = {}
        # self.time_indexes = {}
        self.time_resolution = 0

        # moving to thread
        self.objThread = QThread(self)
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()
            
    def clear(self):
        self.time_resolution = 0
        self.capsulated_data = {}


    def feed(self, data_dict):
        toa = ((list(data_dict.items())[0])[1]).key
        # data_dict.pop('TOA')
        # if "CW" in data_dict:
        #     data_dict.pop('CW')
        # if "No." in data_dict:
        #     data_dict.pop('No.')
        min_time = toa[0]
        max_time = toa[-1]
        
        time_length = max_time - min_time

        if max_time == min_time:
            time_length = min_time

        self.time_resolution = time_length/self.cell_count_h
        ch_counter = 1
        all_channels = len(data_dict.keys())

        for name, data_packet in data_dict.items():
            final_data_key = []
            final_data_val = []

            data_val = data_packet.data
            min_data = np.amin(data_val)
            max_data = np.amax(data_val)
            data_length = max_data - min_data

            if max_data == min_data:
                if min_data == 0:
                    data_length = 1
                else:
                    data_length = min_data


            data_resolution = data_length/self.cell_count_v

            time_chunks = np.array_split(toa, self.cell_count_h)

            time_index = 0
            time_chunk_index = 0

            for chunk in time_chunks:
                val_checked_indices = []
                final_time = (time_chunk_index + 0.5)*self.time_resolution
                for _ in chunk:
                    val = data_val[time_index]
                    val_index = val//data_resolution
                    if val_index not in val_checked_indices:
                        fianl_val = (val_index + 0.5)*data_resolution
                        final_data_key.append(final_time)
                        final_data_val.append(fianl_val)
                        val_checked_indices.append(val_index)
                    time_index += 1
                time_chunk_index += 1
           
            final_data = DataPacket()
            final_data.key = np.array(final_data_key)
            final_data.data = np.array(final_data_val)
            final_data.id = ch_counter
            ch_counter += 1
            Channel_id_to_name[final_data.id] = name
            self.capsulated_data[name] = final_data
            self.progress_is_ready.emit({ProgressType.capsulator: 1 if (ch_counter/all_channels)>=1 else ch_counter/all_channels})
        self.capsulated_data_is_reaady.emit(self.capsulated_data, FeedMood.main_data)

    @pyqtSlot(str, tuple, tuple)
    def prepare_requested_select_data(self,ch_name, time_range, value_range):
        if ch_name == "":
            ch_name = list(self.capsulated_data.keys())[0]
        current_channel_time_list = (self.capsulated_data[ch_name]).key
        current_channel_val_list = (self.capsulated_data[ch_name]).data

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
        for name, pack in self.capsulated_data.items():
            required_key = []
            required_val = []
            if name != ch_name:
                for time in outout_key:
                    idxs = np.where(pack.key == time)
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
        self.capsulated_data_is_reaady.emit(select_area, FeedMood.select)


    @pyqtSlot(float)
    def single_row_req(self, time):
        time_list = (list(self.capsulated_data.values())[0]).key
        index = find_nearest_value_indx(time_list, time)
        searched_val = time_list[index]
        output_data = {}
        for name, pack in self.capsulated_data.items():
            idx = ((np.where(pack.key == searched_val))[0])[0]
            output_data[name] = pack.data[idx]
        self.markerLineResultIsReady.emit(output_data)

    @pyqtSlot(str, tuple)
    def single_data_req(self,ch_name, data_point):
        req_ch = self.capsulated_data[ch_name]
        index = find_nearest_value_indx(req_ch.key, data_point[0])
        searched_val = req_ch.key[index]
        indices = np.where(req_ch.key == searched_val)[0]
        for idx in indices:
            if req_ch.data[idx] == data_point[1]:
                self.pointMarkerResultIsReady.emit((searched_val,req_ch.data[idx]))
                break

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

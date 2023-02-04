from visualization.visualizationparams import DataPacket, DataMode
from visualization.helper_functions import find_nearest_value_indx
import numpy as np

class PDWHistory:
    history_index = -1

    def __init__(self, data_mode = DataMode.normal):
        self._data = None
        self._time_range = None
        self._val_range = None
        self._data_mode = data_mode
        PDWHistory.history_index += 1 
        self.index = PDWHistory.history_index
        self._selected_area = {} # {name : data}
        self._selected_area_indexes = {} # {name : data}

    def __del__(self):
        PDWHistory.history_index -= 1

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _data):
        self._data = _data


    @property
    def data_mode(self):
        return self._data_mode

    @data_mode.setter
    def data_mode(self, _data_mode):
        self._data_mode = _data_mode

    @property
    def selected_area(self):
        return self._selected_area

    @selected_area.setter
    def selected_area(self, _selected_area):
        self._selected_area = _selected_area

    @property
    def selected_area_indexes(self):
        return self._selected_area_indexes

    @selected_area_indexes.setter
    def selected_area_indexes(self, _selected_area_indexes):
        self._selected_area_indexes = _selected_area_indexes

    @property
    def time_range(self):
        return self._time_range

    @time_range.setter
    def time_range(self, _time_range):
        self._time_range = _time_range

    @property
    def val_range(self):
        return self._val_range

    @val_range.setter
    def val_range(self, _val_range):
        self._val_range = _val_range

    def add_selected(self, reg, indexes):
        if len(self.selected_area) == 0:
            self.selected_area = reg
            # self.selected_area_indexes = indexes
            return

        for name , ch in reg.items():
            idxs = indexes[name]
            
            if name not in self.selected_area_indexes.keys():
                self.selected_area_indexes[name] = set() 
            self.selected_area_indexes[name].update(idxs)


            selected_obj = self.selected_area[name]
            min_time_reg = ch.key[0]
            max_time_reg = ch.key[-1]
            min_time_sel = selected_obj.key[0]
            max_time_sel = selected_obj.key[-1]

            if min_time_reg >= min_time_sel:
                selected_obj.key = np.append(selected_obj.key,ch.key)
                selected_obj.data = np.append(selected_obj.data,ch.data)
            if max_time_reg < max_time_sel: 
                selected_obj.key = np.concatenate((selected_obj.key, ch.key), axis=None)
                selected_obj.data = np.concatenate((selected_obj.data, ch.data), axis=None)



            



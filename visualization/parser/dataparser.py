from abc import ABC, abstractmethod

import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject


class Parser(ABC):
    @abstractmethod
    def parse(self) -> dict:
        pass


class FinalMeta(type(QObject), type(Parser)):
    pass


class DataParser(Parser, QObject, metaclass=FinalMeta):
    data_is_ready = pyqtSignal(dict)
    columns_defined = pyqtSignal(list)
    columns = list()
    parsed_data = {}

    def __init__(self):
        super(DataParser, self).__init__()
        # self.received_data = None
        # self.columns = list
        self.initilize_data = True

    @pyqtSlot(dict)
    def set_data(self, received_data) -> None:
        if received_data['data']:
            self.parse(received_data['data'])
            if received_data['end']:
                self.data_is_ready.emit(self.parsed_data)

    def parse(self, received_data) -> None:
        self._set_columns(received_data)
        if self.initilize_data:
            self._init_data()
            self.initilize_data = False

        for line in received_data.split("\n")[2:]:
            cols = line.split()
            for i in range(len(cols)):
                col_name = self.columns[i]
                self.parsed_data[col_name] = np.append(self.parsed_data[col_name], [float(cols[i])])
                # self.parsed_data[col_name].append(cols[i])
        # return self.parsed_data

    def _set_columns(self, received_data) -> None:
        if not self.columns:
            if self._has_columns(received_data):
                self.columns = received_data.split("\n")[0].split()[1:]
                self.columns_defined.emit(self.columns)
            else:
                print("ERORRRRRRR!")

    def _init_data(self) -> None:
        for column in self.columns:
            self.parsed_data[column] = np.ndarray(0)

    def _has_columns(self, received_data) -> bool:
        first_line = received_data.split("\n")[0]
        if first_line[0] != "%":
            return False
        return True

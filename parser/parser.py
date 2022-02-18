from abc import ABC, abstractmethod


class Product(ABC):
    @abstractmethod
    def parse(self) -> str:
        pass


class Data(Product):
    def __init__(self, recieved_data, columns):
        self.recieved_data = recieved_data
        self.columns = columns
        self.parsed_data = {}

    def parse(self) -> dict:
        self._set_columns()
        self._init_data()
        for line in self.recieved_data.split("\n")[2:]:
            cols = line.split()
            for i in range(len(cols)):
                col_name = self.columns[i]
                self.parsed_data[col_name].append(cols[i])
        return self.parsed_data

    def _set_columns(self) -> void:
        if self.columns == []:
            if self._has_columns():
                self.columns = self.recieved_data.split("\n")[0].split()
            else:
                print("ERORRRRRRR!")

    def _init_data(self) -> void:
        for column in self.columns:
            self.parsed_data[column] = []

    def _has_columns(self) -> bool:
        first_line = self.recieved_data.split("\n")[0]
        if first_line[0] != "%":
            return false
        return true


class Signal(Product):
    def __init__(self, recieved_data):
        self.recieved_data = recieved_data

    def parse(self) -> str:
        pass

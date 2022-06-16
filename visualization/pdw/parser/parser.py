from abc import ABC, abstractmethod


class Product(ABC):
    @abstractmethod
    def parse(self) -> dict:
        pass


class Data(Product):
    def __init__(self, received_data, columns):
        self.received_data = received_data
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

    def _set_columns(self) -> None:
        if not self.columns:
            if self._has_columns():
                self.columns = self.recieved_data.split("\n")[0].split()
            else:
                print("ERORRRRRRR!")

    def _init_data(self) -> None:
        for column in self.columns:
            self.parsed_data[column] = []

    def _has_columns(self) -> bool:
        first_line = self.recieved_data.split("\n")[0]
        if first_line[0] != "%":
            return False
        return True


class Signal(Product):
    def __init__(self, received_data):
        self.received_data = received_data

    def parse(self) -> str:
        pass

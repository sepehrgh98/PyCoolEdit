from abc import ABC, abstractmethod


# class SingletonMeta(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             instance = super().__call__(*args, **kwargs)
#             cls._instances[cls] = instance
#         return cls._instances[cls]


class Product(ABC):
    @abstractmethod
    def parse(self) -> str:
        pass


# class FinalMeta(type(Product), type(SingletonMeta)):
#     pass
#

# class Data(Product, metaclass=FinalMeta):
class Data(Product):
    _instance = None
    columns = None
    parsed_data = {}

    def __new__(cls, *args, **kwargs):
        # print("newwww")
        if Data._instance is not None:
            return Data._instance
        # print("new1")
        obj = super().__new__(cls)
        Data._instance = obj
        return obj

    def __init__(self, received_data):
        # if Data._instance is None:
        #     print("initttttttt")
        # self.columns = None
        self.received_data = received_data

    def parse(self) -> dict:
        # if self.parsed_data is not {}:
        #     print("first: ", len(self.parsed_data['TOA']))
        # print("cooolll: ", self.columns)
        # print("rec: ", self.received_data[:40])
        self._set_columns()
        self._init_data()
        print(Data.parsed_data.keys())
        for line in self._get_pure_data():
            cols = line.split()
            # print(cols)
            for i in range(len(cols)):
                col_name = Data.columns[i]
                # print(col_name)
                # print(cols[i])
                Data.parsed_data[col_name].extend([cols[i]])
        print(len(Data.parsed_data['TOA']), len(Data.parsed_data['Omni']), len(Data.parsed_data['DF']))
        # print((Data.parsed_data['TOA']))
        return Data.parsed_data

    def _set_columns(self) -> None:
        print("parser: ", self, Data.columns)
        if Data.columns is None:
            if self._has_columns():
                # print(self._get_columns_string().split())
                Data.columns = self._get_columns_string().split()
                print("clo1: ", Data.columns)
            else:
                print("ERORRRRRRR!")

    def _init_data(self) -> bool:
        for column in Data.columns:
            # print(column)
            # self.parsed_data
            Data.parsed_data.setdefault(column, [])
            # self.parsed_data[column] =

    def _has_columns(self) -> bool:
        first_line = self.received_data.split("\n")[0]
        # print("bbbbbbbbbbbb: ", first_line, "cc", first_line[0])
        if first_line[0] != "%" and first_line[:2] != " %":
            # print("False")
            return False
        return True

    def _get_columns_string(self) -> str:
        first_line = self.received_data.split("\n")[0]
        if first_line[0] == "%":
            return first_line[1:]
        if first_line[:2] == " %":
            return first_line[2:]

    def _get_pure_data(self) -> str:
        if self._has_columns():
            return self.received_data.split("\n")[2:]
        else:
            return self.received_data.split("\n")

# class Signal(Product):
#     def __init__(self, received_data):
#         self.received_data = received_data
#
#     def parse(self) -> str:
#         pass

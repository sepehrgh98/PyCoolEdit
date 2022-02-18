from abc import ABC, abstractmethod

from parser.parser import Product, Data


#
# class SingletonMeta(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             instance = super().__call__(*args, **kwargs)
#             cls._instances[cls] = instance
#         return cls._instances[cls]
#

class Creator(ABC):
    @abstractmethod
    def make(self):
        pass

    def call_parser(self) -> None:
        product = self.make()
        result = product.parse()
    # signal result


class DataCreator(Creator):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if DataCreator._instance is not None:
            return DataCreator._instance
        obj = super().__new__(cls)
        DataCreator._instance = obj
        return obj

    def __init__(self, received_data):
        self.received_data = received_data
        # self.data_object = None

    def make(self) -> Product:
        # if self.data_object is None:
        #     return Data(self.received_data)
        # else:
        #     self.data_object.received_data = self.received_data
        #     return self.data_object
        return Data(self.received_data)

# class SignalCreator(Creator):
#     def __init__(self, received_data):
#         self.received_data = received_data
#
#     def make(self) -> Product:
#         # return Signal(self.received_data)

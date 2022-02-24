from abc import ABC, abstractmethod

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from visualization.parser.parser import Product, Data


# from visualizationparams import DataPacket


class Creator(ABC):
    @abstractmethod
    def make(self):
        pass

    # def call_parser(self) -> None:
    #     product = self.make()
    #     result = product.parse()
    #     self


class DataParser(Creator):
    data_is_ready = pyqtSignal(dict)

    def __init__(self):
        self.received_data = None
        self.columns = None

    @pyqtSlot(str)
    def set_data(self, received_data):
        self.received_data = received_data

    def make(self) -> Product:
        return Data(self.received_data, self.columns)

    def call_parser(self) -> None:
        product = self.make()
        result = product.parse()
        self.data_is_ready.emit(result)

# class SignalCreator(Creator):
#     def __init__(self, received_data):
#         self.received_data = received_data
#
#     def make(self) -> Product:
#         # return Signal(self.recieved_data)

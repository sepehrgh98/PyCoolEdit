# from abc import ABC, abstractmethod
#
# from PyQt5.QtCore import pyqtSlot, pyqtSignal
#
# from parser.parser import Product, Data
#
#
# class Creator(ABC):
#     @abstractmethod
#     def make(self):
#         pass
#
#     @abstractmethod
#     def call_parser(self) -> None:
#         pass
#
#
# class DataParser(Creator):
#     data_is_ready = pyqtSignal(dict)
#
#     def __init__(self):
#         self.received_data = None
#         # self.columns = None
#
#     @pyqtSlot(dict)
#     def set_data(self, received_data):
#         self.received_data = received_data
#         self.call_parser()
#
#     def make(self) -> Product:
#         return Data(self.received_data)
#
#     def call_parser(self) -> None:
#         product = self.make()
#         result = product.parse()
#         self.data_is_ready.emit(result)
#
# # class SignalCreator(Creator):
# #     def __init__(self, received_data):
# #         self.received_data = received_data
# #
# #     def make(self) -> Product:
# #         # return Signal(self.recieved_data)

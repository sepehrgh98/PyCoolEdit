from abc import ABC, abstractmethod
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from reader.reader import Product, Data


class Creator(ABC):
    @abstractmethod
    def make(self) -> Product:
        pass

    @abstractmethod
    def call_read(self) -> None:
        pass


class FinalMeta(type(QObject), type(Creator)):
    pass


class DataCreator(Creator, QObject, metaclass=FinalMeta):
    reading_batch_file_is_ready = pyqtSignal(str)

    def __init__(self, number_of_line_to_read_one_call=10000):
        Creator.__init__(self)
        QObject.__init__(self)
        self.file_path = ""
        self.number_of_line_to_read_one_call = number_of_line_to_read_one_call

    @pyqtSlot(str)
    def set_file_path(self, file_path):
        print(file_path)
        if file_path != self.file_path:
            self.file_path = file_path

    def make(self) -> Product:
        return Data(self.file_path, self.number_of_line_to_read_one_call)

    def call_read(self) -> None:
        product = self.make()
        # print(product.file_name, product.number_of_line_to_read_one_call)
        result = product.read()
        for res in result:
            # print("res: ", res[:50])
            self.reading_batch_file_is_ready.emit(res)

# class SignalCreator(Creator):
#     def __init__(self, file_name, chunk=1024 * 1024 * 20):
#         self.file_name = file_name
#
#     def make(self) -> Product:
#         pass
#         # return Signal(self.file_name, self.chunk)

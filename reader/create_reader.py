from abc import ABC, abstractmethod

from observer import Observer
from reader.reader import Product, Data


class Creator(ABC):
    @abstractmethod
    def make(self) -> Product:
        pass

    @abstractmethod
    def call_read(self) -> None:
        pass


class DataCreator(Creator, Observer):

    def __init__(self, file_name, number_of_line_to_read_one_call=10000):
        Creator.__init__(self)
        Observer.__init__(self)
        self.file_name = file_name
        self.number_of_line_to_read_one_call = number_of_line_to_read_one_call
        self._batch = ""

    def make(self) -> Product:
        return Data(self.file_name, self.number_of_line_to_read_one_call)

    def call_read(self) -> None:
        product = self.make()
        print(product.file_name, product.number_of_line_to_read_one_call)
        result = product.read()
        for batch in result:
            # print("res: ", batch[:40])
            self.batch = batch

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self._batch = value
        self.notify({"data": self._batch})


# class SignalCreator(Creator):
#     def __init__(self, file_name, chunk=1024 * 1024 * 20):
#         self.file_name = file_name
#
#     def make(self) -> Product:
#         pass
#         # return Signal(self.file_name, self.chunk)
#
#     def call_read(self) -> None:
#         pass

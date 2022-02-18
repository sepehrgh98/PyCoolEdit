from abc import ABC, abstractmethod


class Creator(ABC):
    @abstractmethod
    def make(self):
        pass

    def call_parser(self) -> Void:
        product = self.make()
        result = product.parse()
#        signal result


class DataCreator(Creator):
    def __init__(self, received_data, columns):
        self.received_data = received_data
        self.columns = columns

    def make(self) -> Product:
        return Data(self.received_data, self.columns)


class SignalCreator(Creator):
    def __init__(self, received_data):
        self.received_data = received_data

    def make(self) -> Product:
        # return Signal(self.recieved_data)

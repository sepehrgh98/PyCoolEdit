import abc

class PDWAbstractExport(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def feed(self, data_dict):
      pass


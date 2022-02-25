from abc import ABC, abstractmethod


class Product(ABC):
    @abstractmethod
    def read(self) -> str:
        pass


class Data(Product):
    def __init__(self, file_name, number_of_line_to_read_one_call):
        self.file_name = file_name
        self.number_of_line_to_read_one_call = number_of_line_to_read_one_call

    def read(self):
        # print("read")
        with open(self.file_name, "r") as f:
            result = ""
            number = 0
            for line in f:
                if number < self.number_of_line_to_read_one_call:
                    number += 1
                    result += line
                else:
                    yield [result, False]
                    result = ""
                    number = 0
            yield [result, True]


# class Signal(Product):
#     def __init__(self, file_name, chunk):
#         self.file_name = file_name
#
#     def read(self) -> str:
#         with open(self.file_name) as f:
#             for chunked_signal in self._read_in_chunks(f):
#                 yield chunked_signal
#
#     def _read_in_chunks(self):
#         while True:
#             data = self.file_object.read(self.chunk)
#             if not data:
#                 break
#             yield data

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

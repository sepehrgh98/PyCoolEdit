from create_reader import DataCreator, Creator


def client(creator: Creator) -> None:
    creator.call_read()


if __name__ == "__main__":
    file_name = r"C:\Users\edr\Desktop\visualization" + r"\data.txt"
    chunk = 1024 * 1024 * 100
    number_of_line_to_read_one_call = 50  # lines
    client(DataCreator(file_name, number_of_line_to_read_one_call))
    # client(SignalCreator(file_name, chunk))

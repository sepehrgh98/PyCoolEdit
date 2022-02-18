from reader.create_reader import DataCreator, Creator


def client(creator: Creator) -> None:
    creator.call_read()

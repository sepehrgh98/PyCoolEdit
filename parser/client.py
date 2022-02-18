from parser.create_parser import Creator, DataCreator


def client(creator: Creator) -> None:
    #    get signal from reader and call_parser
    creator.call_parser()


class GetBatchFile:
    # def __init__(self):
    #     self.data = None

    def update(self, subject):
        if "data" in subject:
            batch = subject["data"]
            # if self.data is None:
            #     self.data = DataCreator(batch)
            # self.data.received_data = batch
            # # print(self.data)
            # client(self.data)
            client(DataCreator(batch))
            print("get: ", batch[:40])


if __name__ == "__main__":
    pass

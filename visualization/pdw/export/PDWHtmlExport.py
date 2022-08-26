from visualization.pdw.export.PDWAbstractExport import PDWAbstractExport

@PDWAbstractExport.register
class PDWHtmlExport:
    def __init__(self, file_dir) -> None:
        self.file_dir = file_dir

    def feed(self, data_dict):
        pass
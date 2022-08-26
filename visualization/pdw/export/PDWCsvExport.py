from visualization.pdw.export.PDWAbstractExport import PDWAbstractExport
import csv

@PDWAbstractExport.register
class PDWCsvExport:
    def __init__(self, file_dir) -> None:
        self.file_dir = file_dir

    def feed(self, data_dict):
        header = list(data_dict.keys())
        row_count = len(list(data_dict.values())[0])
        with open(self.file_dir, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for i in range(row_count):
                row = []
                for ch in data_dict.values():
                    row.append(ch[i])
                writer.writerow(row)
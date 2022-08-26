from visualization.pdw.export.PDWAbstractExport import PDWAbstractExport

@PDWAbstractExport.register
class PDWTextExport:
    def __init__(self, file_dir) -> None:
        self.file_dir = file_dir

    def feed(self, data_dict):
        channel_name = list(data_dict.keys())
        row_count = len(list(data_dict.values())[0])
        col_count = len(list(data_dict.keys())[0])
        with open(self.file_dir, 'w') as f: 
            for ch in channel_name:
                f.write(str(ch))
                f.write('\t\t\t')
            f.write('\n')
            f.write("-"*50*col_count)
            f.write('\n')

            for i in range(row_count):
                for ch in data_dict.values():
                    f.write(str(ch[i]))
                    f.write('\t\t\t')
                f.write('\n')

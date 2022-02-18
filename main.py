# if __name__ == '__main__':
#     app = QApplication([])
#     pdwForm = PDWForm()
#     pdwForm.show()
#     sys.exit(app.exec_())

from parser.client import GetBatchFile
from reader.client import client
from reader.create_reader import DataCreator

if __name__ == "__main__":
    file_name = r"C:\Users\edr\Desktop\visualization" + r"\data.txt"
    chunk = 1024 * 1024 * 100
    number_of_line_to_read_one_call = 5000  # lines
    d = DataCreator(file_name, number_of_line_to_read_one_call)
    g = GetBatchFile()
    d.attach(g)
    # print("observer: ", d._observers)
    client(d)

    # client(SignalCreator(file_name, chunk))

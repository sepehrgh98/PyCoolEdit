import re
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QThread
from visualization.visualizationparams import ProgressType
import codecs

class SReader(QObject):
    batch_is_ready = pyqtSignal(list, bool, float)
    progress_is_ready = pyqtSignal(dict)
    def __init__(self, batch_size=10000) :
        super(SReader, self).__init__()
        self.batch_size = batch_size
        self.file_path = None
        self.progress = 0

        # moving to thread
        self.objThread = QThread(self)
        self.moveToThread(self.objThread)
        self.objThread.finished.connect(self.objThread.deleteLater)
        self.objThread.start()

    
    @pyqtSlot(str)
    def set_file_path(self, file_path) :
        if file_path != self.file_path:
            self.file_path = file_path
            self.start()

    def start(self):
        try:
            file_total_size = 0
            with codecs.open(self.file_path, 'r', encoding='utf-8',errors='ignore') as f:
                head = f.readline()
                has_hear = self.check_head(head)
                file_total_size = len(f.readlines())

            if not has_hear : raise ValueError
            number_of_batches = file_total_size / self.batch_size
            with codecs.open(self.file_path, 'r', encoding='utf-8',errors='ignore') as f:
                self.progress = 0
                result = []
                for line in f:
                    result.append(line)
                    if len(result) == self.batch_size:
                        self.progress = self.progress + (self.batch_size/file_total_size)
                        self.progress_is_ready.emit({ProgressType.reader:self.progress})
                        self.batch_is_ready.emit(result, False, number_of_batches)
                        result.clear()
                self.progress = self.progress + (self.batch_size/file_total_size)
                self.progress_is_ready.emit({ProgressType.reader:1})
                self.batch_is_ready.emit(result, True, number_of_batches)
        except UnicodeDecodeError:
            print("Can not decode this file!")
        except ValueError:
            print("no channels found!")

    def clear(self):
        self.file_path = None
        self.progress = 0

    def check_head(self, head):
        l = head.split()
        res = True
        for item in l:
            if item.isnumeric():
                res = False
        return res
                    
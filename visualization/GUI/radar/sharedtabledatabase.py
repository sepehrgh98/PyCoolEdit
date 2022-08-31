import re
from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QMimeData, QByteArray, QDataStream, QIODevice

class SharedTableDataBase(QAbstractTableModel):
    # class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers = [], items = [[]], parent = None):
        super(SharedTableDataBase,self).__init__(parent)
        self.__items = items
        self.__headers = headers

        row_counter = 0
        for row_item in self.__items:
            column_counter = 0
            for column_item in row_item:
                idx = self.createIndex(row_counter, column_counter)
                self.setData(idx, column_item, Qt.EditRole)
                self.dataChanged.emit(idx, idx)
                column_counter += 1
            row_counter += 1        

        num_headers = len(self.__headers)
        for section in range(0, num_headers):
            self.setHeaderData(section, Qt.Horizontal, self.__headers[section])
        self.headerDataChanged.emit(Qt.Horizontal, 0, num_headers)

    def index(self, row, column, parent):
        if row < 0 or row >= len(self.__items):
            return QModelIndex()
        return self.createIndex(row, column, self.__items[row])

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, index):
        if index.isValid():
            return 

        num_rows = len(self.__items)

        # checking for empty nested columns list within a single "row"
        if num_rows == 1:
            if len(self.__items[0]) == 0:
                return 0

        return num_rows

    def columnCount(self, index):
        if index.isValid():
            return 0

        # compute the max column count within all rows
        max_column_count = 0
        for row in self.__items:
            column_count = len(row)
            if column_count > max_column_count:
                max_column_count = column_count

        # if there are no real columns, make the column count return the number of headers instead
        if max_column_count < len(self.__headers):
            max_column_count = len(self.__headers)
        return max_column_count

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | \
                   Qt.ItemIsDropEnabled | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def supportedDropActions(self): 
        return Qt.CopyAction | Qt.MoveAction    

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        num_columns = self.columnCount(index)
        # inserting 'count' empty rows starting at 'row'
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        for i in range(0, count):
            # inserting as many columns as the table currently has
            self.__items.insert(row + i, ["" for i in range(0, num_columns)])
        self.endInsertRows()
        return True

    def removeRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        num_rows = self.rowCount(QModelIndex())
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(count, 0, -1):
            self.__items.pop(row - i + 1)
        self.endRemoveRows()
        return True

    def data(self,index,role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if row < 0 or row >= len(self.__items):
                return ""
            if column < 0 or column >= len(self.__items[row]):
                return ""
            else:
                return self.__items[row][column]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid:
            return False
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            if row < 0 or row >= self.rowCount(QModelIndex()):
                return False
            if column < 0 or column >= len(self.__items[row]):
                return False
            self.__items[row].pop(column)
            self.__items[row].insert(column, value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < 0 or section >= len(self.__headers):
                    return ""
                else:
                    return self.__headers[section]
        return None

    def mimeTypes(self):
        return ['application/vnd.tableviewdragdrop.list']

    def mimeData(self, indexes):
        mimedata = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.DisplayRole)
                stream << QByteArray(text)
        mimedata.setData('application/vnd.tableviewdragdrop.list', encoded_data)
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True
        if not data.hasFormat('application/vnd.tableviewdragdrop.list'):
            return False
        if column > 0:
            return False

        num_rows = self.rowCount(QModelIndex())

        begin_row = 0
        if row != -1:
            begin_row = row
        elif parent.isValid():
            begin_row = parent.row()
        else:
            begin_row = num_rows

        if begin_row == num_rows:
            self.insertRows(begin_row, 1, QModelIndex())

        if column < 0:
            if parent.isValid():
                column = parent.column()
            else:
                column = 0

        encoded_data = data.data('application/vnd.tableviewdragdrop.list')
        stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        new_items = []
        rows = 0
        while not stream.atEnd():
            text = QByteArray()
            stream >> text
            new_items.append(str(text))
            rows += 1

        for text in new_items:
            idx = self.index(begin_row, column, QModelIndex())
            self.setData(idx, text, Qt.EditRole)
            begin_row += 1

        return True
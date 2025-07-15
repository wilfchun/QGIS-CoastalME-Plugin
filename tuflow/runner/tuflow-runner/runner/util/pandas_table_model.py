from pyqt_compat.QtCore import QAbstractTableModel, Qt

from pyqt_compat import QT_ITEM_DATA_DISPLAY_ROLE, QT_HORIZONTAL


class PandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QT_ITEM_DATA_DISPLAY_ROLE):
        if index.isValid():
            if role == QT_ITEM_DATA_DISPLAY_ROLE:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QT_HORIZONTAL and role == QT_ITEM_DATA_DISPLAY_ROLE:
            return self._data.columns[col]
        return None

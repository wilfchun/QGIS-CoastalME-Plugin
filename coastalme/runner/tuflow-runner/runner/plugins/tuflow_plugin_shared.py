from pyqt_compat.QtCore import Qt
from pyqt_compat.QtCore import QSettings, pyqtSlot, QAbstractTableModel, QModelIndex, QPoint, QSize
from . import plugin_base, coastalme_plugin_item
from pyqt_compat.QtWidgets import QFormLayout, QLineEdit, QStyle, QFileDialog, QSpinBox, QTableWidget
from pyqt_compat.QtWidgets import QHeaderView, QCheckBox, QTableView, QHeaderView, QStyledItemDelegate

from pyqt_compat import QT_HEADER_VIEW_STRETCH, QT_STYLE_SP_DIR_OPEN_ICON, QT_LINE_EDIT_TRAILING_POSITION
from pyqt_compat.QtGui import QPixmap

import bit_functions

class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setValue(value if value else 0)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def sizeHint(self, option, index):
        return QSize(100, 30)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class ConfigurationTableModel(QAbstractTableModel):
    def __init__(self, configs):
        super().__init__()
        self.configs = configs
        self.max_num_gpus = 24

    def rowCount(self, parent=QModelIndex()):
        return len(self.configs)

    def columnCount(self, parent=QModelIndex()):
        return self.max_num_gpus + 1

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section < self.max_num_gpus:
                return f"GPU {section + 1}"
            elif section == self.max_num_gpus:
                return "Number CPU threads"
            else:
                return "ERR"
        else:
            return str(section + 1)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.column() < self.max_num_gpus:
            if role == Qt.ItemDataRole.CheckStateRole:
                if bit_functions.test_bit(self.configs[index.row()][0], index.column()):
                    #print("returning checked")
                    return Qt.CheckState.Checked
                else:
                    #print("returning unchecked")
                    return Qt.CheckState.Unchecked
        elif index.column() == self.max_num_gpus:
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self.configs[index.row()][1]
        else:
            return None
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        config_row = self.configs[index.row()]
        if index.column() < self.max_num_gpus:
            if role == Qt.ItemDataRole.CheckStateRole:
                first_value = config_row[0]
                first_value = bit_functions.toggle_bit(first_value, index.column())
                self.configs[index.row()] = (first_value, config_row[1])
                return True
        else:
            if role == Qt.ItemDataRole.EditRole:
                self.configs[index.row()] = (config_row[0], value)
                return True
        return False

    def flags(self, index):
        if index.column() < self.max_num_gpus:
            return (Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable |
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        else:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable

    def set_number_configurations(self, num_new_configs):
        if len(self.configs) == num_new_configs:
            return
        self.beginResetModel()
        if len(self.configs) < num_new_configs:
            while len(self.configs) < num_new_configs:
                self.configs.append((0, 4))
        else:
            self.configs = self.configs[:num_new_configs]
        self.endResetModel()
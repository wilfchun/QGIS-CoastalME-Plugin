from pathlib import Path
import re

from pyqt_compat.QtCore import Qt
from pyqt_compat.QtCore import QSettings, pyqtSlot, QAbstractTableModel, QModelIndex, QPoint, QSize
from . import plugin_base, coastalme_plugin_item, coastalme_plugin_shared
from pyqt_compat.QtWidgets import QFormLayout, QLineEdit, QStyle, QFileDialog, QSpinBox, QTableWidget
from pyqt_compat.QtWidgets import QHeaderView, QCheckBox, QTableView, QHeaderView, QStyledItemDelegate

from pyqt_compat import QT_HEADER_VIEW_STRETCH, QT_STYLE_SP_DIR_OPEN_ICON, QT_LINE_EDIT_TRAILING_POSITION
from pyqt_compat.QtGui import QPixmap

import bit_functions

class CmeflowSettingsTab(plugin_base.PluginSettingsTab):
    def __init__(self, plugin):
        super().__init__()

        self.exe = plugin.get_executable()
        self.configs = plugin.configs
        self.max_num_gpus = 24 # don't let them go over this amount for now

        pg_layout = QFormLayout()

        pixmapi = QT_STYLE_SP_DIR_OPEN_ICON
        icon = self.style().standardIcon(pixmapi)
        self.edt_coastalme_exe = QLineEdit()
        open_action = self.edt_coastalme_exe.addAction(icon, QT_LINE_EDIT_TRAILING_POSITION)
        open_action.triggered.connect(self.on_browse)

        self.edt_coastalme_exe.setText(self.exe)

        pg_layout.addRow(
            "COASTALME Executable",
            self.edt_coastalme_exe
        )

        self.tog_write_hw = QCheckBox()

        pg_layout.addRow(
            "Write hardware flags (2023-03-AB and later)",
            self.tog_write_hw,
        )

        # configurations
        self.spn_numConfigurations = QSpinBox()
        self.spn_numConfigurations.setMinimum(1)
        self.num_configs = max(len(self.configs), 1)
        self.spn_numConfigurations.setValue(self.num_configs)
        pg_layout.addRow("Number of Configurations", self.spn_numConfigurations)

        self.config_model = coastalme_plugin_shared.ConfigurationTableModel(self.configs)

        self.tblConfigurations = QTableView()
        self.tblConfigurations.setModel(self.config_model)
        self.tblConfigurations.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tblConfigurations.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tblConfigurations.horizontalHeader().setStretchLastSection(True)

        self.delegate = coastalme_plugin_shared.SpinBoxDelegate(parent=self)
        self.tblConfigurations.setItemDelegateForColumn(self.max_num_gpus+1, self.delegate)

        #index = self.tblConfigurations.indexAt(QPoint(0, self.max_num_gpus + 1))
        #self.tblConfigurations.openPersistentEditor(index)

        self.spn_numConfigurations.valueChanged.connect(self.on_num_config_changed)

        pg_layout.addRow(self.tblConfigurations)

        self.setLayout(pg_layout)

        self.tog_write_hw.setChecked(plugin.write_hw)

        self.on_num_config_changed(self.num_configs)

    @pyqtSlot(int)
    def on_num_config_changed(self, new_num_config):
        self.config_model.set_number_configurations(new_num_config)
        for row in range(new_num_config):
            index = self.config_model.index(row, self.max_num_gpus)
            self.tblConfigurations.openPersistentEditor(index)
            index = self.config_model.index(row, self.max_num_gpus+1)
            self.tblConfigurations.openPersistentEditor(index)

    def num_gpus_changed(self, n_gpus):
        for col in range(0, n_gpus):
            self.tblConfigurations.setColumnHidden(col, False)
        for col in range(n_gpus, self.max_num_gpus):
            self.tblConfigurations.setColumnHidden(col, True)

    @pyqtSlot()
    def on_browse(self):
        exe_filename, qcmeilter = QFileDialog.getOpenFileName(self,
                                                             "Select COASTALME exe",
                                                             "",
                                                             "Executables (*.exe)")
        if exe_filename:
            self.edt_coastalme_exe.setText(exe_filename)

    def store_settings(self, settings):
        settings.beginGroup('COASTALME')
        settings.setValue("coastalme_exe", self.edt_coastalme_exe.text())
        hw_int = 1 if self.tog_write_hw.isChecked() else 0
        settings.setValue("write_hw", hw_int)

        # print(f'Num configs: {self.num_configs}')
        settings.beginWriteArray("Configurations2")
        for row in range(len(self.config_model.configs)):
            settings.setArrayIndex(row)
            settings.setValue("GPU_bits", self.config_model.configs[row][0])
            settings.setValue("CPUs", self.config_model.configs[row][1])
        settings.endArray()

        settings.endGroup()


class CmeflowPlugin(plugin_base.PluginBase):
    def __init__(self):
        super(CmeflowPlugin, self).__init__()
        self.write_hw = True
        # configurations are (GPUs, CPUs, CPUs counted)
        self.configs = [(1, 1, 0)]
        self.load_from_settings()
        self.tab_settings = None
        self.configs_running = set()

    def get_executable(self):
        settings = QSettings()
        if 'COASTALME' in settings.childGroups():
            settings.beginGroup('COASTALME')
            return settings.value("coastalme_exe")
        return ""

    def load_from_settings(self):
        settings = QSettings()
        total_gpus = settings.value("Resources/GPU Count")

        if 'COASTALME' in settings.childGroups():
            settings.beginGroup('COASTALME')

            self.write_hw = settings.value("write_hw", 0) == 1

            self.configs = []

            last_gpu = -1

            nrows = settings.beginReadArray("Configurations2")
            if nrows:
                for i in range(nrows):
                    settings.setArrayIndex(i)
                    gpu_bits = settings.value("GPU_bits")
                    ncpus = settings.value("CPUs")

                    self.configs.append((gpu_bits, ncpus))
                settings.endArray()
            else:
                # Try to read previous version of settings
                nrows = settings.beginReadArray("Configurations")
                for i in range(nrows):
                    settings.setArrayIndex(i)
                    ngpus = settings.value("GPUs")
                    ncpus = settings.value("CPUs")

                    gpu_bits = 0
                    for igpu in range(ngpus):
                        gpu = last_gpu + 1
                        if gpu >= total_gpus:
                            gpu = 0
                        print(f"row: {i}, turn on GPU {gpu}")
                        gpu_bits = bit_functions.set_bit(gpu_bits, gpu)
                        last_gpu = gpu

                    self.configs.append((gpu_bits, ncpus))
                settings.endArray()

            settings.endGroup()

    @classmethod
    def get_name(cls):
        return "COASTALME"

    @classmethod
    def get_simulation_extension(cls):
        return "*.tcf"

    def get_settings_tabctrl(self):
        self.tab_settings = CmeflowSettingsTab(self)
        return self.tab_settings

    def get_plugin_items(self, simulation_filename):
        # make sure we have a valid executable selected
        exe_path = Path(self.get_executable())

        if not exe_path.exists() or not exe_path.is_file():
            raise ValueError(
                "COASTALME executable not specified or does not exist. Please set the executable in the settings dialog accessed from the menu.")
        return coastalme_plugin_item.dlg_new_plugin_items(self, simulation_filename)

    def start_running_config(self, config_index):
        self.configs_running.add(config_index)

    def finished_running_config(self, config_index):
        # print(f'Finished config: {config_index}')
        self.configs_running.remove(config_index)
        # print(self.configs_running)

    def available_configs(self):
        configs_avail = []
        for i in range(len(self.configs)):
            if i not in self.configs_running:
                configs_avail.append((i, self.configs[i]))

        return configs_avail

    def create_plugin_item(self, sim_filename, plugin_options):
        scenarios_events = plugin_options['scenarios_events']
        sim_items = re.findall(r"(~s\d~)", str(sim_filename))
        n_sims = len(sim_items)
        return coastalme_plugin_item.CmeflowPluginItem(self,
                                                   sim_filename,
                                                   scenarios_events,
                                                   n_sims)

from pathlib import Path
from pyqt_compat import QtCore
from pyqt_compat.QtCore import QSettings, pyqtSlot
from pyqt_compat.QtWidgets import QFormLayout, QLineEdit, QStyle, QFileDialog, QSpinBox, QTableWidget
from pyqt_compat.QtWidgets import QHeaderView, QTableView

from pyqt_compat import QT_HEADER_VIEW_STRETCH, QT_STYLE_SP_DIR_OPEN_ICON, QT_LINE_EDIT_TRAILING_POSITION

from . import plugin_base, coastalmefv_plugin_item, coastalme_plugin_shared

import bit_functions

class CmeflowFvSettingsTab(plugin_base.PluginSettingsTab):
    def __init__(self, plugin):
        super().__init__()

        self.configs = plugin.configs
        self.max_num_gpus = 24

        pg_layout = QFormLayout()

        pixmapi = QT_STYLE_SP_DIR_OPEN_ICON
        icon = self.style().standardIcon(pixmapi)
        self.edt_coastalme_exe = QLineEdit()
        open_action = self.edt_coastalme_exe.addAction(icon, QT_LINE_EDIT_TRAILING_POSITION)
        open_action.triggered.connect(self.on_browse)

        self.edt_coastalme_exe.setText(plugin.get_executable())

        pg_layout.addRow(
            "COASTALME FV Executable",
            self.edt_coastalme_exe
        )

        # configurations
        self.spn_numConfigurations = QSpinBox()
        self.spn_numConfigurations.setMinimum(1)
        self.num_configs = len(self.configs)
        self.spn_numConfigurations.setValue(self.num_configs)
        pg_layout.addRow("Number of Configurations", self.spn_numConfigurations)

        # self.tblConfigurations = QTableWidget()
        # self.tblConfigurations.setColumnCount(3)
        # self.tblConfigurations.setHorizontalHeaderLabels(["Number GPU",
        #                                                   "Number CPU threads",
        #                                                   "CPU threads reserved"])
        #
        # self.tblConfigurations.setRowCount(self.num_configs)
        # pg_layout.addRow(self.tblConfigurations)
        #
        # self.tblConfigurations.horizontalHeader().setSectionResizeMode(QT_HEADER_VIEW_STRETCH)
        # self.tblConfigurations.horizontalHeader().resizeSections()

        self.config_model = coastalme_plugin_shared.ConfigurationTableModel(self.configs)

        self.tblConfigurations = QTableView()
        self.tblConfigurations.setModel(self.config_model)
        self.tblConfigurations.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tblConfigurations.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tblConfigurations.horizontalHeader().setStretchLastSection(True)

        self.delegate = coastalme_plugin_shared.SpinBoxDelegate(parent=self)
        self.tblConfigurations.setItemDelegateForColumn(self.max_num_gpus+1, self.delegate)

        pg_layout.addRow(self.tblConfigurations)

        self.spn_numConfigurations.valueChanged.connect(self.on_num_config_changed)

        self.setLayout(pg_layout)

        self.on_num_config_changed(self.num_configs)


    @pyqtSlot(int)
    def on_num_config_changed(self, new_num_config):
        self.config_model.set_number_configurations(new_num_config)
        for row in range(new_num_config):
            index = self.config_model.index(row, self.max_num_gpus)
            self.tblConfigurations.openPersistentEditor(index)
            index = self.config_model.index(row, self.max_num_gpus + 1)
            self.tblConfigurations.openPersistentEditor(index)
        # # if we have added configurations add to table
        # self.tblConfigurations.setRowCount(new_num_config)
        # if new_num_config > self.num_configs:
        #     self.configs += [(1, 1, 0)]*(new_num_config-self.num_configs)
        #     self.initialize_rows(self.num_configs, new_num_config)
        # self.num_configs = new_num_config

    def num_gpus_changed(self, n_gpus):
        for col in range(0, n_gpus):
            self.tblConfigurations.setColumnHidden(col, False)
        for col in range(n_gpus, self.max_num_gpus):
            self.tblConfigurations.setColumnHidden(col, True)

    @pyqtSlot()
    def on_browse(self):
        exe_filename, filter = QFileDialog.getOpenFileName(self,
                                                           "Select COASTALME FV exe",
                                                           "",
                                                           "Executables (*.exe)")
        if exe_filename:
            self.edt_coastalme_exe.setText(exe_filename)

    def store_settings(self, settings):
        settings.beginGroup('COASTALME FV')
        settings.setValue("coastalmefv_exe", self.edt_coastalme_exe.text())

        self.num_configs = self.spn_numConfigurations.value()
        # print(f'Num configs: {self.num_configs}')
        settings.beginWriteArray("Configurations2")
        for row in range(len(self.config_model.configs)):
            settings.setArrayIndex(row)
            settings.setValue("GPU_bits", self.config_model.configs[row][0])
            settings.setValue("CPUs", self.config_model.configs[row][1])
        settings.endArray()

        settings.endGroup()


class CmeflowFvPlugin(plugin_base.PluginBase):
    def __init__(self):
        super(CmeflowFvPlugin, self).__init__()
        # configurations are (GPUs, CPUs, CPUs counted)
        self.configs = [(1, 1)]
        self.load_from_settings()
        self.tab_settings = None
        self.configs_running = set()

    def load_from_settings(self):
        settings = QSettings()

        if 'COASTALME FV' in settings.childGroups():
            settings.beginGroup('COASTALME FV')
            settings.value("coastalmefv_exe")

            total_gpus = settings.value("Resources/GPU Count")

            self.configs = []
            last_gpu = -1

            if "Configurations2" in settings.childGroups():
                nrows = settings.beginReadArray("Configurations2")
                for i in range(nrows):
                    settings.setArrayIndex(i)
                    gpu_bits = settings.value("GPU_bits")
                    ncpus = settings.value("CPUs")

                    self.configs.append((gpu_bits, ncpus))
                settings.endArray()
            else:
                nrows = settings.beginReadArray("Configurations")
                for i in range(nrows):
                    settings.setArrayIndex(i)
                    ngpus = settings.value("GPUs")
                    ncpus = settings.value("CPUs")

                    gpu_bits = 0
                    for igpu in range(ngpus):
                        gpu = last_gpu + 1
                        if total_gpus is not None and gpu >= total_gpus:
                            gpu = 0
                        print(f"row: {i}, turn on GPU {gpu}")
                        gpu_bits = bit_functions.set_bit(gpu_bits, gpu)
                        last_gpu = gpu

                    self.configs.append((gpu_bits, ncpus))
                settings.endArray()

            settings.endGroup()

    @classmethod
    def get_name(self):
        return "COASTALME FV"

    @classmethod
    def get_simulation_extension(cls):
        return "*.fvc"

    def get_settings_tabctrl(self):
        self.tab_settings = CmeflowFvSettingsTab(self)
        return self.tab_settings

    def get_plugin_items(self, simulation_filename):
        # make sure we have a valid executable selected
        exe_path = Path(self.get_executable())

        if not exe_path.exists() or not exe_path.is_file():
            raise ValueError(
                "COASTALME executable not specified or does not exist. Please set the executable in the settings dialog accessed from the menu.")
        return [coastalmefv_plugin_item.CmeflowFvPluginItem(self, simulation_filename)]

    def get_executable(self):
        # print('Getting COASTALME FV executable from settings')
        settings = QSettings()

        if 'COASTALME FV' in settings.childGroups():
            settings.beginGroup('COASTALME FV')
            return settings.value("coastalmefv_exe")

        # print('COASTALME FV executable not found')
        return None

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

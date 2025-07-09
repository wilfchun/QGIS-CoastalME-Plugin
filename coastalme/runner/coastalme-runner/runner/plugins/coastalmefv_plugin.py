from pathlib import Path
from pyqt_compat import QtCore
from pyqt_compat.QtCore import QSettings, pyqtSlot
from pyqt_compat.QtWidgets import QFormLayout, QLineEdit, QStyle, QFileDialog, QSpinBox, QTableWidget
from pyqt_compat.QtWidgets import QHeaderView

from pyqt_compat import QT_HEADER_VIEW_STRETCH, QT_STYLE_SP_DIR_OPEN_ICON, QT_LINE_EDIT_TRAILING_POSITION

from . import plugin_base, coastalmefv_plugin_item


class TuflowFvSettingsTab(plugin_base.PluginSettingsTab):
    def __init__(self, plugin):
        super().__init__()

        self.configs = plugin.configs

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

        self.tblConfigurations = QTableWidget()
        self.tblConfigurations.setColumnCount(3)
        self.tblConfigurations.setHorizontalHeaderLabels(["Number GPU",
                                                          "Number CPU threads",
                                                          "CPU threads reserved"])

        self.tblConfigurations.setRowCount(self.num_configs)
        pg_layout.addRow(self.tblConfigurations)

        self.tblConfigurations.horizontalHeader().setSectionResizeMode(QT_HEADER_VIEW_STRETCH)
        self.tblConfigurations.horizontalHeader().resizeSections()

        self.initialize_rows(0, self.num_configs)

        self.spn_numConfigurations.valueChanged.connect(self.on_num_config_changed)

        self.setLayout(pg_layout)


    @pyqtSlot(int)
    def on_num_config_changed(self, new_num_config):
        # if we have added configurations add to table
        self.tblConfigurations.setRowCount(new_num_config)
        if new_num_config > self.num_configs:
            self.configs += [(1, 1, 0)]*(new_num_config-self.num_configs)
            self.initialize_rows(self.num_configs, new_num_config)
        self.num_configs = new_num_config

    def initialize_rows(self, start, end):
        # print('Initialize')
        # print(self.configs)
        for row in range(start, end):
            spinbox_gpu = QSpinBox()
            spinbox_gpu.setValue(self.configs[row][0])
            self.tblConfigurations.setCellWidget(row, 0, spinbox_gpu)
            spinbox_cpu = QSpinBox()
            spinbox_cpu.setValue(self.configs[row][1])
            self.tblConfigurations.setCellWidget(row, 1, spinbox_cpu)
            spinbox_cpu_use = QSpinBox()
            spinbox_cpu_use.setValue(self.configs[row][2])
            self.tblConfigurations.setCellWidget(row, 2, spinbox_cpu_use)

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
        settings.beginWriteArray("Configurations")
        for row in range(self.num_configs):
            settings.setArrayIndex(row)
            settings.setValue("GPUs", self.tblConfigurations.cellWidget(row, 0).value())
            settings.setValue("CPUs", self.tblConfigurations.cellWidget(row, 1).value())
            settings.setValue("CPU_resources", self.tblConfigurations.cellWidget(row, 2).value())
        settings.endArray()

        settings.endGroup()


class TuflowFvPlugin(plugin_base.PluginBase):
    def __init__(self):
        super(TuflowFvPlugin, self).__init__()
        # configurations are (GPUs, CPUs, CPUs counted)
        self.configs = [(1, 1, 0)]
        self.load_from_settings()
        self.tab_settings = None
        self.configs_running = set()

    def load_from_settings(self):
        settings = QSettings()

        if 'COASTALME FV' in settings.childGroups():
            settings.beginGroup('COASTALME FV')
            settings.value("coastalmefv_exe")

            self.configs = []
            nrows = settings.beginReadArray("Configurations")
            for i in range(nrows):
                settings.setArrayIndex(i)
                ngpus = settings.value("GPUs")
                ncpus = settings.value("CPUs")
                cpu_counts = settings.value("CPU_resources")
                self.configs.append((ngpus, ncpus, cpu_counts))
            settings.endArray()

            settings.endGroup()

    @classmethod
    def get_name(self):
        return "COASTALME FV"

    @classmethod
    def get_simulation_extension(cls):
        return "*.fvc"

    def get_settings_tabctrl(self):
        self.tab_settings = TuflowFvSettingsTab(self)
        return self.tab_settings

    def get_plugin_items(self, simulation_filename):
        # make sure we have a valid executable selected
        exe_path = Path(self.get_executable())

        if not exe_path.exists() or not exe_path.is_file():
            raise ValueError(
                "COASTALME executable not specified or does not exist. Please set the executable in the settings dialog accessed from the menu.")
        return [coastalmefv_plugin_item.TuflowFvPluginItem(self, simulation_filename)]

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

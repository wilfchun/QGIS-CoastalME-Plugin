from pyqt_compat.QtCore import QSettings
from pyqt_compat.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QVBoxLayout, QGroupBox, QFormLayout, QLabel
from pyqt_compat.QtWidgets import QSpinBox, QWidget, QTabWidget

from pyqt_compat import QT_BUTTON_BOX_CANCEL, QT_BUTTON_BOX_OK


def initializeSettings(plugin_list):
    settings = QSettings()

    settings.beginGroup("Resources")
    if not settings.contains("CPU Count"):
        settings.setValue("CPU Count", 4)
    if not settings.contains("GPU Count"):
        settings.setValue("GPU Count", 1)
    settings.endGroup()

    settings.sync()


def run_settings_dialog(plugin_list):
    dlg = SettingsDialog(plugin_list)
    if dlg.exec():
        dlg.store_settings()

        for plugin in plugin_list:
            plugin.load_from_settings()


class SettingsDialog(QDialog):
    def __init__(self, plugin_list):
        super().__init__()

        self.setMinimumWidth(500)

        self.setWindowTitle("Settings")
        self.plugins = plugin_list

        settings = QSettings()

        QBtn = QT_BUTTON_BOX_OK | QT_BUTTON_BOX_CANCEL

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # self.layout = QVBoxLayout()
        # message = QLabel("Something happened, is that OK?")
        # self.layout.addWidget(message)
        # self.layout.addWidget(self.buttonBox)
        # self.setLayout(self.layout)
        layout = QVBoxLayout()

        resources_group_box = QGroupBox("Resources")

        resources_layout = QFormLayout()
        self.cpu_spin_box = QSpinBox()
        self.cpu_spin_box.setMinimum(1)
        self.cpu_spin_box.setMaximum(144)
        self.cpu_spin_box.setValue(settings.value("Resources/CPU Count"))
        resources_layout.addRow(QLabel("CPU Count (threads)"), self.cpu_spin_box)

        self.gpu_spin_box = QSpinBox()
        self.gpu_spin_box.setMinimum(1)
        self.gpu_spin_box.setMaximum(100)
        self.gpu_spin_box.setValue(settings.value("Resources/GPU Count"))
        resources_layout.addRow(QLabel("GPU Count"), self.gpu_spin_box)

        resources_group_box.setLayout(resources_layout)

        layout.addWidget(resources_group_box)

        self.plugin_tabs = []

        plugin_tab_widget = QTabWidget()
        for plugin in plugin_list:
            tab = plugin.get_settings_tabctrl()
            plugin_tab_widget.addTab(tab,
                                     plugin.get_name())
            self.plugin_tabs.append(tab)

        layout.addWidget(plugin_tab_widget)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def store_settings(self):
        settings = QSettings()

        settings.beginGroup("Resources")
        settings.setValue("CPU Count", self.cpu_spin_box.value())
        settings.setValue("GPU Count", self.gpu_spin_box.value())
        settings.endGroup()

        for plugin_tab in self.plugin_tabs:
            plugin_tab.store_settings(settings)

        settings.sync()

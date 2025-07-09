from abc import ABC, abstractmethod
from pyqt_compat.QtCore import QObject, pyqtSignal
from pyqt_compat.QtWidgets import QWidget


class PluginSettingsTab(QWidget):
    def __init__(self):
        super().__init__()

    def store_settings(self, settings):
        return None  # overload


class PluginItemBase(QObject):
    def __init__(self, plugin):
        super(PluginItemBase, self).__init__()
        self.plugin = plugin

    @abstractmethod
    def clone_info(self):
        return None

    @abstractmethod
    def get_sim_description(self):
        return None

    @abstractmethod
    def get_executable(self):
        return None

    @abstractmethod
    def get_command_switches(self):
        return None

    # returns updated percent complete or None if not updated
    @abstractmethod
    def process_screen_line(self, line_text):
        return None

    @abstractmethod
    def finished_reading_lines(self):
        return None

    @abstractmethod
    def run_finished_successfully(self):
        return False

    @abstractmethod
    def create_additional_tabs(self, tab_widget):
        return None

    @abstractmethod
    def plugin_save_information(self):
        return None

    @abstractmethod
    def create_plugin_item(self, sim_filename, plugin_options):
        return None

    def set_omp_threads(self):
        return False

class PluginBase(ABC):

    @classmethod
    @abstractmethod
    def get_name(self):
        return None

    @classmethod
    @abstractmethod
    def get_simulation_extension(cls):
        return None

    @abstractmethod
    def get_settings_tabctrl(self):
        return None

    @abstractmethod
    def get_plugin_items(self, simulation_filename):
        return None

    @abstractmethod
    def load_from_settings(self):
        return None

import itertools
import json
import pandas as pd
import re

from pyqt_compat.QtGui import QIcon
from pyqt_compat.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QListWidget, QWidget, \
    QLineEdit, QPushButton, QLabel, QListWidgetItem, QListView, QTableView, QSplitter, \
    QVBoxLayout, QToolBar
from pyqt_compat import QtCore
from pyqt_compat.QtCore import Qt, QSettings, QSize, pyqtSlot, pyqtSignal

from pyqt_compat import (is_qt6, QT_CHECKED, QT_BUTTON_BOX_CANCEL, QT_ITEM_FLAG_ITEM_IS_EDITABLE, QT_WINDOW_TYPE,
                         QT_BUTTON_BOX_OK, QT_WINDOW_CONTEXT_HELP_BUTTON_HINT)

if is_qt6:
    from pyqt_compat.QtGui import QAction
else:
    from pyqt_compat.QtWidgets import QAction

from . import plugin_base
from util import pandas_table_model
from . import coastalme_plots

import sys

# setting path
sys.path.append('..')

from file_paths import get_runner_absolute_path


class TuflowPluginItem(plugin_base.PluginItemBase):

    def __init__(self, plugin, sim_filename, sims_events, n_sims):
        super().__init__(plugin)
        self.volume_plot_window = None
        self.sim_filename = sim_filename
        self.scenarios_events = sims_events
        self.n_sims = n_sims
        self.succeeded = False
        self.start_time = None
        self.end_time = None
        self.config_num = None
        self.gpus_to_use = set()  # Set of GPUs to use gets set when gets commandline arguments
        self.cpus_to_use = 0
        self.cpus_counted = 0

        # Run stats
        self.update_plot_window = False
        self.re_rsVolInOut = re.compile("Vi(.*)Vo(.*)dV", re.IGNORECASE)
        self.re_removeNonNumbers = re.compile("[^0123456789\.]")
        self.rs_times = []
        self.rs_volIn = []
        self.rs_volOut = []

    def clone_info(self):
        new_item = TuflowPluginItem(
            self.plugin,
            self.sim_filename,
            self.scenarios_events,
            self.n_sims
        )
        return new_item

    def get_executable(self):
        return self.plugin.get_executable()

    def get_sim_description(self):
        return f'S: {", ".join(self.scenarios_events[:self.n_sims])}\n' + \
            f'E: {", ".join(self.scenarios_events[self.n_sims:])}'

    def resources(self):
        return self.gpus_to_use, self.cpus_counted

    def able_to_run(self, gpus_avail, cpus_avail):
        # See if there is an available configuration available
        avail_configs = self.plugin.available_configs()
        # print(avail_configs)
        ngpus_avail = len(gpus_avail)
        for config_index, (gpus, cpus, cpus_counted) in avail_configs:
            # print(gpus)
            # print(cpus_counted)
            if gpus <= ngpus_avail and cpus_counted <= cpus_avail:
                return True
        return False

    def get_commandline_arguments(self, gpus_avail, cpus_avail):
        args = ['-b', '-nmb', '-nq']

        self.config_num = None

        # GPUs available will be a set of numbers identifying which GPUs are free
        ngpus_avail = len(gpus_avail)

        avail_configs = self.plugin.available_configs()
        for config_index, (gpus, cpus, cpus_counted) in avail_configs:
            if gpus <= ngpus_avail and cpus_counted <= cpus_avail:
                self.config_num = config_index
                gpus_avail_list = sorted(list(gpus_avail))
                self.gpus_to_use = set(gpus_avail_list[:gpus])
                self.cpus_to_use = cpus
                self.cpus_counted = cpus_counted
                break

        if self.config_num is None:
            raise ValueError('get_commandline_arguments config not found')

        self.plugin.start_running_config(self.config_num)

        if self.gpus_to_use:
            if self.plugin.write_hw:
                args.append(f'-hwgpu')
            for gpu in self.gpus_to_use:
                args.append(f'-pu{gpu}')
        else:
            if self.plugin.write_hw:
                args.append(f'-hwcpu')
            args.append(f'-nt{self.cpus_to_use}')

        for i, scenario in enumerate(self.scenarios_events[:self.n_sims]):
            args.append(f'-s{i + 1}')
            args.append(scenario)
        for i, event in enumerate(self.scenarios_events[self.n_sims:]):
            args.append(f'-e{i + 1}')
            args.append(event)

        args.append(str(self.sim_filename))
        # print(args)

        return args

    # returns updated percent complete or None if not updated
    def process_screen_line(self, line_text):
        if self.start_time is None and \
                line_text.find("Start Time (h)") != -1:
            try:
                only_numbers = self.re_removeNonNumbers.sub('', line_text).strip('.')
                self.start_time = float(only_numbers)
                print(f'Start time: {self.start_time}')
                # self.start_time = float(line_text.split(' ')[-1])
            except:
                return None
        elif self.end_time is None and \
                line_text.find('Finish Time (h)') != -1:
            try:
                only_numbers = self.re_removeNonNumbers.sub('', line_text).strip('.')
                self.end_time = float(only_numbers)
                print(f'End time: {self.end_time}')
                # self.start_time = float(line_text.split(' ')[-1])
            except:
                return None
            # print(line_text)
            # self.end_time = float(line_text.split(' ')[-1])

        elif line_text.find('SIM:') != -1:
            line_after_sim = line_text[line_text.find('SIM:') + 4:]
            time_portion = line_after_sim.split()[0]
            hours, minutes, seconds = time_portion.split(':')
            current_time = float(hours) + float(minutes) / 60. + float(seconds) / 3600.
            # print(f'Current time: {current_time}')
            # print(f'Start time: {self.start_time}')
            # print(f'End time: {self.end_time}')
            percent_complete = 100 * ((current_time - self.start_time) / (self.end_time - self.start_time))
            # don't want it to go to 100 percent until the simulation finishes
            percent_complete = min(percent_complete, 99)
            # print(f'Percent complete: {percent_complete}')

            vol_in_out_text = self.re_rsVolInOut.search(line_text)
            if vol_in_out_text:
                vol_in_text = vol_in_out_text.groups()[0].strip()
                vol_out_text = vol_in_out_text.groups()[1].strip()

                vol_in = self.intrepret_volume(vol_in_text)
                vol_out = self.intrepret_volume(vol_out_text)

                self.rs_times.append(current_time)
                self.rs_volIn.append(vol_in)
                self.rs_volOut.append(vol_out)

                self.update_plot_window = True

            return percent_complete

        elif line_text.find("Simulation FINISHED") != -1:
            # print('Found end of simulation')
            self.succeeded = True
        elif line_text.find("Empty 1D and 2D GIS files written.") != -1:
            self.succeeded = True

        return None

    def finished_reading_lines(self):
        if self.update_plot_window:
            self.volume_plot_window.update(self.rs_times,
                                           self.rs_volIn,
                                           self.rs_volOut)
            self.update_plot_window = False

    def intrepret_volume(self, volume_text):
        vol_multiplier = 1.0
        if volume_text.find("'") != -1:
            vol_multiplier = 1000.0
        elif volume_text.find('"') != -1:
            vol_multiplier = 1000000.0
        vol = float(volume_text.strip('\'"')) * vol_multiplier
        return vol

    def sim_finished(self):
        self.plugin.finished_running_config(self.config_num)
        self.config_num = None

    def run_finished_successfully(self):
        # print(f'run succeeded: {self.succeeded}')
        return self.succeeded

    def create_additional_tabs(self, tab_widget):
        self.volume_plot_window = coastalme_plots.VolumePlot()
        tab_widget.addTab(self.volume_plot_window, 'Volumes')

    def plugin_save_information(self):
        return {'scenarios_events': self.scenarios_events}


class ScenarioOptions(QWidget):
    changed = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        layout = QGridLayout()

        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)

        # self.edt_add_name = QLineEdit()
        # self.btn_add = QPushButton()
        # self.btn_add.setText('Add')
        # self.btn_add.clicked.connect(self.on_btn_add)

        self.lst_options = QListWidget()

        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))

        self.plus_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\032.png')),
                                   'Minus Button', self)
        self.plus_action.setStatusTip('Remove scenario/event')
        self.plus_action.triggered.connect(self.on_click_plus)
        self.plus_action.setEnabled(True)
        self.toolbar.addAction(self.plus_action)

        self.minus_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\033.png')),
                                    'Minus Button', self)
        self.minus_action.setStatusTip('Remove scenario/event')
        self.minus_action.triggered.connect(self.on_click_minus)
        self.minus_action.setEnabled(False)
        self.toolbar.addAction(self.minus_action)

        self.up_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\037.png')),
                                 'Down Button', self)
        self.up_action.setStatusTip('Move Scenario/event up')
        self.up_action.triggered.connect(self.on_click_up)
        self.up_action.setEnabled(False)
        self.toolbar.addAction(self.up_action)

        self.down_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\038.png')),
                                   'Down Button', self)
        self.down_action.setStatusTip('Move Scenario/event up')
        self.down_action.triggered.connect(self.on_click_down)
        self.down_action.setEnabled(False)
        self.toolbar.addAction(self.down_action)

        layout.addWidget(QLabel(title), 1, 1, 1, -1)
        # layout.addWidget(self.edt_add_name, 2, 1)
        # layout.addWidget(self.btn_add, 2, 2)
        layout.addWidget(self.lst_options, 3, 1, 1, -1)
        layout.addWidget(self.toolbar, 4, 1, 1, -1)

        self.setLayout(layout)

        self.lst_options.itemChanged.connect(self.on_list_item_changed)
        self.lst_options.itemSelectionChanged.connect(self.on_list_sel_changed)

    def add_options_w_state(self, options):
        for text, checked in options:
            new_item = QListWidgetItem()
            new_item.setText(text)
            if checked:
                new_item.setCheckState(Qt.CheckState.Checked)
            else:
                new_item.setCheckState(Qt.CheckState.Unchecked)
            new_item.setFlags(new_item.flags() | QT_ITEM_FLAG_ITEM_IS_EDITABLE)
            self.lst_options.addItem(new_item)

    def get_options_w_state(self):
        options = []
        for index in range(self.lst_options.count()):
            options.append((self.lst_options.item(index).text(),
                            self.lst_options.item(index).checkState() == QT_CHECKED))
        return options

    def get_options(self):
        options = []
        for index in range(self.lst_options.count()):
            if self.lst_options.item(index).checkState() == QT_CHECKED:
                options.append(self.lst_options.item(index).text())
        return options

    # @pyqtSlot()
    # def on_btn_add(self):
    #    text = self.edt_add_name.text()
    #    if text != "":
    #        new_item = QListWidgetItem()
    #        new_item.setText(text)
    #        new_item.setCheckState(Qt.CheckState.Checked)
    #        new_item.setFlags(new_item.flags() | QT_ITEM_FLAG_ITEM_IS_EDITABLE)
    #        self.lst_options.addItem(new_item)
    #        self.on_changed()

    def on_changed(self):
        self.changed.emit()

    @pyqtSlot(QListWidgetItem)
    def on_list_item_changed(self, item):
        self.on_changed()

    @pyqtSlot()
    def on_list_sel_changed(self):
        self.minus_action.setEnabled(self.lst_options.currentRow() != -1)
        self.up_action.setEnabled(self.lst_options.currentRow() > 0)
        self.down_action.setEnabled(self.lst_options.currentRow() != -1 and
                                    self.lst_options.currentRow() < self.lst_options.count() - 1)

    @pyqtSlot()
    def on_click_plus(self):
        new_item = QListWidgetItem()
        new_item.setText('new')
        new_item.setCheckState(Qt.CheckState.Checked)
        new_item.setFlags(new_item.flags() | QT_ITEM_FLAG_ITEM_IS_EDITABLE)
        self.lst_options.addItem(new_item)
        self.lst_options.editItem(new_item)

    @pyqtSlot()
    def on_click_minus(self):
        if self.lst_options.currentRow() != -1:
            self.lst_options.takeItem(self.lst_options.currentRow())
            self.on_changed()

    @pyqtSlot()
    def on_click_up(self):
        current_row = self.lst_options.currentRow()
        if current_row != -1:
            item = self.lst_options.takeItem(current_row)
            self.lst_options.insertItem(current_row - 1, item)
            self.on_changed()
            self.lst_options.setCurrentRow(current_row)
            self.on_list_sel_changed()

    @pyqtSlot()
    def on_click_down(self):
        current_row = self.lst_options.currentRow()
        if current_row != -1:
            item = self.lst_options.takeItem(current_row)
            self.lst_options.insertItem(current_row + 1, item)
            self.on_changed()
            self.lst_options.setCurrentRow(current_row)
            self.on_list_sel_changed()


class DlgTuflowAddSimulations(QDialog):
    def __init__(self, plugin, sim_filename):
        super().__init__()

        self.plugin = plugin
        self.sim_filename = sim_filename

        sim_items = re.findall(r"(~s\d~)", str(sim_filename.stem))
        event_items = re.findall(r"(~e\d~)", str(sim_filename.stem))

        n_scenarios = len(sim_items)
        n_events = len(event_items)

        if n_scenarios == 0 and n_events == 0:
            raise ValueError('No scenarios or events')

        self.setMinimumWidth(500)

        self.setWindowTitle("Add Simulations")

        self.setWindowFlags(self.windowFlags() & ~QT_WINDOW_CONTEXT_HELP_BUTTON_HINT)

        # settings = QSettings()

        QBtn = QT_BUTTON_BOX_OK | QT_BUTTON_BOX_CANCEL

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        full_layout = QVBoxLayout()
        full_layout.setContentsMargins(5, 5, 5, 5)

        self.top_widgets = QWidget()
        top_layout = QGridLayout()
        top_layout.setContentsMargins(1, 1, 1, 1)
        top_layout.setHorizontalSpacing(1)
        top_layout.setVerticalSpacing(1)

        # Add the scenario controls in the first row
        # Hardcode to 3 for now
        scenario_widget_row = 1

        self.scenario_widgets = []
        for iscenario in range(n_scenarios):
            scenario_options = ScenarioOptions(f'Scenario #{iscenario + 1}')
            scenario_options.changed.connect(self.on_scenarios_changed)
            self.scenario_widgets.append(scenario_options)
            top_layout.addWidget(scenario_options, scenario_widget_row, iscenario + 1)

        # Add the event controls in the second row

        event_widget_row = 2
        self.event_widgets = []
        for ievent in range(n_events):
            event_options = ScenarioOptions(f'Event #{ievent + 1}')
            event_options.changed.connect(self.on_scenarios_changed)
            self.event_widgets.append(event_options)
            top_layout.addWidget(event_options, event_widget_row, ievent + 1)

        self.top_widgets.setLayout(top_layout)

        # Show a preview of the scenarios that will be added
        self.sim_preview = QTableView()
        self.sim_df = pd.DataFrame()
        self.sim_preview.setModel(pandas_table_model.PandasModel(self.sim_df))

        splitter = QSplitter()
        splitter.setContentsMargins(1, 1, 1, 1)
        splitter.addWidget(self.top_widgets)
        splitter.addWidget(self.sim_preview)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        full_layout.addWidget(splitter)

        QBtn = QT_BUTTON_BOX_OK | QT_BUTTON_BOX_CANCEL
        self.buttonBox = QDialogButtonBox(QBtn)
        full_layout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.on_ok)
        self.buttonBox.rejected.connect(self.reject)

        self.setLayout(full_layout)

        # If we have used this file before, start with the previous settings
        settings_obj = QSettings()

        if "COASTALME_file_options" in settings_obj.childGroups():
            settings_obj.beginGroup("COASTALME_file_options")
            child_groups_lower = [x.casefold() for x in settings_obj.childGroups()]
            if str(self.sim_filename).casefold() in child_groups_lower:
                index = child_groups_lower.index(str(self.sim_filename).casefold())
                name = settings_obj.childGroups()[index]
                settings_obj.beginGroup(name)

                scenario_state_string = settings_obj.value('Scenarios_and_state')
                scenarios_w_state = json.loads(scenario_state_string)
                for scenarios_w_state_single, scenario_widget in zip(scenarios_w_state,
                                                                     self.scenario_widgets):
                    scenario_widget.add_options_w_state(scenarios_w_state_single)

                if 'Events_and_state' in settings_obj.childKeys():
                    event_state_string = settings_obj.value('Events_and_state')
                    events_w_state = json.loads(event_state_string)
                    for events_w_state_single, event_widget in zip(events_w_state,
                                                                   self.event_widgets):
                        event_widget.add_options_w_state(events_w_state_single)

                settings_obj.endGroup()
                settings_obj.endGroup()
        self.on_scenarios_changed()

    @pyqtSlot()
    def on_scenarios_changed(self):
        scenario_events = []
        scenario_list = []
        for iscenario, scenario_widget in enumerate(self.scenario_widgets):
            scenario_list.append(f'Scenario #{iscenario + 1}')
            scenario_events.append(scenario_widget.get_options())

        event_list = []
        for ievent, event_widget in enumerate(self.event_widgets):
            event_list.append(f'Event #{ievent + 1}')
            scenario_events.append(event_widget.get_options())

        # print(scenario_events)
        combinations = [p for p in itertools.product(*scenario_events)]
        # print(combinations)

        df = pd.DataFrame(combinations,
                          columns=scenario_list + event_list)
        df['Number'] = df.index + 1
        # print(df.columns)
        # print(['Number'] + list(df.columns[:-1]))
        df = df[['Number'] + list(df.columns[:-1])]
        # print(df.columns)
        # print(df)
        self.sim_preview.setModel(pandas_table_model.PandasModel(df))

    def get_scenarios_events(self):
        scenarios = []
        for iscenario, scenario_widget in enumerate(self.scenario_widgets):
            scenarios.append(scenario_widget.get_options())
        events = []
        for ievent, event_widget in enumerate(self.event_widgets):
            events.append(event_widget.get_options())

        return scenarios, events

    def on_ok(self):
        settings_obj = QSettings()
        settings_obj.beginGroup("COASTALME_file_options")
        settings_obj.beginGroup(str(self.sim_filename).casefold())

        # Need to store scenario and event names and check state
        scenarios_w_state = []
        for scenario_widget in self.scenario_widgets:
            scenarios_w_state.append(scenario_widget.get_options_w_state())

        scenario_state_string = json.dumps(scenarios_w_state)
        # print(scenario_state_string)
        settings_obj.setValue('Scenarios_and_state', scenario_state_string)

        events_w_state = []
        for event_widget in self.event_widgets:
            events_w_state.append(event_widget.get_options_w_state())

        event_state_string = json.dumps(events_w_state)
        settings_obj.setValue('Events_and_state', event_state_string)

        settings_obj.endGroup()
        settings_obj.endGroup()

        self.accept()


def dlg_new_plugin_items(plugin, simulation_filename):
    """
    run the dialog to get settings for new plugin items
    :param simulation_filename:
    :return: a list of plugin items
    """
    coastalme_plugin_items = []
    try:
        dlg = DlgTuflowAddSimulations(plugin, simulation_filename)
        if dlg.exec():
            scenarios, events = dlg.get_scenarios_events()
            scenarios_events = scenarios + events

            combinations = [p for p in itertools.product(*scenarios_events)]

            for s_e in combinations:
                coastalme_plugin_item = TuflowPluginItem(plugin, simulation_filename, s_e, len(scenarios))
                coastalme_plugin_items.append(coastalme_plugin_item)
    except ValueError:
        # No scenarios or events
        coastalme_plugin_item = TuflowPluginItem(plugin, simulation_filename, [], 0)
        coastalme_plugin_items.append(coastalme_plugin_item)

    return coastalme_plugin_items

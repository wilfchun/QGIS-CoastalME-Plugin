from datetime import datetime
import itertools
import json
from abc import ABC
from dateutil import parser

import pandas as pd
import re

from pyqt_compat.QtGui import QIcon
from pyqt_compat.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QListWidget, QWidget, \
    QLineEdit, QPushButton, QLabel, QListWidgetItem, QListView, QTableView, QSplitter, \
    QVBoxLayout, QToolBar
from pyqt_compat import QtCore
from pyqt_compat.QtCore import Qt, QSettings, QSize


from . import plugin_base
from util import pandas_table_model
import bit_functions

class CmeflowFvPluginItem(plugin_base.PluginItemBase):

    def __init__(self, plugin, sim_filename):
        super().__init__(plugin)
        self.sim_filename = sim_filename
        self.succeeded = False
        self.start_time = None
        self.end_time = None
        self.config_num = None
        self.gpu_bits = 0
        self.gpus_to_use = set()  # Set of GPUs to use for simulation
        self.cpus_to_use = 0
        self.fv_uses_dates = False
        self.timeFormatRegex = re.compile(".*TIME FORMAT.*==(.*)", re.IGNORECASE)
        self.startTimeRegex = re.compile(".*START TIME.*==(.*)", re.IGNORECASE)
        self.endTimeRegex = re.compile(".*END TIME.*==(.*)", re.IGNORECASE)
        self.timestepDateTimeRegex = re.compile(".*t =(.*)dt =.*", re.IGNORECASE)
        self.timestepHrsRegex = re.compile(".*t = (.*) hrs.*", re.IGNORECASE)
        self.fatalErrorRegex = re.compile(".*(Fatal Error Encountered).*", re.IGNORECASE)

    def clone_info(self):
        new_item = CmeflowFvPluginItem(self.plugin, self.sim_filename)
        return new_item

    def get_executable(self):
        return self.plugin.get_executable()

    def get_sim_description(self):
        return f''

    def resources(self):
        return self.gpus_to_use, self.cpus_to_use

    def able_to_run(self, gpus_avail, n_gpus_total):
        # See if there is an available configuration available
        avail_configs = self.plugin.available_configs()
        return len(avail_configs) > 0

    def get_commandline_arguments(self, gpus_avail, n_gpus_total):
        args = []

        self.config_num = None

        avail_configs = self.plugin.available_configs()
        for config_index, (gpu_bits, cpus) in avail_configs:
            self.config_num = config_index
            self.gpu_bits = gpu_bits
            self.cpus_to_use = cpus
            break

        if self.config_num is None:
            raise ValueError('get_commandline_arguments config not found')

        self.plugin.start_running_config(self.config_num)

        self.gpus_to_use = set()
        for i_gpu in range(n_gpus_total):
            if bit_functions.test_bit(self.gpu_bits, i_gpu):
                self.gpus_to_use.add(i_gpu)

        if self.gpus_to_use:
            for gpu in self.gpus_to_use:
                args.append(f'-pu{gpu}')

        args.append(str(self.sim_filename))
        # print(args)

        return args

    # returns updated percent complete or None if not updated
    def process_screen_line(self, line_text):
        progress_percent = None
        # figure out if we are using date / times, the start time and the end time
        time_format_text = self.timeFormatRegex.search(line_text)
        if time_format_text:
            time_format_text = time_format_text.groups()[0].strip()
            if time_format_text.strip().lower() != 'hours':
                self.fv_uses_dates = True

        start_time_text = self.startTimeRegex.search(line_text)
        if self.start_time is None and start_time_text:
            start_time_text = start_time_text.groups()[0].strip()
            if self.fv_uses_dates:
                self.start_time = parser.parse(start_time_text, dayfirst=True, fuzzy=True)
                # self.start_time = datetime.strptime(start_time_text, "%d/%m/%Y %H:%M:%S", fuzzy=True)
            else:
                self.start_time = float(start_time_text)
            # print(f'Start time: {self.start_time}')

        end_time_text = self.endTimeRegex.search(line_text)
        if end_time_text:
            end_time_text = end_time_text.groups()[0].strip()
            if self.fv_uses_dates:
                self.end_time = parser.parse(end_time_text, dayfirst=True, fuzzy=True)
                # self.end_time = datetime.strptime(end_time_text, "%d/%m/%Y %H:%M:%S")
            else:
                self.end_time = float(end_time_text)
            # print(f'End time: {self.end_time}')

        if self.fv_uses_dates:
            timestep_date_time_text = self.timestepDateTimeRegex.search(line_text)
            if timestep_date_time_text:
                timestep_date_time_text = timestep_date_time_text.groups()[0].strip()
                curr_time = parser.parse(timestep_date_time_text, dayfirst=True, fuzzy=True)
                progress_percent = ((curr_time - self.start_time) / (self.end_time - self.start_time)) * 100.0
        else:
            timestep_hours_text = self.timestepHrsRegex.search(line_text)
            if timestep_hours_text:
                curr_time = float(timestep_hours_text.groups()[0].strip())
                # print(f'curr time: {curr_time}')
                progress_percent = ((curr_time - self.start_time) / (self.end_time - self.start_time)) * 100.0

        if line_text.find("Run Successful") != -1:
            self.succeeded = True

        if progress_percent is not None:
            # make sure we are at least 1 but less than 99
            progress_percent = max(min(1.0, progress_percent), progress_percent)
        return progress_percent

    def sim_finished(self):
        self.plugin.finished_running_config(self.config_num)
        self.config_num = None

    def run_finished_successfully(self):
        return self.succeeded

    def set_omp_threads(self):
        return self.cpus_to_use > 1

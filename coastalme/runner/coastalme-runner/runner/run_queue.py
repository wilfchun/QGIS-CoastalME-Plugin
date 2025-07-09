import csv
import json
from pathlib import Path
from pyqt_compat.QtCore import QAbstractTableModel, QModelIndex, pyqtSlot, pyqtSignal, Qt
from pyqt_compat.QtGui import *
import queue_item
import version

from pyqt_compat import QT_HORIZONTAL, QT_ITEM_DATA_DISPLAY_ROLE, QT_VERTICAL, QT_ITEM_DATA_FOREGROUND_ROLE


class RunQueueModel(QAbstractTableModel):
    run_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.run_queue = []
        self.column_names = ('Filename', 'Info', 'Status', 'Progress')

    def add_simulation(self, run_item):
        run_item.run_started.connect(self.simulation_started)
        run_item.progress_changed.connect(self.progress_update)
        run_item.run_finished.connect(self.simulation_finished)
        self.run_queue.append(run_item)

    def rowCount(self, parent=QModelIndex()):
        return len(self.run_queue)

    def columnCount(self, parent=QModelIndex()):
        return len(self.column_names)

    def headerData(self, section, orientation, role):
        if role != QT_ITEM_DATA_DISPLAY_ROLE:
            return None

        if orientation == QT_VERTICAL:
            return section + 1

        if orientation == QT_HORIZONTAL:
            return self.column_names[section]

    def data(self, index, role=QT_ITEM_DATA_DISPLAY_ROLE):
        if not index.isValid():
            return None
        if role == QT_ITEM_DATA_DISPLAY_ROLE:
            if self.column_names[index.column()] == "Filename":
                return f'{self.run_queue[index.row()].sim_filename.parent}\n' \
                       f'{self.run_queue[index.row()].sim_filename.name}'
            elif self.column_names[index.column()] == "Info":
                return self.run_queue[index.row()].plugin_item.get_sim_description()
            elif self.column_names[index.column()] == "Status":
                return f'{self.run_queue[index.row()].status.name:15}'
            elif self.column_names[index.column()] == "Progress":
                return self.run_queue[index.row()].progress
        elif role == QT_ITEM_DATA_FOREGROUND_ROLE:
            if self.column_names[index.column()] == "Progress":
                if self.run_queue[index.row()].progress == 100:
                    if self.run_queue[index.row()].status == queue_item.RunStatus.Failed:
                        return QBrush(QColor(255, 159, 128))
                    else:
                        return QBrush(QColor(204, 255, 153))

        else:
            return None

    # returns GPUs and CPUs in use
    def resources_in_use(self):
        gpus_in_use = set()  # Will be a set of GPUs being used
        cpus_in_use = 0

        for row, sim in enumerate(self.run_queue):
            if sim.status == queue_item.RunStatus.Running:
                gpus, cpus = sim.resources()
                gpus_in_use.update(gpus)
                cpus_in_use += cpus

        return gpus_in_use, cpus_in_use

    def run_ready_models(self, ngpus, ncpus):
        for row, sim in enumerate(self.run_queue):
            gpus_in_use, cpus_in_use = self.resources_in_use()
            all_gpus = set(range(ngpus))
            gpus_avail = all_gpus - gpus_in_use
            cpus_avail = ncpus - cpus_in_use
            # print(f'GPUS ready: {gpus_avail}')
            # print(f'CPUS ready: {cpus_avail}')
            # print(f'Ready to run {row}: {sim.able_to_run(gpus_avail, cpus_avail)}')
            if sim.status == queue_item.RunStatus.Waiting and \
                    sim.able_to_run(gpus_avail, cpus_avail):
                sim.run_simulation(gpus_avail, cpus_avail)

    @pyqtSlot(int)
    def simulation_started(self, run_id):
        for row, item in enumerate(self.run_queue):
            if item.run_id == run_id:
                top_left_index = self.createIndex(row, 2)
                bottom_right_index = self.createIndex(row, 3)

                super().dataChanged.emit(top_left_index, bottom_right_index)
                self.run_finished.emit(row)

    @pyqtSlot(int, float)
    def progress_update(self, run_id, percent):
        for row, item in enumerate(self.run_queue):
            if item.run_id == run_id:
                top_left_index = self.createIndex(row, 3)
                bottom_right_index = self.createIndex(row, 3)

                super().dataChanged.emit(top_left_index, bottom_right_index)

    @pyqtSlot(int)
    def simulation_finished(self, run_id):
        for row, item in enumerate(self.run_queue):
            if item.run_id == run_id:
                top_left_index = self.createIndex(row, 2)
                bottom_right_index = self.createIndex(row, 3)

                super().dataChanged.emit(top_left_index, bottom_right_index)
                self.run_finished.emit(row)

    def move_simulation_up(self, row):
        parent = QModelIndex()
        super().beginMoveRows(parent, row, row, parent, row - 1)
        self.run_queue[row - 1], self.run_queue[row] = self.run_queue[row], self.run_queue[row - 1]
        super().endMoveRows()

    def move_simulation_down(self, row):
        parent = QModelIndex()
        super().beginMoveRows(parent, row, row, parent, row + 2)
        self.run_queue.insert(row + 1, self.run_queue.pop(row))
        # self.run_queue[row + 1], self.run_queue[row] = self.run_queue[row], self.run_queue[row + 1]
        super().endMoveRows()

    def remove_simulation(self, row):
        parent = QModelIndex()
        super().beginRemoveRows(parent, row, row)
        self.run_queue.pop(row)
        super().endRemoveRows()

    def copy_plugin_item(self, row):
        # print('Copying sim info')
        return self.run_queue[row].clone_simulation_info()

    def save_queue(self, filename):
        # save the run queue in a json file (dictionary)
        run_queue_items = []
        for item in self.run_queue:
            item_text = {
                'plugin': item.plugin.get_name(),
                'sim_filename': str(item.sim_filename),
                item.plugin.get_name(): item.plugin_item.plugin_save_information()
            }
            run_queue_items.append(item_text)
        save_info = {
            'Version': version.version_text,
            'Run_queue': run_queue_items
        }
        with open(filename, 'w') as f:
            json.dump(save_info, f, indent=4)

        # run_queue_simulations = set()
        # for item in self.run_queue:
        #     item_info = (item.plugin.get_name(),
        #                  item.sim_filename,
        #                  item.plugin_item.plugin_save_information())
        #     run_queue_simulations.add(item_info)
        #
        # run_queue_rows = list(run_queue_simulations)
        #
        # with open(filename, 'wt', newline='') as f:
        #     w = csv.writer(f)
        #     w.writerow(['Plugin', 'Sim filename', 'Plugin info'])
        #     w.writerows(run_queue_rows)

    def load_queue_items(self, filename, plugins):
        run_items = []
        with open(filename, 'r') as f:
            object = json.load(f)

            for item_options in object['Run_queue']:
                plugin_name = item_options['plugin']
                plugin = next(filter(lambda x: x.get_name() == plugin_name, plugins))
                sim_filename = Path(item_options['sim_filename'])
                # print(item_options)
                plugin_item_options = item_options[plugin_name]
                run_items.append(
                    queue_item.RunItem(
                        sim_filename,
                        plugin,
                        plugin.create_plugin_item(
                            sim_filename,
                            plugin_item_options,
                        )
                    )
                )

        return run_items

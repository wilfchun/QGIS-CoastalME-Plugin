"""
This file has a class that stores the information required for each item in the runqueue
"""
from enum import Enum
import os
from pathlib import Path
from pyqt_compat.QtCore import QProcess, pyqtSignal, pyqtSlot, QObject, QProcessEnvironment
from pyqt_compat import QtWidgets
import signal
import time

from pyqt_compat.QtWidgets import QMessageBox

from pyqt_compat import QT_PROCESS_CRASH_EXIT


class RunStatus(Enum):
    Waiting = 1
    Running = 2
    Successful = 3
    Failed = 4


def next_id(static_var=[0]):
    static_var[0] += 1
    return static_var[0]


# See https://www.pythonguis.com/tutorials/PyQt5-qprocess-external-programs/
class RunItem(QObject):
    progress_changed = pyqtSignal(int, float)
    run_finished = pyqtSignal(int)
    run_started = pyqtSignal(int)

    def __init__(self, sim_filename, plugin, plugin_item):
        # Passes the run_id and the progress_changed
        super(RunItem, self).__init__()
        self.process_update_interval = 1.0  # only update if progress has changed at least this much
        self.run_id = next_id()
        self.plugin = plugin
        self.plugin_name = plugin.get_name()
        self.sim_filename = sim_filename
        self.plugin_item = plugin_item
        self.status = RunStatus.Waiting
        self.progress = 0.0
        self.process = None

        self.text_edit = None

    def clone_simulation_info(self):
        plugin_clone = self.plugin_item.clone_info()
        return plugin_clone

    @pyqtSlot(float)
    def update_progress(self, new_progress):
        if new_progress is None:
            return
        if new_progress - self.progress > self.process_update_interval:
            self.progress = new_progress
            self.progress_changed.emit(self.run_id, self.progress)

    def able_to_run(self, gpus_avail, cpus_avail):
        return self.plugin_item.able_to_run(gpus_avail, cpus_avail)

    def resources(self):
        return self.plugin_item.resources()

    def run_simulation(self, gpus_avail, cpus_avail):
        arguments = self.plugin_item.get_commandline_arguments(gpus_avail, cpus_avail)
        executable = self.plugin_item.get_executable()
        self.text_edit.appendPlainText(f'Executable: {executable}')
        self.text_edit.appendPlainText(f'Arguments: {arguments}')

        print(f'Executable: {executable}')

        if not Path(executable).exists():
            QtWidgets.QMessageBox.critical(
                None,
                'ERROR',
                'Invalid executable. Please set executable using the Settings option from the menu.')
            self.status = RunStatus.Failed
            self.update_progress(100.0)
            self.plugin_item.sim_finished()
            return

        # Need to store/retreive plugin executable
        self.process = QProcess(self)

        if self.plugin_item.set_omp_threads():
            env = QProcessEnvironment()
            # print(self.plugin_item.resources())
            env.insert("OMP_NUM_THREADS", str(self.plugin_item.resources()[1]))
            self.process.setProcessEnvironment(env)

        parent_folder = Path(self.sim_filename).parent
        if parent_folder.exists():
            self.process.setWorkingDirectory(str(parent_folder))
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.start(self.plugin_item.get_executable(), arguments)
        self.status = RunStatus.Running
        self.run_started.emit(self.run_id)

    def handle_stdout(self):
        data = None
        try:
            data = self.process.readAllStandardOutput()
            try:
                stdout = bytes(data).decode('utf-8')
            except:
                stdout = bytes(data).decode('iso-8859-1')
            #print(stdout)
            lines = stdout.split('\n')
            #print(lines)
            self.text_edit.appendPlainText(stdout)
            for line in lines:
                self.update_progress(self.plugin_item.process_screen_line(line))
            self.plugin_item.finished_reading_lines()
        except Exception as e:
            if data is not None:
                print(f'Error handling stdout: {data}\n{str(e)}')
            else:
                print(f'Error when reading from stdout')

    def handle_stderr(self):
        data = self.process.readAllStandardOutput()
        stderr = bytes(data).decode('utf8')
        # lines = stderr.split('\n')
        self.text_edit.appendPlainText(stderr)

    def send_stdin(self, text):
        self.process.write(text.encode())

    def handle_finished(self, exitCode, exitStatus):
        self.progress = 100.0
        if exitStatus == QT_PROCESS_CRASH_EXIT:
            self.status = RunStatus.Failed
        elif self.plugin_item.run_finished_successfully():
            self.status = RunStatus.Successful
        else:
            self.status = RunStatus.Failed
        self.plugin_item.sim_finished()
        self.run_finished.emit(self.run_id)

    def kill_simulation(self):
        # https://stackoverflow.com/questions/60651214/how-to-cleanly-exit-a-qprocess-with-ctrlc-input
        # Try to terminate first then kill if it doesn't work
        # print('terminating')
        # Try passing ctrl-c then terminate or kill
        # This was not working. have to rely on terminate or kill
        #try:
        #    os.kill(self.process.processId(), signal.CTRL_C_EVENT)
        #    time.sleep(0.5)
        #except KeyboardInterrupt:
        #    pass

        if self.process.processId() != 0:
            self.process.terminate()
            time.sleep(0.5)
            if self.process.processId() != 0:
                # print('killing')
                self.process.kill()

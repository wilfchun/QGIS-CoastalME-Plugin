# Uncommenting these lines can help with debugging especially silent QT crashes
# import cgitb
# cgitb.enable(format='text')
import ctypes

import sys
from enum import Enum
from functools import partial
from pathlib import Path

from pyqt_compat import QtCore, QtWidgets
from pyqt_compat.QtCore import QSettings, QModelIndex, QSize, QFileSystemWatcher, QDir, pyqtSlot, QPoint
from pyqt_compat.QtGui import QIcon
from pyqt_compat.QtWidgets import QMessageBox, QStackedWidget, QAbstractItemView, QSplitter, QToolBar
from pyqt_compat.QtWidgets import QSizePolicy, QPushButton, QMenu, QTabWidget, QHBoxLayout, QHeaderView

from pyqt_compat import (is_qt6, QT_VERTICAL, QT_HEADER_VIEW_RESIZE_TO_CONTENT, QT_STYLE_SP_DIR_OPEN_ICON,
                         QT_MESSAGE_BOX_YES, QT_ALIGN_RIGHT, QT_HEADER_VIEW_STRETCH, QT_ABSTRACT_ITEM_VIEW_SELECT_ROWS,
                         QT_LINE_EDIT_TRAILING_POSITION, QT_SIZE_POLICY_IGNORED)
if is_qt6:
    from pyqt_compat.QtGui import QAction
else:
    from pyqt_compat.QtWidgets import QAction

import settings
from file_paths import get_runner_absolute_path
from plugins.coastalme_plugin import TuflowPlugin
from plugins.coastalmefv_plugin import TuflowFvPlugin
from progress_bar import ProgressBarDelegate
from queue_item import RunItem, RunStatus
from run_queue import RunQueueModel
from runner_about import about_dialog
from screen_text_viewer import ScreenTextViewer
from version import version_text
import traceback


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error occurred:")
    print("error message:\n", tb)
    QtWidgets.QMessageBox.critical(None,
                                   "Uncaught error in runner",
                                   tb)
    QtWidgets.QApplication.quit()

class QueueActionType(Enum):
    ACT_MOVE_UP = 1
    ACT_MOVE_DOWN = 2
    ACT_KILL = 3
    ACT_RERUN = 4
    ACT_REMOVE = 5


def make_toolbar_w_actions(parent):
    toolbar = QToolBar()
    toolbar.setIconSize(QSize(16, 16))

    # dictionary based upon action type
    actions = {}

    up_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\037.png')),
                        'Up', parent)
    up_action.setStatusTip('Move simulation up in Queue')
    up_action.triggered.connect(parent.on_move_up)
    up_action.setEnabled(False)
    actions[QueueActionType.ACT_MOVE_UP] = up_action

    down_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\038.png')),
                          'Down', parent)
    down_action.setStatusTip('Move simulation up in Queue')
    down_action.triggered.connect(parent.on_move_down)
    down_action.setEnabled(False)
    actions[QueueActionType.ACT_MOVE_DOWN] = down_action

    kill_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\034.png')),
                          'Kill', parent)
    kill_action.setStatusTip('Kill current simulation')
    kill_action.triggered.connect(parent.on_kill)
    kill_action.setEnabled(False)
    actions[QueueActionType.ACT_KILL] = kill_action

    remove_action = QAction(QIcon(get_runner_absolute_path('..\\icons\\bluebits\\basic\\png\\16x16\\033.png')),
                            'Remove', parent)
    remove_action.setStatusTip('Remove current simulation')
    remove_action.triggered.connect(parent.on_remove)
    remove_action.setEnabled(False)
    actions[QueueActionType.ACT_REMOVE] = remove_action

    toolbar.addAction(up_action)
    toolbar.addAction(down_action)
    toolbar.addAction(kill_action)
    toolbar.addAction(remove_action)

    return toolbar, actions


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.max_number_of_recent_folders = 15
        self.recent_folder_actions = []

        # create the plugins

        self.plugins = (
            TuflowPlugin(),
            TuflowFvPlugin(),
        )
        settings.initializeSettings(self.plugins)

        self.run_queue_model = RunQueueModel()

        settings_obj = QSettings()
        settings_obj.beginGroup("MainWindow")

        self.setWindowTitle("COASTALME Runner")

        self.mainWidget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout(self)

        self.cbx_plugin = QtWidgets.QComboBox()

        for plugin in self.plugins:
            self.cbx_plugin.addItem(plugin.get_name())
        self.layout.addWidget(QtWidgets.QLabel("Run type:"), 1, 1, 1, 2)
        self.layout.addWidget(self.cbx_plugin, 1, 2, 1, 2)
        self.cbx_plugin.sizePolicy().setHorizontalStretch(2)

        self.cbx_plugin.setCurrentIndex(
            self.cbx_plugin.findText(
                settings_obj.value("plugin", self.cbx_plugin.itemText(0))
            )
        )
        self.cbx_plugin.currentIndexChanged.connect(self.current_pluging_changed)
        self.plugin = self.plugins[self.cbx_plugin.currentIndex()]

        self.create_menu()

        self.edt_base_folder = QtWidgets.QLineEdit()
        pixmapi = QT_STYLE_SP_DIR_OPEN_ICON
        icon = self.style().standardIcon(pixmapi)
        open_action = self.edt_base_folder.addAction(icon, QT_LINE_EDIT_TRAILING_POSITION)
        open_action.triggered.connect(self.on_browse)
        self.layout.addWidget(QtWidgets.QLabel("Base folder:"), 2, 1, 1, 2)
        # self.layout.addWidget(self.edt_base_folder, 2, 2, 1, 1)
        self.btn_refresh_simulations = QPushButton(
            icon=QIcon(get_runner_absolute_path('..\\icons\\icons8-repeat-16.png')))
        self.btn_refresh_simulations.setFixedSize(QSize(16, 16))
        # self.layout.addWidget(self.btn_refresh_simulations, 2, 3, 1, 1)
        self.btn_refresh_simulations.clicked.connect(self.directory_refresh)
        layout_folder_refresh = QHBoxLayout()
        layout_folder_refresh.addWidget(self.edt_base_folder)
        layout_folder_refresh.addWidget(self.btn_refresh_simulations)
        self.layout.addLayout(layout_folder_refresh, 2, 2, 1, 2)
        self.edt_base_folder.sizePolicy().setHorizontalStretch(2)
        self.edt_base_folder.editingFinished.connect(self.base_folder_changed)
        self.file_system_watcher = QFileSystemWatcher()

        self.cbx_simulation_files = QtWidgets.QComboBox()
        self.layout.addWidget(QtWidgets.QLabel("Simulation file:"), 3, 1, 1, 2)
        self.layout.addWidget(self.cbx_simulation_files, 3, 2, 1, 2)
        self.cbx_simulation_files.sizePolicy().setHorizontalStretch(2)

        self.edt_base_folder.setText(settings_obj.value(f"{self.plugin.get_name()}\\Base Folder", ""))
        self.base_folder_changed()
        self.cbx_simulation_files.setCurrentIndex(
            self.cbx_simulation_files.findText(
                settings_obj.value(f"{self.plugin.get_name()}\\Simulation", "")
            )
        )
        self.file_system_watcher.directoryChanged.connect(self.directory_changed)
        self.file_system_watcher.fileChanged.connect(self.directory_changed)

        self.queueToolbar, self.queueActions = make_toolbar_w_actions(self)

        self.btn_add_simulation = QtWidgets.QPushButton("Add")
        self.btn_add_simulation.clicked.connect(self.on_add_simulation)
        self.btn_add_simulation.sizePolicy().setHorizontalPolicy(QT_SIZE_POLICY_IGNORED)

        self.tog_run = QPushButton(
            'Run',
        )
        self.tog_run.setCheckable(True)
        self.tog_run.clicked.connect(self.on_toggle_run)

        self.layout.addWidget(self.btn_add_simulation, 4, 1, 1, 1, QT_ALIGN_RIGHT)
        self.layout.addWidget(self.tog_run, 4, 2, 1, 1, QT_ALIGN_RIGHT)
        self.layout.addWidget(self.queueToolbar, 4, 3, 1, 1, QT_ALIGN_RIGHT)

        self.tbl_run_queue = QtWidgets.QTableView()
        self.tbl_run_queue.setModel(self.run_queue_model)
        self.tbl_run_queue.setItemDelegateForColumn(3, ProgressBarDelegate())
        self.tbl_run_queue.setSelectionBehavior(QT_ABSTRACT_ITEM_VIEW_SELECT_ROWS)

        self.tbl_run_queue.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tbl_run_queue.customContextMenuRequested.connect(self.run_queue_right_click)

        # self.tbl_run_queue.horizontalHeader().setSectionResizeMode(QT_HEADER_VIEW_STRETCH)
        # self.tbl_run_queue.horizontalHeader().resizeSections()
        # self.tbl_run_queue.horizontalHeader().setStretchLastSection(True)
        # self.tbl_run_queue.horizontalHeader().setSectionResizeMode()

        self.stackedWidget = QStackedWidget()

        self.tbl_run_queue.selectionModel().currentChanged.connect(self.queue_item_changed)
        self.run_queue_model.run_finished.connect(self.simulation_finished)

        self.queueAndToolbar = QtWidgets.QWidget()
        queue_and_toolbar_layout = QtWidgets.QGridLayout()
        # queue_and_toolbar_layout.addWidget(self.queueToolbar, 1, 1, 1, 1, QT_ALIGN_RIGHT)
        self.queueAndToolbar.setLayout(queue_and_toolbar_layout)

        queue_and_toolbar_layout.addWidget(self.tbl_run_queue, 1, 1, 1, 1)

        splitter = QSplitter()
        splitter.addWidget(self.queueAndToolbar)
        splitter.addWidget(self.stackedWidget)
        splitter.setOrientation(QT_VERTICAL)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self.layout.addWidget(splitter, 5, 1, -1, -1)

        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

        if settings_obj.value('first_time', 'true') == 'true':
            QMessageBox.information(self,
                                    'Initial settings',
                                    'Before adding simulations specify executables and hardware configurations'
                                    ' in the Settings option from the menu.'
                                    )
            settings_obj.setValue('first_time', 'false')

        settings_obj.endGroup()

    def create_menu(self):
        action_save_queue = QAction("&Save run queue", self)
        action_save_queue.setStatusTip("Save the run queue to rerun same simulations later")
        action_save_queue.triggered.connect(self.save_queue)

        action_load_queue = QAction("&Load run queue", self)
        action_load_queue.setStatusTip("Load the run queue to rerun same simulations later")
        action_load_queue.triggered.connect(self.load_queue)

        action_settings = QAction("&Settings", self)
        action_settings.setStatusTip("COASTALME Runner Settings")
        action_settings.triggered.connect(self.on_settings)

        action_about = QAction("&About", self)
        action_about.setStatusTip("About dialog")
        action_about.triggered.connect(about_dialog)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&Menu")
        self.file_menu.addAction(action_save_queue)
        self.file_menu.addAction(action_load_queue)

        self.recent_menu = self.file_menu.addMenu('&Recent Folders')
        self.recent_menu.triggered.connect(self.handle_recent_folder)
        self.recent_menu_actions = []
        self.load_recent_filenames()

        self.file_menu.addAction(action_settings)
        self.file_menu.addAction(action_about)

    def handle_recent_folder(self, action):
        self.edt_base_folder.setText(action.text())
        self.base_folder_changed()

    def add_recent_folder(self, folder):
        settings_obj = QSettings()
        settings_obj.beginGroup("MainWindow")
        settings_obj.beginGroup(f"{self.plugin.get_name()}")
        recent_folders = settings_obj.value("Recent_Folders", [])

        # Use a dict to get unique folders sorted with when inserted
        # Value not important
        recent_folders_dict = {folder.path(): 1}
        for recent_folder in recent_folders:
            recent_folders_dict[recent_folder] = 1

        recent_folders = list(recent_folders_dict.keys())
        settings_obj.setValue("Recent_Folders", recent_folders)
        settings_obj.endGroup()

        self.load_recent_filenames()

    def load_recent_filenames(self):
        settings_obj = QSettings()
        settings_obj.beginGroup("MainWindow")
        settings_obj.beginGroup(f"{self.plugin.get_name()}")
        recent_folders = settings_obj.value("Recent_Folders", [])
        # Make max number of recent_folders
        recent_folders = recent_folders[:self.max_number_of_recent_folders]

        self.recent_folder_actions = []
        self.recent_menu.clear()

        for recent_folder in recent_folders:
            action = QAction(recent_folder, self)
            self.recent_menu.addAction(action)

    def update_toolbar(self, sel_row):
        if sel_row is None:
            self.queueActions[QueueActionType.ACT_MOVE_UP].setEnabled(False)
            self.queueActions[QueueActionType.ACT_MOVE_DOWN].setEnabled(False)
            self.queueActions[QueueActionType.ACT_KILL].setEnabled(False)
            self.queueActions[QueueActionType.ACT_REMOVE].setEnabled(False)
        else:
            row_count = self.run_queue_model.rowCount()
            is_running = self.run_queue_model.run_queue[sel_row].status == RunStatus.Running
            self.queueActions[QueueActionType.ACT_MOVE_UP].setEnabled(sel_row > 0)
            self.queueActions[QueueActionType.ACT_MOVE_DOWN].setEnabled(sel_row < row_count - 1)
            self.queueActions[QueueActionType.ACT_KILL].setEnabled(is_running)
            self.queueActions[QueueActionType.ACT_REMOVE].setEnabled(not is_running)

    def queue_item_changed(self, current, _):
        sel_row = current.row()
        self.stackedWidget.setCurrentIndex(current.row())
        self.update_toolbar(sel_row)

    def closeEvent(self, event):
        button = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to Quit?")
        if button == QT_MESSAGE_BOX_YES:
            settings_obj = QSettings()
            settings_obj.beginGroup("MainWindow")
            settings_obj.setValue("plugin", self.cbx_plugin.itemText(self.cbx_plugin.currentIndex()))
            settings_obj.setValue(f"{self.plugin.get_name()}\\Base Folder", self.edt_base_folder.text())
            settings_obj.setValue(f"{self.plugin.get_name()}\\Simulation",
                                  self.cbx_simulation_files.itemText(self.cbx_simulation_files.currentIndex()))
            settings_obj.endGroup()

            event.accept()
        else:
            event.ignore()

    # @pyqtSlot()
    # def magic(self):
    #    self.text.setText(random.choice(self.hello))
    @pyqtSlot(int)
    def current_pluging_changed(self, index):
        # Store the old plugin information in settings
        settings_obj = QSettings()
        settings_obj.beginGroup("MainWindow")
        settings_obj.setValue(f"{self.plugin.get_name()}\\Base Folder", self.edt_base_folder.text())
        settings_obj.setValue(f"{self.plugin.get_name()}\\Simulation",
                              self.cbx_simulation_files.itemText(self.cbx_simulation_files.currentIndex()))
        self.plugin = self.plugins[index]
        self.edt_base_folder.setText(settings_obj.value(f"{self.plugin.get_name()}\\Base Folder", ""))
        self.load_recent_filenames()
        self.refresh_simulations_cbx()
        self.cbx_simulation_files.setCurrentIndex(
            self.cbx_simulation_files.findText(
                settings_obj.value(f"{self.plugin.get_name()}\\Simulation", "")
            )
        )
        self.base_folder_changed()

    @pyqtSlot()
    def base_folder_changed(self):
        self.file_system_watcher.addPath(self.edt_base_folder.text())
        print(f'Watching: {self.file_system_watcher.directories()}')
        # self.observer.stop()
        # base_folder = str(self.edt_base_folder.text())
        # print(base_folder)
        # self.observer.schedule(self.handler,
        #                       self.edt_base_folder.text(),
        #                       recursive=True)
        # self.observer.start()
        # print(self.observer.is_alive())
        self.refresh_simulations_cbx()

    @pyqtSlot()
    def directory_refresh(self):
        self.refresh_simulations_cbx()

    @pyqtSlot(str)
    def directory_changed(self, _):
        self.refresh_simulations_cbx()

    @pyqtSlot()
    def refresh_simulations_cbx(self):
        old_sim_entry = self.cbx_simulation_files.currentText()

        base_folder = QtCore.QDir(self.edt_base_folder.text())
        # print('Refreshing simulation files')
        # print(f'Base folder: {base_folder}')
        # print(f'Extension: {self.plugin.get_simulation_extension()}')
        self.add_recent_folder(base_folder)
        if base_folder.exists():
            base_path = Path(base_folder.path())
            file_list = list(base_path.glob(f'**/{self.plugin.get_simulation_extension()}'))
            relative_paths = [str(x.relative_to(base_path)) for x in file_list]
            if relative_paths:
                # see if anything has changed
                changed = False
                if len(relative_paths) != self.cbx_simulation_files:
                    changed = True
                else:
                    for i in range(len(relative_paths)):
                        if relative_paths[i] != self.cbx_simulation_files.itemText(i):
                            changed = True
                            break
                if changed:
                    self.cbx_simulation_files.clear()
                    self.cbx_simulation_files.addItems(relative_paths)
                    if self.cbx_simulation_files.findText(old_sim_entry):
                        self.cbx_simulation_files.setCurrentText(old_sim_entry)
                    else:
                        self.cbx_simulation_files.setCurrentIndex(0)

    @pyqtSlot()
    def on_settings(self):
        settings.run_settings_dialog(self.plugins)

    @pyqtSlot()
    def on_browse(self):
        base_folder = QDir.toNativeSeparators(
            QtWidgets.QFileDialog.getExistingDirectory(
                directory=self.edt_base_folder.text()
            ))
        if base_folder:
            self.edt_base_folder.setText(base_folder)
            self.refresh_simulations_cbx()

    @pyqtSlot()
    def on_add_simulation(self):
        base_folder = Path(self.edt_base_folder.text())
        sim_filename = base_folder / self.cbx_simulation_files.itemText(self.cbx_simulation_files.currentIndex())
        if not sim_filename or not sim_filename.exists() or not sim_filename.is_file():
            QtWidgets.QMessageBox.critical(self,
                                           "Error Adding Simulation",
                                           "Simulation file does not exist",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        try:
            plugin_items = self.plugin.get_plugin_items(sim_filename)
            self.add_new_plugin_items(sim_filename, plugin_items)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self,
                                           "ERROR adding simulation",
                                           str(e),
                                           QMessageBox.StandardButton.Ok)
        # except Exception:
        #     QtWidgets.QMessageBox.critical(self,
        #                                    "ERROR adding simulation",
        #                                    traceback.format_exc(),
        #                                    QMessageBox.StandardButton.Ok)

    def add_new_run_items(self, run_items):
        self.run_queue_model.beginInsertRows(
            QModelIndex(),
            self.run_queue_model.rowCount(),
            self.run_queue_model.rowCount() + len(run_items) - 1)
        for run_item in run_items:
            self.run_queue_model.add_simulation(
                run_item
            )
            tab_ctrl = QTabWidget()
            run_output = ScreenTextViewer()
            tab_ctrl.addTab(run_output, 'Screen Output')
            run_item.plugin_item.create_additional_tabs(tab_ctrl)
            self.stackedWidget.addWidget(tab_ctrl)
            run_output.appendPlainText(f'{run_item.sim_filename}\n{run_item.plugin_item.get_sim_description()}')
            run_item.text_edit = run_output

        self.run_queue_model.endInsertRows()
        self.tbl_run_queue.resizeRowsToContents()
        # self.tbl_run_queue.horizontalHeader().setStretchLastSection(True)
        # self.tbl_run_queue.resizeColumnsToContents()
        for col in range(self.tbl_run_queue.horizontalHeader().count() - 1):
            self.tbl_run_queue.horizontalHeader().setSectionResizeMode(
                col,
                QT_HEADER_VIEW_RESIZE_TO_CONTENT
            )

        self.tbl_run_queue.horizontalHeader().setSectionResizeMode(
            self.tbl_run_queue.horizontalHeader().count() - 1,
            QT_HEADER_VIEW_STRETCH
        )

        self.run_ready_models()

    def add_new_plugin_items(self, sim_filename, plugin_items):
        # print(f'Number of plugin items: {len(plugin_items)}')

        run_items = [RunItem(sim_filename, self.plugin, plugin_item) for plugin_item in plugin_items]
        self.add_new_run_items(run_items)

    @pyqtSlot(int)
    def simulation_finished(self, _):
        self.run_ready_models()

    @pyqtSlot()
    def on_toggle_run(self):
        self.run_ready_models()

    @pyqtSlot()
    def on_move_up(self):
        sel_row = self.selected_row()
        self.run_queue_model.move_simulation_up(sel_row)
        w = self.stackedWidget.widget(sel_row)
        self.stackedWidget.removeWidget(w)
        self.stackedWidget.insertWidget(sel_row - 1, w)
        self.stackedWidget.setCurrentIndex(sel_row - 1)
        self.update_toolbar(sel_row - 1)

    @pyqtSlot()
    def on_move_down(self):
        sel_row = self.selected_row()
        # print(sel_row)
        self.run_queue_model.move_simulation_down(sel_row)
        w = self.stackedWidget.widget(sel_row)
        self.stackedWidget.removeWidget(w)
        self.stackedWidget.insertWidget(sel_row + 1, w)
        self.stackedWidget.setCurrentIndex(sel_row + 1)
        self.update_toolbar(sel_row + 1)

    @pyqtSlot()
    def on_kill(self):
        button = QMessageBox.question(self, "Confirm Kill Model", "Are you sure you want to kill the running model?")
        if button == QT_MESSAGE_BOX_YES:
            self.run_queue_model.run_queue[self.selected_row()].kill_simulation()

    @pyqtSlot()
    def on_remove(self):
        sel_row = self.selected_row()
        self.run_queue_model.remove_simulation(sel_row)
        w = self.stackedWidget.widget(sel_row)
        self.stackedWidget.removeWidget(w)
        if self.run_queue_model.rowCount() == 0:
            self.update_toolbar(None)
            return
        if sel_row >= self.run_queue_model.rowCount():
            self.tbl_run_queue.selectRow(sel_row - 1)
            self.update_toolbar(sel_row - 1)
            self.stackedWidget.setCurrentIndex(sel_row - 1)
        else:
            self.tbl_run_queue.selectRow(sel_row)
            self.update_toolbar(sel_row)
            self.stackedWidget.setCurrentIndex(sel_row)

    @pyqtSlot(QPoint)
    def run_queue_right_click(self, pos):
        index = self.tbl_run_queue.indexAt(pos)
        if index.isValid():
            # print('Valid index')
            row = index.row()
            # print(f'Row: {row}')
            item = self.run_queue_model.run_queue[row]
            # print(f'Item status: {item.status}')
            if item.status == RunStatus.Running:
                action_send_enter = QAction("Send enter", self)
                action_send_enter.triggered.connect(partial(self.send_enter, row))

                context_menu = QMenu()
                context_menu.addAction(action_send_enter)

                context_menu.exec(self.tbl_run_queue.viewport().mapToGlobal(pos))
            elif item.status in [RunStatus.Failed, RunStatus.Successful]:
                action_rerun = QAction("Rerun simulation", self)
                action_rerun.triggered.connect(partial(self.rerun_row, row))

                context_menu = QMenu()
                context_menu.addAction(action_rerun)

                context_menu.exec(self.tbl_run_queue.viewport().mapToGlobal(pos))

    def rerun_row(self, row):
        plugin_item = self.run_queue_model.copy_plugin_item(row)
        self.add_new_plugin_items(self.run_queue_model.run_queue[row].sim_filename,
                                  [plugin_item])

    def send_enter(self, row):
        self.run_queue_model.run_queue[row].send_stdin('\n')

    def selected_row(self):
        sel_indices = self.tbl_run_queue.selectedIndexes()
        if sel_indices:
            return sel_indices[0].row()
        return None

    def run_ready_models(self):
        if self.tog_run.isChecked():
            thesettings = QSettings()
            cpus = thesettings.value("Resources/CPU Count")
            gpus = thesettings.value("Resources/GPU Count")
            self.run_queue_model.run_ready_models(gpus, cpus)
            self.update_toolbar(self.selected_row())

    @pyqtSlot()
    def save_queue(self):
        save_filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save run queue",
            filter="JSON Files (*.json)"
        )
        # print(save_filename)
        if save_filename:
            self.run_queue_model.save_queue(save_filename)

    @pyqtSlot()
    def load_queue(self):
        load_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open run queue",
            filter="JSON Files (*.json)",
        )
        # print(load_filename)
        if load_filename:
            run_items = self.run_queue_model.load_queue_items(load_filename, self.plugins)
            self.add_new_run_items(run_items)


if __name__ == "__main__":
    myappid = f'coastalme.modelrunner.{version_text}'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtWidgets.QApplication([])
    app.setStyle("fusion")

    if not is_qt6:  # always enabled on Qt6 and attribute is deprecated
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        if hasattr(QtWidgets.QStyleFactory, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    sys.excepthook = excepthook

    app.setOrganizationName("BMT")
    app.setApplicationName("COASTALME Runner")
    qIcon = QIcon(get_runner_absolute_path(r"..\icons\runner\icons8-exercise.ico"))
    qIcon.addFile(get_runner_absolute_path(r"..\icons\runner\icons8-exercise-32.ico"))
    qIcon.addFile(get_runner_absolute_path(r"..\icons\runner\icons8-exercise-64.ico"))
    qIcon.addFile(get_runner_absolute_path(r"..\icons\runner\icons8-exercise-96.ico"))
    app.setWindowIcon(qIcon)
    main_window = MainWindow()

    try:
        main_window.resize(800, 600)
        main_window.show()

        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, 'ERROR in Runner', f'{e}')

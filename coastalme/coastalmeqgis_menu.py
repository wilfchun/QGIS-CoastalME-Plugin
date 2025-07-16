# -*- coding: utf-8 -*-
"""
/***************************************************************************
 coastalmeqgis_menu
                                 A QGIS plugin
 Initialises the COASTALME menu system
                              -------------------
        begin                : 2013-08-27
        copyright            : (C) 2013 by Phillip Ryan
        email                : support@coastalme.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# import setuptools

# Import the PyQt and QGIS libraries
# from qgis.PyQt.QtWidgets  import ( QMenu )

# Import the code for the library functions
from .coastalmeqgis_library import about, resetQgisSettings

# Import the code for the COASTALME viewer
from .coastalmeqgis_cmeviewer.coastalmeqgis_cmeview import CmeView

import os
import sys
from pathlib import Path

from .toc.toc import toc_selected_layers

# Import required Qt/QGIS components
from qgis.PyQt.QtWidgets import QMessageBox, QMenu, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QSize
from qgis.core import QgsProject, Qgis


from .compatibility_routines import (
    QT_MESSAGE_BOX_YES,
    QT_MESSAGE_BOX_NO,
    QT_MESSAGE_BOX_CANCEL,
    QT_DOCK_WIDGET_AREA_BOTTOM,
    QT_DOCK_WIDGET_AREA_RIGHT,
)


class coastalmeqgis_menu:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = Path(os.path.realpath(__file__)).parent
        self.resultsPlottingDockOpened = False
        self.lambdaConnections = []
        self.icons = {}

    def icon(self, icon_name: str) -> QIcon:
        """Get icon."""
        if icon_name in self.icons:
            return self.icons[icon_name]
        p = self.plugin_dir / "icons"
        for p_ in p.glob(f"{icon_name}.*"):
            icon = QIcon(str(p_))
            self.icons[icon_name] = icon
            return icon
        icon = QIcon()
        for p_ in p.glob(f"{icon_name}*"):
            regex = icon_name + r"_\d{2}$"
            if re.findall(regex, p_.stem):
                size = int(p_.stem[-2:])
                icon.addFile(str(p_), QSize(size, size))
        self.icons[icon_name] = icon
        return icon

    # Processing provider removed - only keeping viewer functionality

    def initGui(self):
        dir = os.path.dirname(__file__)
        icon = QIcon(os.path.join(dir, "coastalme.png"))
        self.coastalmeMenu = self.iface.pluginMenu().addMenu(icon, "&COASTALME")

        # About Submenu
        self.about_menu = QMenu(QCoreApplication.translate("COASTALME", "&About"))
        self.coastalmeMenu.addMenu(self.about_menu)

        icon = QIcon(os.path.join(dir, "icons", "info.png"))
        self.about_action = QAction(icon, "About", self.iface.mainWindow())
        self.about_action.triggered.connect(self.about_coastalmeqgis)
        self.about_menu.addAction(self.about_action)

        # CLEAR Submenu
        self.clear_menu = QMenu(QCoreApplication.translate("COASTALME", "&Clear"))
        self.coastalmeMenu.addMenu(self.clear_menu)
        self.clearGlobalSettingsAction = QAction(
            "Clear COASTALME Global Settings", self.iface.mainWindow()
        )
        self.clearProjectSettingsAction = QAction(
            "Clear COASTALME Project Settings", self.iface.mainWindow()
        )
        self.removeCmeviewAction = QAction(
            "Close COASTALME Viewer Completely", self.iface.mainWindow()
        )
        self.reloadCmeviewAction = QAction(
            "Reload COASTALME Viewer", self.iface.mainWindow()
        )
        self.clear_menu.addAction(self.clearGlobalSettingsAction)
        self.clear_menu.addAction(self.clearProjectSettingsAction)
        self.clear_menu.addAction(self.removeCmeviewAction)
        self.clear_menu.addAction(self.reloadCmeviewAction)
        self.clearGlobalSettingsAction.triggered.connect(
            lambda: resetQgisSettings(scope="Global")
        )
        self.clearProjectSettingsAction.triggered.connect(
            lambda: resetQgisSettings(scope="Project")
        )
        self.removeCmeviewAction.triggered.connect(self.removeCmeview)
        self.reloadCmeviewAction.triggered.connect(self.reloadCmeview)

        # Reload Data - Toolbar button
        icon = QIcon(os.path.join(dir, "icons", "Reload_Data.PNG"))
        self.reload_data_action = QAction(icon, "Reload Data", self.iface.mainWindow())
        self.reload_data_action.triggered.connect(self.reload_data)
        self.iface.addToolBarIcon(self.reload_data_action)
        self.coastalmeMenu.addAction(self.reload_data_action)

        # COASTALME Viewer - Toolbar button
        icon = QIcon(os.path.join(dir, "icons", "coastalme.png"))
        self.view_results_action = QAction(
            icon, "COASTALME Viewer", self.iface.mainWindow()
        )
        self.view_results_action.triggered.connect(self.openResultsPlottingWindow)
        self.iface.addToolBarIcon(self.view_results_action)
        self.coastalmeMenu.addAction(self.view_results_action)

        # Removed all other toolbar icons and menu items - keeping only essential functionality

    def unload(self):
        # coastalme viewer
        self.removeCmeview(no_popup=True)

        self.qgisDisconnect()

        self.coastalmeMenu.clear()
        self.iface.pluginMenu().removeAction(self.coastalmeMenu.menuAction())

        # Remove only the toolbar icons we're keeping
        self.iface.removeToolBarIcon(self.reload_data_action)
        self.iface.removeToolBarIcon(self.view_results_action)

    def about_coastalmeqgis(self):
        about(self.iface.mainWindow())

    def reload_data(self):
        from .coastalmeqgis_library import reload_data

        for layer in toc_selected_layers(self.iface):
            reload_data(layer)

    def openResultsPlottingWindow(self, showmessage=True):
        qv = Qgis.QGIS_VERSION_INT
        if self.resultsPlottingDockOpened:
            if not self.resultsPlottingDock.isVisible():
                self.resultsPlottingDock.show()
                self.resultsPlottingDock.qgisConnect()
            elif showmessage:
                bRedock = QMessageBox.question(
                    self.iface.mainWindow(),
                    "COASTALME Viewer",
                    "Would you like to redock COASTALME Viewer?",
                    QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL,
                )
                if bRedock == QT_MESSAGE_BOX_YES:
                    self.resultsPlottingDock.setFloating(False)
        else:
            try:
                self.resultsPlottingDock = CmeView(
                    self.iface,
                    removeCmeview=self.removeCmeviewAction,
                    reloadCmeview=self.reloadCmeviewAction,
                )
            except:
                self.resultsPlottingDock = CmeView(self.iface)
            dockArea = QT_DOCK_WIDGET_AREA_BOTTOM
            isTabified = False
            tabifiedWith = []
            if QSettings().value(
                "COASTALME/cmeview_defaultlayout", "previous_state"
            ) == "narrow" or (
                QSettings().value("COASTALME/cmeview_defaultlayout", "previous_state")
                == "previous_state"
                and QSettings().value("COASTALME/cmeview_previouslayout", "plot")
                == "narrow"
            ):
                dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                if QSettings().contains("COASTALME/cmeview_docklocation"):
                    dockArea = QSettings().value(
                        "COASTALME/cmeview_docklocation", QT_DOCK_WIDGET_AREA_RIGHT
                    )
                    if type(dockArea) is str:
                        try:
                            dockArea = int(dockArea)
                        except ValueError:
                            dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                isTabified = QSettings().value("COASTALME/cmeview_isdocktabified", False)
                if type(isTabified) is str:
                    try:
                        isTabified = bool(isTabified)
                    except ValueError:
                        isTabified = False
                if isTabified:
                    tabifiedWith = QSettings().value("COASTALME/cmeview_tabifiedwith", [])
                    if type(isTabified) is str:
                        tabifiedWith = tabifiedWith.split(",")
                    if not tabifiedWith:
                        isTabified = False

            if isTabified and qv >= 31400:
                self.iface.addTabifiedDockWidget(
                    dockArea, self.resultsPlottingDock, tabifiedWith, True
                )
            else:
                self.iface.addDockWidget(dockArea, self.resultsPlottingDock)
            self.resultsPlottingDockOpened = True

    def removeCmeview(self, **kwargs):
        no_popup = kwargs["no_popup"] if "no_popup" in kwargs else False
        resetQgisSettings(scope="Project", cmeviewer=True, feedback=False)
        try:
            self.resultsPlottingDock.tuPlot.clearAllPlots()
            self.resultsPlottingDock.qgisDisconnect(completely_remove=True)
            self.resultsPlottingDock.close()
            self.iface.removeDockWidget(self.resultsPlottingDock)
            del self.resultsPlottingDock
            self.resultsPlottingDockOpened = False
            if "feedback" in kwargs:
                if not kwargs["feedback"]:
                    return
            if not no_popup:
                QMessageBox.information(
                    self.iface.mainWindow(), "COASTALME", "Completely Closed COASTALME Viewer"
                )
        except:
            if "feedback" in kwargs:
                if not kwargs["feedback"]:
                    return
            if not no_popup:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "COASTALME",
                    "ERROR closing COASTALME Viewer. Please email support@coastalme.com",
                )

    def reloadCmeview(self):
        self.removeCmeview(feedback=False)
        self.openResultsPlottingWindow()

    def select_changed(self):
        """Used with CmePLOT external function. Is called when current selection changes."""

        # check to see if CmePLOT is open
        poll = self.tpOpen.poll()
        if poll == None:  # CmePLOT is open so update .int file
            self.tpOpen, self.intFile, self.defaultPath = self.tpExternal.open(
                self.tpOpen, self.intFile, self.defaultPath
            )
        else:  # CmePLOT is not open so disconnect signals
            # QObject.disconnect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
            self.cLayer.selectionChanged.disconnect(self.select_changed)
            # QObject.disconnect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.layer_changed)
            self.iface.currentLayerChanged.disconnect(self.layer_changed)

    def layer_changed(self):
        """Used with CmePLOT external function. Is called when current layer changes."""

        self.cLayer = self.iface.mapCanvas().currentLayer()
        if self.cLayer is not None:
            # QObject.connect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
            self.cLayer.selectionChanged.connect(self.select_changed)

    def cleaning_res(self):
        QMessageBox.information(self.iface.mainWindow(), "debug", "Dock Closed")
        self.dockOpened = False

    def run_coastalme(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_run_cme_simple_dialog(self.iface, project)
        dialog.exec()

    def launch_runner(self):
        if sys.placmeorm != "win32":
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Not Supported",
                "The COASTALME Runner is currently only supported on Windows",
            )
            return
        dir = os.path.dirname(__file__)
        script_with_path = os.path.join(dir, "runner\\coastalme-runner\\runner\\main.py")
        if not os.path.isfile(script_with_path):
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Not Found",
                f"The COASTALME runner script not found at {script_with_path}",
            )
            return
        command = ["python3", script_with_path]
        # https://stackoverflow.com/questions/70543646/module-does-not-have-the-attribute-subprocess-detached-process
        process = Popen(command, creationflags=DETACHED_PROCESS, start_new_session=True)

    def check_dependencies(self):
        # QMessageBox.critical(self.iface.mainWindow(), "Info", "Not yet implemented!")
        from .coastalmeqgis_library import check_python_lib

        lib_check = check_python_lib(self.iface)

        max_len = max(len(k) for k in lib_check.keys()) + 2
        msg = "\n".join(
            ["{0:{2}s}: {1}".format(k, v, max_len) for k, v in lib_check.items()]
        )

        dlg = QMessageBox(self.iface.mainWindow())
        dlg.setIcon(QT_MESSAGE_BOX_INFORMATION)
        dlg.setWindowTitle("Python Dependencies Check")
        font = QFont("Monospace")
        font.setStyleHint(QT_FONT_MONOSPACE)
        dlg.setFont(font)
        dlg.setText(msg)
        dlg.setStandardButtons(QT_MESSAGE_BOX_OK)
        dlg.exec()

    def about_coastalmeqgis(self):
        # QMessageBox.information(self.iface.mainWindow(), "About COASTALME QGIS", 'This is a developmental version of the COASTALME QGIS utitlity, build: '+build_vers)
        # QMessageBox.information(self.iface.mainWindow(), "About COASTALME QGIS", "This is a {0} version of the COASTALME QGIS utility\nBuild: {1}".format(build_type,build_vers))
        about(self.iface.mainWindow())

    # Added MJS 11/02
    def import_check(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_import_check_dialog(self.iface, project)
        dialog.exec()

    # All other methods removed - keeping only essential functionality

    def openResultsPlottingWindow(self, showmessage=True):
        qv = Qgis.QGIS_VERSION_INT
        if self.resultsPlottingDockOpened:
            if not self.resultsPlottingDock.isVisible():
                self.resultsPlottingDock.show()
                self.resultsPlottingDock.qgisConnect()
            elif showmessage:
                bRedock = QMessageBox.question(
                    self.iface.mainWindow(),
                    "COASTALME Viewer",
                    "Would you like to redock COASTALME Viewer?",
                    QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL,
                )
                if bRedock == QT_MESSAGE_BOX_YES:
                    self.resultsPlottingDock.setFloating(False)
        else:
            try:
                self.resultsPlottingDock = CmeView(
                    self.iface,
                    removeCmeview=self.removeCmeviewAction,
                    reloadCmeview=self.reloadCmeviewAction,
                )
            except:
                self.resultsPlottingDock = CmeView(self.iface)
            dockArea = QT_DOCK_WIDGET_AREA_BOTTOM
            isTabified = False
            tabifiedWith = []
            if QSettings().value(
                "COASTALME/cmeview_defaultlayout", "previous_state"
            ) == "narrow" or (
                QSettings().value("COASTALME/cmeview_defaultlayout", "previous_state")
                == "previous_state"
                and QSettings().value("COASTALME/cmeview_previouslayout", "plot")
                == "narrow"
            ):
                dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                if QSettings().contains("COASTALME/cmeview_docklocation"):
                    dockArea = QSettings().value(
                        "COASTALME/cmeview_docklocation", QT_DOCK_WIDGET_AREA_RIGHT
                    )
                    if type(dockArea) is str:
                        try:
                            dockArea = int(dockArea)
                        except ValueError:
                            dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                isTabified = QSettings().value("COASTALME/cmeview_isdocktabified", False)
                if type(isTabified) is str:
                    try:
                        isTabified = bool(isTabified)
                    except ValueError:
                        isTabified = False
                if isTabified:
                    tabifiedWith = QSettings().value("COASTALME/cmeview_tabifiedwith", [])
                    if type(isTabified) is str:
                        tabifiedWith = tabifiedWith.split(",")
                    if not tabifiedWith:
                        isTabified = False

            if isTabified and qv >= 31400:
                self.iface.addTabifiedDockWidget(
                    dockArea, self.resultsPlottingDock, tabifiedWith, True
                )
            else:
                self.iface.addDockWidget(QT_DOCK_WIDGET_AREA_BOTTOM
, self.resultsPlottingDock)
            self.resultsPlottingDockOpened = True

    def removeCmeview(self, **kwargs):
        no_popup = kwargs["no_popup"] if "no_popup" in kwargs else False
        resetQgisSettings(scope="Project", cmeviewer=True, feedback=False)
        try:
            self.resultsPlottingDock.tuPlot.clearAllPlots()
            self.resultsPlottingDock.qgisDisconnect(completely_remove=True)
            self.resultsPlottingDock.close()
            self.iface.removeDockWidget(self.resultsPlottingDock)
            del self.resultsPlottingDock
            self.resultsPlottingDockOpened = False
            if "feedback" in kwargs:
                if not kwargs["feedback"]:
                    return
            if not no_popup:
                QMessageBox.information(
                    self.iface.mainWindow(), "COASTALME", "Completely Closed COASTALME Viewer"
                )
        except:
            if "feedback" in kwargs:
                if not kwargs["feedback"]:
                    return
            if not no_popup:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "COASTALME",
                    "ERROR closing COASTALME Viewer. Please email support@coastalme.com",
                )

    def reloadCmeview(self):
        self.removeCmeview(feedback=False)
        self.openResultsPlottingWindow()

    def addLambdaConnection(self, conn):
        self.lambdaConnections.append(conn)

    def qgisDisconnect(self):
        for conn in self.lambdaConnections:
            try:
                QgsProject.instance().readProject.disconnect(conn)
            except:
                pass
        try:
            self.about_action.triggered.disconnect(self.about_coastalmeqgis)
        except:
            pass
        try:
            self.clearGlobalSettingsAction.triggered.disconnect()
        except:
            pass
        try:
            self.clearProjectSettingsAction.triggered.disconnect()
        except:
            pass
        try:
            self.removeCmeviewAction.triggered.disconnect(self.removeCmeview)
        except:
            pass
        try:
            self.reloadCmeviewAction.triggered.disconnect(self.reloadCmeview)
        except:
            pass
        try:
            self.reload_data_action.triggered.disconnect(self.reload_data)
        except:
            pass
        try:
            self.view_results_action.triggered.disconnect(
                self.openResultsPlottingWindow
            )
        except:
            pass

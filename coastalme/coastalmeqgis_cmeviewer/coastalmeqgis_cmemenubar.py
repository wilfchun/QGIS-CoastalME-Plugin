import os
import webbrowser
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from .coastalmeqgis_cmemenufunctions import CmeMenuFunctions
from ..coastalmeqgis_library import about, goto_plugin_changelog, goto_coastalme_downloads

from matplotlib.backends.backend_qtagg import FigureManagerQT
from matplotlib.backends.qt_editor import figureoptions
from .coastalmeqgis_figure_options import figure_edit, figure_edit_old

mpl_figure_edit = figureoptions.figure_edit

from coastalme.gui.logging import Logging


class CmeMenuBar:
    """
    Class for handling main menu bar.

    """

    def __init__(self, CmeView, **kwargs):
        from ..coastalmeqgis_cmeviewer.coastalmeqgis_cmeplot import CmePlot

        self.cmeView = CmeView
        self.cmePlot = CmeView.cmePlot
        self.iface = CmeView.iface
        self.connected = False

        # Set up menu bar widget
        self.window = QWidget()
        self.vbox = QVBoxLayout()
        self.window.setLayout(self.vbox)
        self.menuBar = QMenuBar()
        self.menuBar.setNativeMenuBar(False)
        self.vbox.addWidget(self.menuBar)
        if "layout" in kwargs:
            layout = kwargs["layout"]
        else:
            layout = self.cmeView.mainMenu
        layout.addWidget(self.window)

        # menu function class
        self.cmeMenuFunctions = CmeMenuFunctions(CmeView)

        self.removeCmeview = kwargs["removeCmeview"] if "removeCmeview" in kwargs else None
        self.reloadCmeview = kwargs["reloadCmeview"] if "reloadCmeview" in kwargs else None
        self.menu = kwargs["menu_bar"] if "menu_bar" in kwargs else None

        self.plotNoToToolbar = self.cmePlot.cmePlotToolbar.plotNoToToolbar

        self.fileMenu_connected = False
        self.viewMenu_connected = False
        self.settingsMenu_connected = False
        self.exportMenu_connected = False
        self.resultMenu_connected = False
        self.helpMenu_connected = False

    def clear(self):
        if self.menu is not None:
            self.menu.clear()

    def __del__(self):
        self.disconnectMenu()
        self.clear()

    def loadFileMenu(self):
        """
        Loads File menu and menu items.

        :return: bool -> True for successful, False for unsuccessful
        """

        self.fileMenu = self.menuBar.addMenu("&File")
        closeResultsIcon = QgsApplication.getThemeIcon("/mActionRemoveLayer.svg")

        # file menu
        if self.menu is None:
            self.load1d2dResults_action = QAction("Load Results", self.window)
            self.load2dResults_action = QAction(
                "Load Results - Map Outputs", self.window
            )
            self.load1dResults_action = QAction(
                "Load Results - Time Series", self.window
            )
            self.loadFMResults_action = QAction(
                "Load Results - Time Series FM", self.window
            )
            self.loadParticlesResults_action = QAction(
                "Load Results - Particles", self.window
            )
            self.loadNcGridResults_action = QAction(
                "Load Results - NetCDF Grid", self.window
            )
            self.loadHydraulicTable_action = QAction(
                "Import 1D Hydraulic Tables", self.window
            )
            self.loadBcTables_action = QAction("Import BC Tables", self.window)
            self.remove1d2dResults_action = QAction(
                closeResultsIcon, "Close Results", self.window
            )
            self.remove2dResults_action = QAction(
                "Close Results - Map Outputs", self.window
            )
            self.remove1dResults_action = QAction(
                "Close Results - Time Series", self.window
            )
            self.removeParticlesResults_action = QAction(
                "Close Results - Particles", self.window
            )
            self.closeHydraulicTable_action = QAction(
                "Close 1D Hydraulic Tables", self.window
            )
            self.loadFVBCTide_action = QAction("Import FV Tide BC NetCDF", self.window)
            self.fileMenu.addAction(self.load1d2dResults_action)
            self.fileMenu.addAction(self.load2dResults_action)
            self.fileMenu.addAction(self.load1dResults_action)
            self.fileMenu.addAction(self.loadFMResults_action)
            self.fileMenu.addAction(self.loadParticlesResults_action)
            self.fileMenu.addAction(self.loadNcGridResults_action)
            self.fileMenu.addAction(self.loadHydraulicTable_action)
            self.fileMenu.addAction(self.loadBcTables_action)
            self.fileMenu.addAction(self.loadFVBCTide_action)
            self.fileMenu.addSeparator()
            self.fileMenu.addAction(self.remove1d2dResults_action)
            self.fileMenu.addAction(self.remove2dResults_action)
            self.fileMenu.addAction(self.remove1dResults_action)
            self.fileMenu.addAction(self.removeParticlesResults_action)
            self.fileMenu.addAction(self.closeHydraulicTable_action)
            self.fileMenu.addSeparator()
            if self.removeCmeview is not None:
                self.fileMenu.addAction(self.removeCmeview)
            if self.reloadCmeview is not None:
                self.fileMenu.addAction(self.reloadCmeview)

            self.load2dResults_action.triggered.connect(
                self.cmeMenuFunctions.load2dResults
            )
            self.load1dResults_action.triggered.connect(
                self.cmeMenuFunctions.load1dResults
            )
            self.loadFMResults_action.triggered.connect(
                self.cmeMenuFunctions.loadFMResults
            )
            self.loadParticlesResults_action.triggered.connect(
                self.cmeMenuFunctions.loadParticlesResults
            )
            self.loadNcGridResults_action.triggered.connect(
                self.cmeMenuFunctions.loadNcGridResults
            )
            self.load1d2dResults_action.triggered.connect(
                self.cmeMenuFunctions.load1d2dResults
            )
            self.loadHydraulicTable_action.triggered.connect(
                self.cmeMenuFunctions.loadHydraulicTables
            )
            self.loadBcTables_action.triggered.connect(
                self.cmeMenuFunctions.loadBcTables
            )
            self.remove1d2dResults_action.triggered.connect(
                self.cmeMenuFunctions.remove1d2dResults
            )
            self.remove2dResults_action.triggered.connect(
                self.cmeMenuFunctions.remove2dResults
            )
            self.remove1dResults_action.triggered.connect(
                self.cmeMenuFunctions.remove1dResults
            )
            self.removeParticlesResults_action.triggered.connect(
                self.cmeMenuFunctions.removeParticlesResults
            )
            self.closeHydraulicTable_action.triggered.connect(
                self.cmeMenuFunctions.removeHydraulicTables
            )
            self.loadFVBCTide_action.triggered.connect(
                self.cmeMenuFunctions.loadFVBCTide
            )
        else:
            self.fileMenu.addAction(self.menu.load1d2dResults_action)
            self.fileMenu.addAction(self.menu.load2dResults_action)
            self.fileMenu.addAction(self.menu.load1dResults_action)
            self.fileMenu.addAction(self.menu.loadFMResults_action)
            self.fileMenu.addAction(self.menu.loadParticlesResults_action)
            self.fileMenu.addAction(self.menu.loadNcGridResults_action)
            self.fileMenu.addAction(self.menu.loadHydraulicTable_action)
            self.fileMenu.addAction(self.menu.loadBcTables_action)
            self.fileMenu.addAction(self.menu.loadFVBCTide_action)
            self.fileMenu.addSeparator()
            self.fileMenu.addAction(self.menu.remove1d2dResults_action)
            self.fileMenu.addAction(self.menu.remove2dResults_action)
            self.fileMenu.addAction(self.menu.remove1dResults_action)
            self.fileMenu.addAction(self.menu.removeParticlesResults_action)
            self.fileMenu.addSeparator()
            if self.removeCmeview is not None:
                self.fileMenu.addAction(self.removeCmeview)
            if self.reloadCmeview is not None:
                self.fileMenu.addAction(self.reloadCmeview)

    def loadViewMenu(self, plotNo, **kwargs):
        """
        Loads View menu and menu items

        :param plotNo: int enumerator -> 0: time series plot
                                                                         1: long profile plot
                                                                         2: cross section plot
        :param kwargs: dict -> key word arguments
        :return: bool -> True for successful, False for unsuccessful
        """

        from .coastalmeqgis_cmeplot import CmePlot

        update = kwargs["update"] if "update" in kwargs.keys() else False

        # if plotNo == 0:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsTimeSeries
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarTimeSeries
        # elif plotNo == 1:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarLongPlot
        # elif plotNo == 2:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarCrossSection

        toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]

        if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
            self.viewMenu = self.menuBar.addMenu("&View")
        iconRefresh = QgsApplication.getThemeIcon("/mActionRefresh.svg")
        iconRefreshPlot = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "icons",
                "refreshplotblack.png",
            )
        )
        iconClearPlot = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "icons", "ClearPlot.png"
            )
        )

        if self.menu is None:
            # view menu items
            self.freezeAxisLimits_action = (
                viewToolbar.freezeXYAxisButton.defaultAction()
            )
            self.freezeAxisXLimits_action = (
                viewToolbar.freezeXAxisButton.defaultAction()
            )
            self.freezeAxisYLimits_action = (
                viewToolbar.freezeYAxisButton.defaultAction()
            )
            self.freezeAxisLabels_action = QAction("Freeze Axis Labels", self.window)
            self.freezeAxisLabels_action.setCheckable(True)
            self.refreshMapWindow_action = QAction(
                iconRefresh, "Refresh Map Window", self.window
            )
            self.refreshCurrentPlotWindow_action = QAction(
                iconRefreshPlot, "Refresh Plot Window - Current", self.window
            )
            self.refreshAllPlotWindows_action = QAction(
                iconRefreshPlot, "Refresh Plot Window - All", self.window
            )
            self.clearPlotWindow_action = QAction(
                iconClearPlot, "Clear Plot Window - Current", self.window
            )
            self.clearAllPlotWindows_action = QAction(
                iconClearPlot, "Clear Plot Window - All", self.window
            )
            self.viewMenu.addAction(toolbar[0])
            self.viewMenu.addAction(toolbar[1])
            self.viewMenu.addAction(toolbar[2])
            self.viewMenu.addAction(toolbar[4])
            self.viewMenu.addAction(toolbar[5])
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.freezeAxisLimits_action)
            self.viewMenu.addAction(self.freezeAxisXLimits_action)
            self.viewMenu.addAction(self.freezeAxisYLimits_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.refreshMapWindow_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.refreshCurrentPlotWindow_action)
            self.viewMenu.addAction(self.refreshAllPlotWindows_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.clearPlotWindow_action)
            self.viewMenu.addAction(self.clearAllPlotWindows_action)

            self.freezeAxisLimits_action.triggered.connect(viewToolbar.freezeXYAxis)
            self.freezeAxisXLimits_action.triggered.connect(viewToolbar.freezeXAxis)
            self.freezeAxisYLimits_action.triggered.connect(viewToolbar.freezeYAxis)
            self.refreshMapWindow_action.triggered.connect(self.cmeView.renderMap)
            self.refreshCurrentPlotWindow_action.triggered.connect(
                self.cmeView.refreshCurrentPlot
            )
            self.refreshAllPlotWindows_action.triggered.connect(
                self.cmeView.cmePlot.updateAllPlots
            )
            # self.clearPlotWindow_action.triggered.connect(
            # lambda: self.cmeView.cmePlot.clearPlot(self.cmeView.tabWidget.currentIndex(), clear_rubberband=True,
            # clear_selection=True))
            self.clearPlotWindow_action.triggered.connect(
                lambda: self.cmeView.cmePlot.clearPlot2(
                    self.cmeView.tabWidget.currentIndex()
                )
            )
            self.clearAllPlotWindows_action.triggered.connect(
                self.cmeView.cmePlot.clearAllPlots
            )
        else:
            self.viewMenu.addAction(toolbar[0])
            self.viewMenu.addAction(toolbar[1])
            self.viewMenu.addAction(toolbar[2])
            self.viewMenu.addAction(toolbar[4])
            self.viewMenu.addAction(toolbar[5])
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.menu.freezeAxisLimits_action)
            self.viewMenu.addAction(self.menu.freezeAxisXLimits_action)
            self.viewMenu.addAction(self.menu.freezeAxisYLimits_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.menu.refreshMapWindow_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.menu.refreshCurrentPlotWindow_action)
            self.viewMenu.addAction(self.menu.refreshAllPlotWindows_action)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction(self.menu.clearPlotWindow_action)
            self.viewMenu.addAction(self.menu.clearAllPlotWindows_action)

        return True

    def loadSettingsMenu(self, plotNo, **kwargs):
        """
        Loads Edit menu and menu items.

        :param plotNo: int enumerator -> 0: time series plot
                                                                         1: long profile plot
                                                                         2: cross section plot
        :param kwargs: dict -> key word arguments
        :return: bool -> True for successful, False for unsuccessful
        """

        update = kwargs["update"] if "update" in kwargs.keys() else False

        # if plotNo == 0:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsTimeSeries
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarTimeSeries
        # elif plotNo == 1:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarLongPlot
        # elif plotNo == 2:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection
        # 	viewToolbar = self.cmeView.cmePlot.cmePlotToolbar.viewToolbarCrossSection

        toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]

        if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
            self.settingsMenu = self.menuBar.addMenu("&Settings")
        iconOptions = QgsApplication.getThemeIcon("/mActionOptions.svg")
        iconScalar = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "icons", "icon_contours.png"
            )
        )
        iconVector = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "iconsicon_vectors.png"
            )
        )

        if self.menu is None:
            # settings menu items
            self.userPlotDataManager_action = (
                viewToolbar.userPlotDataManagerButton.defaultAction()
            )
            self.saveColorRampForActiveResult_action = QAction(
                iconScalar, "Save Chosen Color Ramp", self.window
            )
            self.saveColorMapForActiveResult_action = QAction(
                iconScalar, "Save Color Map (Exact Values and Colours)", self.window
            )
            self.saveStyleForVectorResult_action = QAction(
                iconVector, "Save Vector Layer Style as Default", self.window
            )
            self.loadStyleForActiveResult_action = QAction(
                iconScalar, "Reload Default Style for Active Layer", self.window
            )
            self.loadStyleForVectorResult_action = QAction(
                iconVector, "Reload Default Style for VectorLayer", self.window
            )
            self.resetDefaultStyles_action = QAction(
                "Reset Default Styles", self.window
            )
            self.options_action = QAction(iconOptions, "Options", self.window)
            self.addPlotColourRamp_action = QAction(
                "Add Colour Ramp to Plot", self.window
            )
            self.resetPlotColours_action = QAction(
                "Reset Plotting Colours", self.window
            )
            self.resetAxisNames_action = QAction("Reset Plot Axis Names", self.window)
            self.dockCmeflowViewer_action = QAction("Redock COASTALME Viewer", self.window)
            self.settingsMenu.addAction(self.userPlotDataManager_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(toolbar[7])
            self.settingsMenu.addSeparator()
            self.saveStyleMenu = self.settingsMenu.addMenu(
                "Save Active Layer Style as Default for Result Type"
            )
            self.saveStyleMenu.addAction(self.saveColorRampForActiveResult_action)
            self.saveStyleMenu.addAction(self.saveColorMapForActiveResult_action)
            self.settingsMenu.addAction(self.saveStyleForVectorResult_action)
            self.settingsMenu.addAction(self.loadStyleForActiveResult_action)
            self.settingsMenu.addAction(self.loadStyleForVectorResult_action)
            self.settingsMenu.addAction(self.resetDefaultStyles_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.addPlotColourRamp_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.resetPlotColours_action)
            self.settingsMenu.addAction(self.resetAxisNames_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.dockCmeflowViewer_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.options_action)

            # self.userPlotDataManager_action.triggered.connect(self.cmeMenuFunctions.openUserPlotDataManager)
            if not self.viewMenu_connected:
                figureoptions.figure_edit = self.custom_figure_edit
                # self.cmeView.cmePlot.cmePlotToolbar.lstActionsTimeSeries[7].triggered.connect(self.cmeMenuFunctions.updateLegend)
                # self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot[7].triggered.connect(self.cmeMenuFunctions.updateLegend)
                # self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection[7].triggered.connect(self.cmeMenuFunctions.updateLegend)
                # self.cmeView.cmePlot.cmePlotToolbar.lstActionsVerticalProfile[7].triggered.connect(self.cmeMenuFunctions.updateLegend)
                self.viewMenu_connected = True

            self.saveColorRampForActiveResult_action.triggered.connect(
                lambda: self.cmeMenuFunctions.saveDefaultStyleScalar("color ramp")
            )
            self.saveColorMapForActiveResult_action.triggered.connect(
                lambda: self.cmeMenuFunctions.saveDefaultStyleScalar("color map")
            )
            self.saveStyleForVectorResult_action.triggered.connect(
                self.cmeMenuFunctions.saveDefaultStyleVector
            )
            self.loadStyleForActiveResult_action.triggered.connect(
                self.cmeMenuFunctions.loadDefaultStyleScalar
            )
            self.loadStyleForVectorResult_action.triggered.connect(
                self.cmeMenuFunctions.loadDefaultStyleVector
            )
            self.resetDefaultStyles_action.triggered.connect(
                self.cmeMenuFunctions.resetDefaultStyles
            )
            self.options_action.triggered.connect(self.cmeMenuFunctions.options)
            self.addPlotColourRamp_action.triggered.connect(
                self.cmeMenuFunctions.addColourRampFromXML
            )
            self.resetPlotColours_action.triggered.connect(
                self.cmeMenuFunctions.resetMatplotColours
            )
            self.resetAxisNames_action.triggered.connect(
                self.cmeMenuFunctions.resetPlotAxisNames
            )
            self.dockCmeflowViewer_action.triggered.connect(
                self.cmeMenuFunctions.redockCmeflowViewer
            )
        else:
            self.settingsMenu.addAction(self.menu.userPlotDataManager_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(toolbar[7])
            self.settingsMenu.addSeparator()
            self.saveStyleMenu = self.settingsMenu.addMenu(
                "Save Active Layer Style as Default for Result Type"
            )
            self.saveStyleMenu.addAction(self.menu.saveColorRampForActiveResult_action)
            self.saveStyleMenu.addAction(self.menu.saveColorMapForActiveResult_action)
            self.settingsMenu.addAction(self.menu.saveStyleForVectorResult_action)
            self.settingsMenu.addAction(self.menu.loadStyleForActiveResult_action)
            self.settingsMenu.addAction(self.menu.loadStyleForVectorResult_action)
            self.settingsMenu.addAction(self.menu.resetDefaultStyles_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.menu.addPlotColourRamp_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.menu.resetPlotColours_action)
            self.settingsMenu.addAction(self.menu.resetAxisNames_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.menu.dockCmeflowViewer_action)
            self.settingsMenu.addSeparator()
            self.settingsMenu.addAction(self.menu.options_action)

        return True

    def custom_figure_edit(self, ax, parent=None):
        idx = self.cmeView.tabWidget.currentIndex()
        cur_ax = self.cmePlot.plotEnumerator(idx)[2] if idx >= 0 else None
        if ax != cur_ax:
            return mpl_figure_edit(ax, parent)
        try:
            dialog = figure_edit(ax, parent, incl_title=False)
        except:
            dialog = figure_edit_old(ax, parent, incl_title=False)
        if isinstance(dialog, QDialog):
            dialog.accepted.connect(self.cmeMenuFunctions.updateLegend)
            dialog.show()

    def loadExportMenu(self, plotNo, **kwargs):
        """
        Load Export menu and menu items

        :param plotNo: int enumerator -> 0: time series plot
                                                                         1: long profile plot
                                                                         2: cross section plot
        :param kwargs: dict -> key word arguments
        :return: bool -> True for successful, False for unsuccessful
        """

        update = kwargs["update"] if "update" in kwargs.keys() else False

        # if plotNo == 0:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsTimeSeries
        # elif plotNo == 1:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot
        # elif plotNo == 2:
        # 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection

        toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]

        if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
            self.exportMenu = self.menuBar.addMenu("&Export")
        lineFeatureIcon = QgsApplication.getThemeIcon("/mActionMoveFeatureLine.svg")
        pointFeatureIcon = QgsApplication.getThemeIcon("/mActionMoveFeaturePoint.svg")
        iconAnimation = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "icons", "icon_video.png"
            )
        )

        if self.menu is None:
            # export menu items
            self.exportAsCSV_action = QAction("Export Plot As CSV", self.window)
            self.autoPlotExport_action = QAction(
                "Batch Plot and Export Features in Shape File", self.window
            )
            self.exportDataToClipboard_action = QAction(
                "Copy Data to Clipboard", self.window
            )
            self.exportImageToClipboard_action = QAction(
                "Copy Image to Clipboard", self.window
            )
            self.exportTempLine_action = QAction(
                lineFeatureIcon, "Export Temporary Line(s) to SHP", self.window
            )
            self.exportTempPoint_action = QAction(
                pointFeatureIcon, "Export Temporary Point(s) to SHP", self.window
            )
            self.exportAnimation_action = QAction(
                iconAnimation, "Export Animation", self.window
            )
            self.exportMaps_action = QAction("Export Maps (beta)", self.window)
            self.exportMenu.addAction(toolbar[9])
            self.exportMenu.addAction(self.exportAsCSV_action)
            self.exportMenu.addAction(self.autoPlotExport_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.exportDataToClipboard_action)
            self.exportMenu.addAction(self.exportImageToClipboard_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.exportTempLine_action)
            self.exportMenu.addAction(self.exportTempPoint_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.exportAnimation_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.exportMaps_action)

            self.exportAsCSV_action.triggered.connect(self.cmeMenuFunctions.exportCSV)
            self.autoPlotExport_action.triggered.connect(
                self.cmeMenuFunctions.batchPlotExportInitialise
            )
            self.exportDataToClipboard_action.triggered.connect(
                self.cmeMenuFunctions.exportDataToClipboard
            )
            self.exportImageToClipboard_action.triggered.connect(
                self.cmeMenuFunctions.exportImageToClipboard
            )
            self.exportTempLine_action.triggered.connect(
                self.cmeMenuFunctions.exportTempLines
            )
            self.exportTempPoint_action.triggered.connect(
                self.cmeMenuFunctions.exportTempPoints
            )
            self.exportAnimation_action.triggered.connect(
                self.cmeMenuFunctions.exportAnimation
            )
            self.exportMaps_action.triggered.connect(self.cmeMenuFunctions.exportMaps)
        else:
            self.exportMenu.addAction(toolbar[9])
            self.exportMenu.addAction(self.menu.exportAsCSV_action)
            self.exportMenu.addAction(self.menu.autoPlotExport_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.menu.exportDataToClipboard_action)
            self.exportMenu.addAction(self.menu.exportImageToClipboard_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.menu.exportTempLine_action)
            self.exportMenu.addAction(self.menu.exportTempPoint_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.menu.exportAnimation_action)
            self.exportMenu.addSeparator()
            self.exportMenu.addAction(self.menu.exportMaps_action)

        return True

    def loadResultsMenu(self):
        """
        Load ARR2016 menu and menu items.

        :return: bool -> True for successful, False for unsuccessful
        """

        resultsMenu = self.menuBar.addMenu("&Results")

        if self.menu is None:
            # ARR2016 menu items
            self.showSelectedElements_action = QAction(
                "Show Selected Element Names", self.window
            )
            self.showMedianEvent_action = QAction("Show Median Event", self.window)
            self.showMedianEvent_action.setCheckable(True)
            self.showMeanEvent_action = QAction("Show Mean Event", self.window)
            self.showMeanEvent_action.setCheckable(True)
            resultsMenu.addAction(self.showSelectedElements_action)
            resultsMenu.addSeparator()
            arrMenu = resultsMenu.addMenu("&ARR2019")
            arrMenu.addAction(self.showMedianEvent_action)
            arrMenu.addAction(self.showMeanEvent_action)

            self.showSelectedElements_action.triggered.connect(
                self.cmeMenuFunctions.showSelectedElements
            )
            self.showMedianEvent_action.triggered.connect(
                self.cmeMenuFunctions.showMedianEvent
            )
            self.showMeanEvent_action.triggered.connect(
                self.cmeMenuFunctions.showMeanEvent
            )
        else:
            resultsMenu.addAction(self.menu.showSelectedElements_action)
            resultsMenu.addSeparator()
            arrMenu = resultsMenu.addMenu("&ARR2019")
            arrMenu.addAction(self.menu.showMedianEvent_action)
            arrMenu.addAction(self.menu.showMeanEvent_action)

        return True

    def loadHelpMenu(self):
        """
        Load Help menu and menu items.

        :return: bool -> True for successful, False for unsuccessful
        """

        helpMenu = self.menuBar.addMenu("&Help")
        helpIcon = QgsApplication.getThemeIcon("/mActionHelpContents.svg")
        aboutIcon = QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "icons", "cmeview.png"
            )
        )

        if self.menu is None:
            # Help Menu
            self.help_action = QAction(helpIcon, "Help", self.window)
            self.about_action = QAction(aboutIcon, "About", self.window)
            self.changelog_action = QAction("Plugin Changelog", self.window)
            self.coastalme_downloads_page_action = QAction("COASTALME Downloads", self.window)
            helpMenu.addAction(self.help_action)
            helpMenu.addAction(self.changelog_action)
            helpMenu.addSeparator()
            helpMenu.addAction(self.about_action)
            helpMenu.addSeparator()
            helpMenu.addAction(self.coastalme_downloads_page_action)

            self.about_action.triggered.connect(self.about)
            self.help_action.triggered.connect(self.help)
            self.changelog_action.triggered.connect(goto_plugin_changelog)
            self.coastalme_downloads_page_action.triggered.connect(goto_coastalme_downloads)
        else:
            helpMenu.addAction(self.menu.help_action)
            helpMenu.addAction(self.menu.changelog_action)
            helpMenu.addSeparator()
            helpMenu.addAction(self.menu.about_action)
            helpMenu.addSeparator()
            helpMenu.addAction(self.menu.coastalme_downloads_page_action)

    def about(self):
        """

        :return:
        """

        about(self.cmeView)

    def help(self):
        """

        :return:
        """

        url = r"https://wiki.coastalme.com/index.php?title=COASTALME_Viewer"
        webbrowser.open(url)

    def qgisDisconnect(self):
        # file menu
        try:
            self.load2dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.load2dResults
            )
        except:
            pass
        try:
            self.load1dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.load1dResults
            )
        except:
            pass
        try:
            self.loadParticlesResults_action.triggered.disconnect(
                self.cmeMenuFunctions.loadParticlesResults
            )
        except:
            pass
        try:
            self.load1d2dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.load1d2dResults
            )
        except:
            pass
        try:
            self.loadHydraulicTable_action.triggered.disconnect(
                self.cmeMenuFunctions.loadHydraulicTables
            )
        except:
            pass
        try:
            self.remove1d2dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.remove1d2dResults
            )
        except:
            pass
        try:
            self.remove2dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.remove2dResults
            )
        except:
            pass
        try:
            self.remove1dResults_action.triggered.disconnect(
                self.cmeMenuFunctions.remove1dResults
            )
        except:
            pass
        try:
            self.removeParticlesResults_action.triggered.disconnect(
                self.cmeMenuFunctions.removeParticlesResults
            )
        except:
            pass
        try:
            self.closeHydraulicTable_action.triggered.disconnect(
                self.cmeMenuFunctions.removeHydraulicTables
            )
        except:
            pass
        # view menu
        for plotNo in range(self.cmeView.cmePlot.TotalPlotNo):
            toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
            try:
                self.freezeAxisLimits_action.triggered.disconnect(
                    viewToolbar.freezeXYAxis
                )
            except:
                pass
            try:
                self.freezeAxisXLimits_action.triggered.disconnect(
                    viewToolbar.freezeXAxis
                )
            except:
                pass
            try:
                self.freezeAxisYLimits_action.triggered.disconnect(
                    viewToolbar.freezeYAxis
                )
            except:
                pass
            try:
                self.refreshMapWindow_action.triggered.disconnect(self.cmeView.renderMap)
            except:
                pass
            try:
                self.refreshCurrentPlotWindow_action.triggered.disconnect(
                    self.cmeView.refreshCurrentPlot
                )
            except:
                pass
            try:
                self.refreshAllPlotWindows_action.triggered.disconnect(
                    self.cmeView.cmePlot.updateAllPlots
                )
            except:
                pass
            try:
                self.clearPlotWindow_action.triggered.disconnect()
            except:
                pass
            try:
                self.clearAllPlotWindows_action.triggered.disconnect(
                    self.cmeView.cmePlot.clearAllPlots
                )
            except:
                pass
        # settings menu
        try:
            self.cmeView.cmePlot.cmePlotToolbar.lstActionsTimeSeries[
                7
            ].triggered.disconnect(self.cmeMenuFunctions.updateLegend)
        except:
            pass
        try:
            self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot[7].triggered.disconnect(
                self.cmeMenuFunctions.updateLegend
            )
        except:
            pass
        try:
            self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection[
                7
            ].triggered.disconnect(self.cmeMenuFunctions.updateLegend)
        except:
            pass
        try:
            self.cmeView.cmePlot.cmePlotToolbar.lstActionsVerticalProfile[
                7
            ].triggered.disconnect(self.cmeMenuFunctions.updateLegend)
        except:
            pass
        try:
            self.saveColorRampForActiveResult_action.triggered.disconnect()
        except:
            pass
        try:
            self.saveColorMapForActiveResult_action.triggered.disconnect()
        except:
            pass
        try:
            self.saveStyleForVectorResult_action.triggered.disconnect(
                self.cmeMenuFunctions.saveDefaultStyleVector
            )
        except:
            pass
        try:
            self.loadStyleForActiveResult_action.triggered.disconnect(
                self.cmeMenuFunctions.loadDefaultStyleScalar
            )
        except:
            pass
        try:
            self.loadStyleForVectorResult_action.triggered.disconnect(
                self.cmeMenuFunctions.loadDefaultStyleVector
            )
        except:
            pass
        try:
            self.resetDefaultStyles_action.triggered.disconnect(
                self.cmeMenuFunctions.resetDefaultStyles
            )
        except:
            pass
        try:
            self.options_action.triggered.disconnect(self.cmeMenuFunctions.options)
        except:
            pass
        try:
            self.addPlotColourRamp_action.triggered.disconnect(
                self.cmeMenuFunctions.addColourRampFromXML
            )
        except:
            pass
        try:
            self.resetPlotColours_action.triggered.disconnect(
                self.cmeMenuFunctions.resetMatplotColours
            )
        except:
            pass
        # export menu
        try:
            self.exportAsCSV_action.triggered.disconnect(self.cmeMenuFunctions.exportCSV)
        except:
            pass
        try:
            self.autoPlotExport_action.triggered.disconnect(
                self.cmeMenuFunctions.batchPlotExportInitialise
            )
        except:
            pass
        try:
            self.exportDataToClipboard_action.triggered.disconnect(
                self.cmeMenuFunctions.exportDataToClipboard
            )
        except:
            pass
        try:
            self.exportImageToClipboard_action.triggered.disconnect(
                self.cmeMenuFunctions.exportImageToClipboard
            )
        except:
            pass
        try:
            self.exportTempLine_action.triggered.disconnect(
                self.cmeMenuFunctions.exportTempLines
            )
        except:
            pass
        try:
            self.exportTempPoint_action.triggered.disconnect(
                self.cmeMenuFunctions.exportTempPoints
            )
        except:
            pass
        try:
            self.exportAnimation_action.triggered.disconnect(
                self.cmeMenuFunctions.exportAnimation
            )
        except:
            pass
        try:
            self.exportMaps_action.triggered.disconnect(self.cmeMenuFunctions.exportMaps)
        except:
            pass
        # result menu
        try:
            self.showSelectedElements_action.triggered.disconnect(
                self.cmeMenuFunctions.showSelectedElements
            )
        except:
            pass
        try:
            self.showMedianEvent_action.triggered.disconnect(
                self.cmeMenuFunctions.showMedianEvent
            )
        except:
            pass
        try:
            self.showMeanEvent_action.triggered.disconnect(
                self.cmeMenuFunctions.showMeanEvent
            )
        except:
            pass
        # help menu
        try:
            self.about_action.triggered.disconnect(self.about)
        except:
            pass
        try:
            self.help_action.triggered.disconnect(self.help)
        except:
            pass


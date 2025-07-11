import os
import webbrowser
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from .coastalmeqgis_tumenufunctions import TuMenuFunctions
from ..coastalmeqgis_library import about, goto_plugin_changelog, goto_coastalme_downloads


class TuMenuBar():
	"""
	Class for handling main menu bar.
	
	"""
	
	def __init__(self, TuView, **kwargs):
		from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot import TuPlot

		self.tuView = TuView
		self.tuPlot = TuView.tuPlot
		self.iface = TuView.iface
		self.connected = False
		
		# Set up menu bar widget
		self.window = QWidget()
		self.vbox = QVBoxLayout()
		self.window.setLayout(self.vbox)
		self.menuBar = QMenuBar()
		self.vbox.addWidget(self.menuBar)
		if "layout" in kwargs:
			layout = kwargs['layout']
		else:
			layout = self.tuView.mainMenu
		layout.addWidget(self.window)

		# menu function class
		self.tuMenuFunctions =  TuMenuFunctions(TuView)
		
		self.removeTuview = kwargs['removeTuview'] if 'removeTuview' in kwargs else None
		self.reloadTuview = kwargs['reloadTuview'] if 'reloadTuview' in kwargs else None
		self.menu = kwargs['menu_bar'] if 'menu_bar' in kwargs else None

		self.plotNoToToolbar = self.tuPlot.tuPlotToolbar.plotNoToToolbar

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
		
		self.fileMenu = self.menuBar.addMenu('&File')
		closeResultsIcon = QgsApplication.getThemeIcon("/mActionRemoveLayer.svg")
		
		# file menu
		if self.menu is None:
			self.load1d2dResults_action = QAction('Load Results', self.window)
			self.load2dResults_action = QAction('Load Results - Map Outputs', self.window)
			self.load1dResults_action = QAction('Load Results - Time Series', self.window)
			self.loadFMResults_action = QAction('Load Results - Time Series FM', self.window)
			self.loadParticlesResults_action = QAction('Load Results - Particles', self.window)
			self.loadNcGridResults_action = QAction('Load Results - NetCDF Grid', self.window)
			self.loadHydraulicTable_action = QAction("Import 1D Hydraulic Tables", self.window)
			self.loadBcTables_action = QAction('Import BC Tables', self.window)
			self.remove1d2dResults_action = QAction(closeResultsIcon, 'Close Results', self.window)
			self.remove2dResults_action = QAction('Close Results - Map Outputs', self.window)
			self.remove1dResults_action = QAction('Close Results - Time Series', self.window)
			self.removeParticlesResults_action = QAction('Close Results - Particles', self.window)
			self.closeHydraulicTable_action = QAction("Close 1D Hydraulic Tables", self.window)
			self.loadFVBCTide_action = QAction('Import FV Tide BC NetCDF', self.window)
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
			if self.removeTuview is not None:
				self.fileMenu.addAction(self.removeTuview)
			if self.reloadTuview is not None:
				self.fileMenu.addAction(self.reloadTuview)

			self.load2dResults_action.triggered.connect(self.tuMenuFunctions.load2dResults)
			self.load1dResults_action.triggered.connect(self.tuMenuFunctions.load1dResults)
			self.loadFMResults_action.triggered.connect(self.tuMenuFunctions.loadFMResults)
			self.loadParticlesResults_action.triggered.connect(self.tuMenuFunctions.loadParticlesResults)
			self.loadNcGridResults_action.triggered.connect(self.tuMenuFunctions.loadNcGridResults)
			self.load1d2dResults_action.triggered.connect(self.tuMenuFunctions.load1d2dResults)
			self.loadHydraulicTable_action.triggered.connect(self.tuMenuFunctions.loadHydraulicTables)
			self.loadBcTables_action.triggered.connect(self.tuMenuFunctions.loadBcTables)
			self.remove1d2dResults_action.triggered.connect(self.tuMenuFunctions.remove1d2dResults)
			self.remove2dResults_action.triggered.connect(self.tuMenuFunctions.remove2dResults)
			self.remove1dResults_action.triggered.connect(self.tuMenuFunctions.remove1dResults)
			self.removeParticlesResults_action.triggered.connect(self.tuMenuFunctions.removeParticlesResults)
			self.closeHydraulicTable_action.triggered.connect(self.tuMenuFunctions.removeHydraulicTables)
			self.loadFVBCTide_action.triggered.connect(self.tuMenuFunctions.loadFVBCTide)
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
			if self.removeTuview is not None:
				self.fileMenu.addAction(self.removeTuview)
			if self.reloadTuview is not None:
				self.fileMenu.addAction(self.reloadTuview)
		
	def loadViewMenu(self, plotNo, **kwargs):
		"""
		Loads View menu and menu items
		
		:param plotNo: int enumerator -> 0: time series plot
										 1: long profile plot
										 2: cross section plot
		:param kwargs: dict -> key word arguments
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_tuplot import TuPlot
		
		update = kwargs['update'] if 'update' in kwargs.keys() else False
		
		# if plotNo == 0:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsTimeSeries
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarTimeSeries
		# elif plotNo == 1:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsLongPlot
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarLongPlot
		# elif plotNo == 2:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsCrossSection
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarCrossSection

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
		
		if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
			self.viewMenu = self.menuBar.addMenu('&View')
		iconRefresh = QgsApplication.getThemeIcon("/mActionRefresh.svg")
		iconRefreshPlot = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "refreshplotblack.png"))
		iconClearPlot = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "ClearPlot.png"))

		if self.menu is None:
			# view menu items
			self.freezeAxisLimits_action = viewToolbar.freezeXYAxisButton.defaultAction()
			self.freezeAxisXLimits_action = viewToolbar.freezeXAxisButton.defaultAction()
			self.freezeAxisYLimits_action = viewToolbar.freezeYAxisButton.defaultAction()
			self.freezeAxisLabels_action = QAction('Freeze Axis Labels', self.window)
			self.freezeAxisLabels_action.setCheckable(True)
			self.refreshMapWindow_action = QAction(iconRefresh, 'Refresh Map Window', self.window)
			self.refreshCurrentPlotWindow_action = QAction(iconRefreshPlot, 'Refresh Plot Window - Current', self.window)
			self.refreshAllPlotWindows_action = QAction(iconRefreshPlot, 'Refresh Plot Window - All', self.window)
			self.clearPlotWindow_action = QAction(iconClearPlot, 'Clear Plot Window - Current', self.window)
			self.clearAllPlotWindows_action = QAction(iconClearPlot, 'Clear Plot Window - All', self.window)
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
			self.refreshMapWindow_action.triggered.connect(self.tuView.renderMap)
			self.refreshCurrentPlotWindow_action.triggered.connect(self.tuView.refreshCurrentPlot)
			self.refreshAllPlotWindows_action.triggered.connect(self.tuView.tuPlot.updateAllPlots)
			#self.clearPlotWindow_action.triggered.connect(
			#	lambda: self.tuView.tuPlot.clearPlot(self.tuView.tabWidget.currentIndex(), clear_rubberband=True,
			#	                                     clear_selection=True))
			self.clearPlotWindow_action.triggered.connect(
				lambda: self.tuView.tuPlot.clearPlot2(self.tuView.tabWidget.currentIndex()))
			self.clearAllPlotWindows_action.triggered.connect(self.tuView.tuPlot.clearAllPlots)
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

		update = kwargs['update'] if 'update' in kwargs.keys() else False
		
		# if plotNo == 0:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsTimeSeries
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarTimeSeries
		# elif plotNo == 1:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsLongPlot
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarLongPlot
		# elif plotNo == 2:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsCrossSection
		# 	viewToolbar = self.tuView.tuPlot.tuPlotToolbar.viewToolbarCrossSection

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
			
		if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
			self.settingsMenu = self.menuBar.addMenu('&Settings')
		iconOptions = QgsApplication.getThemeIcon("/mActionOptions.svg")
		iconScalar = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "icon_contours.png"))
		iconVector = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons" "icon_vectors.png"))

		if self.menu is None:
			# settings menu items
			self.userPlotDataManager_action = viewToolbar.userPlotDataManagerButton.defaultAction()
			self.saveColorRampForActiveResult_action = QAction(iconScalar, 'Save Chosen Color Ramp', self.window)
			self.saveColorMapForActiveResult_action = QAction(iconScalar, 'Save Color Map (Exact Values and Colours)', self.window)
			self.saveStyleForVectorResult_action = QAction(iconVector, 'Save Vector Layer Style as Default', self.window)
			self.loadStyleForActiveResult_action = QAction(iconScalar, 'Reload Default Style for Active Layer', self.window)
			self.loadStyleForVectorResult_action = QAction(iconVector, 'Reload Default Style for VectorLayer', self.window)
			self.resetDefaultStyles_action = QAction('Reset Default Styles', self.window)
			self.options_action = QAction(iconOptions, 'Options', self.window)
			self.addPlotColourRamp_action = QAction("Add Colour Ramp to Plot", self.window)
			self.resetPlotColours_action = QAction("Reset Plotting Colours", self.window)
			self.resetAxisNames_action = QAction("Reset Plot Axis Names", self.window)
			self.dockTuflowViewer_action = QAction('Redock COASTALME Viewer', self.window)
			self.settingsMenu.addAction(self.userPlotDataManager_action)
			self.settingsMenu.addSeparator()
			self.settingsMenu.addAction(toolbar[7])
			self.settingsMenu.addSeparator()
			self.saveStyleMenu = self.settingsMenu.addMenu('Save Active Layer Style as Default for Result Type')
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
			self.settingsMenu.addAction(self.dockTuflowViewer_action)
			self.settingsMenu.addSeparator()
			self.settingsMenu.addAction(self.options_action)

			#self.userPlotDataManager_action.triggered.connect(self.tuMenuFunctions.openUserPlotDataManager)
			if not self.viewMenu_connected:
				self.tuView.tuPlot.tuPlotToolbar.lstActionsTimeSeries[7].triggered.connect(self.tuMenuFunctions.updateLegend)
				self.tuView.tuPlot.tuPlotToolbar.lstActionsLongPlot[7].triggered.connect(self.tuMenuFunctions.updateLegend)
				self.tuView.tuPlot.tuPlotToolbar.lstActionsCrossSection[7].triggered.connect(self.tuMenuFunctions.updateLegend)
				self.tuView.tuPlot.tuPlotToolbar.lstActionsVerticalProfile[7].triggered.connect(self.tuMenuFunctions.updateLegend)
				self.viewMenu_connected = True

			self.saveColorRampForActiveResult_action.triggered.connect(
				lambda: self.tuMenuFunctions.saveDefaultStyleScalar('color ramp'))
			self.saveColorMapForActiveResult_action.triggered.connect(
				lambda: self.tuMenuFunctions.saveDefaultStyleScalar('color map'))
			self.saveStyleForVectorResult_action.triggered.connect(self.tuMenuFunctions.saveDefaultStyleVector)
			self.loadStyleForActiveResult_action.triggered.connect(self.tuMenuFunctions.loadDefaultStyleScalar)
			self.loadStyleForVectorResult_action.triggered.connect(self.tuMenuFunctions.loadDefaultStyleVector)
			self.resetDefaultStyles_action.triggered.connect(self.tuMenuFunctions.resetDefaultStyles)
			self.options_action.triggered.connect(self.tuMenuFunctions.options)
			self.addPlotColourRamp_action.triggered.connect(self.tuMenuFunctions.addColourRampFromXML)
			self.resetPlotColours_action.triggered.connect(self.tuMenuFunctions.resetMatplotColours)
			self.resetAxisNames_action.triggered.connect(self.tuMenuFunctions.resetPlotAxisNames)
			self.dockTuflowViewer_action.triggered.connect(self.tuMenuFunctions.redockTuflowViewer)
		else:
			self.settingsMenu.addAction(self.menu.userPlotDataManager_action)
			self.settingsMenu.addSeparator()
			self.settingsMenu.addAction(toolbar[7])
			self.settingsMenu.addSeparator()
			self.saveStyleMenu = self.settingsMenu.addMenu('Save Active Layer Style as Default for Result Type')
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
			self.settingsMenu.addAction(self.menu.dockTuflowViewer_action)
			self.settingsMenu.addSeparator()
			self.settingsMenu.addAction(self.menu.options_action)
		
		return True
	
	def loadExportMenu(self, plotNo, **kwargs):
		"""
		Load Export menu and menu items
		
		:param plotNo: int enumerator -> 0: time series plot
										 1: long profile plot
										 2: cross section plot
		:param kwargs: dict -> key word arguments
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		update = kwargs['update'] if 'update' in kwargs.keys() else False
		
		# if plotNo == 0:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsTimeSeries
		# elif plotNo == 1:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsLongPlot
		# elif plotNo == 2:
		# 	toolbar = self.tuView.tuPlot.tuPlotToolbar.lstActionsCrossSection

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
		
		if not update:  # only create view menu if not just an update (updates when switching between plot type tabs)
			self.exportMenu = self.menuBar.addMenu('&Export')
		lineFeatureIcon = QgsApplication.getThemeIcon("/mActionMoveFeatureLine.svg")
		pointFeatureIcon = QgsApplication.getThemeIcon("/mActionMoveFeaturePoint.svg")
		iconAnimation = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "icon_video.png"))

		if self.menu is None:
			# export menu items
			self.exportAsCSV_action = QAction('Export Plot As CSV', self.window)
			self.autoPlotExport_action = QAction('Batch Plot and Export Features in Shape File', self.window)
			self.exportDataToClipboard_action = QAction('Copy Data to Clipboard', self.window)
			self.exportImageToClipboard_action = QAction('Copy Image to Clipboard', self.window)
			self.exportTempLine_action = QAction(lineFeatureIcon, 'Export Temporary Line(s) to SHP', self.window)
			self.exportTempPoint_action = QAction(pointFeatureIcon, 'Export Temporary Point(s) to SHP', self.window)
			self.exportAnimation_action = QAction(iconAnimation, 'Export Animation', self.window)
			self.exportMaps_action = QAction('Export Maps (beta)', self.window)
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

			self.exportAsCSV_action.triggered.connect(self.tuMenuFunctions.exportCSV)
			self.autoPlotExport_action.triggered.connect(self.tuMenuFunctions.batchPlotExportInitialise)
			self.exportDataToClipboard_action.triggered.connect(self.tuMenuFunctions.exportDataToClipboard)
			self.exportImageToClipboard_action.triggered.connect(self.tuMenuFunctions.exportImageToClipboard)
			self.exportTempLine_action.triggered.connect(self.tuMenuFunctions.exportTempLines)
			self.exportTempPoint_action.triggered.connect(self.tuMenuFunctions.exportTempPoints)
			self.exportAnimation_action.triggered.connect(self.tuMenuFunctions.exportAnimation)
			self.exportMaps_action.triggered.connect(self.tuMenuFunctions.exportMaps)
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
		
		resultsMenu = self.menuBar.addMenu('&Results')

		if self.menu is None:
			# ARR2016 menu items
			self.showSelectedElements_action = QAction('Show Selected Element Names', self.window)
			self.showMedianEvent_action = QAction('Show Median Event', self.window)
			self.showMedianEvent_action.setCheckable(True)
			self.showMeanEvent_action = QAction('Show Mean Event', self.window)
			self.showMeanEvent_action.setCheckable(True)
			resultsMenu.addAction(self.showSelectedElements_action)
			resultsMenu.addSeparator()
			arrMenu = resultsMenu.addMenu('&ARR2019')
			arrMenu.addAction(self.showMedianEvent_action)
			arrMenu.addAction(self.showMeanEvent_action)

			self.showSelectedElements_action.triggered.connect(self.tuMenuFunctions.showSelectedElements)
			self.showMedianEvent_action.triggered.connect(self.tuMenuFunctions.showMedianEvent)
			self.showMeanEvent_action.triggered.connect(self.tuMenuFunctions.showMeanEvent)
		else:
			resultsMenu.addAction(self.menu.showSelectedElements_action)
			resultsMenu.addSeparator()
			arrMenu = resultsMenu.addMenu('&ARR2019')
			arrMenu.addAction(self.menu.showMedianEvent_action)
			arrMenu.addAction(self.menu.showMeanEvent_action)
		
		return True
	
	def loadHelpMenu(self):
		"""
		Load Help menu and menu items.
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		helpMenu = self.menuBar.addMenu('&Help')
		helpIcon = QgsApplication.getThemeIcon('/mActionHelpContents.svg')
		aboutIcon = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "tuview.png"))

		if self.menu is None:
			# Help Menu
			self.help_action = QAction(helpIcon, 'Help', self.window)
			self.about_action = QAction(aboutIcon, 'About', self.window)
			self.changelog_action = QAction('Plugin Changelog', self.window)
			self.coastalme_downloads_page_action = QAction('COASTALME Downloads', self.window)
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

		about(self.tuView)
		
	def help(self):
		"""
		
		:return:
		"""
		
		url = r'https://wiki.coastalme.com/index.php?title=COASTALME_Viewer'
		webbrowser.open(url)

	def qgisDisconnect(self):
		# file menu
		try:
			self.load2dResults_action.triggered.disconnect(self.tuMenuFunctions.load2dResults)
		except:
			pass
		try:
			self.load1dResults_action.triggered.disconnect(self.tuMenuFunctions.load1dResults)
		except:
			pass
		try:
			self.loadParticlesResults_action.triggered.disconnect(self.tuMenuFunctions.loadParticlesResults)
		except:
			pass
		try:
			self.load1d2dResults_action.triggered.disconnect(self.tuMenuFunctions.load1d2dResults)
		except:
			pass
		try:
			self.loadHydraulicTable_action.triggered.disconnect(self.tuMenuFunctions.loadHydraulicTables)
		except:
			pass
		try:
			self.remove1d2dResults_action.triggered.disconnect(self.tuMenuFunctions.remove1d2dResults)
		except:
			pass
		try:
			self.remove2dResults_action.triggered.disconnect(self.tuMenuFunctions.remove2dResults)
		except:
			pass
		try:
			self.remove1dResults_action.triggered.disconnect(self.tuMenuFunctions.remove1dResults)
		except:
			pass
		try:
			self.removeParticlesResults_action.triggered.disconnect(self.tuMenuFunctions.removeParticlesResults)
		except:
			pass
		try:
			self.closeHydraulicTable_action.triggered.disconnect(self.tuMenuFunctions.removeHydraulicTables)
		except:
			pass
		# view menu
		for plotNo in range(self.tuView.tuPlot.TotalPlotNo):
			toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
			try:
				self.freezeAxisLimits_action.triggered.disconnect(viewToolbar.freezeXYAxis)
			except:
				pass
			try:
				self.freezeAxisXLimits_action.triggered.disconnect(viewToolbar.freezeXAxis)
			except:
				pass
			try:
				self.freezeAxisYLimits_action.triggered.disconnect(viewToolbar.freezeYAxis)
			except:
				pass
			try:
				self.refreshMapWindow_action.triggered.disconnect(self.tuView.renderMap)
			except:
				pass
			try:
				self.refreshCurrentPlotWindow_action.triggered.disconnect(self.tuView.refreshCurrentPlot)
			except:
				pass
			try:
				self.refreshAllPlotWindows_action.triggered.disconnect(self.tuView.tuPlot.updateAllPlots)
			except:
				pass
			try:
				self.clearPlotWindow_action.triggered.disconnect()
			except:
				pass
			try:
				self.clearAllPlotWindows_action.triggered.disconnect(self.tuView.tuPlot.clearAllPlots)
			except:
				pass
		# settings menu
		try:
			self.tuView.tuPlot.tuPlotToolbar.lstActionsTimeSeries[7].triggered.disconnect(self.tuMenuFunctions.updateLegend)
		except:
			pass
		try:
			self.tuView.tuPlot.tuPlotToolbar.lstActionsLongPlot[7].triggered.disconnect(self.tuMenuFunctions.updateLegend)
		except:
			pass
		try:
			self.tuView.tuPlot.tuPlotToolbar.lstActionsCrossSection[7].triggered.disconnect(self.tuMenuFunctions.updateLegend)
		except:
			pass
		try:
			self.tuView.tuPlot.tuPlotToolbar.lstActionsVerticalProfile[7].triggered.disconnect(self.tuMenuFunctions.updateLegend)
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
			self.saveStyleForVectorResult_action.triggered.disconnect(self.tuMenuFunctions.saveDefaultStyleVector)
		except:
			pass
		try:
			self.loadStyleForActiveResult_action.triggered.disconnect(self.tuMenuFunctions.loadDefaultStyleScalar)
		except:
			pass
		try:
			self.loadStyleForVectorResult_action.triggered.disconnect(self.tuMenuFunctions.loadDefaultStyleVector)
		except:
			pass
		try:
			self.resetDefaultStyles_action.triggered.disconnect(self.tuMenuFunctions.resetDefaultStyles)
		except:
			pass
		try:
			self.options_action.triggered.disconnect(self.tuMenuFunctions.options)
		except:
			pass
		try:
			self.addPlotColourRamp_action.triggered.disconnect(self.tuMenuFunctions.addColourRampFromXML)
		except:
			pass
		try:
			self.resetPlotColours_action.triggered.disconnect(self.tuMenuFunctions.resetMatplotColours)
		except:
			pass
		# export menu
		try:
			self.exportAsCSV_action.triggered.disconnect(self.tuMenuFunctions.exportCSV)
		except:
			pass
		try:
			self.autoPlotExport_action.triggered.disconnect(self.tuMenuFunctions.batchPlotExportInitialise)
		except:
			pass
		try:
			self.exportDataToClipboard_action.triggered.disconnect(self.tuMenuFunctions.exportDataToClipboard)
		except:
			pass
		try:
			self.exportImageToClipboard_action.triggered.disconnect(self.tuMenuFunctions.exportImageToClipboard)
		except:
			pass
		try:
			self.exportTempLine_action.triggered.disconnect(self.tuMenuFunctions.exportTempLines)
		except:
			pass
		try:
			self.exportTempPoint_action.triggered.disconnect(self.tuMenuFunctions.exportTempPoints)
		except:
			pass
		try:
			self.exportAnimation_action.triggered.disconnect(self.tuMenuFunctions.exportAnimation)
		except:
			pass
		try:
			self.exportMaps_action.triggered.disconnect(self.tuMenuFunctions.exportMaps)
		except:
			pass
		# result menu
		try:
			self.showSelectedElements_action.triggered.disconnect(self.tuMenuFunctions.showSelectedElements)
		except:
			pass
		try:
			self.showMedianEvent_action.triggered.disconnect(self.tuMenuFunctions.showMedianEvent)
		except:
			pass
		try:
			self.showMeanEvent_action.triggered.disconnect(self.tuMenuFunctions.showMeanEvent)
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
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from .coastalmeqgis_cmemenufunctions import CmeMenuFunctions
from coastalme.toc.toc import coastalmeqgis_find_layer

from ..nc_grid_data_provider import NetCDFGrid



from ..compatibility_routines import QT_CUSTOM_CONTEXT_MENU


class CmeContextMenu():
	"""
	Class for handling Cmeview context menus.
	
	"""
	
	def __init__(self, CmeView):
		self.cmeView = CmeView
		self.cmePlot = CmeView.cmePlot
		self.iface = CmeView.iface
		self.resultTypeContextItem = None  # stores clicked result type for context menu
		
		# menu function class
		self.cmeMenuFunctions = CmeMenuFunctions(CmeView)

		self.plotNoToToolbar = self.cmeView.cmeMenuBar.plotNoToToolbar

		self.signals = []
		
	def loadPlotMenu(self, plotNo, **kwargs):
		"""
		Load context plot menu and items.
		
		:param plotNo: int enumerator -> 0: time series plot
										 1: long profile plot
										 2: cross section plot
		:param kwargs: dict -> key word arguments
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		update = kwargs['update'] if 'update' in kwargs.keys() else False
		
		# if plotNo == 0:
		# 	toolbar = self.cmePlot.cmePlotToolbar.lstActionsTimeSeries
		# 	viewToolbar = self.cmePlot.cmePlotToolbar.viewToolbarTimeSeries
		# elif plotNo == 1:
		# 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsLongPlot
		# 	viewToolbar = self.cmePlot.cmePlotToolbar.viewToolbarLongPlot
		# elif plotNo == 2:
		# 	toolbar = self.cmeView.cmePlot.cmePlotToolbar.lstActionsCrossSection
		# 	viewToolbar = self.cmePlot.cmePlotToolbar.viewToolbarCrossSection

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
		
		if not update:  # only create menu if not just an update (updates when switching between plot type tabs)
			self.plotMenu = QMenu(self.cmeView)
		iconRefreshPlot = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "RefreshPlotBlack.png"))
		iconClearPlot = QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons" "ClearPlot.png"))
		
		self.userPlotDataManager_action = viewToolbar.userPlotDataManagerButton.defaultAction()
		self.freezeAxisLimits_action = viewToolbar.freezeXYAxisButton.defaultAction()
		self.freezeAxisXLimits_action = viewToolbar.freezeXAxisButton.defaultAction()
		self.freezeAxisYLimits_action = viewToolbar.freezeYAxisButton.defaultAction()
		self.flipSecondaryAxis_action = QAction('Switch Secondary Axis', self.plotMenu)
		self.refreshCurrentPlotWindow_action = QAction(iconRefreshPlot, 'Refresh Plot Window', self.plotMenu)
		self.clearPlotWindow_action = QAction(iconClearPlot, 'Clear Plot Window', self.plotMenu)
		self.exportAsCSV_action = QAction('Export Plot As CSV', self.plotMenu)

		self.plotMenu.addAction(self.userPlotDataManager_action)
		self.plotMenu.addSeparator()
		self.plotMenu.addAction(toolbar[0])
		self.plotMenu.addAction(toolbar[4])
		self.plotMenu.addAction(toolbar[5])
		self.plotMenu.addAction(toolbar[7])
		self.plotMenu.addSeparator()
		self.plotMenu.addAction(self.freezeAxisLimits_action)
		self.plotMenu.addAction(self.freezeAxisXLimits_action)
		self.plotMenu.addAction(self.freezeAxisYLimits_action)
		self.plotMenu.addAction(self.flipSecondaryAxis_action)
		self.plotMenu.addSeparator()
		self.plotMenu.addAction(viewToolbar.hGridLines_action)
		self.plotMenu.addAction(viewToolbar.vGridLines_action)
		self.plotMenu.addAction(viewToolbar.axisFontSize_action)
		self.plotMenu.addAction(viewToolbar.axisLabelFontSize_action)
		self.plotMenu.addSeparator()
		self.plotMenu.addAction(self.refreshCurrentPlotWindow_action)
		self.plotMenu.addAction(self.clearPlotWindow_action)
		self.plotMenu.addSeparator()
		copyMenu = self.plotMenu.addMenu('&Copy')
		copyMenu.addAction(self.cmeView.cmeMenuBar.exportDataToClipboard_action)
		copyMenu.addAction(self.cmeView.cmeMenuBar.exportImageToClipboard_action)
		exportMenu = self.plotMenu.addMenu('&Export')
		exportMenu.addAction(self.exportAsCSV_action)
		toolbar[9].setText('Save Plot As Image')
		exportMenu.addAction(toolbar[9])
		if plotNo == CmePlot.CrossSection or plotNo == CmePlot.VerticalProfile:
			self.plotMenu.addSeparator()
			self.plotMenu.addAction(self.cmePlot.verticalMesh_action)
		
		#self.userPlotDataManager_action.triggered.connect(self.cmeMenuFunctions.openUserPlotDataManager)
		signal = self.freezeAxisLimits_action.triggered.connect(viewToolbar.freezeXYAxis)
		self.signals.append(('self.freezeAxisLimits_action.triggered', signal))
		signal = self.freezeAxisXLimits_action.triggered.connect(viewToolbar.freezeXAxis)
		self.signals.append(('self.freezeAxisXLimits_action.triggered', signal))
		signal = self.freezeAxisYLimits_action.triggered.connect(viewToolbar.freezeYAxis)
		self.signals.append(('self.freezeAxisYLimits_action.triggered', signal))
		signal = self.flipSecondaryAxis_action.triggered.connect(lambda: self.cmeMenuFunctions.flipSecondaryAxis(plotNo))
		self.signals.append(('self.flipSecondaryAxis_action.triggered', signal))
		signal = self.refreshCurrentPlotWindow_action.triggered.connect(self.cmeView.refreshCurrentPlot)
		self.signals.append(('self.refreshCurrentPlotWindow_action.triggered', signal))
		# self.clearPlotWindow_action.triggered.connect(
		# 	lambda: self.cmeView.cmePlot.clearPlot(self.cmeView.tabWidget.currentIndex(), clear_rubberband=True, clear_selection=True))
		signal = self.clearPlotWindow_action.triggered.connect(
			lambda: self.cmeView.cmePlot.clearPlot2(self.cmeView.tabWidget.currentIndex()))
		self.signals.append(('self.clearPlotWindow_action.triggered', signal))
		signal = self.exportAsCSV_action.triggered.connect(self.cmeMenuFunctions.exportCSV)
		self.signals.append(('self.exportAsCSV_action.triggered', signal))
		
		return True
	
	def showPlotMenu(self, pos, plotNo):
		"""
		Context menus for plot windows.
		
		:param pos: QPoint
		:param plotNo: int enumerator -> 0: time series plot
										 1: long profile plot
										 2: cross section plot
		:return: bool -> True for successful, False for unsuccessful
		"""

		parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, yAxisLabels, xAxisLabels, xAxisLimits, yAxisLimits = \
			self.cmePlot.plotEnumerator(plotNo)

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]

		if toolbar[4].isChecked():
			return True
		if toolbar[5].isChecked():
			return True

		self.plotMenu.popup(plotWidget.mapToGlobal(pos))

		return True
	
	def loadResultsMenu(self):
		"""
		Load context plot menu and items.

		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.resultsMenu = QMenu(self.cmeView)
		closeResultsIcon = QgsApplication.getThemeIcon("/mActionRemoveLayer.svg")

		self.load1d2dResults_action = QAction('Load Results', self.resultsMenu)
		self.load2dResults_action = QAction('Load Results - Map Outputs', self.resultsMenu)
		self.load1dResults_action = QAction('Load Results - Time Series', self.resultsMenu)
		self.loadFMResults_action = QAction('Load Results - Time Series FM', self.resultsMenu)
		self.loadParticlesResults_action = QAction('Load Results - Particles', self.resultsMenu)
		self.loadNcGridResults_action = QAction('Load Results - NetCDF Grid', self.resultsMenu)
		self.loadHydraulicTable_action = QAction("Import 1D Hydraulic Tables", self.resultsMenu)
		self.loadBcTables_action = QAction('Import BC Tables', self.resultsMenu)
		self.remove1d2dResults_action = QAction(closeResultsIcon, 'Close Results', self.resultsMenu)
		self.remove2dResults_action = QAction('Close Results - Map Outputs', self.resultsMenu)
		self.remove1dResults_action = QAction('Close Results - Time Series', self.resultsMenu)
		self.removeParticlesResults_action = QAction('Close Results - Particles', self.resultsMenu)
		self.closeHydraulicTable_action = QAction("Close 1D Hydraulic Tables", self.resultsMenu)
		self.loadFVBCTide_action = QAction('Import FV Tide BC NetCDF', self.resultsMenu)

		self.resultsMenu.addAction(self.load1d2dResults_action)
		self.resultsMenu.addAction(self.load2dResults_action)
		self.resultsMenu.addAction(self.load1dResults_action)
		self.resultsMenu.addAction(self.loadFMResults_action)
		self.resultsMenu.addAction(self.loadParticlesResults_action)
		self.resultsMenu.addAction(self.loadNcGridResults_action)
		self.resultsMenu.addAction(self.loadHydraulicTable_action)
		self.resultsMenu.addAction(self.loadBcTables_action)
		self.resultsMenu.addAction(self.loadFVBCTide_action)
		self.resultsMenu.addSeparator()
		self.resultsMenu.addAction(self.remove1d2dResults_action)
		self.resultsMenu.addAction(self.remove2dResults_action)
		self.resultsMenu.addAction(self.remove1dResults_action)
		self.resultsMenu.addAction(self.removeParticlesResults_action)
		self.resultsMenu.addAction(self.closeHydraulicTable_action)

		signal = self.load2dResults_action.triggered.connect(self.cmeMenuFunctions.load2dResults)
		self.signals.append(('self.load2dResults_action.triggered', signal))
		signal = self.load1dResults_action.triggered.connect(self.cmeMenuFunctions.load1dResults)
		self.signals.append(('self.load1dResults_action.triggered', signal))
		signal = self.loadFMResults_action.triggered.connect(self.cmeMenuFunctions.loadFMResults)
		self.signals.append(('self.loadFMResults_action.triggered', signal))
		signal = self.loadParticlesResults_action.triggered.connect(self.cmeMenuFunctions.loadParticlesResults)
		self.signals.append(('self.loadParticlesResults_action.triggered', signal))
		signal = self.loadNcGridResults_action.triggered.connect(self.cmeMenuFunctions.loadNcGridResults)
		self.signals.append(('self.loadNcGridResults_action.triggered', signal))
		signal = self.load1d2dResults_action.triggered.connect(self.cmeMenuFunctions.load1d2dResults)
		self.signals.append(('self.load1d2dResults_action.triggered', signal))
		signal = self.loadHydraulicTable_action.triggered.connect(self.cmeMenuFunctions.loadHydraulicTables)
		self.signals.append(('self.loadHydraulicTable_action.triggered', signal))
		signal = self.loadBcTables_action.triggered.connect(self.cmeMenuFunctions.loadBcTables)
		self.signals.append(('self.loadBcTables_action.triggered', signal))
		signal = self.remove1d2dResults_action.triggered.connect(self.cmeMenuFunctions.remove1d2dResults)
		self.signals.append(('self.remove1d2dResults_action.triggered', signal))
		signal = self.remove2dResults_action.triggered.connect(self.cmeMenuFunctions.remove2dResults)
		self.signals.append(('self.remove2dResults_action.triggered', signal))
		signal = self.remove1dResults_action.triggered.connect(self.cmeMenuFunctions.remove1dResults)
		self.signals.append(('self.remove1dResults_action.triggered', signal))
		signal = self.removeParticlesResults_action.triggered.connect(self.cmeMenuFunctions.removeParticlesResults)
		self.signals.append(('self.removeParticlesResults_action.triggered', signal))
		signal = self.closeHydraulicTable_action.triggered.connect(self.cmeMenuFunctions.removeHydraulicTables)
		self.signals.append(('self.closeHydraulicTable_action.triggered', signal))
		signal = self.loadFVBCTide_action.triggered.connect(self.cmeMenuFunctions.loadFVBCTide)
		self.signals.append(('self.loadFVBCTide_action.triggered', signal))

		return True
	
	def showResultsMenu(self, pos):
		"""
		Context menu for open results list widget.
		
		:param pos: QPoint
		:return: bool -> True for successful, False for unsuccessful
		"""

		row = -1
		clicked_item = self.cmeView.OpenResults.itemAt(pos)
		if clicked_item is not None and self.cmeView.OpenResults.count() > 1:
			index = self.cmeView.OpenResults.indexFromItem(clicked_item)
			row = index.row()

		for action in self.resultsMenu.actions():
			if action == self.load1d2dResults_action:
				break
			else:
				self.resultsMenu.removeAction(action)

		self.moveUp_action = QAction(QgsApplication.getThemeIcon('/mActionArrowUp.svg'), 'Move Up', self.resultsMenu)
		self.moveDown_action = QAction(QgsApplication.getThemeIcon('/mActionArrowDown.svg'), 'Move Down',
									   self.resultsMenu)
		self.moveToTop_action = QAction('Move To Top', self.resultsMenu)
		self.moveToBottom_action = QAction('Move To Bottom', self.resultsMenu)

		if self.cmeView.OpenResults.count() > 1:
			if row > 0:
				moveUp_action = QAction(QgsApplication.getThemeIcon('/mActionArrowUp.svg'), 'Move Up', self.resultsMenu)
				moveUp_action.triggered.connect(lambda: self.cmeView.reorderOpenResults(index, 'up'))
				self.resultsMenu.insertAction(self.load1d2dResults_action, moveUp_action)
			if row + 1 < self.cmeView.OpenResults.count():
				moveDown_action = QAction(QgsApplication.getThemeIcon('/mActionArrowDown.svg'), 'Move Down', self.resultsMenu)
				moveDown_action.triggered.connect(lambda: self.cmeView.reorderOpenResults(index, 'down'))
				self.resultsMenu.insertAction(self.load1d2dResults_action, moveDown_action)
			if row > 0:
				moveToTop_action = QAction('Move To Top', self.resultsMenu)
				moveToTop_action.triggered.connect(lambda: self.cmeView.reorderOpenResults(index, 'top'))
				self.resultsMenu.insertAction(self.load1d2dResults_action, moveToTop_action)
			if row + 1 < self.cmeView.OpenResults.count():
				moveToBottom_action = QAction('Move To Bottom', self.resultsMenu)
				moveToBottom_action.triggered.connect(lambda: self.cmeView.reorderOpenResults(index, 'bottom'))
				self.resultsMenu.insertAction(self.load1d2dResults_action, moveToBottom_action)
			if row > -1:
				self.resultsMenu.insertSeparator(self.load1d2dResults_action)

		for action in self.resultsMenu.actions():
			if action.text() == 'Set Reference Time':
				self.resultsMenu.removeAction(action)

		if clicked_item is not None and isinstance(coastalmeqgis_find_layer(clicked_item.text()), NetCDFGrid):
			layer = coastalmeqgis_find_layer(clicked_item.text())
			setReferenceTime_action = QAction('Set Reference Time', self.resultsMenu)
			setReferenceTime_action.triggered.connect(lambda: self.cmeMenuFunctions.setReferenceTime(layer))
			self.resultsMenu.addSeparator()
			self.resultsMenu.addAction(setReferenceTime_action)

		self.resultsMenu.popup(self.cmeView.OpenResults.mapToGlobal(pos))
		
		return True
	
	def loadResultTypesMenu(self):
		"""
		Load context menu and items for the result types dataview
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.resultTypesMenu = QMenu(self.cmeView)
		
		self.setToMaximumResult_action = QAction('Maximum', self.resultTypesMenu)
		self.setToMaximumResult_action.setCheckable(True)
		self.setToMinimumResult_action = QAction('Minimum', self.resultTypesMenu)
		self.setToMinimumResult_action.setCheckable(True)
		self.setToSecondaryAxis_action = QAction('Secondary Axis', self.resultTypesMenu)
		self.setToSecondaryAxis_action.setCheckable(True)
		self.copyStyle_action = QAction('Copy Style')
		self.pasteStyle_action = QAction('Paste Style')
		self.saveDefaultStyleRamp_action = QAction('Colour Ramp', self.resultTypesMenu)
		self.saveDefaultStyleMap_action = QAction('Colour Map (Exact Values and Colours)', self.resultTypesMenu)
		self.saveDefaultVectorStyle_action = QAction('Save Vector Style as Default', self.resultTypesMenu)
		self.loadDefaultStyle_action = QAction('Load Default Style', self.resultTypesMenu)
		self.loadDefaultVectorStyle_action = QAction('Load Default Vector Style', self.resultTypesMenu)
		self.propertiesDialog_action = QAction('Properties', self.resultTypesMenu)
		self.includeFlowRegime_action = QAction('Flow Regime', self.resultTypesMenu)
		self.includeFlowRegime_action.setCheckable(True)
		
		self.resultTypesMenu.addAction(self.setToMaximumResult_action)
		self.resultTypesMenu.addAction(self.setToMinimumResult_action)
		self.resultTypesMenu.addAction(self.setToSecondaryAxis_action)
		self.resultTypesMenu.addAction(self.includeFlowRegime_action)
		self.resultTypesMenu.addSeparator()
		self.resultTypesMenu.addAction(self.copyStyle_action)
		self.resultTypesMenu.addAction(self.pasteStyle_action)
		self.saveStyleMenu = self.resultTypesMenu.addMenu('Save Style as Default')
		self.saveStyleMenu.addAction(self.saveDefaultStyleRamp_action)
		self.saveStyleMenu.addAction(self.saveDefaultStyleMap_action)
		self.resultTypesMenu.addAction(self.saveDefaultVectorStyle_action)
		self.resultTypesMenu.addAction(self.loadDefaultStyle_action)
		self.resultTypesMenu.addAction(self.loadDefaultVectorStyle_action)
		self.resultTypesMenu.addSeparator()
		self.resultTypesMenu.addAction(self.propertiesDialog_action)
		
		signal = self.setToMaximumResult_action.triggered.connect(self.cmeMenuFunctions.toggleResultTypeToMax)
		self.signals.append(('self.setToMaximumResult_action.triggered', signal))
		signal = self.setToMinimumResult_action.triggered.connect(self.cmeMenuFunctions.toggleResultTypeToMin)
		self.signals.append(('self.setToMinimumResult_action.triggered', signal))
		signal = self.setToSecondaryAxis_action.triggered.connect(self.cmeMenuFunctions.toggleResultTypeToSecondaryAxis)
		self.signals.append(('self.setToSecondaryAxis_action.triggered', signal))
		signal = self.saveDefaultStyleRamp_action.triggered.connect(lambda: self.cmeMenuFunctions.saveDefaultStyleScalar('color ramp', use_clicked=True))
		self.signals.append(('self.saveDefaultStyleRamp_action.triggered', signal))
		signal = self.saveDefaultStyleMap_action.triggered.connect(lambda: self.cmeMenuFunctions.saveDefaultStyleScalar('color map', use_clicked=True))
		self.signals.append(('self.saveDefaultStyleMap_action.triggered', signal))
		signal = self.saveDefaultVectorStyle_action.triggered.connect(lambda: self.cmeMenuFunctions.saveDefaultStyleVector(use_clicked=True))
		self.signals.append(('self.saveDefaultVectorStyle_action.triggered', signal))
		signal = self.loadDefaultStyle_action.triggered.connect(lambda: self.cmeMenuFunctions.loadDefaultStyleScalar(use_clicked=True))
		self.signals.append(('self.loadDefaultStyle_action.triggered', signal))
		signal = self.loadDefaultVectorStyle_action.triggered.connect(lambda: self.cmeMenuFunctions.loadDefaultStyleVector(use_clicked=True))
		self.signals.append(('self.loadDefaultVectorStyle_action.triggered', signal))
		signal = self.propertiesDialog_action.triggered.connect(lambda: self.cmeView.resultTypeDoubleClicked(None))
		self.signals.append(('self.propertiesDialog_action.triggered', signal))
		signal = self.includeFlowRegime_action.triggered.connect(self.cmeMenuFunctions.flowRegimeToggled)
		self.signals.append(('self.includeFlowRegime_action.triggered', signal))
		signal = self.copyStyle_action.triggered.connect(self.cmeMenuFunctions.copyStyle)
		self.signals.append(('self.copyStyle_action.triggered', signal))
		signal = self.pasteStyle_action.triggered.connect(self.cmeMenuFunctions.pasteStyle)
		self.signals.append(('self.pasteStyle_action.triggered', signal))
		
		return True
	
	def showResultTypesMenu(self, pos):
		"""
		Context menu for open result types dataview.
		
		:param pos: QPoint
		:return: bool -> True for successful, False for unsuccessful
		"""

		flowRegimeExists = 'flow regime' in [x.ds_name.lower() for x in self.cmeView.OpenResultTypes.model().timeSeriesItem.children()]

		modelIndex = self.cmeView.OpenResultTypes.indexAt(pos)
		if modelIndex.isValid():
			item = self.cmeView.OpenResultTypes.model().index2item(modelIndex)
		else:
			item = None
		
		if item is None:
			self.resultTypeContextItem = None
			return False
		else:
			if item.ds_name.lower() == 'none':
				self.resultTypeContextItem = None
				return False
			elif item.parentItem == self.cmeView.OpenResultTypes.model().rootItem:
				self.resultTypeContextItem = None
				return False
			else:
				# secondary axis
				self.setToSecondaryAxis_action.setEnabled(True)
				if item.secondaryActive:
					self.setToSecondaryAxis_action.setChecked(True)
				else:
					self.setToSecondaryAxis_action.setChecked(False)
				# maximum
				if item.hasMax:
					self.setToMaximumResult_action.setEnabled(True)
					if item.isMax:
						self.setToMaximumResult_action.setChecked(True)
					else:
						self.setToMaximumResult_action.setChecked(False)
				else:
					self.setToMaximumResult_action.setEnabled(False)
				# minimum
				if item.hasMin:
					self.setToMinimumResult_action.setEnabled(True)
					if item.isMin:
						self.setToMinimumResult_action.setChecked(True)
					else:
						self.setToMinimumResult_action.setChecked(False)
				else:
					self.setToMinimumResult_action.setEnabled(False)
				# flow regime
				if item.hasFlowRegime:
					self.includeFlowRegime_action.setEnabled(True)
					if item.isFlowRegime:
						self.includeFlowRegime_action.setChecked(True)
					else:
						self.includeFlowRegime_action.setChecked(False)
				else:
					self.includeFlowRegime_action.setEnabled(False)

				# save and load styling
				if item.ds_type == 1:  # scalar
					self.copyStyle_action.setVisible(True)
					self.pasteStyle_action.setVisible(True)
					self.saveStyleMenu.menuAction().setVisible(True)
					self.loadDefaultStyle_action.setVisible(True)
					self.saveDefaultVectorStyle_action.setVisible(False)
					self.loadDefaultVectorStyle_action.setVisible(False)
					self.propertiesDialog_action.setVisible(True)
					self.includeFlowRegime_action.setVisible(False)
				elif item.ds_type == 2:  # vector
					self.copyStyle_action.setVisible(True)
					self.pasteStyle_action.setVisible(True)
					self.saveStyleMenu.menuAction().setVisible(False)
					self.loadDefaultStyle_action.setVisible(False)
					self.saveDefaultVectorStyle_action.setVisible(True)
					self.loadDefaultVectorStyle_action.setVisible(True)
					self.propertiesDialog_action.setVisible(True)
					self.includeFlowRegime_action.setVisible(False)
				elif item.ds_type == 4 or item.ds_type == 5:  # time series plot
					self.copyStyle_action.setVisible(False)
					self.pasteStyle_action.setVisible(False)
					self.saveStyleMenu.menuAction().setVisible(False)
					self.loadDefaultStyle_action.setVisible(False)
					self.saveDefaultVectorStyle_action.setVisible(False)
					self.loadDefaultVectorStyle_action.setVisible(False)
					self.propertiesDialog_action.setVisible(False)
					self.includeFlowRegime_action.setVisible(True)
				else:  # long plot
					self.copyStyle_action.setVisible(False)
					self.pasteStyle_action.setVisible(False)
					self.saveStyleMenu.menuAction().setVisible(False)
					self.loadDefaultStyle_action.setVisible(False)
					self.saveDefaultVectorStyle_action.setVisible(False)
					self.loadDefaultVectorStyle_action.setVisible(False)
					self.propertiesDialog_action.setVisible(False)
					self.includeFlowRegime_action.setVisible(False)
		
		if not flowRegimeExists:
			self.includeFlowRegime_action.setVisible(False)
		self.resultTypeContextItem = item
		self.resultTypesMenu.popup(self.cmeView.OpenResultTypes.mapToGlobal(pos))
		
		return True
	
	def connectMenu(self):
		"""
		Connects menu items to their functions.

		:return: bool -> True for successful, False for unsuccessful
		"""

		self.cmePlot.plotWidgetTimeSeries.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.cmePlot.plotWidgetLongPlot.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.cmePlot.plotWidgetCrossSection.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.cmePlot.plotWidgetVerticalProfile.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.cmeView.OpenResults.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.cmeView.OpenResultTypes.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		signal = self.cmePlot.plotWidgetTimeSeries.customContextMenuRequested.connect(lambda pos: self.showPlotMenu(pos, 0))
		self.signals.append(('self.cmePlot.plotWidgetTimeSeries.customContextMenuRequested', signal))
		signal = self.cmePlot.plotWidgetLongPlot.customContextMenuRequested.connect(lambda pos: self.showPlotMenu(pos, 1))
		self.signals.append(('self.cmePlot.plotWidgetLongPlot.customContextMenuRequested', signal))
		signal = self.cmePlot.plotWidgetCrossSection.customContextMenuRequested.connect(lambda pos: self.showPlotMenu(pos, 2))
		self.signals.append(('self.cmePlot.plotWidgetCrossSection.customContextMenuRequested', signal))
		signal = self.cmePlot.plotWidgetVerticalProfile.customContextMenuRequested.connect(lambda pos: self.showPlotMenu(pos, 3))
		self.signals.append(('self.cmePlot.plotWidgetVerticalProfile.customContextMenuRequested', signal))
		signal = self.cmeView.OpenResults.customContextMenuRequested.connect(self.showResultsMenu)
		self.signals.append(('self.cmeView.OpenResults.customContextMenuRequested', signal))
		signal = self.cmeView.OpenResultTypes.customContextMenuRequested.connect(self.showResultTypesMenu)
		self.signals.append(('self.cmeView.OpenResultTypes.customContextMenuRequested', signal))
		
		return True

	def qgisDisconnect(self):
		nsignals = len(self.signals)
		for i, (signal_caller, signal) in enumerate(reversed(self.signals[:])):
			try:
				signal_caller = eval(signal_caller)
			except Exception as e:
				pass
			try:
				signal_caller.disconnect(signal)
			except:
				pass
			try:
				self.signals.pop(nsignals - i - 1)
			except Exception as e:
				pass
		# # plot menu
		# for plotNo in range(self.cmePlot.TotalPlotNo):
		# 	toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
		# 	try:
		# 		self.freezeAxisLimits_action.triggered.disconnect(viewToolbar.freezeXYAxis)
		# 	except:
		# 		pass
		# 	try:
		# 		self.freezeAxisXLimits_action.triggered.disconnect(viewToolbar.freezeXAxis)
		# 	except:
		# 		pass
		# 	try:
		# 		self.freezeAxisYLimits_action.triggered.disconnect(viewToolbar.freezeYAxis)
		# 	except:
		# 		pass
		# 	try:
		# 		self.refreshCurrentPlotWindow_action.triggered.disconnect(self.cmeView.refreshCurrentPlot)
		# 	except:
		# 		pass
		# 	try:
		# 		self.clearPlotWindow_action.triggered.disconnect()
		# 	except:
		# 		pass
		# 	try:
		# 		self.exportAsCSV_action.triggered.disconnect(self.cmeMenuFunctions.exportCSV)
		# 	except:
		# 		pass
		# # results menu
		# try:
		# 	self.load2dResults_action.triggered.disconnect(self.cmeMenuFunctions.load2dResults)
		# except:
		# 	pass
		# try:
		# 	self.load1dResults_action.triggered.disconnect(self.cmeMenuFunctions.load1dResults)
		# except:
		# 	pass
		# try:
		# 	self.loadParticlesResults_action.triggered.disconnect(self.cmeMenuFunctions.loadParticlesResults)
		# except:
		# 	pass
		# try:
		# 	self.load1d2dResults_action.triggered.disconnect(self.cmeMenuFunctions.load1d2dResults)
		# except:
		# 	pass
		# try:
		# 	self.loadHydraulicTable_action.triggered.disconnect(self.cmeMenuFunctions.loadHydraulicTables)
		# except:
		# 	pass
		# try:
		# 	self.remove1d2dResults_action.triggered.disconnect(self.cmeMenuFunctions.remove1d2dResults)
		# except:
		# 	pass
		# try:
		# 	self.remove2dResults_action.triggered.disconnect(self.cmeMenuFunctions.remove2dResults)
		# except:
		# 	pass
		# try:
		# 	self.remove1dResults_action.triggered.connect(self.cmeMenuFunctions.remove1dResults)
		# except:
		# 	pass
		# try:
		# 	self.removeParticlesResults_action.triggered.disconnect(self.cmeMenuFunctions.removeParticlesResults)
		# except:
		# 	pass
		# try:
		# 	self.closeHydraulicTable_action.triggered.disconnect(self.cmeMenuFunctions.removeHydraulicTables)
		# except:
		# 	pass
		# # result types menu
		# try:
		# 	self.setToMaximumResult_action.triggered.disconnect(self.cmeMenuFunctions.toggleResultTypeToMax)
		# except:
		# 	pass
		# try:
		# 	self.setToMinimumResult_action.triggered.disconnect(self.cmeMenuFunctions.toggleResultTypeToMin)
		# except:
		# 	pass
		# try:
		# 	self.setToSecondaryAxis_action.triggered.disconnect(self.cmeMenuFunctions.toggleResultTypeToSecondaryAxis)
		# except:
		# 	pass
		# try:
		# 	self.saveDefaultStyleRamp_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.saveDefaultStyleMap_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.saveDefaultVectorStyle_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.loadDefaultStyle_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.loadDefaultVectorStyle_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.propertiesDialog_action.triggered.disconnect()
		# except:
		# 	pass
		# try:
		# 	self.includeFlowRegime_action.triggered.disconnect(self.cmeMenuFunctions.flowRegimeToggled)
		# except:
		# 	pass

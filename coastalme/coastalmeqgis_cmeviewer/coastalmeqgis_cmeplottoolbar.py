from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.PyQt.QtWidgets  import *
from ..dataset_menu import DatasetMenu, DatasetMenuDepAv
import sys
import os
import matplotlib
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.patches import Polygon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from .coastalmeqgis_cmemenufunctions import CmeMenuFunctions
from .coastalmeqgis_cmeplottoolbar_viewtoolbar import ViewToolbar
from ..spinbox_action import SingleSpinBoxAction, DoubleSpinBoxAction
import numpy as np

from ..compatibility_routines import is_qt6



class CmePlotToolbar():
	"""
	Class for handling plotting toolbar.
	
	"""
	
	def __init__(self, cmePlot):
		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot = cmePlot
		self.cmeView = cmePlot.cmeView
		self.cmeMenuFunctions = CmeMenuFunctions(self.cmeView)
		self.averageMethodActions = []

		self.initialiseMplToolbars()
		self.initialiseMapOutputPlottingToolbar()
		self.initialiseViewToolbar()

		self.plotNoToToolbar = {
			CmePlot.TimeSeries: [self.lstActionsTimeSeries,
			                    self.viewToolbarTimeSeries,
			                    self.mpltoolbarTimeSeries],
			CmePlot.CrossSection: [self.lstActionsLongPlot,
			                      self.viewToolbarLongPlot,
			                      self.mpltoolbarLongPlot],
			CmePlot.CrossSection1D: [self.lstActionsCrossSection,
			                        self.viewToolbarCrossSection,
			                        self.mpltoolbarCrossSection],
			CmePlot.VerticalProfile: [self.lstActionsVerticalProfile,
			                         self.viewToolbarVerticalProfile,
			                         self.mpltoolbarVerticalProfile]
		}
		
	def initialiseMplToolbars(self):
		"""
		Initialises the mpl toolbars for all plot windows.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		qv = Qgis.QGIS_VERSION_INT

		w = self.cmeView.cmeOptions.iconSize
		if qv >= 31600:
			w = int(QgsApplication.scaleIconSize(self.cmeView.cmeOptions.iconSize, True))

		w2 = int(np.ceil(w*1.5))
		w3 = int(np.ceil(w2 * 6))
		w4 = int(np.ceil(w3 + w2 * 2))
		self.cmeView.mplToolbarFrame.setMinimumHeight(w2)
		self.cmeView.mplToolbarFrame.setMinimumWidth(w3)

		# Plotting Toolbar - Time series
		self.mpltoolbarTimeSeries = matplotlib.backends.backend_qt5agg.NavigationToolbar2QT(
			self.cmePlot.plotWidgetTimeSeries,
			self.cmeView.mplToolbarFrame)
		self.mpltoolbarTimeSeries.setIconSize(QSize(w, w))
		self.mpltoolbarTimeSeries.resize(QSize(w4, w2))
		self.lstActionsTimeSeries = self.mpltoolbarTimeSeries.actions()
		#self.mpltoolbarTimeSeries.removeAction(self.lstActionsTimeSeries[6])  # remove customise subplot
		self.mpltoolbarTimeSeries.removeAction(self.lstActionsTimeSeries[-1])
		self.mpltoolbarTimeSeries.removeAction(self.lstActionsTimeSeries[8])
		self.mpltoolbarTimeSeries.removeAction(self.lstActionsTimeSeries[6])
		self.mpltoolbarTimeSeries.removeAction(self.lstActionsTimeSeries[3])

		
		# Plotting Toolbar - Long plot
		self.mpltoolbarLongPlot = matplotlib.backends.backend_qt5agg.NavigationToolbar2QT(
			self.cmePlot.plotWidgetLongPlot,
			self.cmeView.mplToolbarFrame)
		self.mpltoolbarLongPlot.setIconSize(QSize(w, w))
		self.mpltoolbarLongPlot.resize(QSize(w4, w2))
		self.lstActionsLongPlot = self.mpltoolbarLongPlot.actions()
		# self.mpltoolbarLongPlot.removeAction(self.lstActionsLongPlot[6])  # remove customise subplot
		self.mpltoolbarLongPlot.removeAction(self.lstActionsLongPlot[-1])
		self.mpltoolbarLongPlot.removeAction(self.lstActionsLongPlot[8])
		self.mpltoolbarLongPlot.removeAction(self.lstActionsLongPlot[6])
		self.mpltoolbarLongPlot.removeAction(self.lstActionsLongPlot[3])
		self.mpltoolbarLongPlot.setVisible(False)
		
		# Plotting Toolbar - Cross section
		self.mpltoolbarCrossSection = matplotlib.backends.backend_qt5agg.NavigationToolbar2QT(
			self.cmePlot.plotWidgetCrossSection,
			self.cmeView.mplToolbarFrame)
		self.mpltoolbarCrossSection.setIconSize(QSize(w, w))
		self.mpltoolbarCrossSection.resize(QSize(w4, w2))
		self.lstActionsCrossSection = self.mpltoolbarCrossSection.actions()
		# self.mpltoolbarCrossSection.removeAction(self.lstActionsCrossSection[6])  # remove customise subplot
		self.mpltoolbarCrossSection.removeAction(self.lstActionsCrossSection[-1])
		self.mpltoolbarCrossSection.removeAction(self.lstActionsCrossSection[8])
		self.mpltoolbarCrossSection.removeAction(self.lstActionsCrossSection[6])
		self.mpltoolbarCrossSection.removeAction(self.lstActionsCrossSection[3])
		self.mpltoolbarCrossSection.setVisible(False)

		# Plotting Toolbar - vertical profile
		self.mpltoolbarVerticalProfile = matplotlib.backends.backend_qt5agg.NavigationToolbar2QT(
			self.cmePlot.plotWidgetVerticalProfile,
			self.cmeView.mplToolbarFrame)
		self.mpltoolbarVerticalProfile.setIconSize(QSize(w, w))
		self.mpltoolbarVerticalProfile.resize(QSize(w4, w2))
		self.lstActionsVerticalProfile = self.mpltoolbarVerticalProfile.actions()
		# self.mpltoolbarVerticalProfile.removeAction(self.lstActionsVerticalProfile[6])  # remove customise subplot
		self.mpltoolbarVerticalProfile.removeAction(self.lstActionsVerticalProfile[-1])
		self.mpltoolbarVerticalProfile.removeAction(self.lstActionsVerticalProfile[8])
		self.mpltoolbarVerticalProfile.removeAction(self.lstActionsVerticalProfile[6])
		self.mpltoolbarVerticalProfile.removeAction(self.lstActionsVerticalProfile[3])
		self.mpltoolbarVerticalProfile.setVisible(False)

		# self.mpltoolbarTimeSeries.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mpltoolbarTimeSeries, self.cmeView.mplToolbarFrame))
		# self.mpltoolbarLongPlot.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mpltoolbarLongPlot, self.cmeView.mplToolbarFrame))
		# self.mpltoolbarCrossSection.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mpltoolbarCrossSection, self.cmeView.mplToolbarFrame))
		# self.mpltoolbarVerticalProfile.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mpltoolbarVerticalProfile, self.cmeView.mplToolbarFrame))

		return True
		
	def initialiseMapOutputPlottingToolbar(self):
		"""
		Initialises toolbar for the map output plotting i.e. time series, cross section / long plot, flux
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		qv = Qgis.QGIS_VERSION_INT

		w = self.cmeView.cmeOptions.iconSize
		if qv >= 31600:
			w = int(QgsApplication.scaleIconSize(self.cmeView.cmeOptions.iconSize, True))

		w2 = int(np.ceil(w * 1.5))
		w3 = int(np.ceil(w2 * 6))
		w4 = int(np.ceil(w3 + w2 * 2))

		# toolbar settings
		self.mapOutputPlotToolbar = QToolBar('Map Output Plotting', self.cmeView.MapOutputPlotFrame)
		self.mapOutputPlotToolbar.setIconSize(QSize(w, w))
		self.cmeView.MapOutputPlotFrame.setMinimumHeight(w2)
		self.mapOutputPlotToolbar.resize(QSize(w4, w2))

		# 3D mesh averaging plotting
		self.mesh3dPlotToolbar = QToolBar('3D Mesh Plotting', self.cmeView.Mesh3DToolbarFrame)
		self.mesh3dPlotToolbar.setIconSize(QSize(w, w))
		self.cmeView.Mesh3DToolbarFrame.setMinimumHeight(w2)
		self.cmeView.Mesh3DToolbarFrame.setMinimumWidth(w3)
		self.mesh3dPlotToolbar.resize(QSize(w4, w2))
		
		# icons
		dir = os.path.dirname(os.path.dirname(__file__))
		tsIcon = QIcon(os.path.join(dir, "icons", "results.svg"))
		csIcon = QIcon(os.path.join(dir, "icons", "cross_section.svg"))
		fluxIcon = QIcon(os.path.join(dir, "icons", "flux_line.svg"))
		fluxSecAxisIcon = QIcon(os.path.join(dir, "icons", "2nd_axis.svg"))
		cursorTrackingIcon = QIcon(os.path.join(dir, "icons", "cursor_tracking.svg"))
		meshGridIcon = QIcon(os.path.join(dir, "icons", "mesh_grid.svg"))
		#meshAveragingIcon = QgsApplication.getThemeIcon('/propertyicons/meshaveraging.svg')
		tsDepthAvIcon = QIcon(os.path.join(dir, "icons", "results_ts_3d.svg"))
		csDepthAvIcon = QIcon(os.path.join(dir, "icons", "results_xs_3d.svg"))
		curtainPlotIcon = QIcon(os.path.join(dir, "icons", "curtain_plot.svg"))
		verticalProfileIcon = QIcon(os.path.join(dir, "icons", "vertical_profile.svg"))
		
		# buttons
		self.plotTSMenu = DatasetMenu('Plot Time Series From Map Output')
		self.plotTSMenu.menuAction().setIcon(tsIcon)
		self.plotTSMenu.menuAction().setCheckable(True)
		self.plotLPMenu = DatasetMenu('Plot Cross Section / Long Plot From Map Output')
		self.plotLPMenu.menuAction().setIcon(csIcon)
		self.plotLPMenu.menuAction().setCheckable(True)
		self.plotFluxButton = QToolButton(self.mapOutputPlotToolbar)
		self.plotFluxButton.setCheckable(True)
		self.plotFluxButton.setIcon(fluxIcon)
		self.plotFluxButton.setToolTip('Plot Flux From Map Output')
		self.fluxSecAxisButton = QToolButton(self.mapOutputPlotToolbar)
		self.fluxSecAxisButton.setCheckable(True)
		self.fluxSecAxisButton.setIcon(fluxSecAxisIcon)
		self.fluxSecAxisButton.setToolTip('Flux Plot Secondary Axis')
		self.cursorTrackingButton = QToolButton(self.mapOutputPlotToolbar)
		self.cursorTrackingButton.setCheckable(True)
		self.cursorTrackingButton.setChecked(False)
		self.cursorTrackingButton.setIcon(cursorTrackingIcon)
		self.cursorTrackingButton.setToolTip('Live Map Tracking')
		self.meshGridButton = QToolButton(self.mapOutputPlotToolbar)
		self.meshGridButton.setCheckable(True)
		self.meshGridButton.setToolTip('Toggle Mesh')
		self.meshGridAction = QAction(meshGridIcon, 'Toggle Mesh Rendering', self.meshGridButton)
		self.meshGridAction.setCheckable(True)
		self.meshGridButton.setDefaultAction(self.meshGridAction)
		self.averageMethodTSMenu = DatasetMenuDepAv("3D to 2D Averaging Time Series")
		self.averageMethodTSMenu.menuAction().setIcon(tsDepthAvIcon)
		self.averageMethodTSMenu.menuAction().setCheckable(True)
		self.averageMethodCSMenu = DatasetMenuDepAv("3D to 2D Averaging Cross Section")
		self.averageMethodCSMenu.menuAction().setIcon(csDepthAvIcon)
		self.averageMethodCSMenu.menuAction().setCheckable(True)
		self.addAverageMethods(self.averageMethodTSMenu)
		self.addAverageMethods(self.averageMethodCSMenu)
		self.curtainPlotMenu = DatasetMenu("Curtain Plot")
		self.curtainPlotMenu.menuAction().setIcon(curtainPlotIcon)
		self.curtainPlotMenu.menuAction().setCheckable(True)
		self.plotVPMenu = DatasetMenu("Vertical Profile")
		self.plotVPMenu.menuAction().setIcon(verticalProfileIcon)
		self.plotVPMenu.menuAction().setCheckable(True)

		# add buttons to toolbar
		self.mapOutputPlotToolbar.addAction(self.plotTSMenu.menuAction())
		self.mapOutputPlotToolbar.addAction(self.plotLPMenu.menuAction())
		self.mapOutputPlotToolbar.addWidget(self.plotFluxButton)
		self.mapOutputPlotToolbar.addWidget(self.fluxSecAxisButton)
		self.mapOutputPlotToolbar.addWidget(self.cursorTrackingButton)
		self.mapOutputPlotToolbar.addWidget(self.meshGridButton)
		self.mesh3dPlotToolbar.addAction(self.averageMethodTSMenu.menuAction())
		self.mesh3dPlotToolbar.addAction(self.averageMethodCSMenu.menuAction())
		self.mesh3dPlotToolbar.addAction(self.curtainPlotMenu.menuAction())
		self.mesh3dPlotToolbar.addAction(self.plotVPMenu.menuAction())
		
		# connect buttons
		self.plotTSMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataTimeSeries2D))
		self.plotLPMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataCrossSection2D))
		self.plotFluxButton.released.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataFlow2D))
		self.cursorTrackingButton.released.connect(self.cursorTrackingToggled)
		self.meshGridAction.triggered.connect(self.cmeMenuFunctions.toggleMeshRender)
		self.curtainPlotMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataCurtainPlot))
		self.averageMethodTSMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataTimeSeriesDepAv))
		self.averageMethodCSMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataCrossSectionDepAv))
		self.plotVPMenu.menuAction().triggered.connect(lambda: self.mapOutputPlottingButtonClicked(CmePlot.DataVerticalProfile))

		self.plotDataToPlotMenu = {
			CmePlot.DataTimeSeries2D: self.plotTSMenu.menuAction(),
			CmePlot.DataCrossSection2D: self.plotLPMenu.menuAction(),
			CmePlot.DataFlow2D: self.plotFluxButton,
			CmePlot.DataTimeSeries1D: None,
			CmePlot.DataCrossSection1D: None,
			CmePlot.DataUserData: None,
			CmePlot.DataCurrentTime: None,
			CmePlot.DataTimeSeriesStartLine: None,
			CmePlot.DataCrossSectionStartLine: None,
			CmePlot.DataCrossSectionStartLine1D: None,
			CmePlot.DataCurtainPlot: self.curtainPlotMenu.menuAction(),
			CmePlot.DataTimeSeriesDepAv: self.averageMethodTSMenu.menuAction(),
			CmePlot.DataCrossSectionDepAv: self.averageMethodCSMenu.menuAction(),
			CmePlot.DataVerticalProfileStartLine: None,
			CmePlot.DataVerticalProfile: self.plotVPMenu.menuAction(),
			CmePlot.DataCrossSection1DViewer: None,
			CmePlot.DataHydraulicProperty: None,
			CmePlot.DataVerticalMesh: None,
		}

		# self.mapOutputPlotToolbar.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mapOutputPlotToolbar, self.cmeView.MapOutputPlotFrame))
		# self.mesh3dPlotToolbar.iconSizeChanged.connect(lambda e: self.cmeView.toolbarIconSizeChanged(e, self.mesh3dPlotToolbar, self.cmeView.Mesh3DToolbarFrame))

		return True
	
	def initialiseViewToolbar(self):

		from .coastalmeqgis_cmeplot import CmePlot
		
		# view menu - time series
		self.viewToolbarTimeSeries = ViewToolbar(self, CmePlot.TimeSeries)
		
		# view menu - long plot
		self.viewToolbarLongPlot = ViewToolbar(self, CmePlot.CrossSection)
		self.viewToolbarLongPlot.setVisible(False)
		
		# view menu - 1D cross section plot
		self.viewToolbarCrossSection = ViewToolbar(self, CmePlot.CrossSection1D)
		self.viewToolbarCrossSection.setVisible(False)

		# view menu - vertical profile plot
		self.viewToolbarVerticalProfile = ViewToolbar(self, CmePlot.VerticalProfile)
		self.viewToolbarVerticalProfile.setVisible(False)
		
		return True
		
	def setToolbarActive(self, plotNo):
		"""
		Sets the toolbar active based on the enumerator.
		
		:param plotNo: int enumerator -> 0: time series plot
										 1: long profile plot
										 2: cross section plot
		:return: bool -> True for successful, False for unsuccessful
		"""
		

		toolbar, viewToolbar, mplToolbar = self.plotNoToToolbar[plotNo]
		viewToolbar.setVisible(True)
		mplToolbar.setVisible(True)
		for pn, tb in self.plotNoToToolbar.items():
			if pn != plotNo:
				tb[1].setVisible(False)
				tb[2].setVisible(False)
		
		# menubar
		self.cmeView.cmeMenuBar.viewMenu.clear()
		self.cmeView.cmeMenuBar.loadViewMenu(plotNo, update=True)
		self.cmeView.cmeMenuBarSecond.viewMenu.clear()
		self.cmeView.cmeMenuBarSecond.loadViewMenu(plotNo, update=True)

		self.cmeView.cmeMenuBar.settingsMenu.clear()
		self.cmeView.cmeMenuBar.loadSettingsMenu(plotNo, update=True)
		self.cmeView.cmeMenuBarSecond.settingsMenu.clear()
		self.cmeView.cmeMenuBarSecond.loadSettingsMenu(plotNo, update=True)

		self.cmeView.cmeMenuBar.exportMenu.clear()
		self.cmeView.cmeMenuBar.loadExportMenu(plotNo, update=True)
		self.cmeView.cmeMenuBarSecond.exportMenu.clear()
		self.cmeView.cmeMenuBarSecond.loadExportMenu(plotNo, update=True)

		# context menu
		self.cmeView.cmeContextMenu.plotMenu.clear()
		self.cmeView.cmeContextMenu.loadPlotMenu(plotNo, update=True)

		return True
	
	def mapOutputPlottingButtonClicked(self, dataType, **kwargs):

		from .coastalmeqgis_cmeplot import CmePlot

		menu = self.plotDataToPlotMenu[dataType]
		graphic = self.cmePlot.plotDataToGraphic[dataType]
		if menu.isChecked():
			for dtp in self.cmePlot.plotDataPlottingTypes:
				menu2 = self.plotDataToPlotMenu[dtp]
				graphic2 = self.cmePlot.plotDataToGraphic[dtp]
				if menu != menu2:
					if menu2 is not None: menu2.setChecked(False)
				if graphic != graphic2:
					if graphic2 is not None:
						if graphic2.cursorTrackingConnected:
							graphic2.mouseTrackDisconnect()
			if self.getCheckedItemsFromPlotOptions(dataType):
				self.cmeView.tabWidget.setCurrentIndex(self.cmePlot.plotDataToPlotType[dataType])
				if self.cmeView.cboSelectType.currentText() == 'Layer Selection':
					self.cmePlot.cmePlotSelection.useSelection(dataType, **kwargs)
				else:
					graphic.startRubberBand()
			else:
				menu.setChecked(False)
		else:
			if graphic.cursorTrackingConnected:
				graphic.mouseTrackDisconnect()

		return False
	
	def addItemToPlotOptions(self, type, dataType=None, static=False):

		from .coastalmeqgis_cmeplot import CmePlot

		if dataType is None:
			for dataType in self.cmePlot.plotDataPlottingTypes:
				if static and dataType in self.cmePlot.plotDataTemporalPlottingTypes:
					continue
				self.addItemToPlotOption(type, dataType)
		else:
			self.addItemToPlotOption(type, dataType)
		
		return True

	def addItemToPlotOption(self, type, dataType):

		from .coastalmeqgis_cmeplot import CmePlot

		menu = self.plotDataToPlotMenu[dataType]

		if menu is not None:
			if isinstance(menu, QAction):
				if is_qt6:
					menu = menu.parent()
				else:
					menu = menu.parentWidget()

			action = QAction(type, menu)
			action.setCheckable(True)
			if dataType == CmePlot.DataTimeSeriesDepAv or dataType == CmePlot.DataCrossSectionDepAv:
				menu.addActionToSubMenus(action)
			else:
				menu.addAction(action)
	
	def getItemsFromPlotOptions(self, plotNo, method='plot'):

		from .coastalmeqgis_cmeplot import CmePlot

		if method == 'plot':
			if plotNo == CmePlot.TimeSeries:
				menu = self.plotTSMenu
			elif plotNo == CmePlot.CrossSection:
				menu = self.plotLPMenu
			else:
				return []
		elif method == 'data type':
			if plotNo == CmePlot.DataTimeSeries2D:
				menu = self.plotTSMenu
			elif plotNo == CmePlot.DataCrossSection2D:
				menu = self.plotLPMenu
			elif plotNo == CmePlot.DataCurtainPlot:
				menu = self.curtainPlotMenu
			elif plotNo == CmePlot.DataTimeSeriesDepAv:
				menu = self.averageMethodTSMenu
			elif plotNo == CmePlot.DataCrossSectionDepAv:
				menu = self.averageMethodCSMenu
			elif plotNo == CmePlot.DataVerticalProfile:
				menu = self.plotVPMenu
			else:
				return []

		if method == 'data type' and (plotNo == CmePlot.DataTimeSeriesDepAv or plotNo == CmePlot.DataCrossSectionDepAv):
			return [x for x in menu.resultTypes()]

		return [x.text() for x in menu.actions()]

	def getCheckedItemsFromPlotOptions(self, dataType, *args, **kwargs):

		from .coastalmeqgis_cmeplot import CmePlot

		if dataType not in self.plotDataToPlotMenu:
			return False

		menu = self.plotDataToPlotMenu[dataType]
		if isinstance(menu, QAction):
			if is_qt6:
				menu = menu.parent()
			else:
				menu = menu.parentWidget()
		elif isinstance(menu, QToolButton):
			return True

		return menu.checkedActions(*args, **kwargs)

	def setCheckedItemsPlotOptions(self, dataType, items):

		from .coastalmeqgis_cmeplot import CmePlot

		menu = self.plotDataToPlotMenu[dataType]
		if isinstance(menu, QAction):
			if is_qt6:
				menu = menu.parent()
			else:
				menu = menu.parentWidget()
		elif isinstance(menu, QToolButton):
			return True

		return menu.setCheckedActions(items)
	
	def cursorTrackingToggled(self):
		if self.cursorTrackingButton.isChecked():
			self.cmeView.cmeOptions.liveMapTracking = True
		else:
			self.cmeView.cmeOptions.liveMapTracking = False
			
		return True

	def addAverageMethods(self, parentMenu):
		methods = [
			"Single Vertical Level (from top)",
			"Single Vertical Level (from bottom)",
			"Multi Vertical Level (from top)",
			"Multi Vertical Level (from bottom)",
			"Sigma",
			"Depth (relative to surface)",
			"Height (relative to bed level)",
			"Elevation (absolute to model's dacmem)"
		]

		parentMenu.clear()
		for method in methods:
			menu = DatasetMenu(method, self.averageMethodTSMenu)
			menu.menuAction().setCheckable(True)

			if "Single Vertical Level" in method:
				self.singleVerticalLevelMethod(menu, False)
			elif 'Multi Vertical Level' in method:
				self.multiVerticalLevelMethod(menu, False)
			elif 'Sigma' in method:
				self.sigmaMethod(menu, False)
			elif 'relative to' in method:
				self.relativeDepthMethod(menu, False)
			elif 'absolute to' in method:
				self.absoluteElevationMethod(menu, False)

			parentMenu.addAction(menu.menuAction())
			self.averageMethodActions.append(menu)

	def generateDepthAveragingAction(self, avType, parentMenu, bAdd=False):
		from .coastalmeqgis_cmeplot import CmePlot

		if not [x for x in parentMenu.menu().actions() if avType.lower() in x.text().lower()]:
			return None
		menu = [x for x in parentMenu.menu().actions() if avType.lower() in x.text().lower()][0]
		if 'single vertical level' in avType.lower():
			action = SingleSpinBoxAction(menu, bAdd, "Vertical Layer Index", range=(1, 99999))
		elif 'multi vertical level' in avType.lower():
			action = SingleSpinBoxAction(menu, bAdd, "Start Vertical Layer Index", "End Vertical Layer Index",
			                             range=(1, 99999))
		elif 'sigma' in avType.lower():
			action = DoubleSpinBoxAction(menu, bAdd, "Start Fraction", "End Fraction",
			                             range=(0, 99999), decimals=2, single_step=0.1,
			                             value=(0, 1))
		elif 'relative to' in avType.lower():
			action = DoubleSpinBoxAction(menu, bAdd, "Start Depth", "End Depth",
			                             range=(0, 99999), decimals=2, single_step=1.0,
			                             value=(0, 10))
		elif 'absolute to' in avType.lower():
			action = DoubleSpinBoxAction(menu, bAdd, "Start Elevation", "End Elevation",
			                             range=(-99999, 99999), decimals=2, single_step=1.0,
			                             value=(0, -10))

		items = []
		while True:
			if is_qt6:
				parentMenu0 = parentMenu.parent()
			else:
				parentMenu0 = parentMenu.parentWidget()
			if parentMenu0 is None:
				break
			parentMenu = parentMenu0
		if isinstance(parentMenu, QMenu):
			if 'time series' in parentMenu.menuAction().text().lower():
				items = self.getItemsFromPlotOptions(CmePlot.DataTimeSeries2D, 'data type')
			else:
				items = self.getItemsFromPlotOptions(CmePlot.DataCrossSection2D, 'data type')
		elif isinstance(parentMenu, QAction):
			if 'time series' in parentMenu.text().lower():
				items = self.getItemsFromPlotOptions(CmePlot.DataTimeSeries2D, 'data type')
			else:
				items = self.getItemsFromPlotOptions(CmePlot.DataCrossSection2D, 'data type')

		action.cboSetItems(items)
		return action

	def singleVerticalLevelMethod(self, menu: QMenu, bAdd: bool) -> None:
		if bAdd:
			action = SingleSpinBoxAction(menu, bAdd, "Vertical Layer Index", range=(1, 99999))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			lastAction = menu.actions()[-2]  # insert before separator
			menu.insertAction(lastAction, action)
			if len(menu.actions()) > 3:
				if not menu.actions()[0].bCheckBox:
					menu.actions()[0].insertCheckbox()
				items = menu.actions()[0].cboItems()
				ci = menu.actions()[-4].cboCurrentItem()
				action.cboSetItems(items, set_cbo_current_item=ci)
		else:
			action = SingleSpinBoxAction(menu, bAdd, "Vertical Layer Index", range=(1, 99999))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			menu.addAction(action)
			menu.addSeparator()
			action = QAction("Add Additional...", menu)
			menu.addAction(action)
			action.triggered.connect(lambda e: self.singleVerticalLevelMethod(menu, True))

	def multiVerticalLevelMethod(self, menu: QMenu, bAdd: bool) -> None:
		if bAdd:
			action = SingleSpinBoxAction(menu, bAdd, "Start Vertical Layer Index", "End Vertical Layer Index",
			                             range=(1, 99999))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			lastAction = menu.actions()[-2]  # insert before separator
			menu.insertAction(lastAction, action)
			if len(menu.actions()) > 3:
				if not menu.actions()[0].bCheckBox:
					menu.actions()[0].insertCheckbox()
				items = menu.actions()[0].cboItems()
				ci = menu.actions()[-4].cboCurrentItem()
				action.cboSetItems(items, set_cbo_current_item=ci)
		else:
			action = SingleSpinBoxAction(menu, bAdd, "Start Vertical Layer Index", "End Vertical Layer Index",
			                             range=(1, 99999))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			menu.addAction(action)
			menu.addSeparator()
			action = QAction("Add Additional...", menu)
			menu.addAction(action)
			action.triggered.connect(lambda e: self.multiVerticalLevelMethod(menu, True))

	def sigmaMethod(self, menu: QMenu, bAdd: bool) -> None:
		if bAdd:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Fraction", "End Fraction",
			                             range=(0, 99999), decimals=2, single_step=0.1,
			                             value=(0, 1))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			lastAction = menu.actions()[-2]  # insert before separator
			menu.insertAction(lastAction, action)
			if len(menu.actions()) > 3:
				if not menu.actions()[0].bCheckBox:
					menu.actions()[0].insertCheckbox()
				items = menu.actions()[0].cboItems()
				ci = menu.actions()[-4].cboCurrentItem()
				action.cboSetItems(items, set_cbo_current_item=ci)
		else:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Fraction", "End Fraction",
			                             range=(0, 99999), decimals=2, single_step=0.1,
			                             value=(0, 1))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			menu.addAction(action)
			menu.addSeparator()
			action = QAction("Add Additional...", menu)
			menu.addAction(action)
			action.triggered.connect(lambda e: self.sigmaMethod(menu, True))

	def relativeDepthMethod(self, menu: QMenu, bAdd: bool) -> None:
		if bAdd:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Depth", "End Depth",
			                             range=(0, 99999), decimals=2, single_step=1.0,
			                             value=(0, 10))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			lastAction = menu.actions()[-2]  # insert before separator
			menu.insertAction(lastAction, action)
			if len(menu.actions()) > 3:
				if not menu.actions()[0].bCheckBox:
					menu.actions()[0].insertCheckbox()
				items = menu.actions()[0].cboItems()
				ci = menu.actions()[-4].cboCurrentItem()
				action.cboSetItems(items, set_cbo_current_item=ci)
		else:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Depth", "End Depth",
			                             range=(0, 99999), decimals=2, single_step=1.0,
			                             value=(0, 10))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			menu.addAction(action)
			menu.addSeparator()
			action = QAction("Add Additional...", menu)
			menu.addAction(action)
			action.triggered.connect(lambda e: self.relativeDepthMethod(menu, True))

	def absoluteElevationMethod(self, menu: QMenu, bAdd: bool) -> None:
		if bAdd:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Elevation", "End Elevation",
			                             range=(-99999, 99999), decimals=2, single_step=1.0,
			                             value=(0, -10))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			lastAction = menu.actions()[-2]  # insert before separator
			menu.insertAction(lastAction, action)
			if len(menu.actions()) > 3:
				if not menu.actions()[0].bCheckBox:
					menu.actions()[0].insertCheckbox()
				items = menu.actions()[0].cboItems()
				ci = menu.actions()[-4].cboCurrentItem()
				action.cboSetItems(items, set_cbo_current_item=ci)
		else:
			action = DoubleSpinBoxAction(menu, bAdd, "Start Elevation", "End Elevation",
			                             range=(-99999, 99999), decimals=2, single_step=1.0,
			                             value=(0, -10))
			action.setCheckable(True)
			action.removeActionRequested.connect(lambda e: self.removeAveragingMethod(e, menu))
			menu.addAction(action)
			menu.addSeparator()
			action = QAction("Add Additional...", menu)
			menu.addAction(action)
			action.triggered.connect(lambda e: self.absoluteElevationMethod(menu, True))

	def removeAveragingMethod(self, p, menu):
		if len(menu.actions()) > 3:
			action = menu.actionAt(p)
			menu.removeAction(action)
			if len(menu.actions()) <= 3:
				if menu.actions()[0].bCheckBox:
					menu.actions()[0].removeCheckbox()

	def getAveragingMethods(self, dataType, groupMetadata):
		"""

		"""

		from .coastalmeqgis_cmeplot import CmePlot

		# if groupMetadata.maximumVerticalLevelsCount() < 2: return [None]

		if dataType == CmePlot.DataTimeSeriesDepAv or dataType == CmePlot.DataCrossSectionDepAv:
			if isinstance(self.plotDataToPlotMenu[dataType], (QAction, QWidgetAction)) and is_qt6:
				menu = self.plotDataToPlotMenu[dataType].parent()
			else:
				menu = self.plotDataToPlotMenu[dataType].parentWidget()
		else:
			return [None]

		averagingMethods = []
		for action in menu.actions():
			if action.isChecked():
				counter = 0
				for action2 in action.menu().actions():
					if action2.isChecked():
						if groupMetadata.maximumVerticalLevelsCount() < 2:
							averagingMethods.append(None)
						else:
							averagingMethods.append('{0}_{1}'.format(action.text(), counter))
							counter += 1

		if averagingMethods:
			return averagingMethods
		else:
			return [None]

	def getAveragingParameters(self, dataType, averagingMethod):
		if isinstance(self.plotDataToPlotMenu[dataType], (QAction, QWidgetAction)) and is_qt6:
			menu = self.plotDataToPlotMenu[dataType].parent()
		else:
			menu = self.plotDataToPlotMenu[dataType].parentWidget()

		for action in menu.actions():
			if action.text() in averagingMethod:
				counter = 0
				for action2 in action.menu().actions():
					if action2.isChecked():
						if counter == int(averagingMethod[-1]):
							return action2.values()
						else:
							counter += 1

		return None

	def qgisDisconnect(self):
		# mpl toolbar
		try:
			self.plotTSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotLPMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotFluxButton.released.disconnect()
		except:
			pass
		try:
			self.cursorTrackingButton.released.disconnect(self.cursorTrackingToggled)
		except:
			pass
		try:
			self.meshGridAction.triggered.disconnect(self.cmeMenuFunctions.toggleMeshRender)
		except:
			pass
		try:
			self.curtainPlotMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.averageMethodTSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.averageMethodCSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotVPMenu.menuAction().triggered.disconnect()
		except:
			pass
		# view toolbars
		self.viewToolbarTimeSeries.qgisDisconnect()
		self.viewToolbarLongPlot.qgisDisconnect()
		self.viewToolbarCrossSection.qgisDisconnect()
		self.viewToolbarVerticalProfile.qgisDisconnect()
		# map plotting toolbar
		try:
			self.plotTSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotLPMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotFluxButton.released.disconnect()
		except:
			pass
		try:
			self.cursorTrackingButton.released.disconnect(self.cursorTrackingToggled)
		except:
			pass
		try:
			self.meshGridAction.triggered.disconnect(self.cmeMenuFunctions.toggleMeshRender)
		except:
			pass
		try:
			self.curtainPlotMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.averageMethodTSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.averageMethodCSMenu.menuAction().triggered.disconnect()
		except:
			pass
		try:
			self.plotVPMenu.menuAction().triggered.disconnect()
		except:
			pass








from datetime import datetime, timedelta
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.PyQt.QtWidgets import *
from .coastalmeqgis_turesults1d import TuResults1D
from .coastalmeqgis_turesults2d import TuResults2D
from .coastalmeqgis_turesultsParticles import TuResultsParticles
from .tuResultsNcGrid import TuResultsNcGrid
from ..dataset_view import DataSetModel
from ..coastalmeqgis_library import (convertFormattedTimeToTime,
                                  convertTimeToFormattedTime, roundSeconds,
                                  isSame_float, dt2qdt, roundSeconds2, datetime2timespec, qdt2dt,
                                  isSame_time)
from coastalme.toc.toc import coastalmeqgis_find_layer, findAllMeshLyrs
from ..dataset_menu import DatasetMenuDepAv
from ..COASTALME_XS import XS
import numpy as np
import re
try:
	from pathlib import Path
except ImportError:
	from ..pathlib_ import Path_ as Path
from ..coastalme_results_gpkg import ResData_GPKG
from ..gui import Logging

from ..compatibility_routines import QT_ITEM_SELECTION_SELECT, QT_TIMESPEC_UTC, is_qt6, QT_ITEM_SELECTION_DESELECT


PROFILING = False

class TuResults():
	"""
	Parent class for handling 1D, 2D and Particles results classes.

	"""

	Results2D = [1, 2]
	Results1D = [4, 5, 6, 7, 8]
	TimePrecision = 0.000001
	OtherTypes = ['_ts', '_lp', '_particles', '_cs', '_nc_grid']

	def __init__(self, TuView=None):
		qv = Qgis.QGIS_VERSION_INT
		if TuView is not None:
			self.tuView = TuView
			self.iface = TuView.iface
			self.results = {}  # dict - e.g. { M01_5m_001: { depth: { '0.000000': ( timestep, type, QgsMeshDatasetIndex )}, point_ts: ( types, timesteps ) } }
			self.cboTime2timekey = {}
			self.timekey2time = {}  # e.g. {'1.833333': 1.8333333}
			self.timekey2date = {}  # e.g. {'1.833333': '01/01/2000 09:00:00'}
			self.time2date = {}
			self.date2timekey = {}
			self.date2time = {}
			# date stuff with timespec for display purposes
			self.timekey2date_tspec = {}
			self.time2date_tspec = {}
			self.date_tspec2timekey = {}
			self.date_tspec2time = {}
			self.date2date_tspec = {}
			self.date_tspec2date = {}

			self.secondaryAxisTypes = []
			self.maxResultTypes = []
			self.minResultTypes = []
			self.activeTime = None  # active time for rendering
			self.activeTime_ = None
			self.activeResults = []  # str result type names
			self.activeResultsTypes = []  # int result types (e.g. 1 - scalar, 2 - vector...)
			self.activeResultsIndexes = []  # QModelIndex
			self.activeResultsItems = []  # DataSetTreeNode
			self.dateFormat = '%d/%m/%Y %H:%M:%S'  # for time combobox not plotting
			self._dateFormat = '{0:%d}/{0:%m}/{0:%Y} {0:%H}:{0:%M}:{0:%S}'  # for time combobox not plotting
			if qv >= 31300:
				if self.iface is not None:
					self.timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
				else:
					self.timeSpec = QT_TIMESPEC_UTC
			else:
				self.timeSpec = QT_TIMESPEC_UTC
			self.defaultTimeSpec = QT_TIMESPEC_UTC
			self.loadedTimeSpec = QT_TIMESPEC_UTC

			# 1D results
			self.tuResults1D = TuResults1D(TuView)

			# 2D results
			self.tuResults2D = TuResults2D(TuView)

			# Particles results
			self.tuResultsParticles = TuResultsParticles(TuView)

			# netcdf grid
			self.tuResultsNcGrid = TuResultsNcGrid(TuView)

			self.dt = None
			self._res_names = [x for x in self.results.keys()]

			self.tmp_reference_time = None

	def importResults(self, type, inFileNames, **kwargs):
		"""
		Import results 1D or 2D or Particles

		:param type: str -> 'mesh' or 'timeseries' or 'particles'
		:param inFileNames: list -> str file path
		:return: bool -> True for successful, False for unsuccessful
		"""

		result = False
		if type.lower() == 'mesh':
			result = self.tuResults2D.importResults(inFileNames)
		elif type.lower() == 'timeseries fm':
			result = self.tuResults1D.importResultsFM(inFileNames[0], inFileNames[1], inFileNames[2:])
		elif type.lower() == 'timeseries':
			result = self.tuResults1D.importResults(inFileNames)
		elif type.lower() == 'particles':
			result = self.tuResultsParticles.importResults(inFileNames)
		elif type.lower() == 'nc_grid':
			try:
				result = self.tuResultsNcGrid.importResults(inFileNames, **kwargs)
			except Exception as e:
				QMessageBox.warning(self.tuView, 'Load NetCDF Grid', str(e))
				result = False
		if not result:
			return False

		update = self.updateResultTypes(select_first_dataset=True)

		if not update:
			return False

		return True

	def updateActiveTime(self):
		qv = Qgis.QGIS_VERSION_INT
		if qv < 31600:
			self.updateActiveTime_old()
		else:
			self.updateActiveTime_31600()

	def updateActiveTime_old(self):
		"""
		Updates the active time based on the time in the ui.

		:return: bool -> True for successful, False for unsuccessful
		"""

		i = self.tuView.cboTime.currentIndex()
		self.tuView.sliderTime.setSliderPosition(i)

		self.activeTime = None
		if i != -1:
			self.activeTime = self.tuView.cboTime.currentText()
			if not self.tuView.tuOptions.xAxisDates:
				#unit = self.tuView.tuOptions.timeUnits
				#self.activeTime = '{0:.6f}'.format(convertFormattedTimeToTime(self.activeTime, unit=unit))
				if self.activeTime in self.cboTime2timekey:
					self.activeTime = self.cboTime2timekey[self.activeTime]
				else:
					unit = self.tuView.tuOptions.timeUnits
					self.activeTime = '{0:.6f}'.format(convertFormattedTimeToTime(self.activeTime, unit=unit))
			else:
				# modelDates = sorted([x for x in self.date2time.keys()])
				modelDates = sorted([x for x in self.date_tspec2time.keys()])
				self.activeTime = datetime.strptime(self.activeTime, self.dateFormat)
				self.activeTime = self.findTimeClosest(None, None, self.activeTime, modelDates, True, 'higher')
				# self.activeTime = self.date2timekey[self.activeTime]
				self.activeTime = self.date_tspec2timekey[self.activeTime]

		self.updateQgsTime()
		self.tuResultsParticles.updateActiveTime()

	def updateActiveTime_31600(self):
		"""
		Updates the active time based on the time in the ui.
		"""

		i = self.tuView.cboTime.currentIndex()
		self.tuView.sliderTime.setSliderPosition(i)

		self.activeTime = None
		if i != -1:
			self.activeTime = self.tuView.cboTime.currentText()
			if not self.tuView.tuOptions.xAxisDates:
				if self.activeTime in self.cboTime2timekey:
					self.activeTime = self.cboTime2timekey[self.activeTime]
					self.activeTime = self.timekey2time[self.activeTime]
				else:
					unit = self.tuView.tuOptions.timeUnits
					self.activeTime = convertFormattedTimeToTime(self.activeTime, unit=unit)
				zt = self.tuView.tuOptions.zeroTime
				self.activeTime = zt + timedelta(hours=self.activeTime)
			else:
				self.activeTime = datetime.strptime(self.activeTime, self.dateFormat)

		self.updateQgsTime()
		self.tuResultsParticles.updateActiveTime()
		self.tuResultsNcGrid.updateActiveTime()

	def timeFromString(self, time, return_rel_time=True):
		"""
		Takes a time string and returns model time, considering
		such things as timespec.
		"""

		return_time = None
		if not self.tuView.tuOptions.xAxisDates:
			if time in self.cboTime2timekey:
				return_time = self.cboTime2timekey[time]
			else:
				unit = self.tuView.tuOptions.timeUnits
				return_time = '{0:.6f}'.format(convertFormattedTimeToTime(time, unit=unit))
		else:
			modelDates = sorted([x for x in self.date_tspec2time.keys()])
			return_time = datetime.strptime(time, self.dateFormat)
			return_time = self.findTimeClosest(None, None, return_time, modelDates, True, 'higher')
			return_time = self.date_tspec2timekey[return_time]

		if return_rel_time:
			if return_time in self.timekey2time:
				return_time = self.timekey2time[return_time]
			else:
				return_time = 0
		else:
			if return_time in self.timekey2date:
				return_time = self.timekey2date[return_time]
			else:
				return_time = 0

		return return_time

	def updateOpenResults(self, *args):
		"""

		"""

		sel = []
		for i in range(self.tuView.OpenResults.count()):
			item = self.tuView.OpenResults.item(i)
			if item.isSelected():
				sel.append(item.text())

		self.tuView.OpenResults.clear()
		self.tuView.OpenResults.addItems(self.results.keys())

		for i in range(self.tuView.OpenResults.count()):
			item = self.tuView.OpenResults.item(i)
			if item.text() in sel:
				item.setSelected(True)
			if item.text() in args:
				item.setSelected(True)

		self.updateResultTypes()

	def resetResultTypes(self):
		"""
		Resets the result types in the tree widget

		:return: bool -> True for succssful, False for unsuccessful
		"""

		# Remove all children of Map Outputs and time series
		self.tuView.initialiseDataSetView()

		# Reset multi combobox to empty
		for dataType in self.tuView.tuPlot.plotDataPlottingTypes:
			menu = self.tuView.tuPlot.tuPlotToolbar.plotDataToPlotMenu[dataType]
			if isinstance(menu, QAction):
				if is_qt6:
					menu = menu.parent()
				else:
					menu = menu.parentWidget()
			if isinstance(menu, DatasetMenuDepAv):
				menu.clearAllSubMenus()
				continue
			elif isinstance(menu, QToolButton):
				continue

			menu.clear()

		return True

	def getDataFromResultsDict(self, resultName):
		"""
		Returns list of meta data available in the results dictionary

		:param resultName: str - name of open result mesh layer
		:return: list -> float timestep
		:return: list -> str maximum result type e.g. 'depth'
		:return: list -> str temporal result type e.g. 'depth'
		:return: list -> tuple -> ( str type, int type, bool hasMax ) point time series type  e.g. ( 'water level', 4, False )
		:return: list -> tuple -> ( str type, int type, bool hasMax ) line time series type  e.g. ( 'flow', 5, False )
		:return: list -> tuple -> ( str type, int type, bool hasMax ) region time series type  e.g. ( 'volume', 6, False )
		:return: list -> tuple -> ( str type, int type, bool hasMax ) line long plot type  e.g. ( 'water level', 7, True )
		"""
		if PROFILING:
			st1 = datetime.now()

		qv = Qgis.QGIS_VERSION_INT

		timesteps, minResultTypes, maxResultTypes, temporalResultTypes, pTypeTS, lTypeTS, rTypeTS, lTypeLP, csTypes = [], [], [], [], [], [], [], [], []
		timestepsTS = []
		timestepsLP = []
		timestepsParticles = []
		timestepsNcGrid = []

		r = self.results[resultName]
		for type, t in r.items():
			info = ()  # (name, type, haMax) e.g. (depth, 1, True) 1=Scalar 2=Vector, 3=none
			if TuResults.isMaximumResultType(type):
				if type not in maxResultTypes:
					rt = TuResults.stripMaximumName(type)
					maxResultTypes.append(rt)
			elif TuResults.isMinimumResultType(type):
				if type not in minResultTypes:
					rt = TuResults.stripMinimumName(type)
					minResultTypes.append(rt)
			elif '_ts' in type:
				if qv < 31600:
					timestepsTS = t[-1]
				else:
					timestepsTS = sorted(y[0] for x, y in t['times'].items())
					refTime = t['referenceTime'] if 'referenceTime' in t else self.tuView.tuOptions.zeroTime
					if self.tuView.tuOptions.timeUnits == 's':
						timestepsTS = [refTime + timedelta(seconds=float(x)) for x in timestepsTS]
					else:
						try:
							timestepsTS = [refTime + timedelta(hours=float(x)) for x in timestepsTS]
						except OverflowError:
							timestepsTS = [refTime + timedelta(seconds=float(x)) for x in timestepsTS]
				if type == 'point_ts':
					if qv < 31600:
						pTypeTS = [[x, 4, True] for x in t[0]]
					else:
						hasMax = self.results[resultName][type]['hasMax'] if 'hasMax' in self.results[resultName][type] else True
						pTypeTS = [[x, 4, hasMax] for x in t['metadata'][0]]
					if ['MB', 4, True] in pTypeTS:
						index = pTypeTS.index(['MB', 4, True])
						info = pTypeTS[index]
						info[2] = False
					if ['Flow Regime', 4, True] in pTypeTS:
						index = pTypeTS.index(['Flow Regime', 4, True])
						info = pTypeTS[index]
						info[2] = False
				elif type == 'line_ts':
					if qv < 31600:
						lTypeTS = [[x, 5, True] for x in t[0]]
					else:
						lTypeTS = [[x, 5, True] for x in t['metadata'][0]]
					if ['Flow Area', 5, True] in lTypeTS:
						index = lTypeTS.index(['Flow Area', 5, True])
						info = lTypeTS[index]
						info[2] = False
					if ['Losses', 5, True] in lTypeTS:
						index = lTypeTS.index(['Losses', 5, True])
						info = lTypeTS[index]
						info[2] = False
					if ['Flow Regime', 4, False] in pTypeTS and ['Flow Regime', 5, True] in lTypeTS:
						lTypeTS.remove(['Flow Regime', 5, True])
				elif type == 'region_ts':
					types = []
					if qv < 31600:
						if 'point_ts' in r:
							for type_ in t[0]:
								if type_ not in r['points_ts'][0]:
									types.append(type_)
						else:
							types = t[0]
					else:
						if 'point_ts' in r:
							for type_ in t['metadata'][0]:
								if type_ not in r['point_ts']['metadata'][0]:
									types.append(type_)
						else:
							types = t['metadata'][0]
					rTypeTS = [(x, 6, True) for x in types]
			elif '_lp' in type:
				if qv < 31600:
					timestepsLP = t[-1]
				else:
					timestepsLP = sorted(y[0] for x, y in t['times'].items())
					refTime = t['referenceTime'] if 'referenceTime' in t else self.tuView.tuOptions.zeroTime
					if self.tuView.tuOptions.timeUnits == 's':
						timestepsLP = [refTime + timedelta(seconds=float(x)) for x in timestepsLP]
					else:
						try:
							timestepsLP = [refTime + timedelta(hours=float(x)) for x in timestepsLP]
						except OverflowError:
							timestepsLP = [refTime + timedelta(seconds=float(x)) for x in timestepsLP]
				# for x in t[0]:
				# 	#if x == 'Water Level' or x == 'Energy Level':
				# 	#	lTypeLP.append((x, 7, True))
				# 	#else:
				# 	lTypeLP.append((x, 7, False))
				if qv < 31600:
					lTypeLP = [(x, 7, False) for x in t[0]]
				else:
					lTypeLP = [(x, 7, False) for x in t['metadata'][0]]
			elif '_cs' in type:
				if type == 'line_cs':
					for x in t:
						csTypes.append((x, 8, False))
			elif '_particles' in type:
				if qv < 31600:
					timestepsParticles = t[0]
				else:
					timestepsParticles = sorted(y[0] for x, y in t['times'].items())
					refTime = t['referenceTime'] if 'referenceTime' in t else self.tuView.tuOptions.zeroTime
					if self.tuView.tuOptions.timeUnits == 's':
						timestepsParticles = [refTime + timedelta(seconds=float(x)) for x in timestepsParticles]
					else:
						try:
							timestepsParticles = [refTime + timedelta(hours=float(x)) for x in timestepsParticles]
						except OverflowError:
							timestepsParticles = [refTime + timedelta(seconds=float(x)) for x in timestepsParticles]
			elif '_nc_grid' in type:
				if qv < 31600:
					timestepsNcGrid = t[0]
				else:
					timestepsNcGrid = sorted(y[0] for x, y in t['times'].items())
					refTime = t['referenceTime'] if 'referenceTime' in t else self.tuView.tuOptions.zeroTime
					if self.tuView.tuOptions.timeUnits == 's':
						timestepsNcGrid = [refTime + timedelta(seconds=float(x)) for x in timestepsNcGrid]
					else:
						try:
							timestepsNcGrid = [refTime + timedelta(hours=float(x)) for x in timestepsNcGrid]
						except OverflowError:
							timestepsNcGrid = [refTime + timedelta(seconds=float(x)) for x in timestepsNcGrid]
			else:
				temporalResultTypes.append(type)
				refTime = t['referenceTime'] if 'referenceTime' in t else self.tuView.tuOptions.zeroTime
				for i, (time, values) in enumerate(t['times'].items()):
					if values[0] != 9999.0:
						if qv < 31600:
							ts = values[0]
						else:
							if self.tuView.tuOptions.timeUnits == 's':
								ts = refTime + timedelta(seconds=float(values[0]))
							else:
								try:
									ts = refTime + timedelta(hours=float(values[0]))
								except OverflowError:
									ts = refTime + timedelta(seconds=float(values[0]))
						if ts not in timesteps:
							timesteps.append(ts)

		if PROFILING:
			st = datetime.now()

		timesteps = self.joinResultTypes(timesteps, timestepsNcGrid, type='time')

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'getDataFromResultsDict::stage 1 {tt}')
			st = datetime.now()

		if not self.tuView.lock2DTimesteps:
			timesteps = self.joinResultTypes(timesteps, timestepsTS, timestepsLP, timestepsParticles, type='time')

			if PROFILING:
				tt = datetime.now() - st
				Logging.info(f'getDataFromResultsDict::stage 2 {tt}')

		if PROFILING:
			tt = datetime.now() - st1
			Logging.info(f'getDataFromResultsDict::Total {tt}')

		return timesteps, minResultTypes, maxResultTypes, temporalResultTypes, pTypeTS, lTypeTS, rTypeTS, lTypeLP, csTypes

	def joinResultTypes(self, *args, **kwargs):
		"""
		Joins open result type lists so that there is no duplicates

		:param args: list -> list
		:param kwargs: dict
		:return: list
		"""
		qv = Qgis.QGIS_VERSION_INT
		final = []
		arrays = []

		is_time_type = kwargs.get('type', '') == 'time'
		for i, arg in enumerate(args):
			if is_time_type:
				# arg = (np.array(arg, dtype='datetime64[ms]') + np.timedelta64(500, 'ms')).astype('datetime64[s]')
				if qv < 31600:
					arg = np.round(arg, 6)
				else:
					arg = np.array([roundSeconds(x, 2) for x in arg])

			if is_time_type:
				arrays.append(arg)
			else:
				for item in arg:
					if item not in final:
						final.append(item)

		# make sure times are sorted ascendingly
		if 'type' in kwargs.keys() and kwargs['type'] == 'time':
			final = np.unique(np.concatenate(arrays))
			final = np.sort(final).tolist()

		return final

	def applyPreviousResultTypeSelections(self, currentPlotData, time, **kwargs):
		"""
		Applies the previously selected result types to updated DataSetView.

		:param names: list -> str result type
		:param time: str -> time key
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_tuplot import TuPlot

		# kwargs
		select_first_dataset = kwargs['select_first_dataset'] if'select_first_dataset' in kwargs else True

		qv = Qgis.QGIS_VERSION_INT

		openResultTypes = self.tuView.OpenResultTypes  # DataSetView
		#mcboResultType = self.tuView.mcboResultType  # QgsCheckableComboBox
		cboTime = self.tuView.cboTime  # QgsComboBox

		# repopulate active results with new model indexes
		self.activeResultsIndexes = []  # QModelIndex
		self.activeResultsItems = []  # DataSetTreeNode
		for item in openResultTypes.model().mapOutputsItem.children():
			name = item.ds_name
			index = openResultTypes.model().item2index(item)
			if name in self.activeResults:
				openResultTypes.selectionModel().select(index, QT_ITEM_SELECTION_SELECT)
				if item.ds_type == 1:
					openResultTypes.activeScalarIdx = index
				elif item.ds_type == 2:
					openResultTypes.activeVectorIdx = index
				self.activeResultsItems.append(item)
				self.activeResultsIndexes.append(index)
		for item in openResultTypes.model().timeSeriesItem.children():
			nameAppend = ''
			if item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6:
				nameAppend = '_TS'
			elif item.ds_type == 7:
				nameAppend = '_LP'
			elif item.ds_type == 8:
				nameAppend = '_CS'
			name = item.ds_name + nameAppend
			index = openResultTypes.model().item2index(item)
			if name in self.activeResults:
				openResultTypes.selectionModel().select(index, QT_ITEM_SELECTION_SELECT)
				self.activeResultsItems.append(item)
				self.activeResultsIndexes.append(openResultTypes.model().item2index(item))

		# if there are no active results assume first dataset and select first result
		if not self.activeResults and select_first_dataset:
			openResultTypes = self.tuView.OpenResultTypes
			ind = openResultTypes.model().index(0, 0)
			index = openResultTypes.indexBelow(ind)
			if index.internalPointer().ds_name != 'None':
				openResultTypes.selectionModel().select(index, QT_ITEM_SELECTION_SELECT)
				self.tuView.tuResults.activeResultsIndexes.append(index)
				self.tuView.tuResults.activeResultsItems.append(index.internalPointer())
				self.tuView.tuResults.activeResultsTypes.append(index.internalPointer().ds_type)
				self.tuView.tuResults.activeResults.append(index.internalPointer().ds_name)
				if index.internalPointer().ds_type == 1:
					self.tuResults2D.activeScalar = index.internalPointer().ds_name
					openResultTypes.activeScalarIdx = index
					openResultTypes.activeScalarName = index.internalPointer().ds_name
				elif index.internalPointer().ds_type == 2:
					self.tuResults2D.activeVector = index.internalPointer().ds_name
					openResultTypes.activeVectorIdx = index
					openResultTypes.activeVectorName = index.internalPointer().ds_name

		self.updateActiveResultTypes(None)

		# apply max and secondary axis toggle to result types
		for item in openResultTypes.model().mapOutputsItem.children():
			if item.ds_name in self.secondaryAxisTypes:
				item.toggleSecondaryActive()
			if item.ds_name in self.maxResultTypes:
				if item.hasMax:
					item.toggleMaxActive()
				else:
					self.maxResultTypes.remove(item.ds_name)
		for item in openResultTypes.model().timeSeriesItem.children():
			if '{0}_1d'.format(item.ds_name) in self.secondaryAxisTypes:
				item.toggleSecondaryActive()
			if '{0}_1d'.format(item.ds_name) in self.maxResultTypes:
				if item.hasMax:
					item.toggleMaxActive()
				else:
					self.maxResultTypes.remove('{0}_1d'.format(item.ds_name))

		# apply selection to plotting result types
		#mcboResultType.setCheckedItems(names)
		#self.tuView.tuPlot.tuPlotToolbar.setCheckedItemsPlotOptions(namesTS, 0)
		#self.tuView.tuPlot.tuPlotToolbar.setCheckedItemsPlotOptions(namesLP, 1)
		for dataType, plotData in currentPlotData.items():
			if dataType != TuPlot.DataTimeSeriesDepAv and dataType != TuPlot.DataCrossSectionDepAv:
				self.tuView.tuPlot.tuPlotToolbar.setCheckedItemsPlotOptions(dataType, plotData)

		# apply active time
		if qv >= 31600:
			if time is not None:
				self.activeTime = time
			else:
				if cboTime.count():
					# self.activeTime = [x for x in sorted(self.cboTime2timekey)][0]
					self.activeTime = cboTime.itemText(0)
					self.updateActiveTime()
			# set closest time in combobox
			time2, closestTimeIndex = self.dateToTimeInCombobox(self.activeTime)
			cboTime.setCurrentIndex(closestTimeIndex)
		else:
			if time is not None:
				if time not in self.timekey2date:
					if self.timekey2date:
						time = [x for x in self.timekey2date.keys()][0]
			if time is not None:
				#if time in self.timekey2date:
				#	date = self.timekey2date[time]
				if time in self.timekey2date_tspec:
					date = self.timekey2date_tspec[time]
				#dateProper = datetime.strptime(date, self.tuView.tuOptions.dateFormat)  # datetime object
				if time in self.timekey2time:
					timeProper = self.timekey2time[time]
				if not self.tuView.tuOptions.xAxisDates:
					unit = self.tuView.tuOptions.timeUnits
					timeFormatted = convertTimeToFormattedTime(timeProper, unit=unit)
					closestTimeDiff = 99999
				else:
					timeFormatted = self.tuView.tuOptions.dateFormat.format(date)
					closestTimeDiff = timedelta(days=99999)
				timeFound = False
				closestTimeIndex = None
				for i in range(cboTime.count()):
					if cboTime.itemText(i) == timeFormatted:
						cboTime.setCurrentIndex(i)
						timeFound = True
						break
					else:
						# record the closest time index so it can be applied if no exact match is found
						if not self.tuView.tuOptions.xAxisDates:
							unit = self.tuView.tuOptions.timeUnits
							timeConverted = convertFormattedTimeToTime(cboTime.itemText(i), unit=unit)
							timeDiff = abs(timeConverted - timeProper)
						else:
							timeConverted = datetime.strptime(cboTime.itemText(i), self.dateFormat)
							timeDiff = abs(timeConverted - date)
						closestTimeDiff = min(closestTimeDiff, timeDiff)
						if closestTimeDiff == timeDiff:
							closestTimeIndex = i
				if not timeFound and closestTimeIndex is not None:
					cboTime.setCurrentIndex(closestTimeIndex)
				else:
					self.activeTime = time
			else:
				if cboTime.count():
					#self.activeTime = '{0:.6f}'.format(convertFormattedTimeToTime(cboTime.currentText()))
					if cboTime.currentText() in self.cboTime2timekey:
						self.activeTime = self.cboTime2timekey[cboTime.currentText()]
					else:
						# if self.cboTime2timekey is empty reset active time to none
						if not self.cboTime2timekey:
							self.activeTime = None
						else:  # set it to the first value
							self.activeTime = self.cboTime2timekey[[x for x in sorted(self.cboTime2timekey)][0]]

		changed = self.updateActiveResultTypes(None)
		if not changed:
			return False

		return True

	def updateResultTypes(self, **kwargs):
		qv = Qgis.QGIS_VERSION_INT
		if qv < 31600:
			return self.updateResultTypes_old()
		else:
			return self.updateResultTypes_31600(**kwargs)

	def updateResultTypes_old(self):
		"""
		Populates the plotting ui with available result types in the selected open mesh results

		:return: bool -> True for successful, False for unsuccessful
		"""

		qv = Qgis.QGIS_VERSION_INT

		from .coastalmeqgis_tuplot import TuPlot

		sliderTime = self.tuView.sliderTime  # QSlider
		cboTime = self.tuView.cboTime  # QComboBox
		#mcboResultType = self.tuView.mcboResultType  # QgsCheckableComboBox
		openResults = self.tuView.OpenResults  # QListWidget
		openResultTypes = self.tuView.OpenResultTypes  # DataSetView

		# record existing plotting 2D result types and time so it can be re-applied after the update
		#currentNames = mcboResultType.checkedItems()
		#currentNamesTS = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(TuPlot.DataTimeSeries2D)
		#currentNamesLP = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(TuPlot.DataCrossSection2D)
		currentPlotData = {}
		for dataType in self.tuView.tuPlot.plotDataPlottingTypes:
			plotData = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(dataType, all_details=True)
			if plotData:
				currentPlotData[dataType] = plotData

		if qv < 31600:
			currentTime = str(self.activeTime) if self.activeTime is not None else None
		else:
			currentTime = self.activeTime

		# reset types
		reset = self.resetResultTypes()  # reset result types
		if not reset:
			return False
		timesteps, minResultTypes, maxResultTypes, temporalResultTypes = [], [], [], []
		pointTypesTS, lineTypesTS, regionTypesTS, lineTypesLP, crossSectionTypes = [], [], [], [], []
		for result in openResults.selectedItems():
			# Populate metadata lists
			ts, minResTypes, maxResTypes, tResTypes, pTypesTS, lTypesTS, rTypesTS, lTypesLP, csTypes = self.getDataFromResultsDict(result.text())

			# Join already open result types with new types
			timesteps = self.joinResultTypes(timesteps, ts, type='time')
			minResultTypes = self.joinResultTypes(minResultTypes, minResTypes)
			maxResultTypes = self.joinResultTypes(maxResultTypes, maxResTypes)
			temporalResultTypes = self.joinResultTypes(temporalResultTypes, tResTypes)
			pointTypesTS = self.joinResultTypes(pointTypesTS, pTypesTS)
			lineTypesTS = self.joinResultTypes(lineTypesTS, lTypesTS)
			regionTypesTS = self.joinResultTypes(regionTypesTS, rTypesTS)
			lineTypesLP = self.joinResultTypes(lineTypesLP, lTypesLP)
			crossSectionTypes = self.joinResultTypes(crossSectionTypes, csTypes)

		# Populate tuview interface
		mapOutputs = []
		if openResults.selectedItems():
			result = openResults.selectedItems()[0]  # just take the first selection
			for rtype in temporalResultTypes:
				if rtype not in self.results[result.text()].keys():
					# find the selected result that has it
					for result in openResults.selectedItems():
						if rtype in self.results[result.text()].keys():
							break
				t = self.results[result.text()][rtype]
				for i, (time, values) in enumerate(t['times'].items()):
					if i == 0:  # get the data type from the first timestep i.e. scalar or vector
						info = (rtype, values[1], rtype in maxResultTypes, rtype in minResultTypes)
						mapOutputs.append(info)
					else:
						break
				self.tuView.tuPlot.tuPlotToolbar.addItemToPlotOptions(rtype, static=self.results[result.text()][rtype]['isStatic'])

				#mcboResultType.addItem(type)
			for rtype in maxResultTypes:  # check - there may be results that only have maximums
				if rtype not in temporalResultTypes:
					mrtype = self.findMaxResultType(result.text(), rtype)
					if not mrtype:
						# find the selected result that has it
						for result in openResults.selectedItems():
							mrtype = self.findMaxResultType(result.text(), rtype)
							if mrtype:
								break
					if not mrtype:  # couldn't be found - hopefully not the case!
						continue
					t = self.results[result.text()][mrtype]
					for i, (time, values) in enumerate(t['times'].items()):
						if i == 0:  # get the data type from the first timestep i.e. scalar or vector
							info = (rtype, values[1], True, False)
							mapOutputs.append(info)
						else:
							break
		if not mapOutputs:
			mapOutputs = [("None", 3, False)]

		timeSeries = []
		timeSeries = timeSeries + pointTypesTS + lineTypesTS + regionTypesTS + lineTypesLP + crossSectionTypes
		if not timeSeries:
			timeSeries = [("None", 3, False, False)]
		openResultTypes.setModel(DataSetModel(mapOutputs, timeSeries))
		openResultTypes.expandAll()

		# timesteps
		connected = True
		try:
			self.tuView.cboTime.currentIndexChanged.disconnect(self.tuView.timeSliderChanged)
		except:
			# if dock is closed cboTime will already be disconnected
			# record this fact so we don't connect it back up after this
			# function when we don't want to
			connected = False
		cboTime.clear()
		self.cboTime2timekey.clear()
		if timesteps:
			if not self.tuView.tuOptions.xAxisDates:  # use Time (hrs)
				unit = self.tuView.tuOptions.timeUnits
				if (unit == 'h' and timesteps[-1] < 100) or (unit == 's' and timesteps[-1] / 3600 < 100):
					#cboTime.addItems([convertTimeToFormattedTime(x, unit=unit) for x in timesteps])
					for x in timesteps:
						timeformatted = convertTimeToFormattedTime(x, unit=unit)
						cboTime.addItem(timeformatted)
						self.cboTime2timekey[timeformatted] = '{0:.6f}'.format(x)
				else:
					#cboTime.addItems([convertTimeToFormattedTime(x, hour_padding=3, unit=unit) for x in timesteps])
					for x in timesteps:
						timeformatted = convertTimeToFormattedTime(x, unit=unit, hour_padding=3)
						cboTime.addItem(timeformatted)
						self.cboTime2timekey[timeformatted] = '{0:.6f}'.format(x)
			else:  # use datetime format
				# cboTime.addItems([self._dateFormat.format(self.time2date[x]) for x in timesteps])
				cboTime.addItems([self._dateFormat.format(self.time2date_tspec[x]) for x in timesteps])
			sliderTime.setMaximum(len(timesteps) - 1)  # slider
		if connected:
			self.tuView.cboTime.currentIndexChanged.connect(self.tuView.timeSliderChanged)

		# Apply selection
		self.applyPreviousResultTypeSelections(currentPlotData, currentTime)

		# Update viewport with enabled / disabled items
		# self.tuView.currentLayerChanged()
		self.tuView.setTsTypesEnabled()

		return True

	def updateResultTypes_31600(self, **kwargs):
		"""
		Populates the plotting ui with available result types in the selected open mesh results

		:return: bool -> True for successful, False for unsuccessful
		"""
		if PROFILING:
			st = datetime.now()
		qv = Qgis.QGIS_VERSION_INT

		from .coastalmeqgis_tuplot import TuPlot

		sliderTime = self.tuView.sliderTime  # QSlider
		cboTime = self.tuView.cboTime  # QComboBox
		#mcboResultType = self.tuView.mcboResultType  # QgsCheckableComboBox
		openResults = self.tuView.OpenResults  # QListWidget
		openResultTypes = self.tuView.OpenResultTypes  # DataSetView

		# record existing plotting 2D result types and time so it can be re-applied after the update
		#currentNames = mcboResultType.checkedItems()
		#currentNamesTS = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(TuPlot.DataTimeSeries2D)
		#currentNamesLP = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(TuPlot.DataCrossSection2D)
		currentPlotData = {}
		for dataType in self.tuView.tuPlot.plotDataPlottingTypes:
			plotData = self.tuView.tuPlot.tuPlotToolbar.getCheckedItemsFromPlotOptions(dataType, all_details=True)
			if plotData:
				currentPlotData[dataType] = plotData

		if self.activeTime is None:
			self.activeTime = self.activeTime_
		else:
			self.activeTime_ = self.activeTime

		if qv < 31600:
			currentTime = str(self.activeTime) if self.activeTime is not None else None
		else:
			currentTime = self.activeTime

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 1: {tt}')
			st = datetime.now()

		# reset types
		reset = self.resetResultTypes()  # reset result types

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 2: {tt}')
			st = datetime.now()

		if not reset:
			return False
		timesteps, minResultTypes, maxResultTypes, temporalResultTypes = [], [], [], []
		pointTypesTS, lineTypesTS, regionTypesTS, lineTypesLP, crossSectionTypes = [], [], [], [], []
		for result in openResults.selectedItems():
			# Populate metadata lists
			if PROFILING:
				st1 = datetime.now()

			ts, minResTypes, maxResTypes, tResTypes, pTypesTS, lTypesTS, rTypesTS, lTypesLP, csTypes = self.getDataFromResultsDict(result.text())

			if PROFILING:
				tt = datetime.now() - st1
				Logging.info(f'updateResultTypes_31600::Stage 3-1: {tt}')
				st1 = datetime.now()

			# Join already open result types with new types
			timesteps = self.joinResultTypes(timesteps, ts, type='time')
			minResultTypes = self.joinResultTypes(minResultTypes, minResTypes)
			maxResultTypes = self.joinResultTypes(maxResultTypes, maxResTypes)
			temporalResultTypes = self.joinResultTypes(temporalResultTypes, tResTypes)
			pointTypesTS = self.joinResultTypes(pointTypesTS, pTypesTS)
			lineTypesTS = self.joinResultTypes(lineTypesTS, lTypesTS)
			regionTypesTS = self.joinResultTypes(regionTypesTS, rTypesTS)
			lineTypesLP = self.joinResultTypes(lineTypesLP, lTypesLP)
			crossSectionTypes = self.joinResultTypes(crossSectionTypes, csTypes)

			if PROFILING:
				tt = datetime.now() - st1
				Logging.info(f'updateResultTypes_31600::Stage 3-2: {tt}')

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 3: {tt}')
			st = datetime.now()

		# Populate tuview interface
		mapOutputs = []
		if openResults.selectedItems():
			result = openResults.selectedItems()[0]  # just take the first selection
			for rtype in temporalResultTypes:
				if rtype not in self.results[result.text()].keys():
					# find the selected result that has it
					for result in openResults.selectedItems():
						if rtype in self.results[result.text()].keys():
							break
				t = self.results[result.text()][rtype]
				for i, (time, values) in enumerate(t['times'].items()):
					if i == 0:  # get the data type from the first timestep i.e. scalar or vector
						info = (rtype, values[1], rtype in maxResultTypes, rtype in minResultTypes)
						mapOutputs.append(info)
					else:
						break
				self.tuView.tuPlot.tuPlotToolbar.addItemToPlotOptions(rtype, static=self.results[result.text()][rtype]['isStatic'])

				#mcboResultType.addItem(type)
			for rtype in maxResultTypes:  # check - there may be results that only have maximums
				if rtype not in temporalResultTypes:
					mrtype = self.findMaxResultType(result.text(), rtype)
					if not mrtype:
						# find the selected result that has it
						for result in openResults.selectedItems():
							mrtype = self.findMaxResultType(result.text(), rtype)
							if mrtype:
								break
					if not mrtype:  # couldn't be found - hopefully not the case!
						continue
					t = self.results[result.text()][mrtype]
					for i, (time, values) in enumerate(t['times'].items()):
						if i == 0:  # get the data type from the first timestep i.e. scalar or vector
							info = (rtype, values[1], True, False)
							mapOutputs.append(info)
						else:
							break
					self.tuView.tuPlot.tuPlotToolbar.addItemToPlotOptions(rtype, static=True)
		if not mapOutputs:
			mapOutputs = [("None", 3, False)]

		# add nc grids to plotting options
		for result_name, (nc_grid, times) in self.tuResultsNcGrid.results.items():
			self.tuView.tuPlot.tuPlotToolbar.addItemToPlotOptions(result_name, static=nc_grid.static)

		timeSeries = []
		timeSeries = timeSeries + pointTypesTS + lineTypesTS + regionTypesTS + lineTypesLP + crossSectionTypes
		if not timeSeries:
			timeSeries = [("None", 3, False, False)]
		openResultTypes.setModel(DataSetModel(mapOutputs, timeSeries))
		openResultTypes.expandAll()

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 4: {tt}')
			st = datetime.now()

		# timesteps
		connected = True
		try:
			self.tuView.cboTime.currentIndexChanged.disconnect(self.tuView.timeSliderChanged)
		except:
			# if dock is closed cboTime will already be disconnected
			# record this fact so we don't connect it back up after this
			# function when we don't want to
			connected = False
		cboTime.clear()
		self.cboTime2timekey.clear()
		self.cboTime2timekey.clear()
		self.timekey2time.clear()
		if timesteps:
			if not self.tuView.tuOptions.xAxisDates:  # use Time (hrs)
				timesteps = [(x - self.tuView.tuOptions.zeroTime).total_seconds() / 60. / 60. for x in timesteps]
				pad = 2 if timesteps[-1] < 100 else 3
				for x in timesteps:
					timeformatted = convertTimeToFormattedTime(x, unit='h', hour_padding=pad)
					cboTime.addItem(timeformatted)
					self.cboTime2timekey[timeformatted] = '{0:.6f}'.format(x)
					self.timekey2time['{0:.6f}'.format(x)] = x
			else:  # use datetime format
				#cboTime.addItems([self._dateFormat.format(self.time2date_tspec[x]) for x in timesteps])
				cboTime.addItems([self._dateFormat.format(x) for x in timesteps])
			sliderTime.setMaximum(len(timesteps) - 1)  # slider
		if connected:
			self.tuView.cboTime.currentIndexChanged.connect(self.tuView.timeSliderChanged)

		# Apply selection
		try:
			self.tuView.OpenResults.itemSelectionChanged.disconnect(self.tuView.resultSelectionChangeSignal)
		except:
			pass
		meshLayers = findAllMeshLyrs()
		for ml in meshLayers:
			layer = coastalmeqgis_find_layer(ml)
			try:
				layer.repaintRequested.disconnect(self.tuResults2D.repaintRequested)
			except:
				pass

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 5: {tt}')
			st = datetime.now()

		self.applyPreviousResultTypeSelections(currentPlotData, currentTime, **kwargs)

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 6: {tt}')
			st = datetime.now()

		self.tuResults2D.repaintRequested()  # this is the step that changes the 'reference time' property in the result dict
		self.tuView.resultSelectionChangeSignal = self.tuView.OpenResults.itemSelectionChanged.connect(
			lambda: self.tuView.resultsChanged('item clicked'))
		for ml in meshLayers:
			layer = coastalmeqgis_find_layer(ml)
			layer.repaintRequested.connect(self.tuResults2D.repaintRequested)

		# Update viewport with enabled / disabled items
		# self.tuView.currentLayerChanged()
		self.tuView.setTsTypesEnabled()

		if PROFILING:
			tt = datetime.now() - st
			Logging.info(f'updateResultTypes_31600::Stage 7: {tt}')
			st = datetime.now()

		return True

	def updateActiveResultTypes(self, resultIndex, geomType=None, skip_already_selected=False, force_selection=None):
		"""
		Updates the active results based on the selected result types in DataSetView

		:param resultIndex: QModelIndex
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_tuplot import TuPlot
		openResultTypes = self.tuView.OpenResultTypes

		self.tuView.setTsTypesEnabled(context='update_active_1d_types')

		# remove all active results if no longer available at all (i.e. results have been closed)
		for resultType in self.activeResults:
			if resultType == 'none':
				continue
			found = False
			for res, resType1 in self.results.items():
				if re.findall(r'_(TS|LP|CS)$', resultType):
					for resType2, resType3 in resType1.items():
						if 'metadata' in resType3:
							for metadata in resType3['metadata']:
								if metadata == resultType:
									found = True
									break
								elif type(metadata) is list:
									if resultType[:-3] in metadata:
										found = True
										break
						elif isinstance(resType3, dict) and resultType.strip('_CS') in resType3:
							found = True
							break
						if found:
							break
				else:
					if resultType in resType1:
						found = True
				if found:
					break
			if not found:
				i = self.activeResults.index(resultType)
				self.activeResults.remove(resultType)
				if len(self.activeResultsTypes) >= i + 1:
					self.activeResultsTypes.pop(i)
				if resultType[:-3] in self.tuResults1D.typesTS:
					self.tuResults1D.typesTS.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.pointTS:
					self.tuResults1D.pointTS.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.lineTS:
					self.tuResults1D.lineTS.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.regionTS:
					self.tuResults1D.regionTS.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.typesLP:
					self.tuResults1D.typesLP.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.typesXS:
					self.tuResults1D.typesXS.remove(resultType[:-3])
				if resultType[:-3] in self.tuResults1D.lineXS:
					self.tuResults1D.lineXS.remove(resultType[:-3])

		# if geomtype then change the TS result options
		if geomType is not None:
			if geomType == QgsWkbTypes.PointGeometry:
				self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.pointTS if x not in self.tuResults1D.typesTS)
				self.tuResults1D.typesXS.extend(x for x in self.tuResults1D.lineXS if x not in self.tuResults1D.typesXS)
			elif geomType == QgsWkbTypes.LineGeometry:
				self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.lineTS + self.tuResults1D.pointTS if x not in self.tuResults1D.typesTS)
				self.tuResults1D.typesXS.extend(x for x in self.tuResults1D.lineXS if x not in self.tuResults1D.typesXS)
			elif geomType == QgsWkbTypes.PolygonGeometry:
				self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.regionTS if x not in self.tuResults1D.typesTS)
				self.tuResults1D.typesXS.extend(x for x in self.tuResults1D.lineXS if x not in self.tuResults1D.typesXS)
			else:
				self.tuResults1D.typesTS = []

			return True


		# if not a map output item there is no need to rerender the map
		layer = self.tuResults2D.activeMeshLayers[0] if self.tuResults2D.activeMeshLayers else None
		skip = False
		if resultIndex is None or resultIndex.internalPointer() is None or \
				resultIndex.internalPointer().ds_name == 'None' or \
				resultIndex.internalPointer().parentItem == openResultTypes.model().rootItem:  # don't need to update active result lists
			pass
		else:
			# check if clicked result type is a map output or a time series
			item = resultIndex.internalPointer()
			parent = item.parentItem
			if parent.ds_name != 'Map Outputs':
				skip = True  # click occured on a time series result not map output

			nameAppend = ''
			if item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6:
				nameAppend = '_TS'
			elif item.ds_type == 7:
				nameAppend = '_LP'
			elif item.ds_type == 8:
				nameAppend = '_CS'

			# update active result type lists - start by figuring out what type it is and add to specific lists
			if item not in self.activeResultsItems:
				if item.ds_type == 1:  # scalar
					self.tuResults2D.activeScalar = item.ds_name
				elif item.ds_type == 2:  # vector
					self.tuResults2D.activeVector = item.ds_name
				#elif item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6 or item.ds_type == 7:  # 1d result
				elif item.ds_type in TuResults.Results1D:  # 1d result
					self.tuResults1D.items1d.append(item)
					#if item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6:  # time series
					if item.ds_type == 4:  # point
						if item.ds_name not in self.tuResults1D.pointTS:
							self.tuResults1D.pointTS.append(item.ds_name)
					elif item.ds_type == 5:  # line
						if item.ds_name not in self.tuResults1D.lineTS:
							self.tuResults1D.lineTS.append(item.ds_name)
					elif item.ds_type == 6:
						if item.ds_name not in self.tuResults1D.regionTS:
							self.tuResults1D.regionTS.append(item.ds_name)
					elif item.ds_type == 7:  # long plot
						if item.ds_name not in self.tuResults1D.typesLP:
							self.tuResults1D.typesLP.append(item.ds_name)
						self.tuResults1D.typesXSRes.extend(x for x in self.tuResults1D.typesLP if x not in self.tuResults1D.typesXSRes)
					elif item.ds_type == 8:  # XS
						if item.ds_name not in self.tuResults1D.typesXS:
							self.tuResults1D.lineXS.append(item.ds_name)
					# if self.tuResults1D.activeType == 0:
					if 0 in self.tuResults1D.activeType:
						self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.pointTS if x not in self.tuResults1D.typesTS)
						self.tuResults1D.typesXSRes.extend(x for x in self.tuResults1D.pointTS if x not in self.tuResults1D.typesXSRes)
					# elif self.tuResults1D.activeType == 1:
					if 1 in self.tuResults1D.activeType:
						self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.lineTS + self.tuResults1D.pointTS if x not in self.tuResults1D.typesTS)
						self.tuResults1D.typesXS.extend(x for x in self.tuResults1D.lineXS if x not in self.tuResults1D.typesXS)
						self.tuResults1D.typesXSRes.extend(x for x in self.tuResults1D.pointTS if x not in self.tuResults1D.typesXSRes)
					# elif self.tuResults1D.activeType == 2:
					if 2 in self.tuResults1D.activeType:
						self.tuResults1D.typesTS.extend(x for x in self.tuResults1D.regionTS if x not in self.tuResults1D.typesTS)
						self.tuResults1D.typesXSRes.extend(x for x in self.tuResults1D.pointTS if x not in self.tuResults1D.typesXSRes)
					# elif self.tuResults1D.activeType == 3:
					# 	self.tuResults1D.typesXS = self.tuResults1D.lineXS[:]
					# 	self.tuResults1D.typesXSRes = self.tuResults1D.pointTS[:]
					#else:
					#	self.tuResults1D.typesTS = []
					#elif item.ds_type == 7:  # long plot
					#	self.tuResults1D.typesLP.append(item.ds_name)
				# if result type is vector or scalar, need to remove previous vector or scalar results
				if item.ds_type == 1 or item.ds_type == 2:
					while 'none' in self.activeResults:
						self.activeResults.remove('none')
					while item.ds_type in self.activeResultsTypes:
						i_item = self.activeResultsTypes.index(item.ds_type)
						if len(self.activeResults) >= i_item + 1:
							self.activeResults.pop(i_item)
						if len(self.activeResultsIndexes) >= i_item + 1:
							self.activeResultsIndexes.pop(i_item)
						if len(self.activeResultsItems) >= i_item + 1:
							self.activeResultsItems.pop(i_item)
						self.activeResultsTypes.remove(item.ds_type)  # should only be one
					#if resultIndex in self.activeResultsIndexes:
					#	self.activeResultsIndexes.remove(resultIndex)
					#if item in self.activeResultsItems:
					#	self.activeResultsItems.remove(item)
					#for i, result in enumerate(self.activeResults):
					#	if item.ds_type == self.activeResultsTypes[i]:
					#		self.activeResults.pop(i)
					#		self.activeResultsTypes.pop(i)
					#		if self.activeResultsIndexes:
					#			self.activeResultsIndexes.pop(i)
					#			self.activeResultsItems.pop(i)
					#		break  # there will only be one to remove
				# finally add clicked result type to generic active lists - applicable regardless of result type
				self.activeResults.append(item.ds_name + nameAppend)
				self.activeResultsTypes.append(item.ds_type)
				self.activeResultsIndexes.append(resultIndex)
				self.activeResultsItems.append(item)
			elif not skip_already_selected:  # already in lists so click is a deselect and types need to be removed from lists
				# remove 2D from lists
				i = -1
				if item in self.activeResultsItems:
					i = self.activeResultsItems.index(item)
				# self.activeResults.pop(i)
				# self.activeResultsTypes.pop(i)
				# self.activeResultsIndexes.pop(i)
				# self.activeResultsItems.pop(i)

				if item.ds_name + nameAppend in self.activeResults:
					self.activeResults.remove(item.ds_name + nameAppend)
				# if i > 0 and len(self.activeResultsTypes) >= i + 1:
				if i >= 0 and len(self.activeResultsTypes) >= i + 1:
					self.activeResultsTypes.pop(i)
					if item.ds_type == 1 or item.ds_type == 2:
						if 1 not in self.activeResultsTypes and 2 not in self.activeResultsTypes:
							self.activeResults.append('none')
				if resultIndex in self.activeResultsIndexes:
					self.activeResultsIndexes.remove(resultIndex)
				if i >= 0:
					self.activeResultsItems.pop(i)

				if item.ds_type == 1:
					self.tuResults2D.activeScalar = None
				elif item.ds_type == 2:
					self.tuResults2D.activeVector = None
				# remove 1D from lists
				if item in self.tuResults1D.items1d:
					self.tuResults1D.items1d.remove(item)
				if item.ds_name in self.tuResults1D.typesTS:
					self.tuResults1D.typesTS.remove(item.ds_name)
				elif item.ds_name in self.tuResults1D.typesLP:
					self.tuResults1D.typesLP.remove(item.ds_name)
					if item.ds_name in self.tuResults1D.typesXSRes:
						self.tuResults1D.typesXSRes.remove(item.ds_name)
				elif item.ds_name in self.tuResults1D.typesXS:
					self.tuResults1D.typesXS.remove(item.ds_name)
				if item.ds_name in self.tuResults1D.pointTS:
					self.tuResults1D.pointTS.remove(item.ds_name)
					if item.ds_name in self.tuResults1D.typesXSRes:
						self.tuResults1D.typesXSRes.remove(item.ds_name)
				elif item.ds_name in self.tuResults1D.lineTS:
					self.tuResults1D.lineTS.remove(item.ds_name)
				elif item.ds_name in self.tuResults1D.regionTS:
					self.tuResults1D.regionTS.remove(item.ds_name)
				elif item.ds_name in self.tuResults1D.lineXS:
					self.tuResults1D.lineXS.remove(item.ds_name)

			# double check active results vs selected results
			if force_selection == '1D': return
			count = 0
			for itm in openResultTypes.model().timeSeriesItem.children():
				index = openResultTypes.model().item2index(itm)
				if openResultTypes.selectionModel().isSelected (index):
					count += 1
			if count != len(self.tuResults1D.items1d):
				self.forceSelection1D()

		if not skip:
			# rerender map
			if layer is not None:
				# rs = layer.rendererSettings()
				# # if no scalar or vector turn off dataset
				# if self.tuResults2D.activeScalar is None:
				# 	rs.setActiveScalarDataset(QgsMeshDatasetIndex(-1, -1))
				# 	layer.setRendererSettings(rs)
				# if self.tuResults2D.activeVector is None:
				# 	rs.setActiveVectorDataset(QgsMeshDatasetIndex(-1, -1))
				# 	layer.setRendererSettings(rs)

				# double check active results vs selected results
				count = 0
				for itm in openResultTypes.model().mapOutputsItem.children():
					index = openResultTypes.model().item2index(itm)
					if openResultTypes.selectionModel().isSelected(index):
						count += 1
				if count > 2 or count != self.activeResultsTypes.count(1) + self.activeResultsTypes.count(2) \
						or len(self.activeResults) != len(self.activeResultsTypes) != len(self.activeResultsIndexes) \
						!= len(self.activeResultsItems):
					self.forceSelection2D()

				self.tuView.renderMap()

				# update default item in the depth averaging methods
				self.tuView.tuPlot.tuPlotToolbar.averageMethodTSMenu.updateDefaultItem(self.tuResults2D.activeScalar)
		else:
			# redraw plot
			if item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6:
				self.tuView.tuPlot.updateCurrentPlot(TuPlot.TimeSeries)
				if self.tuResults1D.typesXS:
					self.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection)
			elif item.ds_type == 7:
				self.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection)
			elif item.ds_type == 8:
				self.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection)
			else:
				self.tuView.tuPlot.updateCurrentPlot(self.tuView.tabWidget.currentIndex(), update='1d only')


		return True

	def forceSelection1D(self):
		"""
		Force active 1D types to match selection (opposite to 2D results)

		Untested - hard to replicate when this needs to happen
		"""

		openResultTypes = self.tuView.OpenResultTypes

		for item in openResultTypes.model().timeSeriesItem.children():
			index = openResultTypes.model().item2index(item)
			if openResultTypes.selectionModel().isSelected (index):
				if item not in self.tuResults1D.items1d:
					if item in self.activeResultsItems:
						self.activeResultsItems.remove(item)
					self.updateActiveResultTypes(index, force_selection='1D')
			else:
				if item in self.tuResults1D.items1d:
					if item not in self.activeResultsItems:
						self.activeResultsItems.append(item)
					self.updateActiveResultTypes(index, force_selection='1D')

	def forceSelection2D(self):
		"""
		Force selection to match active 2D types (opposite to 1D results)

		Untested - hard to replicate when this needs to happen
		"""

		openResultTypes = self.tuView.OpenResultTypes

		for item in openResultTypes.model().mapOutputsItem.children():
			index = openResultTypes.model().item2index(item)
			if openResultTypes.selectionModel().isSelected (index):
				if item.ds_type == 1 and not self.tuResults2D.activeScalar:
					# deselect
					openResultTypes.selectionModel().select(index, QT_ITEM_SELECTION_DESELECT)
				if item.ds_type == 2 and not self.tuResults2D.activeVector:
					# deselect
					openResultTypes.selectionModel().select(index, QT_ITEM_SELECTION_DESELECT)

		# force lists
		self.activeResults = [x for x in self.activeResults if not TuResults.isMapOutputType(x)]
		if self.tuResults2D.activeScalar:
			self.activeResults.append(self.tuResults2D.activeScalar)
		if self.tuResults2D.activeVector:
			self.activeResults.append(self.tuResults2D.activeVector)
		self.activeResultsItems = [x for x in
		                           sum([x.children() for x in openResultTypes.model().rootItem.children()], [])
		                           if
		                           openResultTypes.selectionModel().isSelected(openResultTypes.model().item2index(x))]
		self.activeResultsIndexes = [openResultTypes.model().item2index(x) for x in
		                             sum([x.children() for x in openResultTypes.model().rootItem.children()], [])
		                             if
		                             openResultTypes.selectionModel().isSelected(openResultTypes.model().item2index(x))]
		self.activeResultsTypes = [x.ds_type for x in
		                           sum([x.children() for x in openResultTypes.model().rootItem.children()], [])
		                           if
		                           openResultTypes.selectionModel().isSelected(openResultTypes.model().item2index(x))]

	def updateSecondaryAxisTypes(self, clickedItem):
		"""
		Updates the list of result types to be plotted on the secondary axis.

		:param clickedItem: dict -> { 'parent': DataSetTreeNode, 'index': DataSetTreeNode }
		:return: bool -> True for successful, False for unsuccessful
		"""

		openResultTypes = self.tuView.OpenResultTypes

		if clickedItem is not None:
			openResultTypes.model().setActiveSecondaryIndex(clickedItem['parent'], clickedItem['index'])

		self.secondaryAxisTypes = []
		for i in range(openResultTypes.model().mapOutputsItem.childCount()):
			item = openResultTypes.model().dsindex2item[i]
			if item.enabled:
				if item.secondaryActive:
					self.secondaryAxisTypes.append(item.ds_name)

		for item in openResultTypes.model().timeSeriesItem.children():
			if item.enabled:
				if item.secondaryActive:
					if item.ds_type == 8:
						self.secondaryAxisTypes.append('{0}_CS'.format(item.ds_name))
					else:
						self.secondaryAxisTypes.append('{0}_1d'.format(item.ds_name))

		if self.tuView.tuPlot.tuPlotToolbar.fluxSecAxisButton.isChecked():
			self.secondaryAxisTypes.append('2D Flow')

		return True

	def updateMinMaxTypes(self, clickedItem, mtype):
		"""
		Updates the list of result types that should plot max.

		:param clickedItem: dict -> { 'parent': DataSetTreeNode, 'index': DataSetTreeNode }
		:return: bool -> True for successful, False for unsuccessful
		"""

		openResultTypes = self.tuView.OpenResultTypes

		if clickedItem is not None:
			if mtype == 'max':
				openResultTypes.model().setActiveMax(clickedItem['parent'], clickedItem['index'])
			elif  mtype == 'min':
				openResultTypes.model().setActiveMin(clickedItem['parent'], clickedItem['index'])

		self.maxResultTypes = []
		for item in openResultTypes.model().mapOutputsItem.children():
			if item.enabled:
				if item.isMax:
					self.maxResultTypes.append(item.ds_name)
		self.minResultTypes = []
		for item in openResultTypes.model().mapOutputsItem.children():
			if item.enabled:
				if item.isMin:
					self.minResultTypes.append(item.ds_name)

		for item in openResultTypes.model().timeSeriesItem.children():
			if item.enabled:
				if item.isMax:
					self.maxResultTypes.append('{0}_1d'.format(item.ds_name))
				if item.isMin:
					self.minResultTypes.append('{0}_1d'.format(item.ds_name))

		return True

	def getResult(self, index, **kwargs):
		"""
		Gets data from the indexed results.

		:param index: TuResultsIndex
		:return: tuple -> result metadata
		"""

		# get version
		qv = Qgis.QGIS_VERSION_INT

		forceGetTime = kwargs['force_get_time'] if 'force_get_time' in kwargs.keys() else None
		meshIndexOnly = kwargs['mesh_index_only'] if 'mesh_index_only' in kwargs else False
		results = self.tuView.tuResults.results  # dict

		if index is None:
			if qv < 31300:
				return QgsMeshDatasetIndex(-1, -1)
			else:
				return -1

		key1 = index.result if 'result_name' not in kwargs else kwargs['result_name']
		key2 = index.resultType if 'result_type' not in kwargs else kwargs['result_type']
		key3 = index.timestep if 'timestep' not in kwargs else kwargs['timestep']

		if key1 not in results.keys():
			if qv < 31300:
				return QgsMeshDatasetIndex(-1, -1)
			else:
				return -1

		if key2 not in results[key1].keys():
			if qv < 31300:
				return QgsMeshDatasetIndex(-1, -1)
			else:
				return -1

		roundedTimes = [np.round(float(x), 4) for x in results[key1][key2]['times'].keys()]
		if key3 is not None:
			roundedKey3 = np.round(float(key3), 4)

		if key3 is not None:
			# if key3 not in results[key1][key2]['times'].keys():
			if roundedKey3 not in roundedTimes:
				if len(results[key1][key2]['times']) == 1:
					for k in results[key1][key2]['times']:
						key3 = k
						roundedKey3 = np.round(float(key3), 4)
				elif forceGetTime == 'next lower':
					key3 = self.findTimeNextLower(key1, key2, key3)
					roundedKey3 = np.round(float(key3), 4)

		if key3 is not None:
			i = roundedTimes.index(roundedKey3)
			time = list(results[key1][key2]['times'].keys())[i]
			# res = results[key1][key2]['times'][key3]
			res = results[key1][key2]['times'][time]
			if qv < 31300:
				if meshIndexOnly:
					if res and type(res) is tuple:
						return res[-1]
					else:
						return QgsMeshDatasetIndex(-1, -1)
				else:
					return results[key1][key2]['times'][key3]
			else:
				if meshIndexOnly:
					if res and type(res) is tuple:
						return res[-1].group()
					else:
						return -1
				else:
					return res
		else:
			if meshIndexOnly:
				if qv < 31300:
					return QgsMeshDatasetIndex(-1, -1)
				else:
					return -1
			else:
				return results[key1][key2]['times']

	def is3d(self, index, **kwargs):
		"""

		"""

		results = self.tuView.tuResults.results  # dict
		key1 = index.result if 'result_name' not in kwargs else kwargs['result_name']
		key2 = index.resultType if 'result_type' not in kwargs else kwargs['result_type']

		if key1 not in results.keys():
			return False
		if key2 not in results[key1].keys():
			return False

		return results[key1][key2]['is3dDataset']

	def getTimeUnit(self, index, **kwargs):
		"""

		"""

		results = self.tuView.tuResults.results  # dict
		key1 = index.result if 'result_name' not in kwargs else kwargs['result_name']
		key2 = index.resultType if 'result_type' not in kwargs else kwargs['result_type']

		if key1 not in results.keys():
			return 'h'
		if key2 not in results[key1].keys():
			return 'h'

		return results[key1][key2]['timeUnit']

	def findTimeNextLower(self, key1, key2, key3):
		"""
		Finds the previous available 2D timestep.

		:param key1: str -> result name e.g. M01_5m_001
		:param key2: str -> result type e.g. 'depth'
		:param key3: str -> time e.g. '1.0000'
		:return: str -> next lower time
		"""

		times = sorted(y[0] for x, y in self.results[key1][key2]['times'].items())
		timekeys = sorted(x for x in self.results[key1][key2]['times'])
		for i, time in enumerate(times):
			if time > key3:
				return timekeys[max(0, i-1)]

		if timekeys:
			return timekeys[-1]
		else:
			return None

	def findTimeClosest(self, key1, key2, key3, times=(), is_date=False, method='lower'):
		"""
		Finds the next available time after specified time
		"""

		if is_date:
			if type(key3) is str:
				rt = datetime.strptime(key3, self.dateFormat)
			else:
				rt = key3
		else:
			if type(key3) is str:
				rt = float(key3)
			else:
				rt = key3

		if not times:
			times = [y for x, y in self.results[key1][key2]['times'].items()]

		assert(len(times) > 0)
		if method == 'higher':
			for time in times:
				if time >= rt:
					return time
		elif method == 'lower':
			i = 1
			for time in times[1:]:
				if time == rt:
					return time
				elif time > rt:
					return times[i-1]
				else:
					i += 1
		else:  #  closest
			for i, time in enumerate(times):
				if time == rt:
					return time
				if i == 0:
					diff = abs((time - rt).total_seconds())
				elif time > rt:
					diff2 = abs((time - rt).total_seconds())
					if diff <= diff2:
						return times[i-1]
					else:
						return time
				else:
					diff = abs((time - rt).total_seconds())

		return time

	@staticmethod
	def findTimeClosest_31600(tuResults, key1, key2, key3, times=(), method='lower', units='h'):
		"""
		Finds the next available time after specified time
		"""

		# for 1d results change key2 so it can be found in results dict
		if key1 is not None and key2 is not None:
			if key1 in tuResults.results:
				if '_1d' in key2:
					for type_1d in ['point_ts', 'line_ts', 'region_ts', 'line_lp']:
						if type_1d in tuResults.results[key1]:
							if 'times' in tuResults.results[key1][type_1d]:
								key2 = type_1d
								break

		if not times:
			if key1 not in tuResults.results:
				return
			if key2 not in tuResults.results[key1]:
				return
		if key3 is None:
			return

		if not times:
			if 'times' not in tuResults.results[key1][key2]:
				return
			times = sorted(y[0] for x, y in tuResults.results[key1][key2]['times'].items())

		if 'referenceTime' not in tuResults.results[key1][key2]:
			return
		rt = tuResults.results[key1][key2]['referenceTime']
		for i, time in enumerate(times):
			if units == 's':
				date = rt + timedelta(seconds=float(time))
			else:
				try:
					date = rt + timedelta(hours=float(time))
				except OverflowError:
					date = rt + timedelta(seconds=float(time))
			if method == 'higher':
				if date >= key3:
					return time
			elif method == 'lower':
				if date == key3:
					return time
				elif date > key3:
					return times[max(0,i-1)]
			else:  # closest
				if date == key3:
					return time
				if i == 0:
					diff = abs((date - key3).total_seconds())
				if time > key3:
					diff2 = abs((date - key3).total_seconds())
					if diff <= diff2:
						return times[max(0, i-1)]
					else:
						return time
				else:
					diff = abs((date - key3).total_seconds())
		if not times:
			return None
		else:
			return time

	@staticmethod
	def findDateClosest_31600(tuResults, key1, key2, key3, dates=(), method='lower', units='h'):
		"""
        Finds the next available time after specified time
        """

		if not dates:
			if key1 not in tuResults.results:
				return
			if key2 not in tuResults.results[key1]:
				return
		if key3 is None:
			return

		if not dates:
			if 'times' not in tuResults.results[key1][key2]:
				return
			times = sorted(y[0] for x, y in tuResults.results[key1][key2]['times'].items())
			if 'referenceTime' not in tuResults.results[key1][key2]:
				return
			rt = tuResults.results[key1][key2]['referenceTime']
			dates = []
			for t in times:
				if units == 's':
					dates.append(rt + timedelta(seconds=float(t)))
				else:
					try:
						dates.append(rt + timedelta(hours=float(t)))
					except OverflowError:
						dates.append(rt + timedelta(seconds=float(t)))

		for i, date in enumerate(dates):
			if method == 'higher':
				if date >= key3:
					return date
			elif method == 'lower':
				if date == key3:
					return date
				elif date > key3:
					return dates[max(0, i - 1)]
			else:  # closest
				if date == key3:
					return date
				if i == 0:
					diff = abs((date - key3).total_seconds())
				if date > key3:
					diff2 = abs((date - key3).total_seconds())
					if diff <= diff2:
						return dates[max(0, i - 1)]
					else:
						return date
				else:
					diff = abs((date - key3).total_seconds())

		return date

	def isMax(self, typ):
		"""
		Returns whether the result type is max or not. Can put 'scalar' or 'vector' to auto get active scalar or vector.

		:param type: str
		:return: bool -> True for max, False for not max
		"""

		maxResultTypes = self.tuView.tuResults.maxResultTypes  # list -> str

		if typ == 'scalar':
			return True if self.tuResults2D.activeScalar in maxResultTypes else False
		elif typ == 'vector':
			return True if self.tuResults2D.activeVector in maxResultTypes else False
		else:
			return True if typ in maxResultTypes else False

	def isMin(self, typ):
		"""
		Returns whether the result type is max or not. Can put 'scalar' or 'vector' to auto get active scalar or vector.

		:param type: str
		:return: bool -> True for max, False for not max
		"""

		minResultTypes = self.tuView.tuResults.minResultTypes  # list -> str

		if typ == 'scalar':
			return True if self.tuResults2D.activeScalar in minResultTypes else False
		elif typ == 'vector':
			return True if self.tuResults2D.activeVector in minResultTypes else False
		else:
			return True if typ in minResultTypes else False

	def removeResults(self, resList, **kwargs):
		"""
		Removes the results from the indexed results and ui.

		:param resList: list -> str result name e.g. M01_5m_001
		:return: bool -> True for successful, False for unsuccessful
		"""

		# kwargs
		ignoreMeshResults = kwargs['ignore_mesh_results'] if 'ignore_mesh_results' in kwargs else False

		results = self.tuView.tuResults.results
		results2d = self.tuView.tuResults.tuResults2D.results2d
		results1d = self.tuView.tuResults.tuResults1D.results1d
		resultsParticles = self.tuView.tuResults.tuResultsParticles.resultsParticles

		self.tuResultsParticles.removeResults(resList)
		self.tuResultsNcGrid.removeResults(resList)

		for res in resList:
			self.tuView.crossSectionsFM.delByLayername(res)

		for res in resList:
			if ignoreMeshResults and res in results2d:
				continue
			if res in results.keys():
				# remove from indexed results
				del results[res]
			if res in results2d.keys():
				if res in results2d:
					del results2d[res]
			if res in results1d.keys():
				if res in results1d:
					for res_ in results1d[res]:
						if isinstance(res_, ResData_GPKG):
							self.tuResults1D.remove_gpkg_gis(res_)
					del results1d[res]
				# if res in resultsParticles:
				#	del resultsParticles[res]

				#layer = coastalmeqgis_find_layer(res)
				#self.tuView.project.removeMapLayer(layer)
				#self.tuView.canvas.refresh()

			# remove from ui
			for i in range(self.tuView.OpenResults.count()):
				item = self.tuView.OpenResults.item(i)
				if item is not None and item.text() == res:
					if res not in results:
						self.tuView.OpenResults.takeItem(i)

		return True

	def updateActiveResults(self):
		"""
		Updates the list of selected 2D results.

		:return: bool -> True for successful, False for unsuccessful
		"""

		self.activeMeshLayers = []
		openResults = self.tuView.OpenResults  # QListWidget

		for r in range(openResults.count()):
			item = openResults.item(r)

			# find selected layer
			layer = coastalmeqgis_find_layer(item.text())
			if layer is not None:
				if layer.type() == 3:
					if item.isSelected():
						self.activeMeshLayers.append(layer)
					else:
						rs = layer.rendererSettings()
						rs.setActiveScalarDataset(QgsMeshDatasetIndex(-1, -1))
						layer.setRendererSettings(rs)
						rs.setActiveVectorDataset(QgsMeshDatasetIndex(-1, -1))
						layer.setRendererSettings(rs)

		return True

	def updateTimeUnits(self):
		# turn off x axis freezing on time series plot
		self.tuView.tuPlot.tuPlotToolbar.viewToolbarTimeSeries.freezeXAxisAction.setChecked(False)
		self.tuView.tuPlot.tuPlotToolbar.viewToolbarTimeSeries.freezeXYAxisAction.setChecked(False)

		meshLayers = findAllMeshLyrs()
		for ml in meshLayers:
			layer = coastalmeqgis_find_layer(ml)
			self.tuResults2D.getResultMetaData(ml, layer, loadRenderStyle=False)

			# update 1D results based on new reference time for mesh layer
			for result in self.results:
				if result == layer.name():
					for result_type in self.results[result]:
						if self.isTimeSeriesType(result_type):
							self.results[result][result_type]['referenceTime'] = self.tuResults2D.getReferenceTime(layer, self.tuView.tuOptions.defaultZeroTime)

		self.updateResultTypes()

	def checkSelectedResults(self):
		"""
		Checks the selected results match active result types.

		:return:
		"""

		openResultTypes = self.tuView.OpenResultTypes
		selectedIndexes = sorted(openResultTypes.selectedIndexes())

		if selectedIndexes != sorted(self.activeResultsIndexes[:]):
			# Reset active results so it matches selection
			self.tuResults2D.activeScalar = None
			self.tuResults2D.activeVector = None
			self.activeResults.clear()  # str result type names
			self.activeResultsTypes.clear()  # int result types (e.g. 1 - scalar, 2 - vector...)
			self.activeResultsIndexes.clear()  # QModelIndex
			self.activeResultsItems.clear()  # DataSetTreeNode
			self.tuResults1D.items1d.clear()  # list -> Dataset_View Tree node selected dataset view tree node item
			self.tuResults1D.typesTS.clear()  # list -> str selected 1D time series result types
			self.tuResults1D.pointTS.clear()
			self.tuResults1D.lineTS.clear()
			self.tuResults1D.regionTS.clear()
			self.tuResults1D.typesLP.clear()  # list -> str selected 1D long plot result types
			self.tuResults1D.typesXS.clear()
			for index in selectedIndexes:
				item = index.internalPointer()
				if item.ds_type == 1:  # scalar
					self.tuResults2D.activeScalar = item.ds_name
					self.activeResults.append(item.ds_name)
				elif item.ds_type == 2:  # vector
					self.tuResults2D.activeVector = item.ds_name
					self.activeResults.append(item.ds_name)
				# elif item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6 or item.ds_type == 7:  # 1d result
				elif item.ds_type in TuResults.Results1D:  # 1d result
					self.tuResults1D.items1d.append(item)
					nameAppend = ''
					if item.ds_type == 4 or item.ds_type == 5 or item.ds_type == 6:  # time series
						nameAppend = '_TS'
						if item.ds_type == 4:  # point
							self.tuResults1D.pointTS.append(item.ds_name)
						elif item.ds_type == 5:  # line
							self.tuResults1D.lineTS.append(item.ds_name)
						elif item.ds_type == 6:
							self.tuResults1D.regionTS.append(item.ds_name)
						# if self.tuResults1D.activeType == 0:
						if 0 in self.tuResults1D.activeType:
							self.tuResults1D.typesTS.extend(self.tuResults1D.pointTS[:])
						# elif self.tuResults1D.activeType == 1:
						if 1 in self.tuResults1D.activeType:
							self.tuResults1D.typesTS.extend(self.tuResults1D.lineTS[:] + self.tuResults1D.pointTS[:])
						# elif self.tuResults1D.activeType == 2:
						if 2 in self.tuResults1D.activeType:
							self.tuResults1D.typesTS.extend(self.tuResults1D.regionTS[:])
						# else:
						# 	self.tuResults1D.typesTS = []
					elif item.ds_type == 7:  # long plot
						nameAppend = '_LP'
						self.tuResults1D.typesLP.append(item.ds_name)
					elif item.ds_type == 8:  # cross section
						nameAppend = '_CS'
						self.tuResults1D.typesXS = self.tuResults1D.lineTS[:]
						self.tuResults1D.activeType.append(3)
					self.activeResults.append(item.ds_name + nameAppend)

	def findMaxResultType(self, result: str, resultType: str) -> str:
		"""
		Find maximum result type in results.
		Used when only maximum result type exists (no temporal results)

		It is assumed that there is no temporal output for result type.

		:param result: str result name e.g. 'M03_5m_001'
		:param resultType: str result type e.g. 'depth'
		:return: str max result type e.g. 'depth/Maximums'
		"""

		for rtype in self.results[result]:
			if TuResults.isMaximumResultType(rtype):
				if TuResults.stripMaximumName(rtype) == resultType:
					return rtype

		return ''

	@staticmethod
	def stripMaximumName(resultType: str) -> str:
		"""
		Strips the maximum identifier from the name.

		e.g. 'depth/Maximum' will return 'depth'

		:param resultType: str
		:return: str
		"""

		if '/Maximums' in resultType:
			rtype = ''.join(resultType.split('/Maximums'))
		else:
			# rtype = resultType.split('/')[0]
			rtype = resultType
		if 'max_' in rtype and 'time' not in rtype:
			rtype = rtype.split('max_')[1]

		return rtype

	@staticmethod
	def stripMinimumName(resultType: str) -> str:
		"""
		Strips the minimum identifier from the name.

		e.g. 'depth/Maximum' will return 'depth'

		:param resultType: str
		:return: str
		"""

		if '/Minimums' in resultType:
			rtype = ''.join(resultType.split('/Minimums'))
		else:
			# rtype = resultType.split('/')[0]
			rtype = resultType
		if 'min_' in rtype and 'time' not in rtype:
			rtype = rtype.split('min_')[1]

		return rtype

	@staticmethod
	def isMaximumResultType(resultType: str,
	                        lyr: QgsMeshLayer = QgsMeshLayer(),
	                        groupIndex: int = -1) -> bool:
		"""
		Determines if the result type is a maximum or not.

		e.g. Depth/Maximums will return True

		:param resultType: str
		:param dp: QgsMeshDataProvider
		:param groupIndex: int
		:return: bool
		"""

		if '/Maximums' in resultType or ('max_' in resultType and 'time' not in resultType):
			return True

		if '/Final' in resultType:
			return True

		# special case for 'Minimum dt'
		# this is recorded as 'Final/Minimum dt' in xmdf - MDAL does not retain folder name
		# will treat this as 'max'
		# if only only one timestep, then this is the final / max value
		if 'minimum dt' in resultType.lower():
			if lyr is not None:
				if lyr.isValid():
					if lyr.datasetCount(QgsMeshDatasetIndex(groupIndex,-1)) == 1:
						return True

		return False

	@staticmethod
	def isMinimumResultType(resultType: str,
						lyr: QgsMeshLayer = QgsMeshLayer().dataProvider(),
	                        groupIndex: int = -1) -> bool:
		"""
		Determines if the result type is a minimum or not.

		e.g. Depth/Minimums will return True

		:param resultType: str
		:param dp: QgsMeshDataProvider
		:param groupIndex: int
		:return: bool
		"""

		# if '/Minimums' in resultType or ('min_' in resultType and 'time' not in resultType):
		if '/Minimums' in resultType or (re.findall(r'\Dmin_', resultType, flags=re.IGNORECASE) and 'time' not in resultType):
			return True

		return False

	@staticmethod
	def isStatic(resultType: str,
                lyr: QgsMeshLayer = QgsMeshLayer().dataProvider(),
                groupIndex: int = -1) -> bool:
		"""
        Determines if the result type is a static or not

        e.g. bed elevation

        :param resultType: str
        :param dp: QgsMeshDataProvider
        :param groupIndex: int
        :return: bool
        """

		if TuResults.isMaximumResultType(resultType, lyr, groupIndex) \
				or TuResults.isMinimumResultType(resultType, lyr, groupIndex):
			return True

		if lyr is not None:
			if lyr.isValid():
				if lyr.datasetCount(QgsMeshDatasetIndex(groupIndex, -1)) == 1:
					return True

		return False

	@staticmethod
	def isTemporal(resultType: str,
	               lyr: QgsMeshLayer = QgsMeshLayer().dataProvider(),
	               groupIndex: int = -1) -> bool:
		"""
        Determines if the result type is a static or not

        e.g. bed elevation

        :param resultType: str
        :param dp: QgsMeshDataProvider
        :param groupIndex: int
        :return: bool
        """

		return not TuResults.isStatic(resultType, lyr, groupIndex)

	def updateDateTimes2(self):
		"""Supersedes updateDateTimes"""
		qv = Qgis.QGIS_VERSION_INT

		for resname, res in self.results.items():
			meshprocessed = False
			tsprocessed = False
			for restype, resinfo in res.items():
				if TuResults.isMapOutputType(restype):
					layer = coastalmeqgis_find_layer(resname)
					if layer is not None:
						if not meshprocessed:
							if qv >= 31300 and not resinfo['hadTemporalProperties']:
								layer.setReferenceTime(dt2qdt(datetime2timespec(self.tuView.tuOptions.zeroTime, self.loadedTimeSpec, QT_TIMESPEC_UTC), QT_TIMESPEC_UTC))
							self.tuResults2D.getResultMetaData(resname, layer, resinfo['ext'], resinfo['hadTemporalProperties'], loadRenderStyle=False)
							meshprocessed = True
				elif TuResults.isParticleType(restype):
					self.tuResultsParticles.reloadTimesteps(resname)
				elif TuResults.isTimeSeriesType(restype):
					if not tsprocessed:
						self.tuResults1D.reloadTimesteps(resname)
						tsprocessed = True
		self.updateResultTypes()

	def updateDateTimes(self, **kwargs):
		qv = Qgis.QGIS_VERSION_INT

		if qv < 31600:
			self.updateDateTimes2()
		else:
			self.updateDateTimes_31600(**kwargs)

	def updateDateTimes_old(self):
		"""
		Updates date2time dictionary and time2date dictionary

		:return: None
		"""

		qv = Qgis.QGIS_VERSION_INT

		self.date2timekey.clear()
		self.date2time.clear()
		self.timekey2date.clear()

		self.timekey2date_tspec.clear()
		self.time2date_tspec.clear()
		self.date_tspec2timekey.clear()
		self.date_tspec2time.clear()
		self.date2date_tspec.clear()
		self.date_tspec2date.clear()

		zeroDate = self.tuView.tuOptions.zeroTime
		for t in self.time2date:
			if t == '-99999' or t == -99999:
				self.time2date[t] = -99999
				self.timekey2date[t] = -99999
				self.date2time[-99999] = t
				self.date2timekey[-99999] = t

				self.time2date_tspec[t] = -99999
				self.timekey2date_tspec[t] = -99999
				self.date_tspec2time[-99999] = t
				self.date_tspec2timekey[-99999] = t
			else:
				if self.tuView.tuOptions.timeUnits == 's':
					date = zeroDate + timedelta(seconds=float(t))
				else:
					date = zeroDate + timedelta(hours=float(t))

				# format date to 2 decimal places i.e. dd/mm/yyyy hh:mm:ss.ms
				date = roundSeconds(date, 2)
				self.time2date[t] = date
				self.timekey2date['{0:.6f}'.format(t)] = date
				self.date2time[date] = t
				self.date2timekey[date] = '{0:.6f}'.format(t)

				if qv >= 31300:
					if self.iface is not None:
						date_tspec = datetime2timespec(date, self.iface.mapCanvas().temporalRange().begin().timeSpec(), QT_TIMESPEC_UTC)
					else:
						date_tspec = 1
				else:
					date_tspec = date
				self.time2date_tspec[t] = date_tspec
				self.timekey2date_tspec['{0:.6f}'.format(t)] = date_tspec
				self.date_tspec2time[date_tspec] = t
				self.date_tspec2timekey[date_tspec] = '{0:.6f}'.format(t)
				self.date2date_tspec[date] = date_tspec
				self.date_tspec2date[date_tspec] = date

		self.tuView.cboTime.clear()
		# timeCopy = [x for x in self.time2date.keys()]
		timeCopy = [x for x in self.time2date_tspec.keys()]
		if '-99999' in timeCopy:
			timeCopy.remove('-99999')
		if -99999 in timeCopy:
			timeCopy.remove(-99999)

		# self.tuView.cboTime.addItems([self._dateFormat.format(self.time2date[x]) for x in timeCopy])
		self.tuView.cboTime.addItems([self._dateFormat.format(self.time2date_tspec[x]) for x in timeCopy])

	def updateDateTimes_31600(self, **kwargs):
		"""update the dates of results for qgis 3.16 +"""

		get_metadata = kwargs['get_metadata'] if 'get_metadata' in kwargs else True

		self.timekey2date.clear()
		self.time2date.clear()
		self.date2timekey.clear()
		self.date2time.clear()

		self.timekey2date_tspec.clear()
		self.time2date_tspec.clear()
		self.date_tspec2timekey.clear()
		self.date_tspec2time.clear()
		self.date2date_tspec.clear()
		self.date_tspec2date.clear()

		for result in self.results:
			# if get_metadata:
			# 	layer = coastalmeqgis_find_layer(result)
			# 	if layer is not None and layer.dataProvider().datasetGroupCount() > 0:
			# 		self.tuResults2D.getResultMetaData(result, layer)
			for restype in self.results[result]:
				rt = None
				if 'referenceTime' in self.results[result][restype]:
					if restype == '_nc_grid':
						lyr = self.tuResultsNcGrid.results.get(result)
						if lyr is not None:
							lyr = lyr[0]
							self.results[result][restype]['referenceTime'] = lyr.reference_time
					rt = self.results[result][restype]['referenceTime']
				if rt is not None:
					if 'times' in self.results[result][restype]:
						for timeKey in self.results[result][restype]['times']:
							time = self.results[result][restype]['times'][timeKey][0]
							if self.tuView.tuOptions.timeUnits == 's':
								date = rt + timedelta(seconds=float(time))
							else:
								try:
									date = rt + timedelta(hours=float(time))
								except OverflowError:
									date = rt + timedelta(seconds=float(time))
							date = roundSeconds(date, 2)
							self.timekey2date[timeKey] = date
							self.time2date[time] = date
							self.date2timekey[date] = timeKey
							self.date2time[date] = time
							date_tspec = datetime2timespec(date, QT_TIMESPEC_UTC, QT_TIMESPEC_UTC)
							self.timekey2date_tspec[timeKey] = date_tspec
							self.time2date_tspec[time] = date_tspec
							self.date_tspec2timekey[date_tspec] = '{0:.6f}'.format(time)
							self.date_tspec2time[date_tspec] = time
							self.date2date_tspec[date] = date_tspec
							self.date_tspec2date[date_tspec] = date

	def updateQgsTime(self, time=None, qgsObject=None, timeSpec=None):

		qv = Qgis.QGIS_VERSION_INT

		if qv < 31600:
			self.updateQgsTime_old(time, qgsObject, timeSpec)
		else:
			self.updateQgsTime_31600(time, qgsObject, timeSpec)

	def updateQgsTime_old(self, time=None, qgsObject=None, timeSpec=None):
		"""

		"""

		qv = Qgis.QGIS_VERSION_INT
		tt = 0.01  # tiny time (seconds)

		if qv >= 31300:
			TuResults.layersToMethodLower(self.tuResults2D.activeMeshLayers)
			if time is None:
				if self.activeTime is None:
					return
				try:
					time = self.timekey2time[self.activeTime]
					# maybe can delete this later - but at the moment last dataset isn't rendered
					# if qgs temporal range is outside layer temporal range - so switch the lookup method
					for resname, res in self.results.items():
						for restype in res:
							if restype in self.activeResults:
								if self.results[resname][restype]['isTemporal']:
									if TuResults.isMapOutputType(restype):
										if 'times' in self.results[resname][restype]:
											a = [self.timekey2time[x] for x in self.results[resname][restype]['times'].keys()]
											if time >= max(a):
											# if sorted([x for x in self.results[resname][restype]['times'].keys()]).index(self.activeTime) == len(self.results[resname][restype]['times']) - 1:
												TuResults.layersToMethodHigher(self.tuResults2D.activeMeshLayers)
												if tt > 0:
													tt *= -1
												break
				except:
					time = float(self.activeTime)
			if qgsObject is None:
				if self.iface is not None:
					qgsObject = self.iface.mapCanvas()
				else:
					qgsObject = None
			if timeSpec is None:
				if self.iface is not None:
					timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
				else:
					timeSpec = 1
			zt = self.tuView.tuOptions.zeroTime
			#rt = dt2qdt(zt, self.iface.mapCanvas().temporalRange().begin().timeSpec())
			rt = dt2qdt(zt, self.loadedTimeSpec)
			rt = rt.toTimeSpec(timeSpec)
			# rt = QDateTime(QDate(zt.year, zt.month, zt.day),
			#                QTime(zt.hour, zt.minute, zt.second, zt.microsecond / 1000.))
			# rt.setTimeSpec(self.iface.mapCanvas().temporalRange().begin().timeSpec())
			secs = roundSeconds2(time, 2)
			# begin = rt.addSecs(time * 60. * 60 - tt)
			begin = rt.addMSecs((secs + tt) * 1000)
			end = begin.addSecs(60.*60.)
			dtr = QgsDateTimeRange(begin, end)


			#self.iface.mapCanvas().setTemporalRange(dtr)
			#self.iface.mapCanvas().refresh()
			if qgsObject is not None:
				qgsObject.setTemporalRange(dtr)
				qgsObject.refresh()

	def updateQgsTime_31600(self, time=None, qgsObject=None, timeSpec=None):
		"""

		"""

		qv = Qgis.QGIS_VERSION_INT
		tt = 0.01  # tiny time (seconds)

		TuResults.layersToMethodHigher(self.tuResults2D.activeMeshLayers)
		if time is None:
			if self.activeTime is None:
				return
			time = self.activeTime

		if qgsObject is None:
			if self.iface is not None:
				qgsObject = self.iface.mapCanvas()
		if timeSpec is None:
			if self.iface is not None:
				timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
			else:
				timeSpec = 1
		begin = dt2qdt(time, QT_TIMESPEC_UTC)
		end = begin.addSecs(int(self.output_timestep() * 60. * 60.))
		dtr = QgsDateTimeRange(begin, end)
		if qgsObject is not None:
			if qv >= 31300 and self.iface is not None:
				try:
					self.iface.mapCanvas().temporalRangeChanged.disconnect(self.tuView.qgsTimeChanged)
				except:
					pass
			qgsObject.setTemporalRange(dtr)
			qgsObject.refresh()
			if qv >= 31300 and self.iface is not None:
				self.iface.mapCanvas().temporalRangeChanged.connect(self.tuView.qgsTimeChanged)

	def initialiseTemporalController(self, qgsObject=None, timeSpec=None):
		if qgsObject is None:
			if self.iface is not None:
				qgsObject = self.iface.mapCanvas()
		if timeSpec is None:
			if self.iface is not None:
				timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
			else:
				timeSpec = 1

		# check if temporal controller has already been initialised
		if self.iface is not None:
			if timeSpec == 0 or not qgsObject.temporalRange().begin().isValid() or not qgsObject.temporalRange().end().isValid():
				wasConnected = False
				try:
					self.iface.mapCanvas().temporalRangeChanged.disconnect(self.qgsTimeChanged)
					wasConnected = True
				except:
					pass
				begin = datetime.now()
				end = begin + timedelta(seconds=1)
				begin = dt2qdt(begin, QT_TIMESPEC_UTC)
				end = dt2qdt(end, QT_TIMESPEC_UTC)
				dtr = QgsDateTimeRange(begin, end)
				qgsObject.setTemporalRange(dtr)
				qgsObject.refresh()
				if wasConnected:
					if self.iface is not None:
						self.iface.mapCanvas().temporalRangeChanged.connect(self.qgsTimeChanged)

	def getTuViewTimeFromQgsTime(self):
		qv = Qgis.QGIS_VERSION_INT
		if qv < 31600:
			return self.getTuViewTimeFromQgsTime_old()
		else:
			return self.getTuViewTimeFromQgsTime_31600()

	def getTuViewTimeFromQgsTime_old(self):
		"""

		"""

		qv = Qgis.QGIS_VERSION_INT

		if qv >= 31300:
			if self.iface is not None:
				qdt = self.iface.mapCanvas().temporalRange().begin()  # QDateTime
			else:
				qdt = QgsDateTimeRange()
			if not qdt.isValid():
				return float(self.activeTime)
			else:
				if self.timeSpec > 0:
					modelDates = sorted([x for x in self.date_tspec2time.keys()])
				else:
					modelDates = sorted([x for x in self.date2time.keys()])
				if modelDates:
					# fdt = modelDates[0]  # first datetime
					# ldt = modelDates[-1]  # last datetime
					# modelBegin = QDateTime(QDate(fdt.year, fdt.month, fdt.day),
					#                        QTime(fdt.hour, fdt.minute, fdt.second, fdt.microsecond / 1000.))
					# modelBegin.setTimeSpec(self.iface.mapCanvas().temporalRange().begin().timeSpec())
					# modelEnd = QDateTime(QDate(ldt.year, ldt.month, ldt.day),
					#                      QTime(ldt.hour, ldt.minute, ldt.second, ldt.microsecond / 1000.))
					# modelEnd.setTimeSpec(self.iface.mapCanvas().temporalRange().begin().timeSpec())
					# modelRange = QgsDateTimeRange(modelBegin, modelEnd)
					# qdt = self.iface.mapCanvas().temporalRange().begin()  # QDateTime
					pdt = datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),     # python datetime
					               qdt.time().hour(), qdt.time().minute(), qdt.time().second(),
					               int(round(qdt.time().msec(), -1) * 1000.))
					if self.loadedTimeSpec > 0:
						pdt = datetime2timespec(pdt, self.timeSpec, self.loadedTimeSpec)
					# qgsEnd = self.iface.mapCanvas().temopralRange().end()

					return self.findTimeClosest(None, None, pdt, modelDates, True, 'closest')
				else:
					return 0

	def getTuViewTimeFromQgsTime_31600(self):
		if self.iface is not None:
			qdt = self.iface.mapCanvas().temporalRange().begin()  # QDateTime
		else:
			qdt = QgsDateTimeRange()
		if not qdt.isValid():
			return self.activeTime
		modelDates = sorted([x for x in self.date2time.keys()])
		if not modelDates:
			return self.activeTime
		pdt = qdt2dt(qdt)
		if self.loadedTimeSpec > 0:
			pdt = datetime2timespec(pdt, self.timeSpec, self.loadedTimeSpec)
		return TuResults.findDateClosest_31600(self, None, None, pdt, modelDates, 'closest', self.tuView.tuOptions.timeUnits)

	def addCrossSectionLayerToResults(self, lyr):
		"""

		"""

		from .coastalmeqgis_tuplot import TuPlot

		updateOpenResults = False
		if lyr.name() not in self.results:
			self.results[lyr.name()] = {}
			updateOpenResults = True
		if 'line_cs' not in self.results[lyr.name()]:
			self.results[lyr.name()]['line_cs'] = {}

		for t in XS.getAllTypes(lyr):
			self.results[lyr.name()]['line_cs'][t] = XS.getAllSourcesForType(lyr, t, NULL)

		if updateOpenResults:
			self.updateOpenResults(lyr.name(), NULL)
		else:
			self.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection, plot='1d only')

	def add1dHydTableToResults(self, displayName, table):
		"""

		"""

		from .coastalmeqgis_tuplot import TuPlot

		if displayName not in self.results:
			self.results[displayName] = {}
		if 'line_cs' not in self.results[displayName]:
			self.results[displayName]['line_cs'] = {}

		for t in sorted(table.getAllTypes()):
			self.results[displayName]['line_cs'][t] = table.getAllIdsForType(t)

		self.updateOpenResults(displayName)

	def remove1dHydTable(self, displayName):
		"""

		"""

		if displayName in self.results:
			del self.results[displayName]

		self.updateOpenResults(displayName)

	@staticmethod
	def isMapOutputType(resultType):
		"""Returns true if resultType is a Map Output"""

		a = [True for x in TuResults.OtherTypes if x in resultType.lower()]
		return len(a) == 0

	@staticmethod
	def isParticleType(resultType):
		"""Returns true if resultType is a ptm output"""

		return '_particles' in resultType

	@staticmethod
	def isTimeSeriesType(resultType):
		"""Returns true if resultType is a Map Output"""

		a = [True for x in [x for x in TuResults.OtherTypes if '_particles' not in x] if x in resultType.lower()]
		return len(a) > 0

	def updateTemporalProperties(self):
		#for res, val in self.results.items():
		#	for restype in val:
		#		if TuResults.isMapOutputType(restype):
		#			layer = coastalmeqgis_find_layer(res)
		#			layer.setReferenceTime(dt2qdt(self.tuResults2D.getReferenceTime(layer),
		#		                                  self.iface.mapCanvas().temporalRange().begin().timeSpec()))
		#			break
		if self.iface is not None:
			self.timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
		else:
			self.timeSpec = 1
		self.updateQgsTime()

	@staticmethod
	def layersToMethodLower(layers):
		"""turns layers to find next lower timestep"""

		for lyr in layers:
			if type(lyr) is str:
				lyr = coastalmeqgis_find_layer(lyr)
			lyr.setTemporalMatchingMethod(QgsMeshDataProviderTemporalCapabilities.FindClosestDatasetBeforeStartRangeTime)

	@staticmethod
	def layersToMethodHigher(layers):
		"""turns layers to find next lower timestep"""

		for lyr in layers:
			if type(lyr) is str:
				lyr = coastalmeqgis_find_layer(lyr)
			if lyr is None:
				return
			lyr.setTemporalMatchingMethod(QgsMeshDataProviderTemporalCapabilities.FindClosestDatasetFromStartRangeTime)

	def dateToTimeInCombobox(self, inputDate):
		rt = self.tuView.tuOptions.zeroTime
		dateFormat = self.tuView.tuOptions.xAxisDates
		time = 0
		for i in range(self.tuView.cboTime.count()):  # find closest
			item = self.tuView.cboTime.itemText(i)
			if dateFormat:
				date = datetime.strptime(item, self.dateFormat)
			else:
				timeKey = convertFormattedTimeToTime(item)
				t = self.tuView.tuResults.timekey2time[timeKey] if timeKey in self.tuView.tuResults.timekey2time else float(
					timeKey)
				if self.tuView.tuOptions.timeUnits == 's':
					date = rt + timedelta(seconds=t)
				else:
					try:
						date = rt + timedelta(hours=t)
					except OverflowError:
						date = rt + timedelta(seconds=t)
			if date == inputDate:
				if dateFormat:
					return date, i
				else:
					return t, i
			if i == 0:
				diff = abs((date - inputDate).total_seconds())
			if date > inputDate:
				diff2 = abs((date - inputDate).total_seconds())
				if diff <= diff2:
					item = self.tuView.cboTime.itemText(max(0, i - 1))
					if dateFormat:
						return datetime.strptime(item, self.dateFormat), max(0, i-1)
					else:
						timeKey = convertFormattedTimeToTime(item)
						time = self.tuView.tuResults.timekey2time[
							timeKey] if timeKey in self.tuView.tuResults.timekey2time else float(timeKey)
						return time, max(0, i-1)
				else:
					if dateFormat:
						return date, i
					else:
						return t, i
			else:
				diff = abs((date - inputDate).total_seconds())

		i = 0
		item = self.tuView.cboTime.itemText(i)
		if dateFormat:
			if item == '':
				return self.tuView.tuOptions.zeroTime, i
			date = datetime.strptime(item, self.dateFormat)
			return date, i
		timeKey = convertFormattedTimeToTime(item)
		time = self.tuView.tuResults.timekey2time[timeKey] if timeKey in self.tuView.tuResults.timekey2time else float(
			timeKey)
		return time, 0

	def output_timestep(self):
		if self.dt and [x for x in self.results.keys()] == self._res_names:
			return self.dt
		dt = None
		for key, value in self.results.items():
			if 'timestep' in value:
				pass
			elif isinstance(value, dict):
				for key_, value_ in value.items():
					if 'times' in value_:
						prev_time = None
						for key__, value__ in value_['times'].items():
							if (isinstance(value__, list) or isinstance(value__, tuple)) and value__:
								x = value__[0]
								if isinstance(x, float):
									if prev_time is not None:
										dt_ = x - prev_time
										if dt:
											dt = min(dt, dt_)
										else:
											dt = dt_
									else:
										prev_time = x
							elif isinstance(value__, float):
								if prev_time is not None:
									dt_ = value__ - prev_time
									if dt:
										dt = min(dt, dt_)
									else:
										dt = dt_
								else:
									prev_time = value__

		self.dt = dt if dt is not None else None
		self._res_names = [x for x in self.results.keys()]
		return dt if dt is not None else 1.0



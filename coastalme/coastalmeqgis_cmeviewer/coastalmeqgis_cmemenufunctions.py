import os
import sys
import numpy as np
import io
import datetime
import re
import glob
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import QgsDateTimeEdit
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtXml import QDomDocument
from matplotlib.patches import Polygon
from matplotlib.quiver import Quiver
from matplotlib.collections import PolyCollection
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from ..coastalmeqgis_library import (loadLastFolder, getResultPathsFromTCF, getScenariosFromTcf, getEventsFromTCF,
                                  getUnit, getCellSizeFromTCF, getOutputZonesFromTCF,
									   getPathFromRel, convertTimeToFormattedTime, convertFormattedTimeToTime,
									   getResultPathsFromTLF, browse, qgsxml_as_mpl_cdict,
									   generateRandomMatplotColours2, getResultPathsFromTCF_v2, mpl_version_int,
									   labels_about_to_break, labels_already_broken, applyMatplotLibArtist,
                                       qdt2dt)
from coastalme.toc.toc import coastalmeqgis_find_layer
from ..coastalmeqgis_dialog import (coastalmeqgis_scenarioSelection_dialog, coastalmeqgis_eventSelection_dialog,
									  CmeOptionsDialog, CmeSelectedElementsDialog, coastalmeqgis_meshSelection_dialog,
									  CmeBatchPlotExportDialog, CmeUserPlotDataManagerDialog,
									  coastalmeqgis_outputZoneSelection_dialog, coastalmeqgis_brokenLinks_dialog,
                                      FloodModellerResultImportDialog, coastalmeqgis_outputSelection_dialog,
									  getOutputFolderFromTCF)
from .coastalmeqgis_cmeanimation import CmeAnimationDialog
from .coastalmeqgis_cmemap import CmeMapDialog
from .coastalmeqgis_cmeresults import CmeResults
from ..nc_grid_data_provider import NetCDFGrid

from ..gui import Logging

from ..compatibility_routines import QT_MESSAGE_BOX_CANCEL, Path, QT_DOCK_WIDGET_AREA_RIGHT, QT_MESSAGE_BOX_YES, QT_ABSTRACT_ITEM_VIEW_EXTENDED_SELECTION, QT_MESSAGE_BOX_NO, QT_MESSAGE_BOX_RETRY, QT_ALIGN_RIGHT, QT_DOCK_WIDGET_AREA_BOTTOM
from ..coastalme_results_gpkg import ResData_GPKG

from ..fvbc_tide_dlg import ImportFVBCTideDlg


class CmeMenuFunctions():
	"""
	Generic class for handling menu functions.
	
	"""
	
	def __init__(self, CmeView):
		self.cmeView = CmeView
		self.iface = CmeView.iface
		self.labels_about_to_break = 0
	
	def load2dResults(self, **kwargs):
		"""
		Loads 2D results into map window and plotting ui

		:return: bool -> True for successful, False for unsuccessful
		"""

		qv = Qgis.QGIS_VERSION_INT

		result2D = kwargs['result_2D'] if 'result_2D' in kwargs.keys() else None  # list of xmdfs or dats
		
		if not result2D:
			# Get last loaded settings
			# fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_2DResults/lastFolder")
			fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/lastFolder")

			# User get 2D result file
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(), 'Open COASTALME 2D results file',
			                                           fpath,
			                                           "COASTALME 2D Results (*.xmdf *.dat *.sup *.2dm *.nc)")
			if not inFileNames[0]:  # empty list
				return False
			
		else:
			inFileNames = result2D
			if not inFileNames[0]:  # empty list
				return False
		
		# if .sup file - read and extract mesh and result datasets
		for file in inFileNames[0]:
			filename, ext = os.path.splitext(file)
			filename = os.path.basename(filename)
			res = {'path': file}
			self.cmeView.cmeResults.cmeResults2D.results2d[filename] = res

			if ext.upper() == '.SUP':
				# sups, engine, build = self.resultsFromSuperFiles(inFileNames[0])
				sups, engine, build = self.resultsFromSuperFiles([file])
				# # did xmdf always get written in hrs? should i use build instead of ext?
				# dsext = '.dat'
				# if sups:
				# 	if sups[list(sups.keys())[0]]['datasets']:
				# 		dsext = os.path.splitext(sups[list(sups.keys())[0]]['datasets'][0])[1]
				# if engine == 'FV' and dsext.lower() == '.dat':
				if engine == 'FV' and qv < 31300:
					self.cmeView.cmeOptions.timeUnits = 's'
				else:
					self.cmeView.cmeOptions.timeUnits = 'h'

			# import into qgis
			if ext.upper() == '.SUP':
				loaded = self.cmeView.cmeResults.importResults('mesh', sups)
			# elif ext.upper() == '.NC' and NetCDFGrid.is_nc_grid(file):
			# 	loaded = self.cmeView.cmeResults.importResults('nc_grid', file)
			else:
				# loaded = self.cmeView.cmeResults.importResults('mesh', inFileNames[0])
				loaded = self.cmeView.cmeResults.importResults('mesh', [file])

		# finally save the last folder location
		fpath = os.path.dirname(inFileNames[0][0])
		settings = QSettings()
		settings.setValue("COASTALME_Results/lastFolder", fpath)
		
		if not loaded:
			return False
		
		return True
	
	def load1dResults(self, **kwargs):
		"""
		Loads 1D results into ui and prompts user to load GIS files.

		:return: bool -> True for successful, False for unsuccessful
		"""
		
		result1D = kwargs['result_1D'] if 'result_1D' in kwargs.keys() else None
		unlock = kwargs['unlock'] if 'unlock' in kwargs else True
		askGis = kwargs['ask_gis'] if 'ask_gis' in kwargs else True
		openGis = kwargs['open_gis'] if 'open_gis' in kwargs else None

		success = False
		if openGis is not None:
			askGis = False
		
		if not result1D:
			# Get last loaded settings
			# fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_1DResults/lastFolder")
			fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/lastFolder")

			# User get 1D result file
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(), 'Open COASTALME 1D results file',
			                                           fpath,
			                                           "COASTALME 1D Results (*.tpc *.info *.gpkg);;TPC (*.tpc);;INFO (*.info);;GPKG (*.gpkg)")
			if not inFileNames[0]:  # empty list
				return False
			
		else:
			# check if the result paths exist
			# for loading in project - check if links are not broken
			inFileNames = []
			brokenLinks = []
			for inFileName in result1D[0]:
				if os.path.exists(inFileName):
					inFileNames.append(inFileName)
				else:
					brokenLinks.append(inFileName)
			if brokenLinks:
				brokenLinksDialog = coastalmeqgis_brokenLinks_dialog(self.iface, brokenLinks)
				brokenLinksDialog.exec()
			inFileNames = [inFileNames]
			
		if not inFileNames[0]:
			return False
		
		# Prompt user if they want to load in GIS files
		for inFileName in inFileNames[0]:
			if os.path.splitext(inFileName)[1].lower() == '.gpkg':
				if askGis:
					alsoOpenGis = QT_MESSAGE_BOX_YES
				else:
					alsoOpenGis = QT_MESSAGE_BOX_NO
				break
			alsoOpenGis = QT_MESSAGE_BOX_NO
			if os.path.splitext(inFileName)[1].lower() in ['.tpc']:
				if askGis:
					alsoOpenGis = QMessageBox.question(self.iface.mainWindow(),
					                                   "COASTALME Viewer", 'Do you also want to open result GIS layer?',
					                                   QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL)
				else:
					if openGis is not None:
						alsoOpenGis = QT_MESSAGE_BOX_YES if openGis else QT_MESSAGE_BOX_NO
			break  # only need to ask once
		# if alsoOpenGis == QT_MESSAGE_BOX_YES:
		# 	self.cmeView.cmeResults.cmeResults1D.openGis(inFileNames[0][0])
		if alsoOpenGis == QT_MESSAGE_BOX_CANCEL:
			return False
		
		# import results
		success = self.cmeView.cmeResults.importResults('timeseries', inFileNames[0])
		if success:
			self.cmeView.cmeResults.cmeResults1D.open_gis(alsoOpenGis == QT_MESSAGE_BOX_YES)
		
		# unlock map output timesteps only
		if unlock:
			if self.cmeView.lock2DTimesteps:
				self.cmeView.timestepLockChanged()
		
		# finally save the last folder location
		if askGis:  # if not ask gis then not being loaded from interface
			fpath = os.path.dirname(inFileNames[0][0])
			settings = QSettings()
			settings.setValue("COASTALME_Results/lastFolder", fpath)
		
		return success

	def loadFMResults(self, **kwargs):
		"""
		Loads 1D FM results into ui.

		:return: bool -> True for successful, False for unsuccessful
		"""

		unlock = kwargs['unlock'] if 'unlock' in kwargs else True
		gxy = kwargs['gxy'] if 'gxy' in kwargs else None
		dat = kwargs['dat'] if 'dat' in kwargs else None
		result_FM = kwargs['result_FM'] if 'result_FM' in kwargs else None

		success = False
		self.fmResultsDialog = FloodModellerResultImportDialog()
		if gxy is not None and result_FM is not None:
			self.fmResultsDialog.gxy = gxy
			self.fmResultsDialog.dat = dat
			self.fmResultsDialog.results = result_FM
		else:
			self.fmResultsDialog.exec()

		# check file paths exist
		# done in dialog class

		# import results
		success = self.cmeView.cmeResults.importResults('timeseries FM', [self.fmResultsDialog.gxy, self.fmResultsDialog.dat] + self.fmResultsDialog.results)

		# unlock map output timesteps only
		if unlock:
			if self.cmeView.lock2DTimesteps:
				self.cmeView.timestepLockChanged()

		return success

	def loadParticlesResults(self, **kwargs):
		"""
		Loads Particles results into ui and prompts user to load GIS files.

		:return: bool -> True for successful, False for unsuccessful
		"""

		resultParticles = kwargs['result_particles'] if 'result_particles' in kwargs.keys() else None
		unlock = kwargs['unlock'] if 'unlock' in kwargs else True
		askGis = kwargs['ask_gis'] if 'ask_gis' in kwargs else True

		if not resultParticles:
			# Get last loaded settings
			fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_ParticlesResults/lastFolder")

			# User get 1D result file
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(), 'Open COASTALME Particles results file',
													   fpath,
													   "COASTALME Particles Results (*.nc)")
			if not inFileNames[0]:  # empty list
				return False

		else:
			# check if the result paths exist
			# for loading in project - check if links are not broken
			inFileNames = []
			brokenLinks = []
			for inFileName in resultParticles[0]:
				if os.path.exists(inFileName):
					inFileNames.append(inFileName)
				else:
					brokenLinks.append(inFileName)
			if brokenLinks:
				brokenLinksDialog = coastalmeqgis_brokenLinks_dialog(self.iface, brokenLinks)
				brokenLinksDialog.exec()
			inFileNames = [inFileNames]

		if not inFileNames[0]:
			return False

		# Prompt user if they want to load in GIS files
		for inFileName in inFileNames[0]:
			alsoOpenGis = QT_MESSAGE_BOX_NO
			if os.path.splitext(inFileName)[1].lower() == '.tpc':
				if askGis:
					alsoOpenGis = QMessageBox.question(self.iface.mainWindow(),
													   "COASTALME Viewer", 'Do you also want to open result GIS layer?',
													   QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL)
			break  # only need to ask once
		if alsoOpenGis == QT_MESSAGE_BOX_YES:
			self.cmeView.cmeResults.cmeResults1D.openGis(inFileNames[0][0])
		elif alsoOpenGis == QT_MESSAGE_BOX_CANCEL:
			return False

		# import results
		self.cmeView.cmeResults.importResults('particles', inFileNames[0])

		# unlock map output timesteps only
		if unlock:
			if self.cmeView.lock2DTimesteps:
				self.cmeView.timestepLockChanged()

		# finally save the last folder location
		fpath = os.path.dirname(inFileNames[0][0])
		settings = QSettings()
		settings.setValue("COASTALME_ParticlesResults/lastFolder", fpath)

		return True

	def loadNcGridResults(self, **kwargs):
		if not NetCDFGrid.capable():
			QMessageBox.warning(self.cmeView, 'Python NetCDF Library Not Installed',
								'NetCDF4 Python library not installed. Please see the following wiki page for more information:<p>'
								'<a href="https://wiki.coastalme.com/index.php?title=COASTALME_Viewer_-_Load_Results_-_NetCDF_Grid"'
								'<span style=" text-decoration: underline; color:#0000ff;">wiki.coastalme.com/index.php?title=COASTALME_Viewer_-_Load_Results_-_NetCDF_Grid'
								'</span></a>'
								)
			return

		inFileNames = kwargs['files'] if 'files' in kwargs else None

		# Get last loaded settings
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/lastFolder")

		# User get file
		if inFileNames is None:
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(), 'Open COASTALME results file',
													   fpath,
													   "NetCDF (*.nc)")

		if not inFileNames[0]:  # empty list
			return False

		# import results
		self.cmeView.cmeResults.importResults('nc_grid', inFileNames[0])

		# finally save the last folder location
		fpath = os.path.dirname(inFileNames[0][0])
		settings = QSettings()
		settings.setValue("COASTALME_Results/lastFolder", fpath)

		return True

	def load1d2dResults(self, **kwargs):
		"""
		Loads 1D and 2D reuslts from TCF file.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		inFileNames = kwargs['files'] if 'files' in kwargs else None

		# Get last loaded settings
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/lastFolder")
		
		# User get TCF file
		if inFileNames is None:
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(), 'Open COASTALME results file',
			                                           fpath,
			                                           "All Available (*.tcf *.tlf *.TCF *.TLF);;COASTALME Control File (*.tcf *.TCF);;COASTALME Log File (*.tlf *.TLF)")
		
		if not inFileNames[0]:  # empty list
			return False

		# get 1D and 2D results from TCF or TLF
		results1D, results2D, messages = [], [], []
		for file in inFileNames[0]:
			ext = os.path.splitext(file)[1].lower()
			
			if ext == '.tcf':
				if self.cmeView.cmeOptions.tcfLoadMethod == 'scenario_selection':
					# get scenarios from TCF and prompt user to select desired scenarios
					error, message, scenarios = getScenariosFromTcf(file)
					if error:
						if message:
							QMessageBox.critical(self.cmeView, "Load From TCF", message)
					if scenarios:
						if self.iface is not None:
							self.scenarioDialog = coastalmeqgis_scenarioSelection_dialog(self.iface, file, scenarios)
							self.scenarioDialog.exec()
							if self.scenarioDialog.scenarios is None:
								scenarios = []
							else:
								scenarios = self.scenarioDialog.scenarios
						elif 'scenarios' in kwargs:
							scenarios = kwargs['scenarios']

					# get events from TCF and prompt user to select desired events
					events = getEventsFromTCF(file)
					if events:
						self.eventDialog = coastalmeqgis_eventSelection_dialog(self.iface, file, events)
						self.eventDialog.exec()
						if self.eventDialog.events is None:
							events = []
						else:
							events = self.eventDialog.events

					# get output zones from TCF and prompt user to select desired output zones
					outputZones = getOutputZonesFromTCF(file)
					selectedOutputZones = []
					if outputZones:
						self.outputZoneDialog = coastalmeqgis_outputZoneSelection_dialog(self.iface, file, outputZones)
						self.outputZoneDialog.exec()
						for opz in outputZones:
							if opz['name'] in self.outputZoneDialog.outputZones:
								selectedOutputZones.append(opz)

					res1D, res2D, mess = getResultPathsFromTCF(file, scenarios=scenarios, events=events, output_zones=selectedOutputZones)
				elif self.cmeView.cmeOptions.tcfLoadMethod == 'result_selection':
					res1D, res2D, = [], []
					old_method = sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 9)
					paths, names, mess = getResultPathsFromTCF_v2(file, old_method)
					if names:
						if len(names) > 1:
							if self.iface is not None:
								output_selection = coastalmeqgis_outputSelection_dialog(self.iface, names)
								output_selection.exec()
								names = output_selection.outputs
							else:
								names = names[:1]
						for output in names:
							possible_paths = [x for x in paths if output in os.path.splitext(os.path.basename(x))[0] == output]
							for p in paths:
								if '_swmm_ts.gpkg' in os.path.basename(p):
									n = os.path.splitext(os.path.basename(p))[0]
									n = n.replace('_swmm_ts', '')
									if n == output:
										possible_paths.append(p)
							for pp in possible_paths:
								if old_method:
									suffix = os.path.splitext(pp)[1]
								else:
									suffix = pp.suffix
								if suffix.lower() in ['.xmdf', '.dat']:
									res2D.append(str(pp))
								elif suffix.lower() in ['.tpc', '.gpkg']:
									res1D.append(str(pp))
				else:
					res1D, res2D, mess = [], [], ''

			else:
				res1D, res2D, mess = getResultPathsFromTLF(file)
			
			if res1D:
				if results1D:
					results1D[0] += res1D
				else:
					results1D.append(res1D)
			if res2D:
				if results2D:
					results2D[0] += res2D
				else:
					results2D.append(res2D)
			if mess:
				messages += mess

		kwargs['result_2D'] = results2D
		kwargs['result_1D'] = results1D
		kwargs['unlock'] = False

		ts_gpkg = [x for x in res1D if Path(x).suffix == '.gpkg']
		if ts_gpkg:
			res = ResData_GPKG()
			err, msg = res.Load(ts_gpkg[0])
			if not err:
				rt = res.reference_time
				self.cmeView.cmeResults.tmp_reference_time = rt
				res.close()

		# load 2D results
		if results2D:
			# self.load2dResults(result_2D=results2D)
			self.load2dResults(**kwargs)

		# load 1D results
		if results1D:
			# self.load1dResults(result_1D=results1D, unlock=False)
			self.load1dResults(**kwargs)

		# if no results found
		if not results2D and not results1D:
			mes = ''
			for i, m in enumerate(messages):
				if i == 0:
					mes += m
				else:
					mes += '\n\n{0}'.format(m)
			if self.iface is not None:
				QMessageBox.information(self.iface.mainWindow(), "COASTALME Viewer", "Failed to load results from {1}\n\n{0}".format(mes, ext.upper()[1:]))
			else:
				print("Failed to load results from {1}\n\n{0}".format(mes, ext.upper()[1:]))
			
		# finally save the last folder location
		fpath = os.path.dirname(inFileNames[0][0])
		settings = QSettings()
		settings.setValue("COASTALME_Results/lastFolder", fpath)

		if self.cmeView.cmeResults.tmp_reference_time is not None:
			self.cmeView.cmeResults.tmp_reference_time = None
		
		return True

	def loadBcTables(self, **kwargs):
		inFileNames = kwargs['files'] if 'files' in kwargs else None

		# Get last loaded settings
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/lastFolder")

		# User get TCF file
		if inFileNames is None:
			inFileNames = QFileDialog.getOpenFileNames(self.iface.mainWindow(),
			                                           'Open COASTALME 2d_bc_tables_check file',
			                                           fpath,
			                                           "CSV (*.csv *.CSV)")

		if not inFileNames[0]:  # empty list
			return False

		# import results
		success = self.cmeView.cmeResults.importResults('timeseries', inFileNames[0])
		fpath = os.path.dirname(inFileNames[0][0])
		settings = QSettings()
		settings.setValue("COASTALME_Results/lastFolder", fpath)

		return success

	def loadFVBCTide(self, **kwargs):
		unlock = kwargs['unlock'] if 'unlock' in kwargs else True
		nc_fpath = kwargs['nc_fpath'] if 'nc_fpath' in kwargs else None
		gis_fpath = kwargs['gis_fpath'] if 'gis_fpath' in kwargs else None
		use_local_time = kwargs['use_local_time'] if 'use_local_time' in kwargs else True
		if isinstance(use_local_time, str):
			use_local_time = True if use_local_time.lower() == 'true' else False

		res = None
		load_gis = True
		if nc_fpath is None or gis_fpath is None:
			dlg = ImportFVBCTideDlg(self.cmeView)
			if dlg.exec():
				res = self.cmeView.cmeResults.cmeResults1D.importResultsFVBCTide(dlg.nc_fpath, dlg.node_string_fpath, dlg.use_local_time)
		else:
			res = self.cmeView.cmeResults.cmeResults1D.importResultsFVBCTide(nc_fpath, gis_fpath, use_local_time)
			load_gis = False

		if res:
			if not load_gis:  # remove empty layers - memory layers aren't saved in projects
				for lyr in QgsProject.instance().mapLayersByName(res.gis_point_layer_name):
					QgsProject.instance().removeMapLayer(lyr.id())

			plyr = QgsVectorLayer(res.gis_point_fpath, res.gis_point_layer_name, 'memory')
			if not plyr.isValid():
				QMessageBox.critical(self.cmeView, 'Error', 'Failed to load point layer')
				return False
			plyr.setCustomProperty("skipMemoryLayersCheck", 1)
			plyr.setCustomProperty('isCOASTALMEPlotLayer', 1)

			feats = []
			for label in res.ids():
				points = res.provider.get_ch_points(label)
				for i, row in enumerate(points):
					ch, x, y = row[0], row[1], row[2]
					feat = QgsFeature()
					feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
					feat.setAttributes([f'{label}_{i}', ch, 'BC_NS', 'H_'])
					feats.append(feat)
			plyr.dataProvider().addFeatures(feats)
			plyr.updateExtents()

			if load_gis:
				llyr = QgsVectorLayer(res.gis_line_fpath, res.gis_line_layer_name, 'ogr')
				if not llyr.isValid():
					QMessageBox.critical(self.cmeView, 'Error', 'Failed to load line layer')
					return False
				llyr.setCustomProperty('isCOASTALMEPlotLayer', 1)

				self.cmeView.project.addMapLayer(llyr)

			self.cmeView.project.addMapLayer(plyr)

		if unlock and res:
			if self.cmeView.lock2DTimesteps:
				self.cmeView.timestepLockChanged()

		return True
	
	def remove1d2dResults(self):
		"""
		Removes the selected results from the ui.
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		results = []
		for item in self.cmeView.OpenResults.selectedItems():
			if self.cmeView.hydTables.getData(item.text()) is None:
				results.append(item.text())

		self.cmeView.cmeResults.removeResults(results)
		for result in results:
			layer = coastalmeqgis_find_layer(result)
			# self.cmeView.project.removeMapLayer(layer)
			if layer is not None:
				try:
					layer.nameChanged.disconnect()
				except:
					pass
				try:
					signal = self.cmeView.cmeResults.cmeResults2D.layer_style_changed_signals.get(layer.id())
					if signal is not None:
						layer.rendererChanged.disconnect(signal)
						del self.cmeView.cmeResults.cmeResults2D.layer_style_changed_signals[layer.id()]
				except:
					print('ERROR: disconnecting style changed signal')
				if Qgis.QGIS_VERSION_INT >= 32800:
					try:
						signal = self.cmeView.cmeResults.cmeResults2D.layer_reloaded_signals.get(layer.id())
						if signal is not None:
							layer.reloaded.disconnect(signal)
							del self.cmeView.cmeResults.cmeResults2D.layer_reloaded_signals[layer.id()]
					except:
						pass
				self.cmeView.project.removeMapLayer(layer.id())

		if self.cmeView.canvas is not None:
			self.cmeView.canvas.refresh()
		self.cmeView.resultsChanged()
		
		return True
	
	def remove2dResults(self):
		"""
		Removes the selected results from the ui - 2D results only
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		results = []
		for item in self.cmeView.OpenResults.selectedItems():
			if self.cmeView.hydTables.getData(item.text()) is None:
				layer = coastalmeqgis_find_layer(item.text())
				if layer:
					self.cmeView.project.removeMapLayer(layer.id())

		if self.cmeView.canvas is not None:
			self.cmeView.canvas.refresh()
		self.cmeView.resultsChanged()
		
		return True
	
	def remove1dResults(self):
		"""
		Removes the selected results from the ui - 1D results only
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		results = []
		for item in self.cmeView.OpenResults.selectedItems():
			if self.cmeView.hydTables.getData(item.text()) is None:
				results.append(item.text())
		
		self.cmeView.cmeResults.cmeResults1D.removeResults(results)
		
		self.cmeView.resultsChanged()
		
		return True

	def removeParticlesResults(self):
		"""
		Removes the selected results from the ui - 1D results only

		:return: bool -> True for successful, False for unsuccessful
		"""

		results = []
		for item in self.cmeView.OpenResults.selectedItems():
			if self.cmeView.hydTables.getData(item.text()) is None:
				results.append(item.text())

		self.cmeView.cmeResults.cmeResultsParticles.removeResults(results)

		self.cmeView.resultsChanged()

		return True

	def updateMapPlotWindows(self):
		"""
		Update map window and all plot windows

		:return: bool -> True for successful, False for unsuccessful
		"""

		self.cmeView.renderMap()
		
		self.cmeView.cmePlot.updateCurrentPlot(self.cmeView.tabWidget.currentIndex())
		
		return True
	
	def options(self):
		"""
		Open options dialog
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		qv = Qgis.QGIS_VERSION_INT
		
		xAxisDatesPrev = self.cmeView.cmeOptions.xAxisDates
		showGridPrev = self.cmeView.cmeOptions.showGrid
		showTrianglesPrev = self.cmeView.cmeOptions.showTriangles
		timeUnitsPrev = self.cmeView.cmeOptions.timeUnits
		zeroDatePrev = self.cmeView.cmeOptions.zeroTime
		plotBackgroundColorPrev = self.cmeView.cmeOptions.plotBackgroundColour
		self.cmeOptionsDialog = CmeOptionsDialog(self.cmeView.cmeOptions)
		self.cmeOptionsDialog.cboIconSize.currentIndexChanged.connect(lambda: self.cmeView.iconSizeChanged(int(self.cmeOptionsDialog.cboIconSize.currentText())))
		self.cmeOptionsDialog.exec()

		if self.cmeView.cmeMenuBar.showMedianEvent_action.isChecked() or self.cmeView.cmeMenuBar.showMeanEvent_action.isChecked():
			self.cmeView.renderMap()
		if self.cmeView.cmeOptions.showGrid != showGridPrev or self.cmeView.cmeOptions.showTriangles != showTrianglesPrev:
			self.cmeView.renderMap()
		if self.cmeView.cmeOptions.xAxisDates != xAxisDatesPrev:
			#self.cmeView.cmeResults.updateResultTypes()
			self.cmeView.cbShowAsDates.setChecked(self.cmeView.cmeOptions.xAxisDates)
			# self.cmeView.cmeResults.updateTimeUnits()
		if self.cmeView.cmeOptions.timeUnits != timeUnitsPrev:
			self.cmeView.cmeResults.updateTimeUnits()
		# if self.cmeView.cmeOptions.xAxisDates:
		if self.cmeView.cmeOptions.zeroTime != zeroDatePrev:
			# if qv >= 31600:
			# 	times = []
			# 	diff = (self.cmeView.cmeOptions.zeroTime - zeroDatePrev).total_seconds() / 60. / 60.
			# 	for i in range(self.cmeView.cboTime.count()):
			# 		if self.cmeView.cmeOptions.xAxisDates:
			# 			time = self.cmeView.cmeResults.date2time[datetime.strptime(item, self.cmeView.cmeResults.dateFormat)]
			# 		else:
			# 			item = self.cmeView.cboTime.itemText(i)
			# 			timeKey = self.cmeView.cmeResults.cboTime2timekey[item]
			# 			time = self.cmeView.cmeResults.timekey2time[timeKey]
			# 		times.append(time + diff)
			# 	self.cmeView.cmeResults.timekey2time.clear()
			# 	self.cmeView.cmeResults.timekey2time = {'{0:.6f}'.format(x): x for x in times}

			self.cmeView.cmeResults.updateTimeUnits()
			self.cmeView.cmeResults.updateDateTimes()

			if qv >= 31600:
				self.cmeView.cmeResults.updateResultTypes()
			#self.cmeView.cmeResults.updateDateTimes2()

		if self.cmeView.cmeOptions.plotBackgroundColour != plotBackgroundColorPrev:
			for plotNo in range(4):
				parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, yAxisLabels, xAxisLabels, xAxisLimits, yAxisLimits = \
					self.cmeView.cmePlot.plotEnumerator(plotNo)
				rect = figure.patch
				rect.set_facecolor(self.cmeView.cmeOptions.plotBackgroundColour)
				plotWidget.draw()

		self.cmeView.iconSizeChanged(self.cmeView.cmeOptions.iconSize)

		self.cmeView.cmePlot.updateCurrentPlot(self.cmeView.tabWidget.currentIndex(), update='1d and 2d only')
		self.cmeView.cmePlot.cmePlotToolbar.cursorTrackingButton.setChecked(self.cmeView.cmeOptions.liveMapTracking)

		return True
	
	def exportCSV(self, e=None, plot_no=None, save_file=None, **kwargs):
		"""
		Export the data as a CSV.

		:return: bool -> True for successful, False for unsuccessful
		"""

		if plot_no is None:
			plotNo = self.cmeView.tabWidget.currentIndex()
		else:
			plotNo = plot_no
		
		dataHeader, data = self.getPlotData(plotNo, **kwargs)

		if dataHeader is None or data is None:
			# QMessageBox.critical(self.iface.mainWindow(), 'COASTALME Viewer', 'Error exporting data')
			if self.iface is not None:
				QMessageBox.warning(self.iface.mainWindow(), 'COASTALME Viewer',
				                    'No data on plot or an error occured - note curtain plots aren\'t able to be exported or copied yet')
			else:
				print(
					'No data on plot or an error occured - note curtain plots aren\'t able to be exported or copied yet')
			return False
		
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/export_csv")
		
		if save_file is None:
			saveFile = QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Save File', fpath)[0]
			if len(saveFile) < 2:
				return
			else:
				if saveFile != os.sep and saveFile.lower() != 'c:\\' and saveFile != '':
					QSettings().setValue("COASTALME_Results/export_csv", saveFile)
				if not os.path.splitext(saveFile)[-1]:  # no extension specified - default to csv
					saveFile = '{0}.csv'.format(saveFile)
		else:
			saveFile = save_file
		
		if saveFile is not None:
			retry = True
			while retry:
				try:
					file = open(saveFile, 'w')
					file.write('{0}\n'.format(dataHeader))
					for i, row in enumerate(data):
						line = ''
						for j, value in enumerate(row):
							if type(data[i][j]) is datetime.datetime:
								# line += '{0}\t'.format(data[i][j])
								line += '{0},'.format(data[i][j])
							elif not np.isnan(data[i][j]):
								line += '{0},'.format(data[i][j])
							else:
								line += '{0},'.format('')
						line += '\n'
						file.write(line)
					file.close()
					msg = 'Successfully exported data.'
					if self.iface is not None:
						QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', msg)
					else:
						print(msg)
					retry = False
				except (IOError, PermissionError):
					msg = 'Could not access {0}. Check file is not open.'.format(saveFile)
					if self.iface is not None:
						questionRetry = QMessageBox.question(self.iface.mainWindow(),
							                                 "COASTALME Viewer", msg,
							                                 QT_MESSAGE_BOX_RETRY | QT_MESSAGE_BOX_CANCEL)
						if questionRetry == QT_MESSAGE_BOX_CANCEL:
							retry = False
							return False
					else:
						print(msg)
						retry = input('Retry? (Y/N)\n')
						if retry.lower() == 'n':
							retry = False
						else:
							retry = True
						
				except Exception as e:
					msg = 'Unexpected error exporting file\n\n{0}'.format(e)
					if self.iface is not None:
						QMessageBox.critical(self.iface.mainWindow(), 'COASTALME Viewer', msg)
					else:
						print(msg)
					retry = False
					return False
		
		return True
	
	def exportDataToClipboard(self, **kwargs):
		"""
		Export plot data to clipboard
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		plotNo = self.cmeView.tabWidget.currentIndex()
		
		dataHeader, data = self.getPlotData(plotNo, **kwargs)
		
		if dataHeader is None or data is None:
			# QMessageBox.critical(self.iface.mainWindow(), 'COASTALME Viewer', 'Error exporting data')
			if self.iface is not None:
				QMessageBox.warning(self.iface.mainWindow(), 'COASTALME Viewer', 'No data on plot or an error occured - note curtain plots aren\'t able to be exported or copied yet')
			else:
				print('No data on plot or an error occured - note curtain plots aren\'t able to be exported or copied yet')
			return False
		
		copyData = '{0}\n'.format(dataHeader.replace(',', '\t'))
		for i, row in enumerate(data):
			line = ''
			for j, value in enumerate(row):
				if type(data[i][j]) is datetime.datetime:
					line += '{0}\t'.format(data[i][j])
				elif not np.isnan(data[i][j]):
					line += '{0}\t'.format(data[i][j])
				else:
					line += '{0}\t'.format('')
			line += '\n'
			copyData += line
		
		clipboard = QApplication.clipboard()
		clipboard.setText(copyData)
		
		return True
	
	def exportImageToClipboard(self):
		"""
		Export plot image to clipboard
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		plotNo = self.cmeView.tabWidget.currentIndex()
		
		parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, \
		yAxisLabel, xAxisLabel, xAxisLimits, yAxisLimits = self.cmeView.cmePlot.plotEnumerator(plotNo)
		
		# thanks to EelkeSpaak for saving figure to clipboard
		# https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
		buf = io.BytesIO()
		figure.savefig(buf)
		
		clipboard = QApplication.clipboard()
		clipboard.setImage(QImage.fromData(buf.getvalue()))
		buf.close()
		
		return True
		
	def getPlotData(self, plotNo, **kwargs):
		"""
		Collects all the plot data into one numpy array.
		
		:return: str Headers, numpy array data
		"""

		parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, yAxisLabels, xAxisLabels, xAxisLimits, yAxisLimits = \
			self.cmeView.cmePlot.plotEnumerator(plotNo)
		
		# get lines and labels for both axis 1 and axis 2
		lines, labels = subplot.get_legend_handles_labels()
		lines2, labels2 = [], []
		if isSecondaryAxis[0]:
			subplot2 = self.cmeView.cmePlot.getSecondaryAxis(plotNo)
			lines2, labels2 = subplot2.get_legend_handles_labels()
		
		# get maximum data length so we can adjust all lengths to be the same (easier to export that way)
		maxLen = 0
		for line in lines:
			if isinstance(line, Polygon):
				maxLen = max(maxLen, len(line.get_xy()))
			elif type(line) is Quiver:
				continue
			elif type(line) is PolyCollection:
				continue
			else:
				maxLen = max(maxLen, len(line.get_data()[0]))
		for line in lines2:
			if isinstance(line, Polygon):
				maxLen = max(maxLen, len(line.get_xy()))
			else:
				maxLen = max(maxLen, len(line.get_data()[0]))
			
		# put all data into one big numpy array and adjust data accordingly to max length - axis 1
		data = None
		for i, line in enumerate(lines):
			if i == 0:
				data = np.zeros((maxLen, 1))  # set up data array.. start with zeros and delete first column once populated
			if isinstance(line, Polygon):
				xy = line.get_xy()
				x = xy[:,0]
				y = xy[:,1]
			elif type(line) is Quiver:
				continue
			elif type(line) is PolyCollection:
				continue
			else:
				x, y = line.get_data()
			if type(x) is list:  # if not a numpy array, convert it to one
				x = np.array(x)
			if type(y) is list:  # if not a numpy array, convert it to one
				y = np.array(y)
			dataX = np.reshape(x, (len(x), 1))  # change the shape so it has 2 axis
			dataY = np.reshape(y, (len(y), 1))  # change the shape so it has 2 axis
			if len(dataX) < maxLen:
				diff = maxLen - len(dataX)
				fill = np.zeros([diff, 1]) * np.nan
				dataX = np.append(dataX, fill, axis=0)
			if len(dataY) < maxLen:
				diff = maxLen - len(dataY)
				fill = np.zeros([diff, 1]) * np.nan
				dataY = np.append(dataY, fill, axis=0)
			data = np.append(data, dataX, axis=1)
			data = np.append(data, dataY, axis=1)
			if i == 0:
				data = np.delete(data, 0, 1)  # delete initialised row of zeros
				
		# put all data into one big numpy array and adjust data accordingly to max length - axis 2
		needToDeleteFirstColumn = False
		for i, line in enumerate(lines2):
			if i == 0:
				if data is None:
					data = np.zeros((maxLen, 1))  # set up data array
					needToDeleteFirstColumn = True
			if isinstance(line, Polygon):
				xy = line.get_xy()
				x = xy[:,0]
				y = xy[:,1]
			elif type(line) is Quiver:
				continue
			elif type(line) is PolyCollection:
				continue
			else:
				x, y = line.get_data()
			if type(x) is list:  # if not a numpy array, convert it to one
				x = np.array(x)
			if type(y) is list:  # if not a numpy array, convert it to one
				y = np.array(y)
			dataX = np.reshape(x, (len(x), 1))  # change the shape so it has 2 axis
			dataY = np.reshape(y, (len(y), 1))  # change the shape so it has 2 axis
			if len(dataX) < maxLen:
				diff = maxLen - len(dataX)
				fill = np.zeros([diff, 1]) * np.nan
				dataX = np.append(dataX, fill, axis=0)
			if len(dataY) < maxLen:
				diff = maxLen - len(dataY)
				fill = np.zeros([diff, 1]) * np.nan
				dataY = np.append(dataY, fill, axis=0)
			data = np.append(data, dataX, axis=1)
			data = np.append(data, dataY, axis=1)
			if i == 0:
				if needToDeleteFirstColumn:
					data = np.delete(data, 0, 1)  # delete initialised row of zeros

		if plotNo == 0:
			dataHeader = self.getTimeSeriesPlotHeaders(labels, labels2, **kwargs)
		elif plotNo == 1:
			dataHeader = self.getLongPlotHeaders(labels, labels2, **kwargs)
		else:
			dataHeader = ''

		if dataHeader == '' or data is None:
			return dataHeader, [[]]

		# delete duplicate Time arrays
		timeColumns = []
		if data is not None:
			for i in range(1, data.shape[1]):
				if i % 2 == 0:
					if data[:, i - 2].dtype == object and data[:, i].dtype == object:  # probably datetime objects
						# if not np.any((data[:, i - 2].astype(np.datetime64) == data[:, i].astype(np.datetime64)) == False):  # allclose doesn't seem to work with datetime
						a1 = np.array([x for x in data[:, i - 2].tolist() if isinstance(x, datetime.datetime)])
						a2 = np.array([x for x in data[:, i].tolist() if isinstance(x, datetime.datetime)])
						if a1.shape == a2.shape and np.all((a1 == a2) == True):
							timeColumns.append(i)
					else:
						if np.allclose(data[:, i - 2], data[:, i], equal_nan=True):		# avoid nan == nan not being True
							timeColumns.append(i)
			data = np.delete(data, timeColumns, axis=1)
		# keep data headers only for remaining arrays
		dataHeader = dataHeader.split(',')
		remainingHeader = []
		for i in range(len(dataHeader)):
			if i not in timeColumns:
				remainingHeader.append(dataHeader[i])
		dataHeader = ','.join(remainingHeader)
		if data is None:
			data = [[]]

		return dataHeader, data

	def getTimeSeriesPlotHeaders(self, labels, labels2, **kwargs):
		"""
		Recmerns column headings in comma delimiter format for time series export to csv.
		
		:param labels: list -> str label axis 1
		:param labels2: list -> str label axis 2
		:return: str column headers
		"""
		
		# get labels into one big comma delimiter string
		dataHeader = None
		for i, label in enumerate(labels):
			# labelUnit = getUnit(label, self.cmeView.canvas)
			labelUnit = self.cmeView.cmePlot.setAxisNames(0, label, return_unit_only=True, **kwargs)
			if i == 0:
				dataHeader = 'Time (hr)'
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
			else:
				dataHeader = '{0},Time (hr)'.format(dataHeader)
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
		for i, label in enumerate(labels2):
			# labelUnit = getUnit(label, self.cmeView.canvas)
			labelUnit = self.cmeView.cmePlot.setAxisNames(0, label, return_unit_only=True, **kwargs)
			if i == 0:
				if not labels:
					dataHeader = 'Time (hr)'
					dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
				else:
					dataHeader = '{0},Time (hr)'.format(dataHeader)
					dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
			else:
				dataHeader = '{0},Time (hr)'.format(dataHeader)
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
				
		return dataHeader
	
	def getLongPlotHeaders(self, labels, labels2, **kwargs):
		"""
		Recmern column headings in comma delimiter format for long plot export to csv.
		
		:param labels: list -> str label axis 1
		:param labels2: list -> str label axis 2
		:return: str column headers
		"""
		
		# get labels into one big comma delimiter string
		dataHeader = None
		xAxisUnit = getUnit(None, self.cmeView.canvas, return_map_units=True)
		for i, label in enumerate(labels):
			# labelUnit = getUnit(label, self.cmeView.canvas)
			labelUnit = self.cmeView.cmePlot.setAxisNames(1, label, return_unit_only=True, **kwargs)
			if i == 0:
				dataHeader = 'Offset ({0})'.format(xAxisUnit)
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
			else:
				dataHeader = '{0},Offset ({1})'.format(dataHeader, xAxisUnit)
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
		for i, label in enumerate(labels2):
			# labelUnit = getUnit(label, self.cmeView.canvas)
			labelUnit = self.cmeView.cmePlot.setAxisNames(1, label, return_unit_only=True, **kwargs)
			if i == 0:
				if not labels:
					dataHeader = 'Offset ({0})'.format(xAxisUnit)
					dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
				else:
					dataHeader = '{0},Offset ({1})'.format(dataHeader, xAxisUnit)
					dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
			else:
				dataHeader = '{0},Offset ({1})'.format(dataHeader, xAxisUnit)
				dataHeader = '{0},{1} ({2})'.format(dataHeader, label, labelUnit) if labelUnit else '{0},{1}'.format(dataHeader, label)
		
		return dataHeader
	
	def freezeAxisLimits(self, enum):
		"""
		Toggles Freeze Axis Y and X limits for both the menu bar and context menu.
		
		:param enum: int -> 0: menu bar
							1: context menu
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		if enum == 0:
			if self.cmeView.cmeMenuBar.freezeAxisLimits_action.isChecked():
				# menu bar
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(True)
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(True)
				# context menu
				self.cmeView.cmeContextMenu.freezeAxisLimits_action.setChecked(True)
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(True)
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(True)
			else:
				# menu bar
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(False)
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(False)
				# context menu
				self.cmeView.cmeContextMenu.freezeAxisLimits_action.setChecked(False)
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(False)
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(False)
		elif enum == 1:
			if self.cmeView.cmeContextMenu.freezeAxisLimits_action.isChecked():
				# menu bar
				self.cmeView.cmeMenuBar.freezeAxisLimits_action.setChecked(True)
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(True)
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(True)
				# context menu
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(True)
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(True)
			else:
				# menu bar
				self.cmeView.cmeMenuBar.freezeAxisLimits_action.setChecked(False)
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(False)
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(False)
				# context menu
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(False)
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(False)
		else:
			return False
			
		return True
	
	def freezeAxisXLimits(self, enum):
		"""
		Toggles Freeze X axis limits for menu bar and context menu.
		
		:param enum: int -> 0: menu bar
							1: context menu
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		if enum == 0:
			if self.cmeView.cmeMenuBar.freezeAxisXLimits_action.isChecked():
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(True)
				self.cmeView.cmePlot.cmePlotToolbar.freezeXAxisButton.setChecked(True)
			else:
				self.cmeView.cmeContextMenu.freezeAxisXLimits_action.setChecked(False)
				self.cmeView.cmePlot.cmePlotToolbar.freezeXAxisButton.setChecked(False)
		elif enum == 1:
			if self.cmeView.cmeContextMenu.freezeAxisXLimits_action.isChecked():
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(True)
			else:
				self.cmeView.cmeMenuBar.freezeAxisXLimits_action.setChecked(False)
		else:
			return False
		
		return True
	
	def freezeAxisYLimits(self, enum):
		"""
		Toggles Freeze Y axis limits for menu bar and context menu.

		:param enum: int -> 0: menu bar
							1: context menu
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		if enum == 0:
			if self.cmeView.cmeMenuBar.freezeAxisYLimits_action.isChecked():
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(True)
			else:
				self.cmeView.cmeContextMenu.freezeAxisYLimits_action.setChecked(False)
		elif enum == 1:
			if self.cmeView.cmeContextMenu.freezeAxisYLimits_action.isChecked():
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(True)
			else:
				self.cmeView.cmeMenuBar.freezeAxisYLimits_action.setChecked(False)
		else:
			return False
		
		return True
	
	def freezeAxisLabels(self, enum):
		"""
		Toggles Freeze Axis Labels for menu bar and context menu
		
		:param enum: int -> 0: menu bar
							1: context menu
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		if enum == 0:
			if self.cmeView.cmeMenuBar.freezeAxisLabels_action.isChecked():
				self.cmeView.cmeContextMenu.freezeAxisLabels_action.setChecked(True)
			else:
				self.cmeView.cmeContextMenu.freezeAxisLabels_action.setChecked(False)
		elif enum == 1:
			if self.cmeView.cmeContextMenu.freezeAxisLabels_action.isChecked():
				self.cmeView.cmeMenuBar.freezeAxisLabels_action.setChecked(True)
			else:
				self.cmeView.cmeMenuBar.freezeAxisLabels_action.setChecked(False)
		else:
			return False
		
		return True
	
	def freezeLegendLabels(self, enum):
		"""
		Toggles Freeze Legend Labels for menu bar and context menu.
		
		:param enum: int -> 0: menu bar
							1: context menu
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		if enum == 0:
			if self.cmeView.cmeMenuBar.freezeLegendLabels_action.isChecked():
				self.cmeView.cmeContextMenu.freezeLegendLabels_action.setChecked(True)
			else:
				self.cmeView.cmeContextMenu.freezeLegendLabels_action.setChecked(False)
		elif enum == 1:
			if self.cmeView.cmeContextMenu.freezeLegendLabels_action.isChecked():
				self.cmeView.cmeMenuBar.freezeLegendLabels_action.setChecked(True)
			else:
				self.cmeView.cmeMenuBar.freezeLegendLabels_action.setChecked(False)
		else:
			return False
		
		self.cmeView.cmePlot.setNewPlotProperties(enum)
		
		return True
		
	def exportTempLines(self):
		"""
		Export rubberband lines as shape file
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		# User defined save path
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/export_shp")
		saveFile = QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Save Shape File', fpath)[0]
		if len(saveFile) < 2:
			return
		else:
			if saveFile != os.sep and saveFile.lower() != 'c:\\' and saveFile != '':
				QSettings().setValue("COASTALME_Results/export_shp", saveFile)
			if not os.path.splitext(saveFile)[-1] or os.path.splitext(saveFile)[-1].lower() != '.shp':
				saveFile = '{0}.shp'.format(saveFile)

		# create shape file
		crs = self.cmeView.project.crs()
		crsId = crs.authid()
		uri = 'linestring?crs={0}'.format(crsId)
		shpLayer = QgsVectorLayer(uri, os.path.splitext(os.path.basename(saveFile))[0], 'memory')
		dp = shpLayer.dataProvider()
		dp.addAttributes([
			QgsField('Type', QVariant.String, len=20),
			QgsField('Label', QVariant.String, len=30),
			QgsField('Comment', QVariant.String, len=250),
		])
		shpLayer.updateFields()
		feats = []  # list of QgsFeature objects
		#for i, rubberBand in enumerate(self.cmeView.cmePlot.cmeCrossSection.rubberBands):
		i = 0
		for line, type_ in self.cmeView.cmePlot.lines.items():
			for rubberBand in line.rubberBands:
				i += 1
				geom = rubberBand.asGeometry().asPolyline()
				feat = QgsFeature()
				try:
					feat.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x) for x in geom]))
				except:
					feat.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x.x(), x.y()) for x in geom]))
				feat.setAttributes([
					"",
					'Line {0}'.format(i),
					"source: COASTALME Viewer - {0}".format(type_)
				])
				feats.append(feat)
		# for i, line in enumerate(self.cmeView.cmePlot.cmeFlowLine.rubberBands):
		# 	geom = line.asGeometry().asPolyline()
		# 	feat = QgsFeature()
		# 	try:
		# 		feat.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x) for x in geom]))
		# 	except:
		# 		feat.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x.x(), x.y()) for x in geom]))
		# 	feat.setAttributes(['Flow Location {0}'.format(i + 1)])
		# 	feats.append(feat)
		error = dp.addFeatures(feats)
		shpLayer.updateExtents()
		QgsVectorFileWriter.writeAsVectorFormat(shpLayer, saveFile, 'CP1250', crs, 'ESRI Shapefile')
		
		# ask user if import or not
		importLayer = QMessageBox.question(self.iface.mainWindow(),
		                                   "COASTALME Viewer", 'Successfully saved {0}. Open in workspace?'.format(os.path.basename(saveFile)),
		                                   QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL)
		if importLayer == QT_MESSAGE_BOX_YES:
			self.iface.addVectorLayer(saveFile, os.path.splitext(os.path.basename(saveFile))[0], 'ogr')
			
		return True
	
	def exportTempPoints(self):
		"""
		Export marker points as shape file
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		# User defined save path
		fpath = loadLastFolder(self.cmeView.currentLayer, "COASTALME_Results/export_shp")
		saveFile = QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Save Shape File', fpath)[0]
		if len(saveFile) < 2:
			return
		else:
			if saveFile != os.sep and saveFile.lower() != 'c:\\' and saveFile != '':
				QSettings().setValue("COASTALME_Results/export_shp", saveFile)
			if not os.path.splitext(saveFile)[-1] or os.path.splitext(saveFile)[-1].lower() != '.shp':
				saveFile = '{0}.shp'.format(saveFile)
		
		# create shape file
		crs = self.cmeView.project.crs()
		crsId = crs.authid()
		uri = 'point?crs={0}'.format(crsId)
		shpLayer = QgsVectorLayer(uri, os.path.splitext(os.path.basename(saveFile))[0], 'memory')
		dp = shpLayer.dataProvider()
		dp.addAttributes([
			QgsField('Type', QVariant.String, len=20),
			QgsField('Label', QVariant.String, len=30),
			QgsField('Comment', QVariant.String, len=250)
		])
		shpLayer.updateFields()
		feats = []  # list of QgsFeature objects
		#for i, point in enumerate(self.cmeView.cmePlot.cmeTSPoint.points):
		i = 0
		for marker, type_ in self.cmeView.cmePlot.markers.items():
			for point in marker.points:
				i += 1
				feat = QgsFeature()
				feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))
				feat.setAttributes([
					"",
					'Point {0}'.format(i),
					"source: COASTALME Viewer - {0}".format(type_)
				])
				feats.append(feat)
		error = dp.addFeatures(feats)
		shpLayer.updateExtents()
		QgsVectorFileWriter.writeAsVectorFormat(shpLayer, saveFile, 'CP1250', crs, 'ESRI Shapefile')
		
		# ask user if import or not
		importLayer = QMessageBox.question(self.iface.mainWindow(),
		                                   "COASTALME Viewer", 'Successfully saved {0}. Open in workspace?'.format(
				os.path.basename(saveFile)),
		                                   QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL)
		if importLayer == QT_MESSAGE_BOX_YES:
			self.iface.addVectorLayer(saveFile, os.path.splitext(os.path.basename(saveFile))[0], 'ogr')
		
		return True
	
	def updateLegend(self):
		"""
		Updates the legend on the figure.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		ax, plotWidget, _, artists, labels = self.cmeView.cmePlot.plotEnumerator(self.cmeView.tabWidget.currentIndex())[2:7]
		labels_about_to_break_ = self.cmeView.cmePlot.labels_about_to_break(self.cmeView.tabWidget.currentIndex())
		if labels_about_to_break_ == -1:
			pass
		elif labels_about_to_break_ == 1:
			labels_about_to_break_ = 2
		elif mpl_version_int() >= 35000 and labels_already_broken(labels[0]):
			labels_about_to_break_ = 2
		elif labels_about_to_break_ == 0 and mpl_version_int() >= 35000 and labels_about_to_break(ax, labels[0]):
			labels_about_to_break_ = 1

		self.cmeView.cmePlot.set_labels_about_to_break(self.cmeView.tabWidget.currentIndex(), labels_about_to_break_)

		if labels_about_to_break_ < 2:
			self.cmeView.cmePlot.updateLegend(self.cmeView.tabWidget.currentIndex())
			self.cmeView.cmePlot.setNewPlotProperties(self.cmeView.tabWidget.currentIndex())
		else:
			labels_, artistTemplates = self.cmeView.cmePlot.getNewPlotProperties(self.cmeView.tabWidget.currentIndex(), labels[0], artists[0], rtype='lines')
			for i, a in enumerate(artists[0]):
				a.set_label(labels_[i])
				applyMatplotLibArtist(a, artistTemplates[i])
			self.cmeView.cmePlot.updateLegend(self.cmeView.tabWidget.currentIndex())
			QMessageBox.warning(self.cmeView, "Plotting", "Unable to update plot styles. "
														 "This has been purposefully prevented due to a known bug in "
														 "Matplotlib v3.5.1 mixing up the plot datasets. Please "
														 "visit the below COASTALME Wiki page for more information.<p>"
														 "<a href=\"https://wiki.coastalme.com/index.php?title=COASTALME_Viewer_Matplotlib_v3.5.1_Bug\">wiki.coastalme.com/index.php?title=COASTALME_Viewer_Matplotlib_v3.5.1_Bug</a>")
			# QMessageBox.warning(self.cmeView, "FFmpeg missing",
			# 					"The tool for video creation (<a href=\"https://wiki.coastalme.com/index.php?title=COASTALME_Viewer_Matplotlib_v3.5.1_Bug\">test</a>) "
			# 					"is missing. Please check your FFmpeg configuration in <i>Video</i> tab.<p>"
			# 					"<b>Windows users:</b> Let the COASTALME plugin download FFmpeg automatically (by clicking OK).<p>"
			# 					"<b>Linux users:</b> Make sure FFmpeg is installed in your system - usually a package named "
			# 					"<tt>ffmpeg</tt>. On Debian/Ubuncme systems FFmpeg was replaced by Libav (fork of FFmpeg) "
			# 					"- use <tt>libav-tools</tt> package.<p>"
			# 					"<b>MacOS users:</b> Make sure FFmpeg is installed in your system <tt>brew install ffmpeg</tt>")

		plotWidget.draw()

		# if self.cmeView.tabWidget.currentIndex() == CmePlot.CrossSection:
		# 	subplot = self.cmeView.cmePlot.plotEnumerator(CmePlot.CrossSection)[2]
		# 	subplot2 = self.cmeView.cmePlot.getSecondaryAxis(CmePlot.CrossSection, create=False)
		# 	self.cmeView.cmePlot.cursorMarker.rename(subplot, subplot2)
		
		return True
	
	def showMeanEvent(self):
		"""
		Shows the mean event from all displayed lines. The mean event is either chosen from the closest or next above.

		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.cmeView.cmePlot.showStatResult(self.cmeView.tabWidget.currentIndex(), 'Mean')
		
		return True
	
	def showMedianEvent(self):
		"""
		Shows the median event from all displayed lines. If even number, will show the n + 1 event

		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.cmeView.cmePlot.showStatResult(self.cmeView.tabWidget.currentIndex(), 'Median')
		
		return True
	
	def showSelectedElements(self):
		"""
		Displays a dialog of all the selected elements in the results.
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		elements = self.cmeView.cmeResults.cmeResults1D.ids
		
		self.selectedElementsDialog = CmeSelectedElementsDialog(self.iface, elements)
		self.selectedElementsDialog.show()
		
		return True
	
	def toggleResultTypeToMax(self):
		"""
		Toggles the result type to max or temporal through context menu.

		:return: bool -> True for successful, False for unsuccessful
		"""

		self.cmeView.cmeContextMenu.resultTypeContextItem.toggleMaxActive()
		if self.cmeView.cmeContextMenu.resultTypeContextItem.isMin:
			self.cmeView.cmeContextMenu.resultTypeContextItem.toggleMinActive()

		self.cmeView.maxResultTypesChanged(None)

		return True

	def toggleResultTypeToMin(self):
		"""
		Toggles the result type to min or temporal through context menu.

		:return: bool -> True for successful, False for unsuccessful
		"""

		self.cmeView.cmeContextMenu.resultTypeContextItem.toggleMinActive()
		if self.cmeView.cmeContextMenu.resultTypeContextItem.isMax:
			self.cmeView.cmeContextMenu.resultTypeContextItem.toggleMaxActive()

		self.cmeView.minResultTypesChanged(None)

		return True
	
	def toggleResultTypeToSecondaryAxis(self):
		"""
		Toggles the result type to primary or secondary axis through context menu.
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.cmeView.cmeContextMenu.resultTypeContextItem.toggleSecondaryActive()
		
		self.cmeView.secondaryAxisResultTypesChanged(None)
		
		return True
		
	def saveDefaultStyleScalar(self, renderType, **kwargs):
		"""
		Saves the current active result type style as default for fucmere similar result types.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		useClicked = kwargs['use_clicked'] if 'use_clicked' in kwargs.keys() else False
		saveType = kwargs['save_type'] if 'save_type' in kwargs else 'xml'
		meshIndex = kwargs['mesh_index'] if 'mesh_index' in kwargs else None
		result = kwargs['result'] if 'result' in kwargs else None

		saved_style_folder = os.path.join(os.path.dirname(__file__), '_saved_styles')
		if not os.path.exists(saved_style_folder):
			os.mkdir(saved_style_folder)
		
		# what happens if there are no mesh layer or more than one active mesh layer
		if meshIndex is not None and result is not None:
			meshLayer = coastalmeqgis_find_layer(result)
		elif not self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
				QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Result Datasets')
				return False
		# elif len(self.cmeView.cmeResults.cmeResults2D.activeMeshLayers) > 1:
		# 	self.meshDialog = coastalmeqgis_meshSelection_dialog(self.iface, self.cmeView.cmeResults.cmeResults2D.activeMeshLayers)
		# 	self.meshDialog.exec()
		# 	if self.meshDialog.selectedMesh is None:
		# 		return False
		# 	else:
		# 		meshLayer = coastalmeqgis_find_layer(self.meshDialog.selectedMesh)
		else:
			meshLayer = self.cmeView.cmeResults.cmeResults2D.activeMeshLayers[0]

		# get data provider and renderer settings
		dp = meshLayer.dataProvider()
		rs = meshLayer.rendererSettings()
		
		# get scalar renderer settings
		activeScalarGroupIndex = None
		if useClicked:
			resultType = self.cmeView.cmeContextMenu.resultTypeContextItem.ds_name
			if self.cmeView.cmeContextMenu.resultTypeContextItem.isMax:
				resultType = '{0}/Maximums'.format(resultType)
			elif self.cmeView.cmeContextMenu.resultTypeContextItem.isMin:
				resultType = '{0}/Minimums'.format(resultType)
			if meshLayer.name() in self.cmeView.cmeResults.results and resultType in self.cmeView.cmeResults.results[
				meshLayer.name()]:
				for _, (_, _, dsi) in self.cmeView.cmeResults.results[meshLayer.name()][resultType]['times'].items():
					activeScalarGroupIndex = dsi.group()
					break
			# for i in range(dp.datasetGroupCount()):
			# 	# is the datasetGroup a maximum?
			# 	isDatasetMax = CmeResults.isMaximumResultType(dp.datasetGroupMetadata(i).name(),
			# 	                                             dp=dp, groupIndex=i)
			# 	if self.cmeView.cmeContextMenu.resultTypeContextItem.isMax and isDatasetMax:
			# 		if CmeResults.stripMaximumName(dp.datasetGroupMetadata(i).name()) == resultType:
			# 			activeScalarGroupIndex = i
			# 			break
			# 	else:
			# 		if dp.datasetGroupMetadata(i).name() == resultType and not isDatasetMax:
			# 			activeScalarGroupIndex = i
			# 			break
		elif meshIndex is not None:
			activeScalarGroupIndex = meshIndex.group()
		else:
			activeScalar = rs.activeScalarDataset()
			activeScalarGroupIndex = activeScalar.group()
			if activeScalarGroupIndex == -1:
				QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Scalar Dataset')
				return False

		if activeScalarGroupIndex is None:
			QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'Unexpected error saving default scalar styling')
			return False
		activeScalarType = dp.datasetGroupMetadata(activeScalarGroupIndex).name()
		activeScalarType = CmeResults.stripMaximumName(activeScalarType)
		rsScalar = rs.scalarSettings(activeScalarGroupIndex)
		
		# save color ramp if option chosen
		if renderType == 'color ramp':
			## get color ramp properties
			shader = rsScalar.colorRampShader()
			file = os.path.join(os.path.dirname(__file__), '_saved_styles', '{0}.xml'.format(activeScalarType))
			doc = QDomDocument(activeScalarType.replace(' ', '_').replace('(', '').replace(')', ''))
			element = shader.writeXml(doc)
			doc.appendChild(element)
			fo = open(file, 'w')
			fo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
			fo.write(doc.toString())
			fo.close()
			
			# save as default for that result type
			key = "COASTALME_scalarRenderer/{0}_ramp".format(activeScalarType)
			settings = QSettings()
			settings.setValue(key, file)
			
			# remove color map key
			key = "COASTALME_scalarRenderer/{0}_map".format(activeScalarType)
			settings = QSettings()
			settings.remove(key)
		
		# save color map if option chosen
		elif renderType == 'color map':
			file = os.path.join(os.path.dirname(__file__), '_saved_styles', '{0}.xml'.format(activeScalarType))
			doc = QDomDocument(activeScalarType.replace(' ', '_'))
			element = rsScalar.writeXml(doc)
			doc.appendChild(element)
			if saveType == 'xml':
				fo = open(file, 'w')
				fo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
				fo.write(doc.toString())
				fo.close()
				
				# save setting so cmeview knows to load it in
				key = "COASTALME_scalarRenderer/{0}_map".format(activeScalarType)
				settings = QSettings()
				settings.setValue(key, file)
				
				# remove color ramp key
				key = "COASTALME_scalarRenderer/{0}_ramp".format(activeScalarType)
				settings = QSettings()
				settings.remove(key)
			else:  # save to project
				style = '<?xml version="1.0" encoding="UTF-8"?>\n' + doc.toString()
				return style
		
		QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'Saved default style for {0}'.format(activeScalarType))
		
		return True
			
	def saveDefaultStyleVector(self, **kwargs):
		"""
		Save the current active vector renderer settings as default for fucmere vector types.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		useClicked = kwargs['use_clicked'] if 'use_clicked' in kwargs.keys() else False
		saveType = kwargs['save_type'] if 'save_type' in kwargs else 'default'
		meshIndex = kwargs['mesh_index'] if 'mesh_index' in kwargs else None

		meshLayer = self.activeMeshLayer(window_title='Select Result to Save Default Style From')
		if meshLayer is None:
			return

		# get active vector layer
		if useClicked:
			if self.clickedResultDataType() != 2:  # not a scalar or vector result type
				return
			index = self.clickedGroupIndex(meshLayer)
		elif meshIndex is not None:
			index = meshIndex.group()
		else:
			index = meshLayer.rendererSettings().activeVectorDatasetGroup()

		if index in [None, -1]:
			if saveType == 'default':
				QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Vector Dataset')
				return False
			else:
				return ''

		rsVector = meshLayer.rendererSettings().vectorSettings(index)
		doc = QDomDocument('coastalme_meshlayer')
		doc.appendChild(rsVector.writeXml(doc))

		if saveType == 'default':
			# save as default for that result type
			key = "COASTALME_vectorRenderer/vector"
			settings = QSettings()
			settings.setValue(key, doc.toString())
		else:  # save to project
			return doc.toString()

		QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'Saved default style for vectors')

		return True

	def loadDefaultStyleScalar(self, **kwargs):
		"""
		Loads the default scalar style for result type.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		useClicked = kwargs['use_clicked'] if 'use_clicked' in kwargs.keys() else False
		
		# what happens if there are no active mesh layers
		if not self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
			QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Result Datasets')
			return False
		
		for layer in self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
			# get renderers and data provider
			dp = layer.dataProvider()
			rs = layer.rendererSettings()
			
			# get active dataset and check if it is scalar
			if useClicked:
				resultType = self.cmeView.cmeContextMenu.resultTypeContextItem.ds_name
				# for i in range(dp.datasetGroupCount()):
				if layer.name() in self.cmeView.cmeResults.results:
					for rtype in self.cmeView.cmeResults.results[layer.name()]:
						if CmeResults.isMapOutputType(rtype):
							# is the datasetGroup a maximum?
							isDatasetMax = CmeResults.isMaximumResultType(rtype)
							isDatasetMin = CmeResults.isMinimumResultType(rtype)
							if self.cmeView.cmeContextMenu.resultTypeContextItem.isMax and isDatasetMax:
								if CmeResults.stripMaximumName(rtype) == resultType:
									mdis = [y[2] for x, y in self.cmeView.cmeResults.results[layer.name()][rtype]['times'].items()]
									if mdis:
										activeScalarGroupIndex = mdis[0].group()
									break
							elif self.cmeView.cmeContextMenu.resultTypeContextItem.isMin and isDatasetMin:
								if CmeResults.stripMaximumName(rtype) == resultType:
									mdis = [y[2] for x, y in self.cmeView.cmeResults.results[layer.name()][rtype]['times'].items()]
									if mdis:
										activeScalarGroupIndex = mdis[0].group()
									break
							else:
								if rtype == resultType:
									mdis = [y[2] for x, y in self.cmeView.cmeResults.results[layer.name()][rtype]['times'].items()]
									if mdis:
										activeScalarGroupIndex = mdis[0].group()
									break
						
			else:
				activeScalar = rs.activeScalarDataset()
				activeScalarGroupIndex = activeScalar.group()
				if not activeScalar.isValid():
					QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Scalar Dataset')
					return False

			# get the name and try and apply default styling
			mdGroup = dp.datasetGroupMetadata(activeScalarGroupIndex)
			# if mdGroup.isScalar():  # should be scalar considering we used activeScalarDataset
			resultType = CmeResults.stripMaximumName(mdGroup.name())
			# try finding if style has been saved as a ramp first
			key = 'COASTALME_scalarRenderer/{0}_ramp'.format(resultType)
			file = QSettings().value(key)
			if file:
				self.cmeView.cmeResults.cmeResults2D.applyScalarRenderSettings(layer, activeScalarGroupIndex, file, type='ramp')
			# else try map
			key = 'COASTALME_scalarRenderer/{0}_map'.format(resultType)
			file = QSettings().value(key)
			if file:
				self.cmeView.cmeResults.cmeResults2D.applyScalarRenderSettings(layer, activeScalarGroupIndex, file, type='map')
					
		return True
	
	def loadDefaultStyleVector(self, **kwargs):
		"""
		Loads the default vector style for result type.
		
		:return: bool -> True for successful, False for unsuccessful
		"""

		if Qgis.QGIS_VERSION_INT < 31600:
			return

		useClicked = kwargs['use_clicked'] if 'use_clicked' in kwargs.keys() else False
		
		# what happens if there are no active mesh layers
		if not self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
			QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Result Datasets')
			return False

		value = QSettings().value('COASTALME_vectorRenderer/vector', None)
		if not value or len(value) < 27 or value[:27] != '<!DOCTYPE coastalme_meshlayer>':
			return
		doc = QDomDocument('coastalme_meshlayer')
		stacmesOK, errorStr, errorLine, errorColumn = doc.setContent(value, True)
		if not stacmesOK:
			QMessageBox.critical(self.cmeView, 'Paste Style', 'Error loading style: {0}'.format(errorStr))
			return
		
		for layer in self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
			# get renderers and data provider
			dp = layer.dataProvider()
			rs = layer.rendererSettings()
			
			# get active dataset and check if it is vector
			if useClicked:
				index = self.clickedGroupIndex(layer)
			else:
				index = rs.activeVectorDatasetGroup()
				if index in [None, -1]:
					QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'No Active Vector Dataset')
					return False

			rsVector = rs.vectorSettings(index)
			rsVector.readXml(doc.documentElement())
			rs.setVectorSettings(index, rsVector)
			layer.setRendererSettings(rs)
					
		return True
	
	def resetDefaultStyles(self):
		"""
		Resets all the default styles back to original i.e. none
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		settings = QSettings()
		for key in settings.allKeys():
			if 'COASTALME_scalarRenderer' in key:
				settings.remove(key)
			elif 'COASTALME_vectorRenderer' in key:
				settings.remove(key)
		
		QMessageBox.information(self.iface.mainWindow(), 'COASTALME Viewer', 'Reset Default Styles')
				
		return True

	def batchPlotExportInitialise(self, **kwargs):
		"""
		Initiates the dialog - automatically loops through all feacmeres in shape file (or selection of feacmeres in
		shape file) and exports set results to CSV or Image.
		
		:return: bool -> True for successful, False for unsuccessful
		"""
		
		self.batchPlotExportDialog = CmeBatchPlotExportDialog(self.cmeView, **kwargs)
		headless = kwargs['headless'] if 'headless' in kwargs else False
		if not headless:
			self.batchPlotExportDialog.exec()
		
	def batchPlotExport(self, gisLayer, resultMesh, resultTypes, timestep, feacmeres, format, outputFolder, nameField, imageFormat, **kwargs):
		"""
		Automatically loops through all feacmeres in shape file (or selection of feacmeres in
		shape file) and exports set results to CSV or Image.
		
		:param gisLayer: str layer name
		:param resultMesh: list -> str mesh name e.g. 'M01_5m_001'
		:param resultTypes: list -> str result type e.g. 'depth'
		:param timestep: str time step e.g. '01:00:00'
		:param feacmeres: str 'all' or 'selection'
		:param format: str 'csv' or 'image'
		:param outputFolder: str output folder
		:param nameField: str attribute field used for naming files
		:param imageFormat: str extension e.g. '.png'
		:return: bool -> True for successful, False for unsuccessful
		"""

		qv = Qgis.QGIS_VERSION_INT

		# get feacmeres to iterate through
		vLayer = coastalmeqgis_find_layer(gisLayer)
		if feacmeres == 'all':
			featIterator = vLayer.getFeatures()
			feacmereCount = vLayer.feacmereCount()
		elif feacmeres == 'selection':
			featIterator = vLayer.getSelectedFeatures()
			feacmereCount = vLayer.selectedFeatureCount()
		else:
			return False
			
		# get mesh layers (QgsMeshLayer)
		mLayers = []
		for mesh in resultMesh:
			mLayers.append(coastalmeqgis_find_layer(mesh))
		if not mLayers:
			return False
			
		# get attribute field index for name
		if nameField is not None and nameField != '-None-':
			nameIndex = vLayer.fields().names().index(nameField)
		else:
			nameIndex = None
			
		# convert formatted time back to what can be used to get results
		if timestep:
			if timestep == 'Maximum':
				timestepKey = timestep
			else:
				if qv < 31600:
					if self.cmeView.cmeOptions.xAxisDates:
						pdt = datetime.datetime.strptime(timestep, self.cmeView.cmeResults.dateFormat)
						modelDates = self.cmeView.cmeResults.date_tspec2time
						if timestep in modelDates:
							timestepKey = modelDates[timestep]
						else:
							modelDates2 = sorted([x for x in modelDates.keys()])
							timestepKey = self.cmeView.cmeResults.findTimeClosest(None, None, pdt, modelDates2, True, 'closest')
							timestepKey = modelDates[timestepKey]
					else:
						timestepKey = convertFormattedTimeToTime(timestep)
				else:
					if not self.cmeView.cmeOptions.xAxisDates:
						if timestep in self.cmeView.cmeResults.cboTime2timekey:
							timestepKey = self.cmeView.cmeResults.cboTime2timekey[timestep]
							timestepKey = self.cmeView.cmeResults.timekey2time[timestepKey]
						else:
							unit = self.cmeView.cmeOptions.timeUnits
							timestepKey = convertFormattedTimeToTime(timestep, unit=unit)
						zt = self.cmeView.cmeOptions.zeroTime
						timestepKey = zt + datetime.timedelta(hours=timestepKey)
					else:
						timestepKey = datetime.datetime.strptime(timestep, self.cmeView.cmeResults.dateFormat)
			
		# secmep progress bar
		if feacmereCount:
			complete = 0
			if self.iface is not None:
				self.iface.messageBar().clearWidgets()
				progressWidget = self.iface.messageBar().createMessage("COASTALME Viewer",
				                                                       " Exporting {0}s . . .".format(format))
				messageBar = self.iface.messageBar()
				progress = QProgressBar()
				progress.setMaximum(100)
				progressWidget.layout().addWidget(progress)
				messageBar.pushWidget(progressWidget, duration=1)
				self.iface.mainWindow().repaint()
			pComplete = 0
			complete = 0
		# loop through feacmeres and output
		for f in featIterator:
			if vLayer.geometryType() == QgsWkbTypes.PointGeometry:
				if nameIndex is not None:
					name = '{1}_{0}'.format(f.attributes()[nameIndex], mLayers[0].name())
				else:
					name = '{1}_{0}_TS'.format(f.id(), mLayers[0].name())
				self.cmeView.cmePlot.cmePlot2D.plotTimeSeriesFromMap(
					vLayer, f, bypass=True, mesh=mLayers, types=resultTypes, export=format,
					export_location=outputFolder, name=name, export_format=imageFormat,
					mesh_rendered=False, **kwargs)
			elif vLayer.geometryType() == QgsWkbTypes.LineGeometry:
				if nameIndex is not None:
					name = '{1}_{0}'.format(f.attributes()[nameIndex], mLayers[0].name())
				else:
					name = 'Cross_Section_{1}_{0}'.format(f.id(), mLayers[0].name())
				self.cmeView.cmePlot.cmePlot2D.plotCrossSectionFromMap(
					vLayer, f, bypass=True, mesh=mLayers, types=resultTypes, export=format,
					export_location=outputFolder, name=name, time=timestepKey, time_formatted=timestep, export_format=imageFormat,
					mesh_rendered=False, **kwargs)
			else:
				return False
			complete += 1
			pComplete = int(complete / feacmereCount * 100)
			if self.iface is not None:
				progress.setValue(pComplete)

		return True
	
	def openUserPlotDataManager(self, **kwargs):
		"""
		Opens the user plot data manage dialog
		
		:return:
		"""

		from .coastalmeqgis_cmeplot import CmePlot
		
		self.userPlotDataDialog = CmeUserPlotDataManagerDialog(self.iface, self.cmeView.cmePlot.userPlotData, **kwargs)
		if 'add_data' not in kwargs:
			self.userPlotDataDialog.exec()
		# self.cmeView.cmePlot.clearPlot(self.cmeView.tabWidget.currentIndex(), retain_1d=True, retain_2d=True, retain_flow=True)
		for i in range(self.userPlotDataDialog.UserPlotDataTable.rowCount()):
			name_ = self.userPlotDataDialog.UserPlotDataTable.item(i, 0).text()
			plotType = self.userPlotDataDialog.UserPlotDataTable.item(i, 1).text()
			self.cmeView.cmePlot.userPlotData.editDataSet(name_, plotType=plotType)
		self.cmeView.cmePlot.clearPlot2(self.cmeView.tabWidget.currentIndex(), CmePlot.DataUserData)

		return True

	def toggleMeshRender(self):
		"""
		Toggles mesh on and off
		
		:return:
		"""
		
		if self.cmeView.cmePlot.cmePlotToolbar.meshGridAction.isChecked():
			self.cmeView.cmeOptions.showGrid = True
		else:
			self.cmeView.cmeOptions.showGrid = False
			
		self.cmeView.renderMap()
		
	def exportAnimation(self, **kwargs):
		"""
		Export animation dialog
		
		:return:
		"""

		headless = kwargs['headless'] if 'headless' in kwargs else False
		
		self.animationDialog = CmeAnimationDialog(self.cmeView, **kwargs)
		if not headless:
			self.animationDialog.show()
		
	def exportMaps(self, **kwargs):
		"""
		Export maps dialog
		
		:return:
		"""

		headless = kwargs['headless'] if 'headless' in kwargs else False
		
		self.mapDialog = CmeMapDialog(self.cmeView, **kwargs)
		if not headless:
			self.mapDialog.show()
		
	def resultsFromSuperFiles(self, files):
		"""
		Extract mesh files and result datasets from .sup files
		
		:param files: list -> str full path to .sup file
		:return: dict -> 'name': dict -> 'mesh': path to mesh, 'datasets': list -> paths to datasets
		"""

		results = {}
		engine = None
		build = None
		
		for file in files:
			
			result = {}
			basename, ext = file, 1
			while ext:
				basename, ext = os.path.splitext(basename)
			name = os.path.basename(basename)
			dir = os.path.dirname(file)
			
			with open(file, 'r') as fo:
				for line in fo:
					if 'mesh2d' in line.lower():
						components = line.split('mesh2d')
						if len(components) < 2:
							components = line.split('MESH2D')
						if len(components) < 2:
							continue
						mesh = components[1].strip().strip('"').strip("'")
						mesh = getPathFromRel(dir, mesh)
						result['mesh'] = mesh
					elif 'data' in line.lower():
						components = line.split('data')
						if len(components) < 2:
							components = line.split('DATA')
						if len(components) < 2:
							continue
						dataset = components[1].strip().strip('"').strip("'")
						dataset = getPathFromRel(dir, dataset)
						if 'datasets' not in result:
							result['datasets'] = []
						result['datasets'].append(dataset)
					elif 'coastalme' in line.lower() and 'build' in line.lower():
						if 'fv' in line.lower():
							engine = 'FV'
						else:
							engine = 'CLA'
						build = line.split(':')[1].strip()
			
			results[name] = result
			
		return results, engine, build

	def flowRegimeToggled(self):

		self.cmeView.cmeContextMenu.resultTypeContextItem.toggleFlowRegime()

		# redraw plot
		self.cmeView.cmePlot.updateCurrentPlot(0, update='1d only')

	def loadHydraulicTables(self, infiles=()):
		"""

		"""

		if infiles:
			inFileNames = infiles[:]
		else:
			inFileNames = browse(self.cmeView, 'existing files', 'COASTALME_Results/lastFolder', 'Load 1D Hydraulic Tables',
			                     'CSV (*.csv *.CSV)')

		success = True
		for f in inFileNames:
			ta, err = self.cmeView.hydTables.loadData(f)
			if err:
				QMessageBox.critical(self.cmeView, "Load 1D Hydraulic Tables", err)
				success = False
			else:
				# dn = re.sub(r"(_1d_ta_tables_check.csv)$", "", os.path.basename(f), flags=re.IGNORECASE)  # displayname
				# dn = '{0}_1d_ta'.format(dn)
				self.cmeView.cmeResults.add1dHydTableToResults(ta.displayName, ta)

		return success

	def removeHydraulicTables(self):
		"""

		"""

		results = []
		for item in self.cmeView.OpenResults.selectedItems():
			ta = self.cmeView.hydTables.getData(item.text())
			if ta is not None:
				self.cmeView.cmeResults.remove1dHydTable(ta.displayName)
				self.cmeView.hydTables.closeData(ta.displayName)

	def addColourRampFromXML(self):
		"""

		"""

		xmlfile = browse(self.cmeView, 'existing file', "COASTALME/plot_colour_ramp", "Load Style XML", "XML (*.xml *.XML)")
		if xmlfile:
			cdicts = qgsxml_as_mpl_cdict(xmlfile)

			if not cdicts:
				QMessageBox.warning(self.cmeView, "Add Colour Ramp to Plot", "Error importing colour ramp styles")

			for name, cdict in cdicts.items():
				lcm = LinearSegmentedColormap(name, cdict)
				cm.register_cmap(name=name, cmap=lcm)

			QMessageBox.information(self.cmeView, "Add Colour Ramp to Plot", "Successfully imported colour ramp(s)")

	def resetMatplotColours(self):
		"""

		"""

		self.cmeView.cmePlot.clearFrozenPlotProperties(rtype='lines')
		self.cmeView.cmePlot.clear_labels_are_about_to_break()
		self.cmeView.cmePlot.colours = generateRandomMatplotColours2(100)
		self.cmeView.cmePlot.updateAllPlots()

	def resetPlotAxisNames(self):
		"""

		"""

		self.cmeView.cmePlot.clearFrozenPlotProperties(rtype='axis labels')
		self.cmeView.cmePlot.updateAllPlots()

	def redockCmeflowViewer(self):
		"""

		"""

		if self.cmeView.PlotLayout.isVisible():
			area = QT_DOCK_WIDGET_AREA_BOTTOM
		else:
			area = QT_DOCK_WIDGET_AREA_RIGHT

		self.iface.addDockWidget(area, self.cmeView)

	def activeMeshLayer(self, allow_multiple=False, window_title=''):
		if not self.cmeView.cmeResults.cmeResults2D.activeMeshLayers:
			return None
		# elif len(self.cmeView.cmeResults.cmeResults2D.activeMeshLayers) > 1:
		# 	self.meshDialog = coastalmeqgis_meshSelection_dialog(self.iface, self.cmeView.cmeResults.cmeResults2D.activeMeshLayers)
		# 	if window_title:
		# 		self.meshDialog.setWindowTitle(window_title)
		# 	if allow_multiple:
		# 		self.meshDialog.mesh_lw.setSelectionMode(QT_ABSTRACT_ITEM_VIEW_EXTENDED_SELECTION)
		# 	self.meshDialog.exec()
		# 	if self.meshDialog.selectedMesh is None:
		# 		return None
		# 	else:
		# 		if allow_multiple:
		# 			return[coastalmeqgis_find_layer(x) for x in self.meshDialog.selectedMesh]
		# 		else:
		# 			return coastalmeqgis_find_layer(self.meshDialog.selectedMesh)
		else:
			if allow_multiple:
				return self.cmeView.cmeResults.cmeResults2D.activeMeshLayers
			else:
				return self.cmeView.cmeResults.cmeResults2D.activeMeshLayers[0]

	def clickedResultDataType(self):
		return self.cmeView.cmeContextMenu.resultTypeContextItem.ds_type

	def clickedGroupIndex(self, meshLayer):
		resultType = self.cmeView.cmeContextMenu.resultTypeContextItem.ds_name
		if self.cmeView.cmeContextMenu.resultTypeContextItem.isMax:
			resultType = '{0}/Maximums'.format(resultType)
		elif self.cmeView.cmeContextMenu.resultTypeContextItem.isMin:
			resultType = '{0}/Minimums'.format(resultType)
		if meshLayer.name() in self.cmeView.cmeResults.results and resultType in self.cmeView.cmeResults.results[
			meshLayer.name()]:
			for _, (_, _, dsi) in self.cmeView.cmeResults.results[meshLayer.name()][resultType]['times'].items():
				return dsi.group()

		return None

	def copyStyle(self):
		meshLayer = self.activeMeshLayer(window_title='Select Result to Copy Style From')

		if meshLayer is None:
			return

		if self.clickedResultDataType() > 2:  # not a scalar result type
			return

		scalar, vector = False, False
		if self.clickedResultDataType() == 1:
			scalar = True
			mimeType = "application/coastalme_viewer_scalar.style"
		elif self.clickedResultDataType() == 2:
			vector = True
			mimeType = "application/coastalme_viewer_vector.style"

		index = self.clickedGroupIndex(meshLayer)
		rsScalar = meshLayer.rendererSettings().scalarSettings(index)
		rsVector = meshLayer.rendererSettings().vectorSettings(index)

		doc = QDomDocument('coastalme_meshlayer')
		if scalar:
			doc.appendChild(rsScalar.writeXml(doc))
		if vector:
			doc.appendChild(rsVector.writeXml(doc))

		clipboard = QApplication.clipboard()
		mimeData = QMimeData()
		mimeData.setData(mimeType, doc.toByteArray())
		mimeData.setText(doc.toString())  # so can be pasted into text editor
		clipboard.setMimeData(mimeData)

	def pasteStyle(self):
		meshLayer = self.activeMeshLayer(allow_multiple=True, window_title='Select Result(s) to Paste Style Into')

		if meshLayer is None:
			return

		if self.clickedResultDataType() > 2:  # not a scalar result type
			return

		scalar, vector = False, False
		if self.clickedResultDataType() == 1:
			scalar = True
			mimeType = "application/coastalme_viewer_scalar.style"
		elif self.clickedResultDataType() == 2:
			vector = True
			mimeType = "application/coastalme_viewer_vector.style"

		for ml in meshLayer:
			index = self.clickedGroupIndex(ml)
			rs = ml.rendererSettings()
			rsScalar = rs.scalarSettings(index)
			rsVector = rs.vectorSettings(index)

			clipboard = QApplication.clipboard()
			mimeData = clipboard.mimeData()

			if not mimeData.hasFormat(mimeType):
				return

			doc = QDomDocument('coastalme_meshlayer')
			stacmesOK, errorStr, errorLine, errorColumn = doc.setContent(mimeData.data(mimeType), True)
			if not stacmesOK:
				QMessageBox.critical(self.cmeView, 'Paste Style', 'Error pasting style: {0}'.format(errorStr))
				return

			if scalar:
				rsScalar.readXml(doc.documentElement())
				rs.setScalarSettings(index, rsScalar)
			if vector:
				rsVector.readXml(doc.documentElement())
				rs.setVectorSettings(index, rsVector)
			ml.setRendererSettings(rs)

			ml.triggerRepaint()

	def setReferenceTime(self, layer):

		class DateTimeEdit(QObject):
			def __init__(self, dt):
				QObject.__init__(self, None)
				self.dialog = QDialog()
				self.dialog.setWindowTitle('NetCDF Grid Reference Time')
				self.label = QLabel()
				self.label.setText('Use box below to change the reference time.')
				self.datetime_select = QgsDateTimeEdit()
				self.datetime_select.setDateTime(dt)
				self.cb = QCheckBox()
				self.cb.setChecked(True)
				self.cb.setText('Set COASTALME Viewer Zero Time to the Same')
				self.pbOk = QPushButton()
				self.pbOk.setText('OK')
				self.pbOk.clicked.connect(self.dialog.accept)
				self.pbCancel = QPushButton()
				self.pbCancel.clicked.connect(self.dialog.reject)
				self.pbCancel.setText('Cancel')
				self.dialog.setMinimumWidth(self.label.sizeHint().width())
				self.dialog.setMinimumHeight(self.label.sizeHint().height())
				layout = QVBoxLayout()
				layout.addWidget(self.label)
				layout.addWidget(self.datetime_select)
				layout.addWidget(self.cb)
				pb_layout = QHBoxLayout()
				pb_layout.addWidget(self.pbOk)
				pb_layout.addWidget(self.pbCancel)
				pb_layout.setAlignment(QT_ALIGN_RIGHT)
				layout.addLayout(pb_layout)
				self.dialog.setLayout(layout)

			def exec(self):
				return self.dialog.exec()

		datetime_select = DateTimeEdit(layer.reference_time)
		accepted = datetime_select.exec()
		if not accepted:
			return

		dt = qdt2dt(datetime_select.datetime_select.dateTime())
		dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)  # remove seconds
		layer.set_reference_time(dt)
		if datetime_select.cb.isChecked():
			self.cmeView.cmeOptions.zeroTime = dt
		self.cmeView.cmeResults.updateDateTimes()
		if Qgis.QGIS_VERSION_INT >= 31600:
			self.cmeView.cmeResults.updateResultTypes()

	def flipSecondaryAxis(self, plotNo):
		if self.cmeView.cmeOptions.secondary_axis_types[plotNo] == 'x-axis':
			self.cmeView.cmeOptions.secondary_axis_types[plotNo] = 'y-axis'
		else:
			self.cmeView.cmeOptions.secondary_axis_types[plotNo] = 'x-axis'
		QSettings().setValue('COASTALME/cmeview_secondary_axis_type_{0}'.format(plotNo), self.cmeView.cmeOptions.secondary_axis_types[plotNo])
		if self.cmeView.cmePlot.getSecondaryAxis(plotNo, create=False):
			self.cmeView.cmePlot.secondary_axis_flipped[plotNo] = True
			self.cmeView.cmePlot.updateCurrentPlot(plotNo)

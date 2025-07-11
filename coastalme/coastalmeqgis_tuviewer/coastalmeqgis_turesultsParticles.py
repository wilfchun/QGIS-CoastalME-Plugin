import os
import glob
import re
from datetime import timedelta, datetime
from qgis.core import *
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.core import QgsVectorLayer, QgsFeature, QgsPointXY, QgsGeometry, QgsField, Qgis
from ..coastalmeqgis_library import isSame_float, roundSeconds, datetime2timespec

try:
	from ..COASTALME_particles_data_provider import TuParticlesDataProvider
	have_netCDF4 = True
except ImportError:
	have_netCDF4 = False


from ..compatibility_routines import QT_MATCH_RECURSIVE, QT_TIMESPEC_UTC


class TuResultsParticles():
	"""
	Class for handling Particles results
	"""
	
	def __init__(self, TuView):
		self.tuView = TuView
		self.iface = TuView.iface
		self.resultsParticles = {} # display name -> [particles data provider, vectorLayer, [relative_times_in_hour]]
		self.debug = self.tuView.tuOptions.particlesWriteDebugInfo  # ES

	def importResults(self, inFileNames):
		"""
		Imports function that opens result particles layer

		:param inFileNames: list -> str - full path to particles result file
		:return: bool -> True for successful, False for unsuccessful
		"""

		qv = Qgis.QGIS_VERSION_INT

		if not have_netCDF4:
			return False

		# disconnect incoming signals for load step
		skipConnect = False
		try:
			self.tuView.project.layersAdded.disconnect(self.tuView.layersAdded)
		except:
			skipConnect = True

		for j, f in enumerate(inFileNames):
			# Load Particles
			if type(inFileNames) is dict:
				m = inFileNames[f]['particles']
				mLayer, name = self._load_file(m)
			else:
				mLayer, name = self._load_file(f)

			if qv >= 31600:
				self.tuView.tuResults.updateDateTimes()

			if mLayer is None or name is None:
				if not skipConnect:
					self.tuView.project.layersAdded.connect(self.tuView.layersAdded)
				return False

			# Open layer in map
			self.tuView.project.addMapLayer(mLayer)
			name = mLayer.name()
			# mLayer.nameChanged.connect(lambda: self.layerNameChanged(mLayer, name, mLayer.name()))  # if name is changed can capture this in indexing
			
			# add to result list widget
			names = []
			for i in range(self.tuView.OpenResults.count()):
				if self.tuView.OpenResults.item(i).text() not in names:
					names.append(self.tuView.OpenResults.item(i).text())
			if name not in names:
				self.tuView.OpenResults.addItem(name)  # add to widget
			k = self.tuView.OpenResults.findItems(name, QT_MATCH_RECURSIVE)[0]
			k.setSelected(True)
			self.tuView.resultChangeSignalCount = 0  # reset signal count back to 0
		
		# connect load signals
		if not skipConnect:
			self.tuView.project.layersAdded.connect(self.tuView.layersAdded)

		return True

	def _load_file(self, filename):
		qv = Qgis.QGIS_VERSION_INT
		if qv < 31600:
			return self._load_file_old(filename)
		else:
			return self._load_file_31600(filename)

	def _load_file_old(self, filename):
		qv = Qgis.QGIS_VERSION_INT

		if not filename:
			return None, None

		self.debug = self.tuView.tuOptions.particlesWriteDebugInfo  # ES

		if self.tuView.OpenResults.count() == 0:
			defaultRefTime = self.tuView.tuOptions.defaultZeroTime
		else:
			defaultRefTime = datetime2timespec(self.tuView.tuOptions.zeroTime, self.tuView.tuResults.loadedTimeSpec, QT_TIMESPEC_UTC)

		particles_data_provider = TuParticlesDataProvider()
		if particles_data_provider.load_file(filename, defaultRefTime):
			# create vector layer with correct attributes
			displayname = os.path.basename(filename)
			self.tuView.tuResults.results[displayname] = {}
			# ES added CRS
			if particles_data_provider.crs is None:
				crs = self.tuView.project.crs()
			else:
				crs = particles_data_provider.crs
			uri = "pointZ?crs={0}".format(crs.authid().lower())
			# vlayer = QgsVectorLayer("PointZ", displayname, "memory")
			vlayer = QgsVectorLayer(uri, displayname, "memory")
			vlayer.dataProvider().addAttributes(self._get_attributes_list(particles_data_provider))
			vlayer.updateFields()

			# add styles
			dir_path = os.path.dirname(os.path.realpath(__file__))
			styles_folder = os.path.join(dir_path, os.pardir, "QGIS_Styles", "particles", "*.qml")
			styles = glob.glob(styles_folder)
			# ES make sure default.qml is last otherwise default style is overwritten by each subsequent style
			styles = sorted(styles, key=lambda x: 1 if re.findall(r'default.qml$', x, flags=re.IGNORECASE) else 0)
			style_manager = vlayer.styleManager()
			for style in styles:
				# style_name = os.path.basename(style).strip('.qml')
				style_name = os.path.splitext(os.path.basename(style))[0]  # ES
				(_, success) = vlayer.loadNamedStyle(style)
				if not success:
					style_manager.removeStyle(style)

				style_manager.addStyleFromLayer(style_name)
			style_manager.setCurrentStyle("default")

			# populate resdata
			timekey2time = self.tuView.tuResults.timekey2time  # dict
			timekey2date = self.tuView.tuResults.timekey2date  # dict
			time2date = self.tuView.tuResults.time2date  # dict
			date2timekey = self.tuView.tuResults.date2timekey
			date2time = self.tuView.tuResults.date2time
			#zeroTime = self.tuView.tuOptions.zeroTime  # datetime
			zeroTime = particles_data_provider.getReferenceTime()  # this is timespec(1)
			if self.tuView.OpenResults.count() == 0:
				if qv >= 31300:
					self.tuView.tuOptions.zeroTime = datetime2timespec(zeroTime, 1, self.tuView.tuResults.timeSpec)
					self.tuView.tuOptions.timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
					self.tuView.tuResults.loadedTimeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
				else:
					self.tuView.tuOptions.zeroTime = zeroTime  # ES
			# if self.tuView.tuResults.timeSpec != self.tuView.tuResults.loadedTimeSpec:
			# 	particles_data_provider.set_reference_time(datetime2timespec(particles_data_provider.reference_time,
			# 	                                                             self.tuView.tuResults.timeSpec,
			# 	                                                             self.tuView.tuResults.loadedTimeSpec))

			timesteps = particles_data_provider.timeSteps(datetime2timespec(self.tuView.tuOptions.zeroTime,
			                                                                self.tuView.tuResults.loadedTimeSpec, 1))
			for t in timesteps:
				date = self.tuView.tuOptions.zeroTime + timedelta(hours=t)
				# date = datetime2timespec(self.tuView.tuOptions.zeroTime,
				#                          self.tuView.tuResults.loadedTimeSpec,
				#                          self.tuView.tuResults.timeSpec) \
				#        + timedelta(hours=t)
				date = roundSeconds(date, 2)
				timekey2time['{0:.6f}'.format(t)] = t
				# timekey2date['{0:.6f}'.format(t)] = zeroTime + timedelta(hours=t)
				timekey2date['{0:.6f}'.format(t)] = date
				# time2date[t] = zeroTime + timedelta(hours=t)
				time2date[t] = date
				# date2timekey[zeroTime + timedelta(hours=t)] = '{0:.6f}'.format(t)
				date2timekey[date] = '{0:.6f}'.format(t)
				# date2time[zeroTime + timedelta(hours=t)] = t
				date2time[date] = t

				if qv >= 31300:
					date_tspec = datetime2timespec(date, self.tuView.tuResults.loadedTimeSpec, QT_TIMESPEC_UTC)
				else:
					date_tspec = date
				self.tuView.tuResults.timekey2date_tspec['{0:.6f}'.format(t)] = date_tspec
				self.tuView.tuResults.time2date_tspec[t] = date_tspec
				self.tuView.tuResults.date_tspec2timekey[date_tspec] = '{0:.6f}'.format(t)
				self.tuView.tuResults.date_tspec2time[date_tspec] =  t
				self.tuView.tuResults.date2date_tspec[date] = date_tspec
				self.tuView.tuResults.date_tspec2date[date_tspec] = date

			self.tuView.tuResults.results[displayname]["_particles"] = [timesteps]

			# add to internal storage
			self.resultsParticles[displayname] = [particles_data_provider, vlayer, timesteps]

			# load first step
			self.updateActiveTime()

			# Return
			return vlayer, displayname

		# Failure
		return None, None

	def _load_file_31600(self, filename):
		qv = Qgis.QGIS_VERSION_INT

		if not filename:
			return None, None

		self.debug = self.tuView.tuOptions.particlesWriteDebugInfo  # ES

		if self.tuView.OpenResults.count() == 0:
			# defaultRefTime = self.tuView.tuOptions.defaultZeroTime
			defaultRefTime = self.tuView.tuOptions.zeroTime
		else:
			defaultRefTime = datetime2timespec(self.tuView.tuOptions.zeroTime, self.tuView.tuResults.loadedTimeSpec, QT_TIMESPEC_UTC)

		particles_data_provider = TuParticlesDataProvider()
		if particles_data_provider.load_file(filename, defaultRefTime):
			# create vector layer with correct attributes
			displayname = os.path.basename(filename)
			self.tuView.tuResults.results[displayname] = {}
			# ES added CRS
			if particles_data_provider.crs is None:
				crs = self.tuView.project.crs()
			else:
				crs = particles_data_provider.crs
			uri = "pointZ?crs={0}".format(crs.authid().lower())
			# vlayer = QgsVectorLayer("PointZ", displayname, "memory")
			vlayer = QgsVectorLayer(uri, displayname, "memory")
			vlayer.dataProvider().addAttributes(self._get_attributes_list(particles_data_provider))
			vlayer.updateFields()

			# add styles
			dir_path = os.path.dirname(os.path.realpath(__file__))
			styles_folder = os.path.join(dir_path, os.pardir, "QGIS_Styles", "particles", "*.qml")
			styles = glob.glob(styles_folder)
			# ES make sure default.qml is last otherwise default style is overwritten by each subsequent style
			styles = sorted(styles, key=lambda x: 1 if re.findall(r'default.qml$', x, flags=re.IGNORECASE) else 0)
			style_manager = vlayer.styleManager()
			for style in styles:
				# style_name = os.path.basename(style).strip('.qml')
				style_name = os.path.splitext(os.path.basename(style))[0]  # ES
				(_, success) = vlayer.loadNamedStyle(style)
				if not success:
					style_manager.removeStyle(style)

				style_manager.addStyleFromLayer(style_name)
			style_manager.setCurrentStyle("default")

			# populate resdata
			timekey2time = self.tuView.tuResults.timekey2time  # dict
			zeroTime = particles_data_provider.getReferenceTime()  # this is timespec(1)
			if self.tuView.OpenResults.count() == 0:
				self.tuView.tuOptions.zeroTime = datetime2timespec(zeroTime, 1, self.tuView.tuResults.timeSpec)
				if self.iface is not None:
					self.tuView.tuOptions.timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
					self.tuView.tuResults.loadedTimeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
				else:
					self.tuView.tuOptions.timeSpec = 1
					self.tuView.tuResults.loadedTimeSpec = 1

			timesteps = particles_data_provider.timeSteps(datetime2timespec(self.tuView.tuOptions.zeroTime, QT_TIMESPEC_UTC, QT_TIMESPEC_UTC))
			for t in timesteps:
				timekey2time['{0:.6f}'.format(t)] = t

			self.tuView.tuResults.results[displayname]["_particles"] = {'times': {'{0:.6f}'.format(x): [x] for x in timesteps},
			                                                            'referenceTime': particles_data_provider.reference_time}


			# add to internal storage
			self.resultsParticles[displayname] = [particles_data_provider, vlayer, timesteps]

			# load first step
			self.updateActiveTime()

			# Return
			return vlayer, displayname

		# Failure
		return None, None

	def removeResults(self, resList, **kwargs):
		"""
		Removes the Particles results from the indexed results and ui.

		:param resList: list -> str result name e.g. M01_5m_001
		:return: bool -> True for successful, False for unsuccessful
		"""

		remove_vlayer = kwargs['remove_vlayer'] if 'remove_vlayer' in kwargs else True

		results = self.tuView.tuResults.results

		try:
			self.tuView.project.layersWillBeRemoved.disconnect(self.tuView.layersRemoved)
		except:
			pass

		for res in resList:
			if res in self.resultsParticles:
				if res in results:
					del results[res]
				vlayer = self.resultsParticles[res][1]
				if remove_vlayer:
					try:
						self.tuView.project.removeMapLayer(vlayer.id())
						del vlayer
					except:
						pass

				try:
					self.resultsParticles[res][0].nc.close()
				except:
					pass
				del self.resultsParticles[res]

			for i in range(self.tuView.OpenResults.count()):
				item = self.tuView.OpenResults.item(i)
				if item is not None and item.text() == res:
					if res not in results:
						self.tuView.OpenResults.takeItem(i)

		if self.tuView.canvas is not None:
			self.tuView.canvas.refresh()
		self.tuView.tuResults.updateResultTypes()
		self.tuView.project.layersWillBeRemoved.connect(self.tuView.layersRemoved)

		return True

	def updateActiveTime(self, time=None):
		qv = Qgis.QGIS_VERSION_INT
		if qv < 31600:
			self.updateActiveTime_old(time)
		else:
			self.updateActiveTime_31600(time)

	def updateActiveTime_old(self, time=None):
		"""
		Loads a new set of particles for next timestep
		"""

		from .coastalmeqgis_turesults import TuResults  # ES
		self.debug = self.tuView.tuOptions.particlesWriteDebugInfo  # ES

		if time is None:
			active_time = self.tuView.tuResults.activeTime
			if active_time is None:
				global_relative_time = 0
			else:
				global_relative_time = self.tuView.tuResults.timekey2time[active_time]
		else:
			global_relative_time = time

		for _, data in self.resultsParticles.items():
			particles_data_provider = data[0]
			vlayer = data[1]
			timesteps = data[2]

			# find nearest lower time
			time_index = 0
			for i, relative_time in enumerate(timesteps):
				time_index = i
				relative_time = timesteps[i]
				if isSame_float(relative_time, global_relative_time, prec=TuResults.TimePrecision):  # ES
					break  # ES
				if relative_time > global_relative_time:
					time_index = max(0, time_index - 1)  # ES
					break

			# re-populate particles
			if vlayer is not None:
				self._updateVectorLayerAttributes(vlayer, self.debug)
				points = self._get_features(particles_data_provider, vlayer, time_index)
				vlayer.dataProvider().truncate()
				vlayer.dataProvider().addFeatures(points)
				vlayer.updateExtents()
				vlayer.triggerRepaint()

	def updateActiveTime_31600(self, date=None):
		"""
		Loads a new set of particles for next timestep
		"""

		self.debug = self.tuView.tuOptions.particlesWriteDebugInfo  # ES

		if date is None:
			active_date = self.tuView.tuResults.activeTime
		else:
			active_date = date

		selectedResults = [x.text() for x in self.tuView.OpenResults.selectedItems()]

		for res_name, data in self.resultsParticles.items():
			particles_data_provider = data[0]
			vlayer = data[1]

			if res_name not in selectedResults or active_date is None:
				time_index = None
			else:
				# find closest
				for time_index, date in enumerate(particles_data_provider.times):
					if date == active_date:
						break
					if time_index == 0:
						diff = abs((date - active_date).total_seconds())
					if date > active_date:
						diff2 = abs((date - active_date).total_seconds())
						if diff <= diff2:
							time_index = max(0, time_index - 1)
							break
						else:
							break
					else:
						diff = abs((date - active_date).total_seconds())

			# re-populate particles
			if vlayer is not None:
				self._updateVectorLayerAttributes(vlayer, self.debug)
				points = self._get_features(particles_data_provider, vlayer, time_index)
				vlayer.dataProvider().truncate()
				vlayer.dataProvider().addFeatures(points)
				vlayer.updateExtents()
				vlayer.triggerRepaint()

	def _get_attributes_list(self, particles_data_provider):
		attrs = []

		# add mandatory attributes
		attrs.extend([
			QgsField("id", QVariant.Int),
			QgsField("stat", QVariant.Int),
			QgsField("groupID", QVariant.Int)
		])

		# add optional attributes (variables) that are in file
		dataset_vars = particles_data_provider.get_all_variable_names(self.debug)
		for var in dataset_vars:
			attrs.append(QgsField(var, QVariant.Double))

		# add some time attributes if debug
		if self.debug:
			attrs.extend(self._timeFields())

		return attrs


	def _get_features(self, particles_data_provider, vlayer, time_index):
		points = []

		if time_index == None:
			return points

		data = particles_data_provider.read_data_at_time(time_index)
		if data is None:
			return points

		if self.debug:  # ES keep coords in attribute table
			x = data.get('x')
			y = data.get('y')
			z = data.get('z')
			absTime = particles_data_provider.timeSteps(particles_data_provider.getReferenceTime())[time_index]
			relTime = particles_data_provider.timeSteps(self.tuView.tuOptions.zeroTime)[time_index]
			dt = particles_data_provider.getReferenceTime() + timedelta(hours=absTime)
			dt = roundSeconds(dt, 2)
		else:
			x = data.pop('x')
			y = data.pop('y')
			z = data.pop('z')
		stats = data.get('stat')

		for i, stat in enumerate(stats):
			# ignore inactive particles
			if int(stat) > 0:
				feat = QgsFeature()
				point = QgsPoint(x[i], y[i], z[i])
				feat.setGeometry(QgsGeometry(point))
				feat.setFields(vlayer.fields())
				for attr in data.keys():
					feat['id'] = i
					feat[attr] = float(
						data.get(attr)[i])  # must be converted to primitive type, otherwise feature data wont be stored
				if self.debug:  # ES
					feat['_absTime'] = absTime
					feat['_relTime'] = relTime
					feat['_dateTime'] = self.tuView.tuResults._dateFormat.format(dt)
				points.append(feat)

		return points

	def _timeFields(self):
		"""Time fields"""

		attrs = [
			QgsField("_absTime", QVariant.Double),
			QgsField("_relTime", QVariant.Double),
			QgsField("_dateTime", QVariant.String, len=20)
		]

		return attrs

	def _spatialFields(self):
		"""Fields for X, Y, Z"""

		attrs = [
			QgsField("x", QVariant.Double),
			QgsField("y", QVariant.Double),
			QgsField("z", QVariant.Double)
		]

		return attrs

	def _updateVectorLayerAttributes(self, vlayer, debug):
		"""Update attributes based on whether debugging or not"""

		changed = False
		if debug:
			if vlayer.fields().lookupField('_absTime') < 0:
				vlayer.startEditing()
				changed = True
				for field in self._spatialFields():
					vlayer.addAttribute(field)
				for field in self._timeFields():
					vlayer.addAttribute(field)
		else:
			if vlayer.fields().lookupField('_absTime') >= 0:
				vlayer.startEditing()
				changed = True
				for field in self._spatialFields():
					i = vlayer.fields().lookupField(field.name())
					vlayer.deleteAttribute(i)
				for field in self._timeFields():
					i = vlayer.fields().lookupField(field.name())
					vlayer.deleteAttribute(i)

		if changed:
			vlayer.commitChanges()

	def reloadTimesteps(self, resname):
		qv = Qgis.QGIS_VERSION_INT

		if resname not in self.resultsParticles:
			return
		particles_data_provider = self.resultsParticles[resname][0]

		if not particles_data_provider.has_reference_time:
			particles_data_provider.default_reference_time = datetime2timespec(self.tuView.tuOptions.zeroTime, self.tuView.tuResults.loadedTimeSpec, 1)
			particles_data_provider._fill_times_arr()

		zeroTime = particles_data_provider.getReferenceTime()  # this is timespec(1)
		timekey2time = self.tuView.tuResults.timekey2time  # dict
		timekey2date = self.tuView.tuResults.timekey2date  # dict
		time2date = self.tuView.tuResults.time2date  # dict
		date2timekey = self.tuView.tuResults.date2timekey
		date2time = self.tuView.tuResults.date2time

		timesteps = particles_data_provider.timeSteps(datetime2timespec(self.tuView.tuOptions.zeroTime,
		                                                                self.tuView.tuResults.loadedTimeSpec, 1))
		for t in timesteps:
			date = self.tuView.tuOptions.zeroTime + timedelta(hours=t)
			#date = datetime2timespec(self.tuView.tuOptions.zeroTime,
			#                         self.tuView.tuResults.loadedTimeSpec,
			#                         self.tuView.tuResults.timeSpec) \
			#       + timedelta(hours=t)
			date = roundSeconds(date, 2)
			timekey2time['{0:.6f}'.format(t)] = t
			timekey2date['{0:.6f}'.format(t)] = date
			time2date[t] = date
			date2timekey[date] = '{0:.6f}'.format(t)
			date2time[date] = t

			if qv >= 31300:
				date_tspec = datetime2timespec(date, self.tuView.tuResults.loadedTimeSpec, QT_TIMESPEC_UTC)
			else:
				date_tspec = date
			self.tuView.tuResults.timekey2date_tspec['{0:.6f}'.format(t)] = date_tspec
			self.tuView.tuResults.time2date_tspec[t] = date_tspec
			self.tuView.tuResults.date_tspec2timekey[date_tspec] = '{0:.6f}'.format(t)
			self.tuView.tuResults.date_tspec2time[date_tspec] = t
			self.tuView.tuResults.date2date_tspec[date] = date_tspec
			self.tuView.tuResults.date_tspec2date[date_tspec] = date

		self.tuView.tuResults.results[resname]["_particles"] = [timesteps]
		self.resultsParticles[resname][2] = timesteps
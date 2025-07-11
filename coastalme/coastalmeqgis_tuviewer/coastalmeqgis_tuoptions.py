from datetime import datetime
from qgis.PyQt.QtCore import *

from ..compatibility_routines import QT_TIMESPEC_UTC



class TuOptions():
	
	def __init__(self):
		settings = QSettings()
		self.defaultZeroTime = datetime(1999, 12, 31, 14, 0, 0)
		self.liveMapTracking = False
		self.meanEventSelection = 'next higher'
		self.playDelay = 1.0
		self.resolution = 1.0
		self.iLabelField = 0
		self.showGrid = False
		self.showTriangles = False
		self.xAxisDates = False
		self.xAxisLabelRotation = 0
		self.timeUnits = 'h'
		self.writeMeshIntersects = False
		self.particlesWriteDebugInfo = False
		self.verticalProfileInterpolated = False
		self.timeSpec = QT_TIMESPEC_UTC
		self.secondary_axis_types = {0: 'y-axis', 1: 'y-axis', 2: 'y-axis', 3: 'x-axis'}
		self.copy_mesh = True if settings.value('COASTALME/tuview_copy_mesh', 'false') in ['True', 'true', True] else False
		self.show_copy_mesh_dlg = True if settings.value('COASTALME/tuview_show_copy_mesh_dlg', 'false') in ['True', 'true', True] else False
		self.del_copied_res = True if settings.value('COASTALME/tuview_del_copied_res', 'true') in ['True', 'true', True] else False
		self.profile_plotting_tasks = True

		if settings.contains("COASTALME/tuview_defaultlayout"):
			self.defaultLayout = settings.value('COASTALME/tuview_defaultlayout')
		else:
			self.defaultLayout = 'previous_state'
		zeroTime = settings.value('COASTALME/tuview_zeroTime')
		if zeroTime:
			self.zeroTime = zeroTime
		else:
			# self.zeroTime = datetime(1990, 1, 1, 0, 0, 0)
			self.zeroTime = self.defaultZeroTime
		dateFormat = settings.value('COASTALME/tuview_dateFormat')
		if dateFormat:
			self.dateFormat = dateFormat
		else:
			self.dateFormat = '%H:%M'
		_dateFormat = settings.value('COASTALME/tuview__dateFormat')
		if _dateFormat:
			self._dateFormat = _dateFormat
		else:
			self._dateFormat = '{0:%H}:{0:%M}'
		if settings.contains("COASTALME/tuview_plotbackgroundcolour"):
			self.plotBackgroundColour = settings.value("COASTALME/tuview_plotbackgroundcolour")
		else:
			self.plotBackgroundColour = '#e5e5e5'

		if settings.contains("COASTALME/tuview_defaultfontsize"):
			try:
				self.defaultFontSize = int(settings.value("COASTALME/tuview_defaultfontsize"))
			except ValueError:
				self.defaultFontSize = 10
		else:
			self.defaultFontSize = 10

		if settings.contains("COASTALME/tuview_iconsize"):
			try:
				self.iconSize = int(settings.value("COASTALME/tuview_iconsize"))
			except ValueError:
				self.iconSize = 24
		else:
			self.iconSize = 24

		if settings.contains("COASTALME/tuview_tcf_load_method"):
			try:
				self.tcfLoadMethod = settings.value("COASTALME/tuview_tcf_load_method")
			except:
				self.tcfLoadMethod = 'result_selection'
		else:
			self.tcfLoadMethod = 'result_selection'

		if settings.contains("COASTALME/tuview_plot_inactive_areas"):
			try:
				self.plotInactiveAreas = True if settings.value("COASTALME/tuview_plot_inactive_areas") == 'true' else False
			except:
				self.plotInactiveAreas = True
		else:
			self.plotInactiveAreas = True

		if settings.contains('COASTALME/tuview_secondary_axis_type_0'):
			self.secondary_axis_types[0] = settings.value('COASTALME/tuview_secondary_axis_type_0')
		if settings.contains('COASTALME/tuview_secondary_axis_type_1'):
			self.secondary_axis_types[1] = settings.value('COASTALME/tuview_secondary_axis_type_1')
		if settings.contains('COASTALME/tuview_secondary_axis_type_3'):
			self.secondary_axis_types[3] = settings.value('COASTALME/tuview_secondary_axis_type_3')

		# curtain vectors
		self.curtain_vector_scale = float(settings.value("COASTALME/tuview_curtain_vector_scale", "0.005"))
		self.curtain_vector_scale_units = settings.value("COASTALME/tuview_curtain_vector_scale_units", "dots")
		if self.curtain_vector_scale_units == 'default':
			self.curtain_vector_scale_units = None
		self.curtain_vector_units = settings.value("COASTALME/tuview_curtain_vector_units", "dots")
		if self.curtain_vector_units == 'default':
			self.curtain_vector_units = None
		self.curtain_vector_width = float(settings.value("COASTALME/tuview_curtain_vector_width", "0.5"))
		self.curtain_vector_head_width = float(settings.value("COASTALME/tuview_curtain_vector_head_width", "10.0"))
		self.curtain_vector_head_length = float(settings.value("COASTALME/tuview_curtain_vector_head_length", "10.0"))
		self.curtain_vector_horizontal_factor = float(settings.value("COASTALME/tuview_curtain_vector_horizontal_factor", "1.0"))
		self.curtain_vector_vertical_factor = float(settings.value("COASTALME/tuview_curtain_vector_vertical_factor", "1.0"))

	def saveProject(self, project):
		try:
			project.writeEntry("TUVIEW", "livemaptracking", str(self.liveMapTracking))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "meaneventselection", self.meanEventSelection)
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "playdelay", str(self.playDelay))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "resolution", str(self.resolution))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "ilabelfield", str(self.iLabelField))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "showgrid", str(self.showGrid))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "showtriangles", str(self.showTriangles))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "xaxisdates", str(self.xAxisDates))
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "xaxislabelrotation", str(self.xAxisLabelRotation))
		except:
			pass

		try:
			zt = self.zeroTime if self.zeroTime else self.defaultZeroTime
			zeroTime = '{0}~~{1}~~{2}~~{3}~~{4}~~{5}'.format(zt.year, zt.month, zt.day,
															 zt.hour, zt.minute, zt.second)
			project.writeEntry("TUVIEW", "zerotime", zeroTime)
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "dateformat", self.dateFormat)
		except:
			pass

		try:
			project.writeEntry("TUVIEW", "_dateformat", self._dateFormat)
		except:
			pass
	
	def readProject(self, project):
		try:
			liveMapTracking = project.readEntry("TUVIEW", "livemaptracking")[0]
			self.liveMapTracking = True if liveMapTracking == 'True' else False
		except:
			pass

		try:
			self.meanEventSelection = project.readEntry("TUVIEW", "meaneventselection")[0]
		except:
			pass

		try:
			self.playDelay = float(project.readEntry("TUVIEW", "playdelay")[0])
		except:
			pass

		try:
			self.resolution = float(project.readEntry("TUVIEW", "resolution")[0])
		except:
			pass

		try:
			self.iLabelField = int(project.readEntry("TUVIEW", "ilabelfield")[0])
		except:
			pass

		try:
			showGrid = project.readEntry("TUVIEW", "showgrid")[0]
			self.showGrid = True if showGrid == 'True' else False
		except:
			pass

		try:
			showTriangles = project.readEntry("TUVIEW", "showtriangles")[0]
			self.showTriangles = True if showTriangles == 'True' else False
		except:
			pass

		try:
			xAxisDates = project.readEntry("TUVIEW", "xaxisdates")[0]
			self.xAxisDates = True if xAxisDates == 'True' else False
		except:
			pass

		try:
			self.xAxisLabelRotation = int(project.readEntry("TUVIEW", "xaxislabelrotation")[0])
		except:
			pass

		try:
			zeroTime = project.readEntry("TUVIEW", "zerotime")[0]
			zeroTime = zeroTime.split('~~')
			self.zeroTime = datetime(int(zeroTime[0]), int(zeroTime[1]), int(zeroTime[2]),
			                         int(zeroTime[3]), int(zeroTime[4]), int(zeroTime[5]))
		except:
			pass

		try:
			self.dateFormat = project.readEntry("TUVIEW", "dateformat")[0]
		except:
			pass

		try:
			self._dateFormat = project.readEntry("TUVIEW", "_dateformat")[0]
		except:
			pass
import platform
import os
import sys
import shutil
import tempfile
import zipfile
import subprocess
import re
from datetime import datetime, timedelta
from qgis.core import QgsApplication as qApp
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsNetworkAccessManager

from ..forms.ui_animation_dialog import Ui_AnimationDialog
from ..forms.animation_plot_properties import Ui_PlotProperties
from ..forms.label_properties import Ui_textPropertiesDialog
from ..forms.image_properties import Ui_ImageProperties
from ..coastalmeqgis_library import (applyMatplotLibArtist, convertTimeToFormattedTime,
                                  convertFormattedTimeToTime, getPolyCollectionExtents, getQuiverExtents,
                                  convertTimeToDate, convertFormattedDateToTime, addColourBarAxes, reSpecPlot,
                                  addLegend, addQuiverKey, datetime2timespec, convert_datetime_to_float,
                                  convert_float_to_datetime, qdt2dt, DownloadBinPackage)
from coastalme.toc.toc import coastalmeqgis_find_layer
from ..forms.animation_axis_limits_warning import Ui_animationPlotLimitsWarning
import matplotlib
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.patches import Polygon
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.collections import PolyCollection
from matplotlib.quiver import Quiver
from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot3d import ColourBar
from ..coastalmeqgis_tuviewer.coastalmeqgis_turesults2d import TuResults2D
from ..coastalmeqgis_tuviewer.coastalmeqgis_turesults import TuResults
import requests
from ..nc_grid_data_provider import NetCDFGrid

from ..compatibility_routines import QT_HEADER_VIEW_RESIZE_TO_CONTENT, QT_MESSAGE_BOX_YES, QT_ALIGN_CENTER, QT_ALIGN_LEFT, QT_EVENT_LOOP_EXCLUDE_USER_INPUT_EVENTS, QT_ITEM_FLAG_ITEM_IS_SELECTABLE, QT_ALIGN_TOP, QT_MESSAGE_BOX_NO, QT_CUSTOM_CONTEXT_MENU, QT_IMAGE_FORMAT_ARGB32, QT_UNCHECKED, QT_NETWORK_REQUEST_HTTP_STATUS_CODE_ATTRIBUTE, is_qt6, QT_CHECKED, QT_CURSOR_WAIT, QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE, QT_BLACK, QT_ITEM_FLAG_ITEM_IS_ENABLED, QT_ITEM_DATA_DISPLAY_ROLE


# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
	"""
	Finds exe either from filepath or in paths
	
	:param program: str
	:return: str
	"""
	
	import os
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file

	return None


def findPlatformVersion():
	platformVersion = platform.system()
	if platform.architecture()[0] == '64bit':
		platformVersion += '64'
	return platformVersion


def downloadBinPackage(packageUrl, destinationFileName):
	# request = QNetworkRequest(QUrl(packageUrl))
	# request.setRawHeader(b'Accept-Encoding', b'gzip,deflate')
	#
	# reply = QgsNetworkAccessManager.instance().get(request)
	# evloop = QEventLoop()
	# reply.finished.connect(evloop.quit)
	# evloop.exec(QT_EVENT_LOOP_EXCLUDE_USER_INPUT_EVENTS)
	# content_type = reply.rawHeader(b'Content-Type')
	#if content_type == QByteArray().append('application/zip'):
	# if content_type == b'application/zip':
	r = requests.get(packageUrl, stream=True)
	if r.status_code == requests.codes.ok and r.headers['Content-Type'] == 'application/zip':
		if os.path.isfile(destinationFileName):
			os.unlink(destinationFileName)

		destinationFile = open(destinationFileName, 'wb')
		# destinationFile.write(bytearray(reply.readAll()))
		destinationFile.write(bytearray(r.content))
		destinationFile.close()
	else:
		# ret_code = reply.attribute(QT_NETWORK_REQUEST_HTTP_STATUS_CODE_ATTRIBUTE)
		raise IOError("{} {}".format(r.status_code, packageUrl))
	
	
def downloadFfmpeg(parent_widget=None):
	
	# downloadBaseUrl = 'https://www.lutraconsulting.co.uk/'
	downloadBaseUrl = 'https://www.gyan.dev/ffmpeg/builds/'
	destFolder = os.path.dirname(os.path.dirname(__file__))
	# ffmpegZip = 'ffmpeg-20150505-git-6ef3426-win32-static.zip'
	ffmpegZip = 'ffmpeg-release-essentials.zip'
	ffmpegZipPath = os.path.join(destFolder, ffmpegZip)
	# ffmpegUrl = downloadBaseUrl+'products/crayfish/viewer/binaries/'+findPlatformVersion()+'/extra/'+ffmpegZip
	ffmpegUrl = '{0}{1}'.format(downloadBaseUrl, ffmpegZip)

	qApp.setOverrideCursor(QCursor(QT_CURSOR_WAIT))
	try:
		# downloadBinPackage(ffmpegUrl, ffmpegZipPath)
		downloader = DownloadBinPackage(ffmpegUrl, ffmpegZipPath, 'Downloading ffmpeg.exe. . . ')
		downloader.start()
		downloader.wait()
		z = zipfile.ZipFile(ffmpegZipPath)
		ffmpeg_loc = None
		for member in z.namelist():
			if 'ffmpeg.exe' in member:
				ffmpeg_loc = z.extract(member, destFolder)
				break
		# z.extractall(destFolder)
		z.close()
		os.unlink(ffmpegZipPath)
		qApp.restoreOverrideCursor()
		# return os.path.join(destFolder, 'ffmpeg.exe')
		return ffmpeg_loc
	except IOError as err:
		qApp.restoreOverrideCursor()
		QMessageBox.critical(parent_widget,
		  'Could Not Download FFmpeg',
		  "Download of FFmpeg failed. Please try again or contact us for "
		  "further assistance.\n\n(Error: %s)" % str(err))
	except Exception as e:
		qApp.restoreOverrideCursor()
		QMessageBox.critical(parent_widget,
		                     'Could Not Download FFmpeg',
		                     "Download of FFmpeg failed. Please try again or contact us for "
		                     "further assistance.\n\n(Error: %s)" % str(e))


def findLayoutItem(layout, id):
	for i in layout.items():
		if isinstance(i, QgsLayoutItemPicture) and i.id() == id:
			return i
		
	return None


def findLayoutGraphic(layout, id):
	for i in layout.items():
		if isinstance(i, QgsLayoutItemPolyline) and i.id() == id:
			return i
	
	return None


def findLayoutLabel(layout, id):
	for i in layout.items():
		if isinstance(i, QgsLayoutItemLabel) and i.id() == id:
			return i
	
	return None


def composition_set_time(c, time):
	for i in c.items():
		if isinstance(i, QgsLayoutItemLabel) and i.id() == "time":
			#txt = time_to_string(time)
			#if time < 100:
			#	txt = convertTimeToFormattedTime(time)
			#else:
			#	txt = convertTimeToFormattedTime(time, hour_padding=3)
			i.setText(time)
			
			
def composition_set_title(c, label):
	for i in c.items():
		if isinstance(i, QgsLayoutItemLabel) and i.id() == "title":
			#txt = time_to_string(time)
			i.setText(label)
			return i
		
	return None


def setPlotProperties(fig, ax, prop, ax2, layout_type, layout_item, dateTime=False, dateformat='', plotType=None):

	if layout_type == 'default':
		fig.set_size_inches(prop.sbFigSizeX.value() / 25.4, prop.sbFigSizeY.value() / 25.4)
	elif layout_type == 'template':
		if layout_item is None:
			return
		r = layout_item.sizeWithUnits()
		fig.set_size_inches(r.width() / 25.4, r.height() / 25.4)
	else:
		return
	# fig.suptitle(prop.leTitle.text())
	ax.set_title(prop.leTitle.text())
	ax.set_xlabel(prop.leXLabel.text())
	ax.set_ylabel(prop.leYLabel.text())
	if ax2:
		if plotType == 'Vert Profile':
			ax2.set_xlabel(prop.leX2Label.text())
			ax2.set_xlim((prop.sbX2min.value(), prop.sbX2Max.value()))
		else:
			ax2.set_ylabel(prop.leY2Label.text())
			ax2.set_ylim((prop.sbY2Min.value(), prop.sbY2Max.value()))
	if dateTime:  # display x axis as dates
		fmt = mdates.DateFormatter(dateformat)
		ax.xaxis.set_major_formatter(fmt)
		for tick in ax.get_xticklabels():
			tick.set_rotation(prop.sbXAxisRotation.value())
			if prop.sbXAxisRotation.value() > 0 and prop.sbXAxisRotation.value() < 90:
				tick.set_horizontalalignment('right')
			elif prop.sbXAxisRotation.value() > 90 and prop.sbXAxisRotation.value() < 180:
				tick.set_horizontalalignment('left')
			elif prop.sbXAxisRotation.value() > 180 and prop.sbXAxisRotation.value() < 270:
				tick.set_horizontalalignment('right')
			elif prop.sbXAxisRotation.value() > 270 and prop.sbXAxisRotation.value() < 360:
				tick.set_horizontalalignment('left')
			elif prop.sbXAxisRotation.value() > -90 and prop.sbXAxisRotation.value() < 0:
				tick.set_horizontalalignment('left')
			elif prop.sbXAxisRotation.value() > -180 and prop.sbXAxisRotation.value() < -90:
				tick.set_horizontalalignment('right')
			elif prop.sbXAxisRotation.value() > -270 and prop.sbXAxisRotation.value() < -180:
				tick.set_horizontalalignment('left')
			elif prop.sbXAxisRotation.value() > -360 and prop.sbXAxisRotation.value() < -270:
				tick.set_horizontalalignment('right')
		if not prop.xUseMatplotLibDefault:
			xmin = datetime(prop.dteXmin.dateTime().date().year(),
			                prop.dteXmin.dateTime().date().month(),
			                prop.dteXmin.dateTime().date().day(),
			                prop.dteXmin.dateTime().time().hour(),
			                prop.dteXmin.dateTime().time().minute(),
			                prop.dteXmin.dateTime().time().second(),
			                prop.dteXmin.dateTime().time().msec())
			xmax = datetime(prop.dteXMax.dateTime().date().year(),
			                prop.dteXMax.dateTime().date().month(),
			                prop.dteXMax.dateTime().date().day(),
			                prop.dteXMax.dateTime().time().hour(),
			                prop.dteXMax.dateTime().time().minute(),
			                prop.dteXMax.dateTime().time().second(),
			                prop.dteXMax.dateTime().time().msec())
			ax.set_xlim((xmin, xmax))
	else:  # display x axis as time (hr)
		if not prop.xUseMatplotLibDefault:
			ax.set_xlim((prop.sbXmin.value(), prop.sbXMax.value()))
	if not prop.yUseMatplotLibDefault:
		ax.set_ylim((prop.sbYMin.value(), prop.sbYMax.value()))
	if prop.cbGridY.isChecked() and prop.cbGridX.isChecked():
		ax.grid()
		ax.tick_params(axis="both", which="major", direction="out", length=10, width=1, bottom=True, top=False,
		               left=True, right=False)
	elif prop.cbGridY.isChecked():
		ax.grid()
		ax.tick_params(axis="y", which="major", direction="out", length=10, width=1, bottom=True, top=False,
		               left=True, right=False)
	elif prop.cbGridX.isChecked():
		ax.grid()
		ax.tick_params(axis="x", which="major", direction="out", length=10, width=1, bottom=True, top=False,
		               left=True, right=False)


def addLineToPlot(fig, ax, line, label, bLegend=False, ax2=None, polyCollAndQuiver=False):
	if label == 'Current Time':
		ylim = ax.get_ylim()
		line.set_ydata(ylim)
		ax.set_ylim(ylim)
	if type(line) is matplotlib.lines.Line2D:
		a, = ax.plot(line.get_data()[0], line.get_data()[1], label=label)
		applyMatplotLibArtist(a, line)
	elif isinstance(line, matplotlib.patches.Polygon):
		xy = line.get_xy()
		poly = Polygon(xy, facecolor='0.9', edgecolor='0.5', label=label)
		ax.add_patch(poly)
	elif type(line) is PolyCollection:
		xy = line.get_paths()
		x = [x.vertices[:,0] for x in xy]
		y = [x.vertices[:,1] for x in xy]
		if not x or not y:
			xy = []
		else:
			xy = np.dstack((x, y))
		values = line.get_array()
		lab = re.sub(r'(\s-\sloc\s\d)?\s\[curtain]', '', label, flags=re.IGNORECASE)
		colSpec = dict(cmap=line.cmap, clim=line.get_clim(), norm=line.norm)
		polyCol = PolyCollection(xy, array=values, edgecolor='face', label=lab, **colSpec)
		ax.add_collection(polyCol, autolim=True)
		if bLegend:
			cax = addColourBarAxes(fig, ax, ax2, False)
			colbar = ColourBar(line, cax)
			colbar.ax.set_xlabel(lab)
			colbar.ax.get_xaxis().set_visible(True)
			reSpecPlot(fig, ax, ax2, colbar.ax, False)
	elif type(line) is Quiver:
		x = line.X
		y = line.Y
		u = line.U
		v = line.V
		config = {
			'scale': line.scale,
			'scale_units': line.scale_units,
			'width': line.width,
			'headwidth': line.headwidth,
			'headlength': line.headlength,
		}
		qv = Quiver(ax, x, y, u, v, **config)
		ax.add_collection(qv, autolim=True)
		lab = re.sub(r' \[curtain]', '', label, flags=re.IGNORECASE)
		addQuiverKey(fig, ax, ax2, polyCollAndQuiver, qv, 'Vector', config['scale'])


def isSecondaryNeeded(neededLabels, allLabels, allAxis):
	if 'axis 1' in allAxis and 'axis 2' in allAxis:
		axis1 = None
		axis2 = None
		for i, label in enumerate(allLabels):
			if label in neededLabels:
				axis = allAxis[i]
				if axis == 'axis 1':
					axis1 = True
					if axis2:
						return True
				elif axis == 'axis 2':
					axis2 = True
					if axis1:
						return True
	
	return False


def isCollectionAndQuiver(lines):
	tps = [type(x) for x in lines]
	return PolyCollection in tps and Quiver in tps


def createText(text, result, scalar, vector, time, outfile, project, number):
	"""
	Update dynamic text to actual text

	:param text: str text to be updated
	:param result: str result name
	:param scalar: str scalar name
	:param vector: str vector name
	:param time: str timestep
	:param outfile: str output file
	:param project: QgsProject
	:param number: int
	:return: str new text after update
	"""
	
	newText = text
	
	# numbering
	newText = newText.replace('<<X>>', str(number))
	# result name
	newText = newText.replace('<<result_name>>', result)
	# result type
	result_type = scalar if scalar != '-None-' else ''
	if not vector:
		vector = '-None-'
	result_type = '{0}, {1}'.format(result_type, vector) if vector != '-None-' else result_type
	newText = newText.replace('<<result_type>>', result_type)
	# time
	newText = newText.replace('<<result_time>>', time)
	# date
	date = '{0:%d}/{0:%m}/{0:%Y}'.format(datetime.now())
	newText = newText.replace('<<date>>', date)
	loc = project.absoluteFilePath()
	newText = newText.replace('<<workspace>>', loc)
	
	return newText


def transformMapCoordToLayout(layout, extent, point, margin):
	# if extent.contains(point):
	# layoutWidth = layout.layoutBounds().width()
	# layoutHeight = layout.layoutBounds().height()
	if margin is None:
		margin = (0, 0, 0, 0)
	layoutWidth = layout.width()
	layoutHeight = layout.height()
	extentWidth = extent.width()
	extentHeight = extent.height()
	xRatio = layoutWidth / extentWidth
	yRatio = layoutHeight / extentHeight
	
	upperLeftExtentX = extent.xMinimum()
	upperLeftExtentY = extent.yMaximum()
	
	distanceX = point.x() - upperLeftExtentX
	distanceY = upperLeftExtentY - point.y()
	
	# layout_map = layout.referenceMap()
	# pos = layout_map.pagePositionWithUnits()
	# xpos = pos.x()
	# ypos = pos.y()
	
	layoutX = distanceX * xRatio
	layoutY = distanceY * yRatio
	
	return QPointF(layoutX + margin[0], layoutY + margin[2])
	
			
def composition_set_plots(dialog, cfg, time, layout, dir, layout_type, showCurrentTime, retainFlow):

	from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot import TuPlot

	qv = Qgis.QGIS_VERSION_INT

	layoutcfg = cfg['layout']
	l = cfg['layer']
	margin = cfg['page margin'] if 'page margin' in cfg else None

	# update tuplot with new time and if time series, show current time - but don't draw
	rendered = cfg['rendered'] if 'rendered' in cfg else True
	dialog.tuView.tuPlot.updateCurrentPlot(TuPlot.TimeSeries, draw=False, time=time,
	                                       show_current_time=showCurrentTime, mesh_rendered=rendered,
	                                       plot_active_scalar=cfg['active scalar'])
	dialog.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection, draw=False, time=time, mesh_rendered=rendered,
	                                       plot_active_scalar=cfg['active scalar'])
	dialog.tuView.tuPlot.updateCurrentPlot(TuPlot.VerticalProfile, draw=False, time=time, mesh_rendered=rendered,
	                                       plot_active_scalar=cfg['active scalar'])
	
	# split out lines into specified plots
	for plot in sorted(layoutcfg['plots']):
		ptype = layoutcfg['plots'][plot]['type']
		position = layoutcfg['plots'][plot]['position']
		positionDict = {'Top-Left': CFItemPosition.TOP_LEFT, 'Top-Right': CFItemPosition.TOP_RIGHT,
		                'Bottom-Left': CFItemPosition.BOTTOM_LEFT, 'Bottom-Right': CFItemPosition.BOTTOM_RIGHT}
		if type(position) is str:
			positionConverted = positionDict[position]
		else:
			positionConverted = position
		properties = layoutcfg['plots'][plot]['properties']
		# isdatetime = dialog.tuView.tuOptions.xAxisDates
		isdatetime = properties.datetime
		dateformat = dialog.tuView.tuOptions.dateFormat
		labels = layoutcfg['plots'][plot]['labels'][:]
		
		# deal with active scalar stuff
		if 'active scalar' in cfg:
			i = None
			label = None
			if 'Active Dataset' in labels :
				i = labels.index('Active Dataset')
				label = cfg['active scalar']
			if 'Active Dataset [Water Level for Depth]' in labels:
				i = labels.index('Active Dataset [Water Level for Depth]')
				if cfg['active scalar'] == 'Depth':
					label = 'Water Level'
				elif cfg['active scalar'] == 'D':
					label = 'H'
				else:
					label = cfg['active scalar']
			if i is not None:
				if label not in labels:
					labels[i] = label
				else:
					labels.pop(i)

		if layout_type == 'default':
			cPlot = QgsLayoutItemPicture(layout)
			cPlot.setId('plot_{0}'.format(plot))
			layout.addItem(cPlot)
			cPlot.attemptResize(QgsLayoutSize(properties.sbFigSizeX.value(), properties.sbFigSizeY.value()))
		elif layout_type == 'template':
			cPlot = findLayoutItem(layout, 'plot_{0}'.format(plot))
		else:
			return

		fig, ax = plt.subplots()
		ax2 = None
		lines, labs, axis = dialog.plotItems(ptype, include_duplicates=True)
		y2 = isSecondaryNeeded(labels, labs, axis)
		if y2:
			if ptype == 'Vert Profile':
				ax2 = ax.twiny()
			else:
				ax2 = ax.twinx()
		setPlotProperties(fig, ax, properties, ax2, layout_type, cPlot, isdatetime, dateformat, layoutcfg['plots'][plot]['type'])
		for i, line in enumerate(lines):
			lab = TuResults.stripMaximumName(labs[i])
			lab = TuResults.stripMinimumName(lab)
			# if labs[i] in labels or labs[i] == 'Current Time':
			if lab in labels or labs[i] == 'Current Time':
				if y2 and axis[i] == 'axis 2':
					addLineToPlot(fig, ax2, line, lab, properties.cbLegend.isChecked(), None)
				else:
					addLineToPlot(fig, ax, line, lab, properties.cbLegend.isChecked(), ax2, isCollectionAndQuiver(lines))
		if properties.cbLegend.isChecked():
			#legend(ax, properties.cboLegendPos.currentIndex())
			ct = [PolyCollection, Quiver]  # curtain types
			blegend = [True for x in lines if type(x) not in ct]
			if blegend:
				addLegend(fig, ax, ax2, properties.cboLegendPos.currentIndex())
		fig.tight_layout()
		datetimestr = '{0}'.format(datetime.now()).replace(':', '-')
		if qv < 31600:
			fname = os.path.join('{0}'.format(cfg['tmpdir']), '{0}-{1}-{2}-{3}.svg'.format(l.name(), plot, time, datetimestr))
		else:
			fname = os.path.join('{0}'.format(cfg['tmpdir']), '{0}-{1}-{2}.svg'.format(l.name(), plot, datetimestr))
		fig.savefig(fname)
		layoutcfg['plots'][plot]['source'] = fname
		
		if cPlot:
			cPlot.setPicturePath(fname)
			if layout_type == 'default':
				set_item_pos(cPlot, positionConverted, layout, margin, buffer=2)


def prepare_composition_from_template(layout, cfg, time, dialog, dir, showCurrentTime, retainFlow, layers=None,
                                      tuResults=None, meshLayer=None):

	layoutcfg = cfg['layout']
	template_path = layoutcfg['file']
	document = QDomDocument()
	with open(template_path) as f:
		document.setContent(f.read())
	context = QgsReadWriteContext()
	context.setPathResolver(QgsProject.instance().pathResolver())
	context.setProjectTranslator(QgsProject.instance())
	layout.readLayoutXml(document.documentElement(), document, context)
	layout_map = layout.referenceMap()
	if layers is not None:
		layout_map.setLayers(layers)

	# check for 3D map
	layout_3d = None
	for n in range(layout.itemsModel().rowCount()):
		for m in range(layout.itemsModel().columnCount()):
			layoutItem = layout.itemsModel().itemFromIndex(layout.itemsModel().index(n, m))
			if layoutItem is not None:
				if layoutItem.displayName() == '3D Map 1':
					layout_3d = layoutItem
					break
		if layout_3d is not None:
			break

	# setTemporalRange(tuResults, layout_map, time, meshLayer)
	setTemporalRange(tuResults, layout, time, meshLayer, layout_3d)

	composition_set_time(layout, cfg['time text'])
	if 'plots' in layoutcfg:
		composition_set_plots(dialog, cfg, time, layout, dir, 'template', showCurrentTime, retainFlow)
	if 'graphics' in layoutcfg:
		margin = cfg['page margin'] if 'page margin' in cfg else None
		composition_set_graphics_from_template(layout, layoutcfg, layout_map, margin)
	cText = composition_set_dynamic_text(dialog, cfg, layout)
	if cText is not None:
		fix_label_box_size(layout, cText, layoutcfg)
	#fix_legend(dialog, cfg, layout)
	
	
def composition_set_graphics_from_template(layout, layoutcfg, layout_map, margin):
	for graphic in layoutcfg['graphics']:
		id = layoutcfg['graphics'][graphic]['id']
		label = layoutcfg['graphics'][graphic]['user label']
		position = layoutcfg['graphics'][graphic]['position']
		gtype = layoutcfg['graphics'][graphic]['type']
		
		# graphic
		if gtype == 'rubberband profile' or gtype == 'rubberband flow' or gtype == 'curtain':
			geom = graphic.asGeometry().asPolyline()
			layoutGeom = [transformMapCoordToLayout(layout_map.rectWithFrame(), layout_map.extent(), x, margin) for x in
			              geom]
		else:
			layoutGeom = [transformMapCoordToLayout(layout_map.rectWithFrame(), layout_map.extent(),
			                                        QgsPointXY(graphic), margin)] * 2
		
		oldItem = findLayoutGraphic(layout, id)
		if oldItem is not None:
			symbol = oldItem.symbol().clone()
			layout.removeItem(oldItem)
			qpolygonf = QPolygonF(layoutGeom)
			polylineGraphic = QgsLayoutItemPolyline(qpolygonf, layout)
			polylineGraphic.setId(id)
			polylineGraphic.setSymbol(symbol)
			layout.addItem(polylineGraphic)
			
			# label
			if label:
				if position.lower() == 'right':
					layoutPosX = max([x.x() for x in layoutGeom])
					ind = [x.x() for x in layoutGeom].index(layoutPosX)
					layoutPosY = layoutGeom[ind].y()
					offset = 3
					pos = (layoutPosX + offset, layoutPosY)
					anchor = QgsLayoutItem.MiddleLeft
				elif position.lower() == 'left':
					layoutPosX = min([x.x() for x in layoutGeom])
					ind = [x.x() for x in layoutGeom].index(layoutPosX)
					layoutPosY = layoutGeom[ind].y()
					offset = 3
					pos = (layoutPosX - offset, layoutPosY)
					anchor = QgsLayoutItem.MiddleRight
				elif position.lower() == 'above':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 3
					pos = (layoutPosX, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerMiddle
				elif position.lower() == 'below':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 3
					pos = (layoutPosX, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperMiddle
				elif position.lower() == 'above-left':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX - offset, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerRight
				elif position.lower() == 'above-right':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX + offset, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerLeft
				elif position.lower() == 'below-left':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX - offset, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperRight
				elif position.lower() == 'below-right':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX + offset, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperLeft
				else:
					return
				
				graphicLabel = findLayoutLabel(layout, id)
				if graphicLabel is not None:
					graphicLabel.attemptMove(QgsLayoutPoint(pos[0], pos[1]))


def fix_legend(dialog, cfg, layout):

	layoutcfg = cfg['layout']
	legend = None
	for i in layout.items():
		if isinstance(i, QgsLayoutItemLegend) and i.id() == "legend":
			legend = i
			break
	if legend is not None:
		model = legend.model()
		if cfg['map number'] == 0:
			if not legend.autoUpdateModel():
				for i in range(model.rowCount()):
					layers = model.index2node(model.index(i, 0)).checkedLayers()
					if len(layers) == 1:
						layer = layers[0]
						if type(layer) is QgsMeshLayer:
							if 'legend' not in layoutcfg:
								layoutcfg['legend'] = {}
							layoutcfg['legend']['name'] = model.index2node(model.index(i, 0)).name()
							layoutcfg['legend']['subname'] = model.layerOriginalLegendNodes(model.index2node(model.index(0, 0)))[0].data(QT_ITEM_DATA_DISPLAY_ROLE)
							layoutcfg['legend']['different name'] = layer.name() != layoutcfg['legend']['name']
							layoutcfg['legend']['needs to be updated'] = True
							nodes = []
							for node in model.layerOriginalLegendNodes(model.index2node(model.index(0, 0))):
								node.setUserLabel('hello world')
							model.index2node(model.index(i, 0)).setName('hello world')
							legend.refresh()

		else:
			if 'legend' in layoutcfg:
				if 'needs to be updated' in layoutcfg['legend']:
					legend.setAutoUpdateModel(True)
					fix_legend_box_size(cfg, legend)
					for i in range(model.rowCount()):
						layers = model.index2node(model.index(i, 0)).checkedLayers()
						if len(layers) == 1:
							layer = layers[0]
							if type(layer) is QgsMeshLayer:
								if layoutcfg['legend']['different name']:
									model.index2node(model.index(i, 0)).setName(layoutcfg['legend']['name'])
								if model.layerOriginalLegendNodes(model.index2node(model.index(0, 0))):
									model.layerOriginalLegendNodes(model.index2node(model.index(0, 0)))[0].setData(layoutcfg['legend']['subname'], QT_ITEM_DATA_DISPLAY_ROLE)
			
	
	
def composition_set_dynamic_text(dialog, cfg, layout):
	layoutcfg = cfg['layout']
	layer = cfg['layer']
	if 'title' in layoutcfg:
		if 'map number' in cfg:
			i = cfg['map number']
			path = cfg['imgfile']
			text = dialog.labelInput.toPlainText()
			result = layer.name()
			scalar = dialog.tableMaps.item(i, 1).text()
			vector = dialog.tableMaps.item(i, 2).text()
			time = dialog.tableMaps.item(i, 3).text()
			label = createText(text, result, scalar, vector, time, path, dialog.project, i + 1)
			cText = composition_set_title(layout, label)
			return cText
	return None

	
def _page_size(layout, margin):
	""" returns QgsLayoutSize """
	main_page = layout.pageCollection().page(0)
	if margin is None:
		margin = (0, 0, 0, 0)
	width = main_page.pageSize().width() - margin[0] - margin[1]
	height = main_page.pageSize().height() - margin[2] - margin[3]
	return QgsLayoutSize(width, height)


def animation(cfg, iface, progress_fn=None, dialog=None, preview=False):
	# get version
	qv = Qgis.QGIS_VERSION_INT

	margin = cfg['page margin'] if 'page margin' in cfg else (0, 0, 0, 0)
	dpi = 96
	cfg["dpi"] = dpi
	l = cfg['layer']
	n = cfg['name']
	w, h = cfg['img_size']
	imgfile = cfg['tmp_imgfile']
	layers = cfg['layers'] if 'layers' in cfg else [l.id()]
	extent = cfg['extent'] if 'extent' in cfg else l.extent()
	crs = cfg['crs'] if 'crs' in cfg else None
	tuResults = cfg['turesults']
	dataset_group_index = cfg['scalar index']
	# assert (dataset_group_index is not None)
	# count = l.dataProvider().datasetCount(dataset_group_index)
	timesteps = cfg['timesteps']
	count = len(timesteps)
	# assert (count > 2)
	nc_grid = cfg['nc_grid']

	time_from, time_to = cfg['time']

	# store original values
	if not nc_grid and l:
		original_rs = l.rendererSettings()

	# render selected mesh layer and turn off others
	dialog.tuView.tuResults.tuResults2D.renderMap(turn_off=True)

	# animate
	imgnum = 0
	#for i in range(count):
	for i, time in enumerate(timesteps):

		if progress_fn:
			progress_fn(i, count)
		#time = l.dataProvider().datasetMetadata(QgsMeshDatasetIndex(dataset_group_index, i)).time()
		#if tuResults.tuResults2D.getReferenceTime(l) != \
		#		datetime2timespec(tuResults.tuView.tuOptions.zeroTime,
		#		                  tuResults.loadedTimeSpec,
		#		                  tuResults.timeSpec):
		#	# dt = self.getReferenceTime(layer) - self.tuView.tuOptions.zeroTime
		#	if tuResults.tuView.tuOptions.timeUnits == 's':
		#		factor = 60. * 60.
		#	else:  # 'h'
		#		factor = 1.
		#	# t += dt.total_seconds() / factor
		#	time /= factor

		#	time += (tuResults.tuResults2D.getReferenceTime(l)
		#	      - datetime2timespec(tuResults.tuView.tuOptions.zeroTime,
		#	                          tuResults.loadedTimeSpec,
		#	                          tuResults.timeSpec)).total_seconds() / 60. / 60.
		if time < time_from or time > time_to:
			continue
		if qv < 31600:
			timetext = convertTimeToFormattedTime(time, unit=dialog.tuView.tuOptions.timeUnits)
			if dialog is not None:
				if dialog.tuView.tuOptions.xAxisDates:
					# if time in dialog.tuView.tuResults.time2date:
					if time in dialog.tuView.tuResults.time2date_tspec:
						# timetext = dialog.tuView.tuResults.time2date[time]
						timetext = dialog.tuView.tuResults.time2date_tspec[time]
						timetext = dialog.tuView.tuResults._dateFormat.format(timetext)
		else:
			if 'layout' in cfg and 'time' in cfg['layout'] and 'format' in cfg['layout']['time'] and cfg['layout']['time']['format']:
				if dialog.tuView.tuOptions.xAxisDates:
					timetext = time.strftime(cfg['layout']['time']['format'])
				else:
					hrs = (time - cfg['reference_time']).total_seconds() / 60. / 60.
					t = datetime(2000, 1, 1) + timedelta(hours=hrs)
					if '%d' in cfg['layout']['time']['format']:
						days = hrs // 24
						fmt = cfg['layout']['time']['format'].replace('%d', '{:d}'.format(int(days)))
						timetext = t.strftime(fmt)
					else:
						timetext = t.strftime(cfg['layout']['time']['format'])
				if '%f' in cfg['layout']['time']['format']:
					timetext = timetext[:-4]
			else:
				if dialog.tuView.tuOptions.xAxisDates:
					timetext = dialog.tuView.tuResults._dateFormat.format(time)
				else:
					hrs = (time - cfg['reference_time']).total_seconds() / 60. / 60.
					timetext = convertTimeToFormattedTime(hrs, unit='h')
		cfg['time text'] = timetext


		# Set to render next timesteps
		if not nc_grid and l:
			rs = l.rendererSettings()
			asd = cfg['scalar index']
			if qv < 31300:
				asd = QgsMeshDatasetIndex(asd, i)
			#rs.setActiveScalarDataset(QgsMeshDatasetIndex(asd, i))
			avd = cfg['vector index']
			if qv < 31300:
				avd = QgsMeshDatasetIndex(avd, i)
			#rs.setActiveVectorDataset(QgsMeshDatasetIndex(avd, i))

			# new api for 3.14
			#if qv < 31600:
			setActiveScalar, setActiveVector = TuResults2D.meshRenderVersion(rs)
			setActiveScalar(asd)
			setActiveVector(avd)
			l.setRendererSettings(rs)

		# particles
		ptms = cfg['particles']
		#if ptm_res:
		for ptm_res in ptms:
			if ptm_res[1] in layers:
				dialog.tuView.tuResults.tuResultsParticles.updateActiveTime(time)
				break

		# Prepare layout
		layout = QgsPrintLayout(QgsProject.instance())
		layout.initializeDefaults()
		layout.setName('coastalme')

		layoutcfg = cfg['layout']
		if layoutcfg['type'] == 'file':
			prepare_composition_from_template(layout, cfg, time, dialog, os.path.dirname(imgfile), True, True,
			                                  tuResults=tuResults, meshLayer=l)
			# when using composition from template, match video's aspect ratio to paper size
			# by updating video's width (keeping the height)
			aspect = _page_size(layout, margin).width() / _page_size(layout, margin).height()
			w = int(round(aspect * h))
		else:  # type == 'default'
			layout.renderContext().setDpi(dpi)
			layout.setUnits(QgsUnitTypes.LayoutMillimeters)
			main_page = layout.pageCollection().page(0)
			main_page.setPageSize(QgsLayoutSize(w * 25.4 / dpi, h * 25.4 / dpi, QgsUnitTypes.LayoutMillimeters))
			prepare_composition(layout, time, cfg, layoutcfg, extent, layers, crs, os.path.dirname(imgfile), dialog,
			                    tuResults=tuResults, meshLayer=l)

		imgnum += 1
		fname = imgfile % imgnum
		layout_exporter = QgsLayoutExporter(layout)
		image_export_settings = QgsLayoutExporter.ImageExportSettings()
		image_export_settings.dpi = dpi
		image_export_settings.imageSize = QSize(w, h)
		res = layout_exporter.exportToImage(os.path.abspath(fname), image_export_settings)
		if res != QgsLayoutExporter.Success:
			raise RuntimeError()
		
		if preview:
			return layout

	if progress_fn:
		progress_fn(count, count)

	# restore original settings
	if not nc_grid and l:
		l.setRendererSettings(original_rs)


def set_composer_item_label(item, itemcfg):
	item.setBackgroundEnabled(itemcfg['background'])
	item.setBackgroundColor(itemcfg['background color'])
	item.setFont(itemcfg['font'])
	item.setFontColor(itemcfg['font colour'])
	item.setFrameEnabled(itemcfg['frame'])
	item.setFrameStrokeColor(itemcfg['frame color'])


class CFItemPosition:
	TOP_LEFT = 0
	TOP_RIGHT = 1
	BOTTOM_LEFT = 2
	BOTTOM_RIGHT = 3
	TOP_CENTER = 4
	BOTTOM_CENTER = 5

def set_item_pos(item, posindex, layout, margin, buffer=0):
	if margin is None:
		margin = (0, 0, 0, 0)
	page_size = _page_size(layout, margin)
	r = item.sizeWithUnits()
	assert (r.units() == QgsUnitTypes.LayoutMillimeters)
	assert (page_size.units() == QgsUnitTypes.LayoutMillimeters)

	if posindex == CFItemPosition.TOP_CENTER: # top-center
		item.attemptMove(QgsLayoutPoint((page_size.width() - r.width()) / 2 + margin[0], margin[2] + buffer, QgsUnitTypes.LayoutMillimeters))
	elif posindex == CFItemPosition.BOTTOM_CENTER:
		item.attemptMove(QgsLayoutPoint((page_size.width() - r.width()) / 2 + margin[0], page_size.height() - r.height() + margin[3] - buffer, QgsUnitTypes.LayoutMillimeters))
	elif posindex == CFItemPosition.TOP_LEFT:  # top-left
		item.attemptMove(QgsLayoutPoint(margin[0] + buffer, margin[2] + buffer))
	elif posindex == CFItemPosition.TOP_RIGHT:  # top-right
		item.attemptMove(QgsLayoutPoint(page_size.width() - r.width() + margin[0] - buffer, margin[2] + buffer, QgsUnitTypes.LayoutMillimeters))
	elif posindex == CFItemPosition.BOTTOM_LEFT:  # bottom-left
		item.attemptMove(QgsLayoutPoint(margin[0] + buffer, page_size.height() - r.height() + margin[2] - buffer, QgsUnitTypes.LayoutMillimeters))
	else: # bottom-right
		item.attemptMove(QgsLayoutPoint(page_size.width() - r.width() + margin[0] - buffer, page_size.height() - r.height() + margin[2] - buffer, QgsUnitTypes.LayoutMillimeters))
		
def fix_legend_box_size(cfg, legend):
	# adjustBoxSize() does not work without
	# call of the paint() function
	w, h = cfg['img_size']
	dpi = cfg['dpi']
	image = QImage(int(w), int(h), QT_IMAGE_FORMAT_ARGB32)
	image.setDevicePixelRatio(int(dpi))
	p = QPainter(image)
	s = QStyleOptionGraphicsItem()
	legend.paint(p, s, None)
	p.end()
	# Now we can adjust box size
	legend.adjustBoxSize()
	
	
def fix_label_box_size(layout, cTitle, layoutcfg):
	# adjustSizeToText does not work with
	# return characters as it treats the
	# text as one long string
	text = cTitle.text()
	s = text.split('\n')
	w, h = 0, 0
	for i in s:
		if i:
			label = QgsLayoutItemLabel(layout)
			label.setText(i)
			set_composer_item_label(label, layoutcfg['title'])
			size = label.sizeForText()
			w = max(w, size.width() + cTitle.marginY()*2)
			h += size.height()
	h += cTitle.marginX() * 2
	if cTitle.sizeWithUnits().width() > w:
		w = cTitle.sizeWithUnits().width()
	if cTitle.sizeWithUnits().height() > h:
		h = cTitle.sizeWithUnits().height()
	cTitle.attemptResize(QgsLayoutSize(w, h))
		
	
def legend(ax, position):
	# get legend labels and artists
	uniqueNames, uniqueNames2, uniqueLines, uniqueLines2 = [], [], [], []
	line, lab = ax.get_legend_handles_labels()
	# remove duplicates i.e. culvert and pipes only need to appear in legend once
	uniqueNames = []
	uniqueLines = []
	for i, l in enumerate(lab):
		if l not in uniqueNames:
			uniqueNames.append(l)
			uniqueLines.append(line[i])
		if len(ax.get_shared_x_axes().get_siblings(ax)) < 2:
			ax2 = ax.get_shared_x_axes().get_siblings(ax)[0]
		line2, lab2 = ax2.get_legend_handles_labels()
		# remove duplicates i.e. culvert and pipes only need to appear in legend once
		uniqueNames2 = []
		uniqueLines2 = []
		for i, l in enumerate(lab2):
			if l not in uniqueNames:
				uniqueNames2.append(l)
				uniqueLines2.append(line2[i])
	lines = uniqueLines + uniqueLines2
	lab = uniqueNames + uniqueNames2
	ax.legend(lines, lab, loc=position)


def createDefaultSymbol(gtype):
	if gtype == 'rubberband profile':
		color = '255, 0, 0'
		symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
	elif gtype == 'rubberband flow':
		color = '0, 0, 255'
		symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
	elif gtype == 'curtain':
		color = '0, 255, 0'
		symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
	elif gtype == 'marker':
		color = '255, 0, 0'
		symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.LineGeometry)
	layer_style = {}
	layer_style['color'] = color
	layer_style['outline'] = '#000000'
	symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)
	symbol_layer = QgsSimpleLineSymbolLayer.create(layer_style)
	symbol_layer.setWidth(1)
	symbol_layer2 = QgsMarkerLineSymbolLayer.create({'placement': 'vertex'})
	layer_style['color_border'] = color
	markerSymbol = QgsSimpleMarkerSymbolLayer.create(layer_style)
	if gtype == 'rubberband profile' or gtype == 'rubberband flow':
		markerSymbol.setShape(QgsSimpleMarkerSymbolLayerBase.Square)
		markerSymbol.setFillColor(QColor(0, 0, 0, 0))
	else:
		markerSymbol.setShape(QgsSimpleMarkerSymbolLayerBase.Circle)
	markerSymbol.setSize(3)
	marker = QgsMarkerSymbol()
	marker.changeSymbolLayer(0, markerSymbol)
	symbol_layer2.setSubSymbol(marker)
	if symbol_layer is not None:
		symbol.changeSymbolLayer(0, symbol_layer)
		if symbol_layer2 is not None:
			symbol.appendSymbolLayer(symbol_layer2)
			
	return symbol



def setTemporalRange(tuResults, layout, time, meshLayer, layout3d=None):
	qv = Qgis.QGIS_VERSION_INT
	if time != -99999. and time != 99999.:
		if qv >= 31300:
			if tuResults is not None:
				if meshLayer is None:
					timeSpec = None
				else:
					if isinstance(meshLayer, QgsMeshLayer):
						timeSpec = meshLayer.temporalProperties().referenceTime().timeSpec()
					else:
						timeSpec = 1
			# 	if layout_map is not None:
			# 		layout_map.setIsTemporal(True)
			# 		tuResults.updateQgsTime(qgsObject=layout_map, time=time, timeSpec=timeSpec)
				# if layout3d is not None:
				# 	layout3d.setIsTemporal(True)
				# 	tuResults.updateQgsTime(qgsObject=layout3d, time=time, timeSpec=timeSpec)
			for n in range(layout.itemsModel().rowCount()):
				for m in range(layout.itemsModel().columnCount()):
					layoutItem = layout.itemsModel().itemFromIndex(layout.itemsModel().index(n, m))
					if layoutItem is not None and isinstance(layoutItem, QgsLayoutItemMap):
						layoutItem.setIsTemporal(True)
						tuResults.updateQgsTime(qgsObject=layoutItem, time=time, timeSpec=timeSpec)
						if isinstance(meshLayer, NetCDFGrid):
							meshLayer.update_band_from_time(layoutItem.temporalRange())


def prepare_composition(layout, time, cfg, layoutcfg, extent, layers, crs, dir, dialog, show_current_time=True,
                        retainFlow=True, tuResults=None, meshLayer=None):
	margin = cfg['page margin'] if 'page margin' in cfg else None
	layout_map = QgsLayoutItemMap(layout)
	layout_map.attemptResize(_page_size(layout, margin))
	set_item_pos(layout_map, CFItemPosition.TOP_LEFT, layout, margin)
	layout_map.setLayers(layers)
	if crs is not None:
		layout_map.setCrs(crs)
	layout_map.setExtent(extent)
	debug = layout_map.extent()
	layout_map.refresh()
	layout.setReferenceMap(layout_map)
	layout.addLayoutItem(layout_map)
	layout_map.attemptResize(_page_size(layout, margin))

	# setTemporalRange(tuResults, layout_map, time, meshLayer)
	setTemporalRange(tuResults, layout, time, meshLayer)

	if 'frame' in cfg:
		layout_map.setFrameEnabled(cfg['frame'])
		layout_map.setFrameStrokeColor(cfg['frame color'])
		layout_map.setFrameStrokeWidth(QgsLayoutMeasurement(cfg['frame thickness']))
	#actualExtent = calculateLayoutExtent(layout, layout_map.extent())
	actualExtent = debug

	if 'title' in layoutcfg:
		cTitle = QgsLayoutItemLabel(layout)
		cTitle.setId('title')
		layout.addLayoutItem(cTitle)

		set_composer_item_label(cTitle, layoutcfg['title'])
		cTitle.setText(layoutcfg['title']['label'])
		cTitle.setHAlign(QT_ALIGN_LEFT)
		cTitle.setVAlign(QT_ALIGN_TOP)
		fix_label_box_size(layout, cTitle, layoutcfg)
		set_item_pos(cTitle, layoutcfg['title']['position'], layout, margin)

	if 'time' in layoutcfg:
		cTime = QgsLayoutItemLabel(layout)
		cTime.setId('time')
		layout.addLayoutItem(cTime)

		set_composer_item_label(cTime, layoutcfg['time'])
		composition_set_time(layout, cfg['time text'])
		cTime.adjustSizeToText()
		set_item_pos(cTime, layoutcfg['time']['position'], layout, margin)

	if 'legend' in layoutcfg:
		cLegend = QgsLayoutItemLegend(layout)
		cLegend.setId('legend')
		cLegend.setLinkedMap(layout_map)
		cLegend.setLegendFilterByMapEnabled(True)
		layout.addLayoutItem(cLegend)

		itemcfg = layoutcfg['legend']
		cLegend.setBackgroundEnabled(itemcfg['background'])
		cLegend.setBackgroundColor(itemcfg['background color'])
		cLegend.setFrameEnabled(itemcfg['frame'])
		cLegend.setFrameStrokeColor(itemcfg['frame color'])
		cLegend.setTitle(itemcfg['label'])
		for s in [QgsLegendStyle.Title,
				  QgsLegendStyle.Group,
				  QgsLegendStyle.Subgroup,
				  QgsLegendStyle.SymbolLabel]:
			cLegend.setStyleFont(s, itemcfg['font'])
		cLegend.setFontColor(itemcfg['font colour'])

		fix_legend_box_size(cfg, cLegend)
		#cLegend.adjustBoxSize()
		set_item_pos(cLegend, itemcfg['position'], layout, margin)
		
	if 'plots' in layoutcfg:
		composition_set_plots(dialog, cfg, time, layout, dir, 'default', show_current_time, retainFlow)
			
	if 'graphics' in layoutcfg:
		for graphic in layoutcfg['graphics']:
			id = layoutcfg['graphics'][graphic]['id']
			label = layoutcfg['graphics'][graphic]['user label']
			position = layoutcfg['graphics'][graphic]['position']
			gtype = layoutcfg['graphics'][graphic]['type']
			
			# graphic
			if gtype == 'rubberband profile' or gtype == 'rubberband flow' or gtype == 'curtain':
				geom = graphic.asGeometry().asPolyline()
				layoutGeom = [transformMapCoordToLayout(layout_map.rectWithFrame(), layout_map.extent(), x, margin) for x in geom]
			else:
				layoutGeom = [transformMapCoordToLayout(layout_map.rectWithFrame(), layout_map.extent(), QgsPointXY(graphic), margin)] * 2
			qpolygonf = QPolygonF(layoutGeom)
			polylineGraphic = QgsLayoutItemPolyline(qpolygonf, layout)
			polylineGraphic.setId(id)
			symbol = createDefaultSymbol(gtype)
			polylineGraphic.setSymbol(symbol)
			layout.addItem(polylineGraphic)
			
			# label
			if label:
				if position.lower() == 'right':
					layoutPosX = max([x.x() for x in layoutGeom])
					ind = [x.x() for x in layoutGeom].index(layoutPosX)
					layoutPosY = layoutGeom[ind].y()
					offset = 3
					pos = (layoutPosX + offset, layoutPosY)
					anchor = QgsLayoutItem.MiddleLeft
				elif position.lower() == 'left':
					layoutPosX = min([x.x() for x in layoutGeom])
					ind = [x.x() for x in layoutGeom].index(layoutPosX)
					layoutPosY = layoutGeom[ind].y()
					offset = 3
					pos = (layoutPosX - offset, layoutPosY)
					anchor = QgsLayoutItem.MiddleRight
				elif position.lower() == 'above':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 3
					pos = (layoutPosX, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerMiddle
				elif position.lower() == 'below':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 3
					pos = (layoutPosX, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperMiddle
				elif position.lower() == 'above-left':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX - offset, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerRight
				elif position.lower() == 'above-right':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX + offset, layoutPosY - offset)
					anchor = QgsLayoutItem.LowerLeft
				elif position.lower() == 'below-left':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX - offset, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperRight
				elif position.lower() == 'below-right':  # only available for points at the moment
					layoutPosX = layoutGeom[0].x()
					layoutPosY = layoutGeom[0].y()
					offset = 1.5
					pos = (layoutPosX + offset, layoutPosY + offset)
					anchor = QgsLayoutItem.UpperLeft
				else:
					return
				
				graphicLabel = QgsLayoutItemLabel(layout)
				graphicLabel.setId(id)
				layout.addLayoutItem(graphicLabel)
				
				graphicLabel.setText(label)
				graphicLabel.setHAlign(QT_ALIGN_CENTER)
				graphicLabel.setVAlign(QT_ALIGN_CENTER)
				set_composer_item_label(graphicLabel, layoutcfg['graphics'][graphic])
				graphicLabel.adjustSizeToText()
				graphicLabel.setReferencePoint(anchor)
				graphicLabel.attemptMove(QgsLayoutPoint(pos[0], pos[1]))
				
	if 'images' in layoutcfg:
		for i, image in enumerate(layoutcfg['images']):
			source = layoutcfg['images'][image]['source']
			properties = layoutcfg['images'][image]['properties']
			position = layoutcfg['images'][image]['position']
			positionDict = {'Top-Left': CFItemPosition.TOP_LEFT, 'Top-Right': CFItemPosition.TOP_RIGHT,
			                'Bottom-Left': CFItemPosition.BOTTOM_LEFT, 'Bottom-Right': CFItemPosition.BOTTOM_RIGHT}
			if type(position) is str:
				positionConverted = positionDict[position]
			else:
				positionConverted = position
			
			cImage = QgsLayoutItemPicture(layout)
			if properties.rbUseOriginalSize.isChecked():
				cImage.setResizeMode(QgsLayoutItemPicture.FrameToImageSize)
			else:
				if properties.cbKeepAspectRatio.isChecked():
					cImage.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)
				else:
					cImage.setResizeMode(QgsLayoutItemPicture.Stretch)
			cImage.setId('image_{0}'.format(i))
			layout.addItem(cImage)
			cImage.attemptResize(QgsLayoutSize(properties.sbSizeX.value(), properties.sbSizeY.value()))
			cImage.setPicturePath(source)
			set_item_pos(cImage, positionConverted, layout, margin, buffer=2)

	if 'scale bar' in layoutcfg:
		itemcfg = layoutcfg['scale bar']
		cScaleBar = QgsLayoutItemScaleBar(layout)
		cScaleBar.setLinkedMap(layout_map)
		cScaleBar.applyDefaultSize()
		cScaleBar.setStyle('Double Box')
		cScaleBar.setNumberOfSegments(3)
		cScaleBar.setNumberOfSegmentsLeft(0)
		cScaleBar.setFont(itemcfg['font'])
		cScaleBar.setFontColor(itemcfg['font color'])
		cScaleBar.setBackgroundEnabled(itemcfg['background'])
		cScaleBar.setBackgroundColor(itemcfg['background color'])
		cScaleBar.setFrameEnabled(itemcfg['frame'])
		cScaleBar.setFrameStrokeColor(itemcfg['frame color'])
		cScaleBar.setId('scale bar')
		layout.addItem(cScaleBar)
		set_item_pos(cScaleBar, itemcfg['position'], layout, margin, buffer=2)
		
	if 'north arrow' in layoutcfg:
		itemcfg = layoutcfg['north arrow']
		path = QgsApplication.defaultThemesFolder()
		path = path[:-19]
		path = os.path.join(path, 'svg', 'arrows', 'NorthArrow_02.svg')
		cNorthArrow = QgsLayoutItemPicture(layout)
		cNorthArrow.setId('north arrow')
		cNorthArrow.setSvgFillColor(QColor(QT_BLACK))
		cNorthArrow.setLinkedMap(layout_map)
		cNorthArrow.setBackgroundEnabled(itemcfg['background'])
		cNorthArrow.setBackgroundColor(itemcfg['background color'])
		cNorthArrow.setFrameEnabled(itemcfg['frame'])
		cNorthArrow.setFrameStrokeColor(itemcfg['frame color'])
		layout.addItem(cNorthArrow)
		cNorthArrow.setPicturePath(path)
		cNorthArrow.setResizeMode(QgsLayoutItemPicture.Stretch)
		cNorthArrow.attemptResize(QgsLayoutSize(7.5, 15))
		set_item_pos(cNorthArrow, itemcfg['position'], layout, margin, buffer=2)
		

def convert_fmt_to_re(name):
	pattern = re.compile(r'\%\d{1,2}d')
	fmt = pattern.findall(name)
	if len(fmt) != 1:
		raise Exception("Wildcards used more than once")
	f = fmt[0]
	d = f.strip('%d')
	mx = re.findall(r'[1-9]', d)[0]
	pad = '0' in d
	if pad:
		sub = r'\\d{' + mx + '}'
	else:
		sub = r'\\d{1,' + mx + '}'
	new_name = pattern.sub(sub, name)

	return  new_name


def count_images(img_dir):
	dir = os.path.dirname(img_dir)  # directory
	bname = os.path.basename(img_dir)  # basename
	new_name = convert_fmt_to_re(bname)  # basename but with regex pattern

	images = [os.path.join(dir, y) for y in [x for x in os.walk(dir)][0][2] if re.findall(new_name, y, flags=re.IGNORECASE)]
	return len(images)


def images_to_video(tmp_img_dir="/tmp/vid/%03d.png", output_file="/tmp/vid/test.avi", fps=10, qual=1,
					ffmpeg_bin="ffmpeg"):
	if qual == 0:  # lossless
		opts = ["-vcodec", "ffv1"]
	else:
		bitrate = 10000 if qual == 1 else 2000
		opts = ["-vcodec", "mpeg4", "-b", str(bitrate) + "K"]

	# if images do not start with 1: -start_number 14
	cmd = [ffmpeg_bin, "-f", "image2", "-framerate", str(fps), "-i", tmp_img_dir]
	cmd += opts
	cmd += ["-r", str(fps), "-f", "avi", "-y", output_file]

	f = tempfile.NamedTemporaryFile(prefix="coastalme", suffix=".txt")
	f.write(str.encode(" ".join(cmd) + "\n\n"))

	# stdin redirection is necessary in some cases on Windows
	res = subprocess.call(cmd, stdin=subprocess.PIPE, stdout=f, stderr=f)
	if res != 0:
		f.delete = False  # keep the file on error

	return res == 0, f.name


def images_to_video2(tmp_img_dir="/tmp/vid/%03d.png", output_file="/tmp/vid/test.avi", fps=10, qual=1,
                    ffmpeg_bin="ffmpeg", target_dur=15):

	t = count_images(tmp_img_dir) / target_dur  # input framerate (not output fps)

	if qual == 0:  # lossless
		opts = ["-vcodec", "ffv1"]
	else:
		bitrate = 10000 if qual == 1 else 2000
		opts = ["-vcodec", "mpeg4", "-b:v", str(bitrate) + "K"]

	cmd = [ffmpeg_bin, "-f", "image2", '-framerate', f'{t}']
	cmd.extend(['-t', f'{target_dur}', '-i', tmp_img_dir])
	cmd.extend(opts)
	cmd.extend(['-r', f'{fps}', '-y', output_file])

	res = subprocess.call(cmd, stdin=subprocess.PIPE)
	return res == 0, ""


def images_to_video_gif(tmp_img_dir="/tmp/vid/%03d.png", output_file="/tmp/vid/test.avi", fps=10, qual=1,
                        ffmpeg_bin="ffmpeg", target_dur=15):
	# get images
	dir = os.path.dirname(tmp_img_dir)
	s = re.sub(r"\%\d*d", r'\\d*', os.path.basename(tmp_img_dir))  # replace string format with regex pattern
	images = [os.path.join(dir, y) for y in [x for x in os.walk(dir)][0][2] if re.findall(s, y, flags=re.IGNORECASE)]
	images = sorted(images, key=lambda x: '{0:03d}'.format(
		int(os.path.splitext(re.findall(s, os.path.basename(x), flags=re.IGNORECASE)[0])[0])))
	nImages = len(images)

	#  duration each image is shown
	t = target_dur / nImages

	cmd = [ffmpeg_bin, "-f", "image2pipe"]
	for img in images:
		cmd.extend(['-framerate', f'{fps}', '-loop', '1', '-t', f'{t}', '-i', img])
	cmd.extend(
		["-filter_complex", f"concat=n={nImages}:v=1:a=0,split[v0][v1];[v0]palettegen[p];[v1][p]paletteuse[v]", "-map",
		 "[v]", '-r', f'{fps}', '-y', output_file])

	#f = tempfile.NamedTemporaryFile(prefix="coastalme", suffix=".txt")
	#f.write(str.encode(" ".join(cmd) + "\n\n"))

	## stdin redirection is necessary in some cases on Windows
	#res = subprocess.call(cmd, stdin=subprocess.PIPE, stdout=f, stderr=f)
	#if res != 0:
	#	f.delete = False  # keep the file on error

	#return res == 0, f.name
	res = subprocess.call(cmd, stdin=subprocess.PIPE)
	return res == 0, ''


class TuAnimationDialog(QDialog, Ui_AnimationDialog):
	
	INSERT_BEFORE = 0
	INSERT_AFTER = 1
	
	def __init__(self, TuView, **kwargs):
		QDialog.__init__(self)
		self.setupUi(self)
		self.tuView = TuView
		self.iface = TuView.iface
		self.project = TuView.project
		self.canvas = TuView.canvas
		self.pbDialogs = {}
		self.pbDialogsImage = {}
		self.dialog2Plot = {}
		self.rowNo2fntDialog = {}
		self.label2graphic = {}
		self.mapTableRows = []
		self.mapTableRowItems = []
		self.plotTableRows = []
		self.plotTableRowItems = []
		self.imageTableRows = []

		self.tablePlots.horizontalHeader().setStretchLastSection(True)
		self.tableGraphics.horizontalHeader().setStretchLastSection(True)
		self.tableImages.horizontalHeader().setStretchLastSection(True)
		self.tablePlots.horizontalHeader().setCascadingSectionResizes(True)
		self.tableGraphics.horizontalHeader().setCascadingSectionResizes(True)
		self.tableImages.horizontalHeader().setCascadingSectionResizes(True)
		self.tableImages.verticalHeader().setSectionResizeMode(QT_HEADER_VIEW_RESIZE_TO_CONTENT)
		self.tablePlots.verticalHeader().setSectionResizeMode(QT_HEADER_VIEW_RESIZE_TO_CONTENT)
		
		total_width = 0
		for i in range(self.tablePlots.columnCount()):
			total_width += self.tablePlots.columnWidth(i)
		self.tablePlots.setColumnWidth(0, int((total_width - 175) / 3.))
		self.tablePlots.setColumnWidth(1, 175)
		self.tablePlots.setColumnWidth(2, int((total_width - 175) / 3.))
		self.tablePlots.setColumnWidth(3, int((total_width - 175) / 3.))
		
		total_width = 0
		for i in range(self.tableGraphics.columnCount()):
			total_width += self.tableGraphics.columnWidth(i)
		self.tableGraphics.setColumnWidth(0, int((total_width - 175) / 3))
		self.tableGraphics.setColumnWidth(1, 175)
		self.tableGraphics.setColumnWidth(2, int((total_width - 175) / 3))
		self.tableGraphics.setColumnWidth(3, int((total_width - 175) / 3))
		
		total_width = 0
		for i in range(self.tableImages.columnCount()):
			total_width += self.tableImages.columnWidth(i)
		self.tableImages.setColumnWidth(0, 250)
		self.tableImages.setColumnWidth(1, int((total_width - 250.) / 2))
		self.tableImages.setColumnWidth(2, int((total_width - 250.) / 2))
		
		self.setPlotTableProperties()
		self.setImageTableProperties()
		self.tablePlots.itemChanged.connect(self.plotTypeChanged)
		self.contextMenuPlotTable()
		self.contextMenuImageTable()
		self.populateGeneralTab(load_project_settings=True)
		self.populateLayoutTab()
		self.populateVideoTab()
		
		self.cboResult.currentIndexChanged.connect(lambda: self.populateGeneralTab(ignore='results'))
		self.btnBrowseOutput.clicked.connect(lambda: self.browse('save', 'COASTALME/animation_outfolder', "MP4 (*.mp4 *.MP4);;AVI (*.avi *.AVI);;GIF (*.gif *.GIF)", self.editOutput))
		self.btnBrowseTemplate.clicked.connect(lambda: self.browse('load', "COASTALME/animation_template", "QGIS Print Layout (*.qpt)", self.editTemplate))
		self.btnBrowseFfmpegPath.clicked.connect(lambda: self.browse('ffmpeg', 'COASTALME/animation_ffmpeg', "FFmpeg (ffmpeg ffmpeg.exe avconv avconv.exe)", self.editFfmpegPath))
		self.btnAddPlot.clicked.connect(self.addPlot)
		self.btnRemovePlot.clicked.connect(self.removePlots)
		self.btnPlotUp.clicked.connect(lambda event: self.movePlot(event, 'up'))
		self.btnPlotDown.clicked.connect(lambda event: self.movePlot(event, 'down'))
		self.btnAddImage.clicked.connect(self.addImage)
		self.btnRemoveImage.clicked.connect(self.removeImages)
		self.btnImageUp.clicked.connect(lambda event: self.moveImage(event, 'up'))
		self.btnImageDown.clicked.connect(lambda event: self.moveImage(event, 'down'))
		self.pbPreview.clicked.connect(lambda: self.check(preview=True))
		self.buttonBox.accepted.connect(self.check)

		if self.tuView.iface is not None:
			self.layers = self.canvas.layers()
			self.extent = self.canvas.extent()
			self.crs = self.canvas.mapSettings().destinationCrs()
			self.mesh_rendered = True
		else:
			self.layers = []
			self.extent = None
			self.crs = None
			self.mesh_rendered = False
		self.pythonPopulateGui(**kwargs)

	def pythonPopulateGui(self, **kwargs):
		if 'start_time' in kwargs:
			self.cboStart.setCurrentText(kwargs['start_time'])
		if 'end_time' in kwargs:
			self.cboEnd.setCurrentText(kwargs['end_time'])
		if 'result' in kwargs:
			self.cboResult.setCurrentText(kwargs['result'])
		if 'active_scalar_result' in kwargs:
			self.cboScalar.setCurrentText(kwargs['active_scalar_result'])
		if 'active_vector_results' in kwargs:
			self.cboVector.setCurrentText(kwargs['active_vector_result'])
		if 'output' in kwargs:
			self.editOutput.setText(kwargs['output'])
		if 'speed' in kwargs:
			self.spinSpeed.setValue(kwargs['speed'])
		if 'target_duration' in  kwargs:
			self.sbTargetDur.setValue(kwargs['target_duration'])
		if 'layout' in kwargs:
			layout = kwargs['layout']
			if 'type' in layout:
				if layout['type'].lower() == 'default':
					self.radLayoutDefault.setChecked(True)
				elif layout['type'].lower() == 'custom':
					self.radLayoutCustom.setChecked(True)
			if 'properties' in layout:
				layout_properties = layout['properties']
				if 'plots' in layout_properties:
					plots = layout_properties['plots']
					self.groupPlot.setChecked(True)
					for i in range(len(plots)):
						self.addPlot()
						if 'plot_type' in plots[i]:
							self.tablePlots.item(i, 0).setText(plots[i]['plot_type'])
						if 'plot_items' in plots[i]:
							if type(plots[i]['plot_items']) is list:
								plot_items = ';;'.join(plots[i]['plot_items'])
							else:
								plot_items = plots[i]['plot_items']
							self.tablePlots.item(i, 1).setText(plot_items)
						if 'properties' in plots[i]:
							plot_prop = plots[i]['properties']
							p = self.pbDialogs[self.tablePlots.cellWidget(i, 3)]
							if 'legend' in plot_prop:
								p.cbLegend.setChecked(plot_prop['legend'])
				if 'template' in layout_properties:
					self.editTemplate.setText(layout_properties['template'])
		if 'quality' in kwargs:
			if kwargs['quality'].lower() == 'best':
				self.radQualBest.setChecked(True)
			elif kwargs['quality'].lower() == 'high':
				self.radQualHigh.setChecked(True)
			elif kwargs['quality'].lower() == 'low':
				self.radQualLow.setChecked(True)
		if 'ffmpeg' in kwargs:
			ffmpeg_properties = kwargs['ffmpeg']
			if 'type' in ffmpeg_properties:
				if ffmpeg_properties['type'].lower() == 'default':
					self.radFfmpegSystem.setChecked(True)
				elif ffmpeg_properties['type'].lower() == 'custom_path':
					self.radFfmpegCustom.setChecked(True)
			if 'path' in ffmpeg_properties:
				self.editFfmpegPath.setText(ffmpeg_properties['path'])
		if 'layers' in kwargs:
			self.layers = kwargs['layers']
		if 'extent' in kwargs:
			self.extent = kwargs['extent']
		if 'crs' in kwargs:
			self.crs = kwargs['crs']

	def populateGeneralTab(self, ignore=None, load_project_settings=False):
		"""
		Populates widgets in general tab.
		
		:return: void
		"""

		if ignore != 'results':
			self.populateResults()
		if ignore != 'times':
			self.populateTimes()
		if ignore != 'types':
			self.populateResultTypes()

		if load_project_settings:
			folderIcon = QgsApplication.getThemeIcon('\mActionFileOpen.svg')
			self.btnBrowseOutput.setIcon(folderIcon)
			# apply project settings
			if self.project.readEntry("COASTALME", 'start_time')[0]:
				for i in range(self.cboStart.count()):
					if self.cboStart.itemText(i) == self.project.readEntry("COASTALME", 'start_time')[0]:
						self.cboStart.setCurrentIndex(i)
						break
			if self.project.readEntry("COASTALME", 'end_time')[0]:
				for i in range(self.cboEnd.count()):
					if self.cboEnd.itemText(i) == self.project.readEntry("COASTALME", 'end_time')[0]:
						self.cboEnd.setCurrentIndex(i)
						break
			if self.project.readEntry("COASTALME", 'result_name')[0]:
				for i in range(self.cboResult.count()):
					if self.cboResult.itemText(i) == self.project.readEntry("COASTALME", 'result_name')[0]:
						self.cboResult.setCurrentIndex(i)
						break
			if self.project.readEntry("COASTALME", 'result_scalar')[0]:
				for i in range(self.cboScalar.count()):
					if self.cboScalar.itemText(i) == self.project.readEntry("COASTALME", 'result_scalar')[0]:
						self.cboScalar.setCurrentIndex(i)
						break
			if self.project.readEntry("COASTALME", 'result_vector')[0]:
				for i in range(self.cboVector.count()):
					if self.cboVector.itemText(i) == self.project.readEntry("COASTALME", 'result_vector')[0]:
						self.cboVector.setCurrentIndex(i)
						break
			if self.project.readEntry("COASTALME", 'video_width')[0]:
				self.spinWidth.setValue(self.project.readNumEntry("COASTALME", 'video_width')[0])
			if self.project.readEntry("COASTALME", 'video_height')[0]:
				self.spinHeight.setValue(self.project.readNumEntry("COASTALME", 'video_height')[0])
			if self.project.readEntry("COASTALME", 'video_fps')[0]:
				self.spinSpeed.setValue(self.project.readNumEntry("COASTALME", 'video_fps')[0])
			if self.project.readEntry("COASTALME", 'output_file')[0]:
				self.editOutput.setText(self.project.readEntry("COASTALME", 'output_file')[0])
		
	def populateLayoutTab(self):
		"""
		Populates widgets in Layout Tab
		
		:return: void
		"""
		
		addIcon = QgsApplication.getThemeIcon('/symbologyAdd.svg')
		removeIcon = QgsApplication.getThemeIcon('/symbologyRemove.svg')
		upIcon = QgsApplication.getThemeIcon('/mActionArrowUp.svg')
		downIcon = QgsApplication.getThemeIcon('/mActionArrowDown.svg')
		folderIcon = QgsApplication.getThemeIcon('/mActionFileOpen.svg')
		
		self.btnAddPlot.setIcon(addIcon)
		self.btnRemovePlot.setIcon(removeIcon)
		self.btnPlotUp.setIcon(upIcon)
		self.btnPlotDown.setIcon(downIcon)
		
		self.btnAddImage.setIcon(addIcon)
		self.btnRemoveImage.setIcon(removeIcon)
		self.btnImageUp.setIcon(upIcon)
		self.btnImageDown.setIcon(downIcon)
		
		self.btnBrowseTemplate.setIcon(folderIcon)
		
		self.tablePlots.horizontalHeader().setVisible(True)
		self.tableGraphics.horizontalHeader().setVisible(True)
		self.populateGraphics()
		
		# load project settings
		# Title
		self.groupTitle.setChecked(self.project.readBoolEntry("COASTALME", 'title_cb')[0])
		self.labelTitle.setText(self.project.readEntry("COASTALME", 'title_label')[0])
		font = QFont()
		font.setFamily(self.project.readEntry("COASTALME", 'title_font_name', 'MS Shell Dlg 2')[0])
		font.setPointSize(self.project.readNumEntry("COASTALME", 'title_font_size', 9)[0])
		font.setBold(self.project.readBoolEntry("COASTALME", 'title_font_bold')[0])
		font.setStyle(QFont.Style(self.project.readNumEntry("COASTALME", 'title_font_italic')[0]))
		font.setStrikeOut(self.project.readBoolEntry("COASTALME", 'title_font_strikeout')[0])
		font.setUnderline(self.project.readBoolEntry("COASTALME", 'title_font_underline')[0])
		self.fbtnTitle.setCurrentFont(font)
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'title_font_color', '#000000')[0])
		self.colorTitleText.setColor(color)
		self.cbTitleBackground.setChecked(self.project.readBoolEntry("COASTALME", 'title_background_cb')[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'title_background_color', '#ffffff')[0])
		self.colorTitleBackground.setColor(color)
		self.cboPosTitle.setCurrentIndex(self.project.readNumEntry("COASTALME", 'title_background_position', 4)[0])
		self.cbTitleFrame.setChecked(self.project.readBoolEntry("COASTALME", 'title_border_cb', False)[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'title_border_color', '#000000')[0])
		self.colorTitleFrame.setColor(color)
		
		# Time
		self.groupTime.setChecked(self.project.readBoolEntry("COASTALME", 'time_cb')[0])
		self.labelTime.setText(self.project.readEntry("COASTALME", 'time_label')[0])
		font = QFont()
		font.setFamily(self.project.readEntry("COASTALME", 'time_font_name', 'MS Shell Dlg 2')[0])
		font.setPointSize(self.project.readNumEntry("COASTALME", 'time_font_size', 9)[0])
		font.setBold(self.project.readBoolEntry("COASTALME", 'time_font_bold')[0])
		font.setStyle(QFont.Style(self.project.readNumEntry("COASTALME", 'time_font_italic')[0]))
		font.setStrikeOut(self.project.readBoolEntry("COASTALME", 'time_font_strikeout')[0])
		font.setUnderline(self.project.readBoolEntry("COASTALME", 'time_font_underline')[0])
		self.fbtnTime.setCurrentFont(font)
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'time_font_color', '#000000')[0])
		self.colorTimeText.setColor(color)
		self.cbTimeBackground.setChecked(self.project.readBoolEntry("COASTALME", 'time_background_cb')[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'time_background_color', '#ffffff')[0])
		self.colorTimeBackground.setColor(color)
		self.cboPosTime.setCurrentIndex(self.project.readNumEntry("COASTALME", 'time_background_position', 1)[0])
		self.cbTimeFrame.setChecked(self.project.readBoolEntry("COASTALME", 'time_border_cb', False)[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'time_border_color', '#000000')[0])
		self.colorTimeFrame.setColor(color)
		
		# Legend
		self.groupLegend.setChecked(self.project.readBoolEntry("COASTALME", 'legend_cb')[0])
		self.labelLegend.setText(self.project.readEntry("COASTALME", 'legend_label')[0])
		font = QFont()
		font.setFamily(self.project.readEntry("COASTALME", 'legend_font_name', 'MS Shell Dlg 2')[0])
		font.setPointSize(self.project.readNumEntry("COASTALME", 'legend_font_size', 9)[0])
		font.setBold(self.project.readBoolEntry("COASTALME", 'legend_font_bold')[0])
		font.setStyle(QFont.Style(self.project.readNumEntry("COASTALME", 'legend_font_italic')[0]))
		font.setStrikeOut(self.project.readBoolEntry("COASTALME", 'legend_font_strikeout')[0])
		font.setUnderline(self.project.readBoolEntry("COASTALME", 'legend_font_underline')[0])
		self.fbtnLegend.setCurrentFont(font)
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'legend_font_color', '#000000')[0])
		self.colorLegendText.setColor(color)
		self.cbLegendBackground.setChecked(self.project.readBoolEntry("COASTALME", 'legend_background_cb')[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'legend_background_color', '#ffffff')[0])
		self.colorLegendBackground.setColor(color)
		self.cboPosLegend.setCurrentIndex(self.project.readNumEntry("COASTALME", 'legend_background_position', 3)[0])
		self.cbLegendFrame.setChecked(self.project.readBoolEntry("COASTALME", 'legend_border_cb', False)[0])
		color = QColor()
		color.setNamedColor(self.project.readEntry("COASTALME", 'legend_border_color', '#000000')[0])
		self.colorLegendFrame.setColor(color)
		
		# layout type
		layout_type = self.project.readEntry("COASTALME", 'layout_type', 'default')[0]
		if layout_type == 'default':
			self.radLayoutDefault.setChecked(True)
		else:
			self.radLayoutCustom.setChecked(True)
		self.editTemplate.setText(self.project.readEntry("COASTALME", 'custom_template_path')[0])
		
		# plots
		self.groupPlot.setChecked(self.project.readBoolEntry("COASTALME", 'plots_cb')[0])
		nPlots = self.project.readNumEntry("COASTALME", 'number_of_plots')[0]
		for i in range(nPlots):
			self.addPlot()
			self.tablePlots.item(i, 0).setText(self.project.readEntry("COASTALME", 'plot_{0}_type'.format(i))[0])
			items = self.project.readListEntry("COASTALME", 'plot_{0}_items'.format(i))[0]
			self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i] = items
			self.tablePlots.item(i, 1).setText(';;'.join(items))
			self.tablePlots.item(i, 2).setText(self.project.readEntry("COASTALME", 'plot_{0}_position'.format(i))[0])
			p = self.pbDialogs[self.tablePlots.cellWidget(i, 3)]
			p.leTitle.setText(self.project.readEntry("COASTALME", 'plot_{0}_title'.format(i))[0])
			p.leXLabel.setText(self.project.readEntry("COASTALME", 'plot_{0}_xlabel'.format(i))[0])
			p.leYLabel.setText(self.project.readEntry("COASTALME", 'plot_{0}_ylabel'.format(i))[0])
			p.leY2Label.setText(self.project.readEntry("COASTALME", 'plot_{0}_y2label'.format(i))[0])
			p.sbXmin.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_xmin'.format(i))[0])
			p.sbXMax.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_xmax'.format(i))[0])
			year = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_year'.format(i), 1990)[0]
			month = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_month'.format(i), 1)[0]
			day = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_day'.format(i), 1)[0]
			hour = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_hour'.format(i), 0)[0]
			minute = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_minute'.format(i), 0)[0]
			second = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_second'.format(i), 0)[0]
			msecond = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemin_msecond'.format(i), 0)[0]
			date = QDate(year, month, day)
			time = QTime(hour, minute, second, msecond)
			dateTime = QDateTime(date, time)
			p.dteXmin.setDateTime(dateTime)
			year = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_year'.format(i), 1990)[0]
			month = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_month'.format(i), 1)[0]
			day = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_day'.format(i), 1)[0]
			hour = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_hour'.format(i), 1)[0]
			minute = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_minute'.format(i), 0)[0]
			second = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_second'.format(i), 0)[0]
			msecond = self.project.readNumEntry("COASTALME", 'plot_{0}_xdatemax_msecond'.format(i), 0)[0]
			date = QDate(year, month, day)
			time = QTime(hour, minute, second, msecond)
			dateTime = QDateTime(date, time)
			p.dteXMax.setDateTime(dateTime)
			p.sbXAxisRotation.setValue(self.project.readNumEntry("COASTALME", 'plot_{0}_xaxis_rotation'.format(i), 0)[0])
			p.sbYMin.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_ymin'.format(i))[0])
			p.sbYMax.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_ymax'.format(i))[0])
			p.sbY2Min.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_y2min'.format(i))[0])
			p.sbY2Max.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_y2max'.format(i))[0])
			p.cbLegend.setChecked(self.project.readBoolEntry("COASTALME", 'plot_{0}_legend_cb'.format(i))[0])
			p.cboLegendPos.setCurrentIndex(self.project.readNumEntry("COASTALME", 'plot_{0}_legend_pos'.format(i))[0])
			p.cbGridY.setChecked(self.project.readBoolEntry("COASTALME", 'plot_{0}_ygrid'.format(i))[0])
			p.cbGridX.setChecked(self.project.readBoolEntry("COASTALME", 'plot_{0}_xgrid'.format(i))[0])
			p.sbFigSizeX.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_xsize'.format(i))[0])
			p.sbFigSizeY.setValue(self.project.readDoubleEntry("COASTALME", 'plot_{0}_ysize'.format(i))[0])
			p.userSet = True
			
		# graphics
		for i in range(self.tableGraphics.rowCount()):
			self.tableGraphics.item(i, 0).setCheckState(self.project.readNumEntry("COASTALME", "graphic_{0}_cb".format(i), 2)[0])
			userLabel = self.project.readEntry("COASTALME", "graphic_{0}_user_label".format(i))[0]
			if userLabel:
				self.tableGraphics.item(i, 1).setText(userLabel)
			self.tableGraphics.item(i, 2).setText(self.project.readEntry("COASTALME", "graphic_{0}_position".format(i), 'Left')[0])
			p = self.rowNo2fntDialog[i]
			font = QFont()
			font.setFamily(self.project.readEntry("COASTALME", 'graphic_{0}_font_name'.format(i), 'MS Shell Dlg 2')[0])
			font.setPointSize(self.project.readNumEntry("COASTALME", 'graphic_{0}_font_size'.format(i), 9)[0])
			font.setBold(self.project.readBoolEntry("COASTALME", 'graphic_{0}_font_bold'.format(i))[0])
			font.setStyle(QFont.Style(self.project.readNumEntry("COASTALME", 'graphic_{0}_font_italic'.format(i))[0]))
			font.setStrikeOut(self.project.readBoolEntry("COASTALME", 'graphic_{0}_font_strikeout'.format(i))[0])
			font.setUnderline(self.project.readBoolEntry("COASTALME", 'graphic_{0}_font_underline'.format(i))[0])
			p.fntButton.setCurrentFont(font)
			color = QColor()
			color.setNamedColor(self.project.readEntry("COASTALME", 'graphic_{0}_font_color'.format(i), '#000000')[0])
			p.fntColor.setColor(color)
			p.cbBackground.setChecked(self.project.readBoolEntry("COASTALME", 'graphic_{0}_background_cb'.format(i), True)[0])
			color = QColor()
			color.setNamedColor(self.project.readEntry("COASTALME", 'graphic_{0}_background_color'.format(i), '#ffffff')[0])
			
		# Images
		self.groupImages.setChecked(self.project.readBoolEntry("COASTALME", 'images_cb')[0])
		nImages = self.project.readNumEntry("COASTALME", 'number_of_images')[0]
		for i in range(nImages):
			self.addImage()
			self.tableImages.item(i, 0).setText(self.project.readEntry("COASTALME", 'image_{0}_source'.format(i))[0])
			self.tableImages.item(i, 1).setText(self.project.readEntry("COASTALME", 'image_{0}_position'.format(i))[0])
			p = self.pbDialogsImage[self.tableImages.cellWidget(i, 2)]
			p.rbUseOriginalSize.setChecked(self.project.readBoolEntry("COASTALME", 'image_{0}_use_original_size'.format(i), True)[0])
			p.rbResizeImage.setChecked(self.project.readBoolEntry("COASTALME", 'image_{0}_resize_image'.format(i))[0])
			p.sbSizeX.setValue(self.project.readDoubleEntry("COASTALME", 'image_{0}_xsize'.format(i))[0])
			p.sbSizeY.setValue(self.project.readDoubleEntry("COASTALME", 'image_{0}_ysize'.format(i))[0])
			p.cbKeepAspectRatio.setChecked(self.project.readBoolEntry("COASTALME", 'image_{0}_maintain_aspect_ratio'.format(i))[0])
		
	def populateVideoTab(self):
		"""
		Populates widgets in Video Tab
		
		:return: void
		"""
		
		folderIcon = QgsApplication.getThemeIcon('/mActionFileOpen.svg')
		self.btnBrowseFfmpegPath.setIcon(folderIcon)
		
		settings = QSettings()
		ffmpeg = settings.value("COASTALME/animation_ffmpeg_switch")
		ffmpegLoc = settings.value("COASTALME/animation_ffmpeg")
		switch = True if ffmpeg == 'custom' else False
		self.radFfmpegCustom.setChecked(switch)
		self.editFfmpegPath.setText(ffmpegLoc)
		
		quality = self.project.readEntry("COASTALME", 'video_quality', 'high')
		if quality == 'best':
			self.radQualBest.setChecked(True)
		elif quality == 'high':
			self.radQualHigh.setChecked(True)
		else:
			self.radQualLow.setChecked(True)
		
	def browse(self, type, key, fileType, lineEdit):
		"""
		Browse folder directory
		
		:param type: str browse type 'folder' or 'file'
		:param key: str settings key
		:param fileType: str file extension e.g. "AVI files (*.avi)"
		:param lineEdit: QLineEdit to be updated by browsing
		:return: void
		"""
		
		settings = QSettings()
		lastFolder = settings.value(key)
		startDir = None
		if lastFolder:  # if outFolder no longer exists, work backwards in directory until find one that does
			while lastFolder:
				if os.path.exists(lastFolder):
					startDir = lastFolder
					break
				else:
					lastFolder = os.path.dirname(lastFolder)
		if type == 'save':
			f = QFileDialog.getSaveFileName(self, 'Ouput', startDir, fileType)[0]
		elif type == 'load':
			f = QFileDialog.getOpenFileName(self, 'Import Template', startDir, fileType)[0]
		elif type == 'image':
			f = QFileDialog.getOpenFileName(self, 'Image File', startDir, fileType)[0]
		elif type == 'ffmpeg':
			f = QFileDialog.getOpenFileName(self, 'FFmpeg Location', startDir, fileType)[0]
		else:
			return
		if f:
			lineEdit.setText(f)
			settings.setValue(key, f)
	
	def populateResults(self):
		"""
		Populates open results combobox
		
		:return: void
		"""
		
		selected = None
		for i in range(self.tuView.OpenResults.count()):
			item = self.tuView.OpenResults.item(i)
			self.cboResult.addItem(item.text())
			if selected is None and item in self.tuView.OpenResults.selectedItems():
				selected = i
		if selected is not None:
			self.cboResult.setCurrentIndex(selected)
			
	def populateTimes(self):
		"""
		Populates start and end time combobox
		
		:return: void
		"""
		
		self.cboStart.clear()
		self.cboEnd.clear()
		for i in range(self.tuView.cboTime.count()):
			item = self.tuView.cboTime.itemText(i)
			self.cboStart.addItem(item)
			self.cboEnd.addItem(item)
		
		self.cboStart.setCurrentIndex(self.tuView.cboTime.currentIndex())
		self.cboEnd.setCurrentIndex(self.tuView.cboTime.count() - 1)
		
	def populateResultTypes(self):
		"""
		Populate scalar and vector result type options.
		
		:return: void
		"""
		
		self.cboScalar.clear()
		self.cboVector.clear()
		
		resultName = self.cboResult.currentText()
		scalarResults, vectorResults = ['-None-'], ['-None-']
		activeScalar, activeVector = 0, 0
		scalarCount, vectorCount = 0, 0
		if resultName:
			result = self.tuView.tuResults.results[resultName]  # dict -> e.g. { 'Depth': { '0.000': ( timestep, scalar / vector type, QgsMeshDatasetIndex ) } }
			for  rtype, ts in result.items():
				if rtype == 'Bed Elevation':
					continue
				if rtype == '_nc_grid':
					scalarCount += 1
					scalarResults.append(resultName)
				elif 'times' in ts:
					ts = ts['times']
					if '_ts' not in rtype and '_lp' not in rtype and '/Maximums' not in rtype:  # temporal map output result type
						for key, item in ts.items():
							if item[1] == 1:
								scalarResults.append(rtype)
								scalarCount += 1
								if rtype in self.tuView.tuResults.activeResults:
									activeScalar = scalarCount
							elif item[1] == 2:
								vectorResults.append(rtype)
								vectorCount += 1
								if rtype in self.tuView.tuResults.activeResults:
									activeVector = vectorCount
							break  # only need to check one entry
		
		self.cboScalar.addItems(scalarResults)
		self.cboVector.addItems(vectorResults)
		self.cboScalar.setCurrentIndex(activeScalar)
		self.cboVector.setCurrentIndex(activeVector)
		
	def plotItems(self, ptype, **kwargs):
		"""
		Returns a list of plot item labels and artists
		
		:param plotNo:
		:return:
		"""

		from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot import TuPlot
		
		# deal with kwargs
		includeDuplicates = kwargs['include_duplicates'] if 'include_duplicates' in kwargs.keys() else False
		
		if ptype == 'Time Series':
			plotNo = TuPlot.TimeSeries
		elif ptype == 'CS / LP':
			plotNo = TuPlot.CrossSection
		elif ptype == 'Vert Profile':
			plotNo = TuPlot.VerticalProfile
		else:
			return [], []
		
		parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, yAxisLabels, xAxisLabels, xAxisLimits, yAxisLimits = \
			self.tuView.tuPlot.plotEnumerator(plotNo)
		
		lines, labs = subplot.get_legend_handles_labels()
		labs = [TuResults.stripMaximumName(TuResults.stripMinimumName(x)) for x in labs]
		ct = [PolyCollection, Quiver]  # curtain types
		# labs = [labs[x] + '{0}'.format(' [Curtain]' if type(lines[x]) in ct else "") for x in range(len(labs))]
		labs = [labs[x] + '{0}'.format(' [Curtain]' if type(lines[x]) in ct else "") for x in range(len(labs))]
		axis = ['axis 1' for x in range(len(lines))]
		if isSecondaryAxis[0]:
			subplot2 = self.tuView.tuPlot.getSecondaryAxis(plotNo)
			lines2, labs2 = subplot2.get_legend_handles_labels()
			for i, line in enumerate(lines2):
				if type(line) is Quiver:
					labs2.insert(i, 'vector')
			labs2 = [labs2[x] + '{0}'.format(' [Curtain]' if type(lines2[x]) is PolyCollection else "") for x in
			        range(len(labs2))]
			axis2 = ['axis 2' for x in range(len(lines2))]
		else:
			lines2, labs2, axis2 = [], [], []
		
		lines += lines2
		labs += labs2
		axis += axis2
		
		uniqLines, uniqLabs, uniqAxis = [], [], []
		for i, lab in enumerate(labs):
			if lab not in uniqLabs:
				uniqLabs.append(lab)
				uniqLines.append(lines[i])
				uniqAxis.append(axis[i])
		
		if includeDuplicates:
			return lines, labs, axis
		else:
			return uniqLines, uniqLabs, uniqAxis
	
	def populateGraphics(self):
		"""
		Populates the graphics table with available TS Point, CS Line, or Flow Line objects that can be included in the
		animation map.

		:param checked: bool -> True means groupbox is checked on
		:return: void
		"""

		self.populateGraphics2(self.tuView.tuPlot.tuTSPoint.points, 'TS Point')
		self.populateGraphics2(self.tuView.tuPlot.tuCrossSection.rubberBands, 'CS / LP Line')
		self.populateGraphics2(self.tuView.tuPlot.tuFlowLine.rubberBands, 'Flow Line')
		self.populateGraphics2(self.tuView.tuPlot.tuCurtainLine.rubberBands, 'Curtain Line')
		self.populateGraphics2(self.tuView.tuPlot.tuTSPointDepAv.points, 'TS DepAv Point')
		self.populateGraphics2(self.tuView.tuPlot.tuCSLineDepAv.rubberBands, 'CS DepAv Line')
		self.populateGraphics2(self.tuView.tuPlot.tuVPPoint.points, 'Vert Profile Point')

	def populateGraphics2(self, graphics, prefix):
		"""
		helper for the function above to stop the need for repeated code
		"""

		for i, graphic in enumerate(graphics):
			if type(graphic) is QgsPoint:
				graphic = QgsPointXY(graphic)
			rowNo = self.tableGraphics.rowCount()
			self.tableGraphics.setRowCount(rowNo + 1)
			self.addGraphicRowToTable('{0} {1}'.format(prefix, i + 1), rowNo)
			self.label2graphic['{0} {1}'.format(prefix, i + 1)] = graphic

	def addGraphicRowToTable(self, label, rowNo, status=True, userLabel=None):
		"""
		Create widget for graphic to insert into graphic table.

		:param label: str e.g. 'TS Point 1' or 'CS Line 1'
		:param rowNo: int row number in graphic options table of graphic being added
		:param checked: bool include graphic in animation
		:param userLabel: str defaults to label if None
		:return: void
		"""
		
		item1 = QTableWidgetItem(0)
		item1.setText(label)
		item1.setFlags(QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE | QT_ITEM_FLAG_ITEM_IS_SELECTABLE | QT_ITEM_FLAG_ITEM_IS_ENABLED)
		if status:
			item1.setCheckState(QT_CHECKED)
		else:
			item1.setCheckState(QT_UNCHECKED)
		self.tableGraphics.setItem(rowNo, 0, item1)
		
		item2 = QTableWidgetItem(0)
		item2.setText(userLabel) if userLabel is not None else item2.setText(label)
		self.tableGraphics.setItem(rowNo, 1, item2)
		
		item3 = QTableWidgetItem(0)
		item3.setText('Left')
		self.tableGraphics.setItem(rowNo, 2, item3)
		items = ['Left', 'Right']
		if 'TS' in label:
			items += ['Above', 'Below', 'Above-Left', 'Below-Left', 'Above-Right', 'Below-Right']
		self.tableGraphics.itemDelegateForColumn(2).itemsInRows[rowNo] = items
		
		pb = QPushButton()
		pb.setText('Text Properties')
		dialog = TextPropertiesDialog()
		self.rowNo2fntDialog[rowNo] = dialog
		pb.clicked.connect(lambda: dialog.exec())
		self.tableGraphics.setCellWidget(rowNo, 3, pb)
		
		if rowNo == 0:
			self.tableGraphics.setColumnWidth(2, self.tableGraphics.columnWidth(
				2) - self.tableGraphics.verticalHeader().sizeHint().width())
	
	def addPlot(self, e=False, item1=None, item2=None, item3=None, dialog=None):
		"""
		Add plot to QTableWidget

		:return: void
		"""
		
		## add to table
		n = self.tablePlots.rowCount()
		self.tablePlots.setRowCount(n + 1)
		if item1 is None:
			item1 = QTableWidgetItem(0)
			item1.setText(self.tablePlots.itemDelegateForColumn(0).default)
		if item2 is None:
			item2 = QTableWidgetItem(0)
		else:
			self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[n] = self.plotTableRowItems[n][1]
		if item3 is None:
			item3 = QTableWidgetItem(0)
			item3.setText(self.tablePlots.itemDelegateForColumn(2).default)
		
		self.tablePlots.setItem(n, 0, item1)
		self.tablePlots.setItem(n, 1, item2)
		self.tablePlots.setItem(n, 2, item3)
		
		pb = QPushButton(self.tablePlots)
		pb.setText('Properties')
		if dialog is None:
			dialog = PlotProperties(self, item1, item2, self.tuView.tuOptions.xAxisDates)
		self.pbDialogs[pb] = dialog
		self.dialog2Plot[dialog] = [item1, item2, item3]
		pb.clicked.connect(lambda: dialog.setDefaults(self, item1, item2, 'not cross sections', static=False))
		pb.clicked.connect(lambda: dialog.show_())
		self.tablePlots.setCellWidget(n, 3, pb)
		if n == 0:
			self.tablePlots.setColumnWidth(2, self.tablePlots.columnWidth(
				2) - self.tablePlots.verticalHeader().sizeHint().width())
		
		plotTableRow = [item1, item2, item3, dialog]
		plotTableRowItems = [[], [], [], [], []]
		self.plotTableRows.append(plotTableRow)
		self.plotTableRowItems.append(plotTableRowItems)
	
	def insertPlotRow(self, index=None, loc=INSERT_BEFORE):
		"""
		Insert a row into the map table.
		Can be inserted before or after clicked row.

		:param index: int
		:param loc: Table
		:return: void
		"""
		
		if index is not None:
			for i, plotTableRow in enumerate(self.plotTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(plotTableRow[0].text())
				item1Items = []
				item2 = QTableWidgetItem(0)
				item2.setText(plotTableRow[1].text())
				if i in self.tablePlots.itemDelegateForColumn(1).currentCheckedItems:
					item2Items = self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
					del self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
				else:
					item2Items = []
				item3 = QTableWidgetItem(0)
				item3.setText(plotTableRow[2].text())
				item3Items = []
				pb = self.tablePlots.cellWidget(i, 3)
				pb.clicked.disconnect()
				item4 = self.pbDialogs[pb]
				del pb
				item4Items = []
				plotTableRow = [item1, item2, item3, item4]
				plotTableRowItems = [item1Items, item2Items, item3Items, item4Items]
				self.plotTableRows[i] = plotTableRow
				self.plotTableRowItems[i] = plotTableRowItems
			
			self.pbDialogs.clear()
			
			if loc == TuAnimationDialog.INSERT_BEFORE:
				j = index
			else:
				j = index + 1
			
			## add to table
			item1 = QTableWidgetItem(0)
			item1.setText(self.tablePlots.itemDelegateForColumn(0).default)
			item2 = QTableWidgetItem(0)
			item3 = QTableWidgetItem(0)
			item3.setText(self.tablePlots.itemDelegateForColumn(2).default)
			item4 = PlotProperties(self, item1, item2, self.tuView.tuOptions.xAxisDates)
			
			plotTableRow = [item1, item2, item3, item4]
			plotTableRowItems = [[], [], [], []]
			self.plotTableRows.insert(j, plotTableRow)
			self.plotTableRowItems.insert(j, plotTableRowItems)
			
			self.reAddPlots()
	
	def removePlots(self, index=None):
		"""Remove plot from table."""
		
		selectionRange = self.tablePlots.selectedRanges()
		selectionRange = [[y for y in range(x.topRow(), x.bottomRow() + 1)] for x in selectionRange]
		selectionRange = sum(selectionRange, [])
		if index:
			if index not in selectionRange:
				selectionRange = [index]
		
		if selectionRange:
			for i, plotTableRow in enumerate(self.plotTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(plotTableRow[0].text())
				item1Items = []
				item2 = QTableWidgetItem(0)
				item2.setText(plotTableRow[1].text())
				if i in self.tablePlots.itemDelegateForColumn(1).currentCheckedItems:
					item2Items = self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
					del self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
				else:
					item2Items = []
				item3 = QTableWidgetItem(0)
				item3.setText(plotTableRow[2].text())
				item3Items = []
				pb = self.tablePlots.cellWidget(i, 3)
				pb.clicked.disconnect()
				item4 = self.pbDialogs[pb]
				del pb
				item4Items = []
				plotTableRow = [item1, item2, item3, item4]
				plotTableRowItems = [item1Items, item2Items, item3Items, item4Items]
				self.plotTableRows[i] = plotTableRow
				self.plotTableRowItems[i] = plotTableRowItems
			for i in reversed(selectionRange):
				self.plotTableRows.pop(i)
				self.plotTableRowItems.pop(i)
			self.pbDialogs.clear()
			self.reAddPlots()
		else:
			if self.tablePlots.rowCount():
				if self.tablePlots.rowCount() == 1:
					self.tablePlots.setColumnWidth(2, self.tablePlots.columnWidth(2) +
					                               self.tablePlots.verticalHeader().sizeHint().width())
				pb = self.tablePlots.cellWidget(self.tablePlots.rowCount() - 1, 3)
				del self.pbDialogs[pb]
				self.tablePlots.setRowCount(self.tablePlots.rowCount() - 1)
				self.plotTableRows.pop()
				self.plotTableRowItems.pop()
				if self.tablePlots.rowCount() in self.tablePlots.itemDelegateForColumn(1).currentCheckedItems:
					del self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[self.tablePlots.rowCount()]
	
	def reAddPlots(self):
		
		self.tablePlots.setColumnWidth(2, self.tablePlots.columnWidth(2) +
		                               self.tablePlots.verticalHeader().sizeHint().width())
		self.tablePlots.setRowCount(0)
		
		plotTableRows = self.plotTableRows[:]
		self.plotTableRows.clear()
		
		for i, plotTableRow in enumerate(plotTableRows):
			item1 = plotTableRow[0]
			item2 = plotTableRow[1]
			item3 = plotTableRow[2]
			item4 = plotTableRow[3]
			self.addPlot(item1=item1, item2=item2, item3=item3, dialog=item4)
	
	def movePlot(self, event=None, action='up'):
		"""Move position of selected map in table. Options 'up' or 'down'."""
		
		selectionRanges = self.tablePlots.selectedRanges()
		selectionRangeIndexes = [[y for y in range(x.topRow(), x.bottomRow() + 1)] for x in selectionRanges]
		selectionRangeIndexes = sum(selectionRangeIndexes, [])
		
		if selectionRangeIndexes:
			for i, plotTableRow in enumerate(self.plotTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(plotTableRow[0].text())
				item1Items = []
				item2 = QTableWidgetItem(0)
				item2.setText(plotTableRow[1].text())
				if i in self.tablePlots.itemDelegateForColumn(1).currentCheckedItems:
					item2Items = self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
					del self.tablePlots.itemDelegateForColumn(1).currentCheckedItems[i]
				else:
					item2Items = []
				item3 = QTableWidgetItem(0)
				item3.setText(plotTableRow[2].text())
				item3Items = []
				pb = self.tablePlots.cellWidget(i, 3)
				pb.clicked.disconnect()
				item4 = self.pbDialogs[pb]
				del pb
				item4Items = []
				plotTableRow = [item1, item2, item3, item4]
				plotTableRowItems = [item1Items, item2Items, item3Items, item4Items]
				self.plotTableRows[i] = plotTableRow
				self.plotTableRowItems[i] = plotTableRowItems
			if action == 'up':
				for i in selectionRangeIndexes:
					if i > 0:
						row = self.plotTableRows.pop(i)
						self.plotTableRows.insert(i - 1, row)
						row = self.plotTableRowItems.pop(i)
						self.plotTableRowItems.insert(i - 1, row)
			else:
				for i in reversed(selectionRangeIndexes):
					if i < self.tablePlots.rowCount() - 1:
						row = self.plotTableRows.pop(i)
						self.plotTableRows.insert(i + 1, row)
						row = self.plotTableRowItems.pop(i)
						self.plotTableRowItems.insert(i + 1, row)
			self.reAddPlots()
			
			for sr in selectionRanges:
				if action == 'up':
					top = sr.topRow() - 1 if sr.topRow() > 0 else sr.topRow()
					bottom = sr.bottomRow() - 1 if sr.bottomRow() > sr.rowCount() - 1 else sr.bottomRow()
					left = sr.leftColumn()
					right = sr.rightColumn()
					newSelectionRange = QTableWidgetSelectionRange(top, left, bottom, right)
				else:
					top = sr.topRow() + 1 if sr.topRow() < self.tablePlots.rowCount() - sr.rowCount() else sr.topRow()
					bottom = sr.bottomRow() + 1 if sr.bottomRow() < self.tablePlots.rowCount() - 1 else sr.bottomRow()
					left = sr.leftColumn()
					right = sr.rightColumn()
					newSelectionRange = QTableWidgetSelectionRange(top, left, bottom, right)
				self.tablePlots.setRangeSelected(newSelectionRange, True)
	
	def plotTypeChanged(self, item=None):
		"""Updates row in map table if one of the combo boxes is changed."""
		
		if item is not None:
			if item.column() == 0:
				lines, labs, axis = self.plotItems(self.tablePlots.item(item.row(), item.column()).text())
				self.tablePlots.itemDelegateForColumn(1).setItems(item.row(), labs)

				for i in range(self.tablePlots.rowCount()):
					if self.tablePlots.item(i, 0) == item:
						pb = self.tablePlots.cellWidget(i, 3)
						if pb is not None:
							dialog = self.pbDialogs[pb]
							if self.tablePlots.item(item.row(), item.column()).text() == 'Time Series':
								dialog.setDateTime(self.tuView.tuOptions.xAxisDates)
							else:
								dialog.setDateTime(False)
	
	def addImage(self, e=False, item1=None, item2=None, dialog=None):
		"""
		Add plot to QTableWidget

		:return: void
		"""
		
		## add to table
		n = self.tableImages.rowCount()
		self.tableImages.setRowCount(n + 1)
		if item1 is None:
			item1 = QTableWidgetItem(0)
		if item2 is None:
			item2 = QTableWidgetItem(0)
			item2.setText(self.tableImages.itemDelegateForColumn(1).default)
		
		self.tableImages.setItem(n, 0, item1)
		self.tableImages.setItem(n, 1, item2)
		
		pb = QPushButton()
		pb.setText('Properties')
		if dialog is None:
			dialog = ImagePropertiesDialog()
		self.pbDialogsImage[pb] = dialog
		pb.clicked.connect(lambda: dialog.exec())
		self.tableImages.setCellWidget(n, 2, pb)
		if n == 0:
			self.tableImages.setColumnWidth(1, self.tableImages.columnWidth(
				1) - self.tableImages.verticalHeader().sizeHint().width())
		
		imageTableRow = [item1, item2, dialog]
		self.imageTableRows.append(imageTableRow)
	
	def insertImageRow(self, index=None, loc=INSERT_BEFORE):
		"""
		Insert a row into the map table.
		Can be inserted before or after clicked row.

		:param index: int
		:param loc: Table
		:return: void
		"""
		
		if index is not None:
			for i, imageTableRow in enumerate(self.imageTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(imageTableRow[0].text())
				item2 = QTableWidgetItem(0)
				item2.setText(imageTableRow[1].text())
				pb = self.tableImages.cellWidget(i, 2)
				pb.clicked.disconnect()
				item3 = self.pbDialogsImage[pb]
				del pb
				imageTableRow = [item1, item2, item3]
				self.imageTableRows[i] = imageTableRow
			
			self.pbDialogsImage.clear()
			
			if loc == TuAnimationDialog.INSERT_BEFORE:
				j = index
			else:
				j = index + 1
			
			## add to table
			item1 = QTableWidgetItem(0)
			item2 = QTableWidgetItem(0)
			item2.setText(self.tableImages.itemDelegateForColumn(1).default)
			item3 = ImagePropertiesDialog()
			
			imageTableRow = [item1, item2, item3]
			self.imageTableRows.insert(j, imageTableRow)
			
			self.reAddImages()
	
	def removeImages(self, index=None):
		"""Remove plot from table."""
		
		selectionRange = self.tableImages.selectedRanges()
		selectionRange = [[y for y in range(x.topRow(), x.bottomRow() + 1)] for x in selectionRange]
		selectionRange = sum(selectionRange, [])
		if index:
			if index not in selectionRange:
				selectionRange = [index]
		
		if selectionRange:
			for i, imageTableRow in enumerate(self.imageTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(imageTableRow[0].text())
				item2 = QTableWidgetItem(0)
				item2.setText(imageTableRow[1].text())
				pb = self.tableImages.cellWidget(i, 2)
				pb.clicked.disconnect()
				item3 = self.pbDialogsImage[pb]
				del pb
				imageTableRow = [item1, item2, item3]
				self.imageTableRows[i] = imageTableRow
			for i in reversed(selectionRange):
				self.imageTableRows.pop(i)
			self.pbDialogsImage.clear()
			self.reAddImages()
		else:
			if self.tableImages.rowCount():
				if self.tableImages.rowCount() == 1:
					self.tableImages.setColumnWidth(1, self.tableImages.columnWidth(1) +
					                                self.tableImages.verticalHeader().sizeHint().width())
				pb = self.tableImages.cellWidget(self.tableImages.rowCount() - 1, 2)
				del self.pbDialogsImage[pb]
				self.tableImages.setRowCount(self.tableImages.rowCount() - 1)
				self.imageTableRows.pop()
	
	def reAddImages(self):
		
		self.tableImages.setColumnWidth(1, self.tableImages.columnWidth(1) +
		                                self.tableImages.verticalHeader().sizeHint().width())
		self.tableImages.setRowCount(0)
		
		imageTableRows = self.imageTableRows[:]
		self.imageTableRows.clear()
		
		for i, imageTableRow in enumerate(imageTableRows):
			item1 = imageTableRow[0]
			item2 = imageTableRow[1]
			item3 = imageTableRow[2]
			self.addImage(item1=item1, item2=item2, dialog=item3)
	
	def moveImage(self, event=None, action='up'):
		"""Move position of selected map in table. Options 'up' or 'down'."""
		
		selectionRanges = self.tableImages.selectedRanges()
		selectionRangeIndexes = [[y for y in range(x.topRow(), x.bottomRow() + 1)] for x in selectionRanges]
		selectionRangeIndexes = sum(selectionRangeIndexes, [])
		
		if selectionRangeIndexes:
			for i, imageTableRow in enumerate(self.imageTableRows):
				item1 = QTableWidgetItem(0)
				item1.setText(imageTableRow[0].text())
				item2 = QTableWidgetItem(0)
				item2.setText(imageTableRow[1].text())
				pb = self.tableImages.cellWidget(i, 2)
				pb.clicked.disconnect()
				item3 = self.pbDialogsImage[pb]
				del pb
				imageTableRow = [item1, item2, item3]
				self.imageTableRows[i] = imageTableRow
			if action == 'up':
				for i in selectionRangeIndexes:
					if i > 0:
						row = self.imageTableRows.pop(i)
						self.imageTableRows.insert(i - 1, row)
			else:
				for i in reversed(selectionRangeIndexes):
					if i < self.tableImages.rowCount() - 1:
						row = self.imageTableRows.pop(i)
						self.imageTableRows.insert(i + 1, row)
			self.reAddImages()
			
			for sr in selectionRanges:
				if action == 'up':
					top = sr.topRow() - 1 if sr.topRow() > 0 else sr.topRow()
					bottom = sr.bottomRow() - 1 if sr.bottomRow() > sr.rowCount() - 1 else sr.bottomRow()
					left = sr.leftColumn()
					right = sr.rightColumn()
					newSelectionRange = QTableWidgetSelectionRange(top, left, bottom, right)
				else:
					top = sr.topRow() + 1 if sr.topRow() < self.tableImages.rowCount() - sr.rowCount() else sr.topRow()
					bottom = sr.bottomRow() + 1 if sr.bottomRow() < self.tableImages.rowCount() - 1 else sr.bottomRow()
					left = sr.leftColumn()
					right = sr.rightColumn()
					newSelectionRange = QTableWidgetSelectionRange(top, left, bottom, right)
				self.tableImages.setRangeSelected(newSelectionRange, True)
	
	def setPlotTableProperties(self):
		
		plotTypes = ['Time Series', 'CS / LP', 'Vert Profile']
		positions = ['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right']
		
		self.tablePlots.itemDelegateForColumn(0).setItems(items=plotTypes, default='Time Series')
		self.tablePlots.itemDelegateForColumn(2).setItems(items=positions, default='Top-Left')
	
	def setImageTableProperties(self):
		
		imageTypes = "All Files(*)"
		positions = ['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right']
		btnSignal = {'parent': self, 'browse type': 'existing file', 'key': 'COASTALME/map_image',
		             'title': "Image", 'file types': imageTypes}
		
		self.tableImages.itemDelegateForColumn(0).setSignalProperties(btnSignal)
		self.tableImages.itemDelegateForColumn(1).setItems(items=positions, default='Top-Left')
	
	def contextMenuPlotTable(self):
		"""
		Context menu for map table - right click on row number
		gives option to delete, insert before, insert after.

		:return: None
		"""
		
		self.tablePlots.verticalHeader().setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.tablePlots.verticalHeader().customContextMenuRequested.connect(self.plotTableMenu)
	
	def plotTableMenu(self, pos):
		"""
		Prepare the context menu for the map table.

		:param pos: QPoint
		:return: None
		"""
		
		self.plotTableMenu = QMenu()
		self.plotTableInsertRowBefore = QAction("Insert Above", self.plotTableMenu)
		self.plotTableInsertRowAfter = QAction("Insert Below", self.plotTableMenu)
		self.plotTableDeleteRow = QAction("Delete", self.plotTableMenu)
		
		index = self.tablePlots.rowAt(pos.y())
		self.plotTableInsertRowBefore.triggered.connect(lambda: self.insertPlotRow(index, TuAnimationDialog.INSERT_BEFORE))
		self.plotTableInsertRowAfter.triggered.connect(lambda: self.insertPlotRow(index, TuAnimationDialog.INSERT_AFTER))
		self.plotTableDeleteRow.triggered.connect(lambda: self.removePlots(index))
		
		self.plotTableMenu.addAction(self.plotTableInsertRowBefore)
		self.plotTableMenu.addAction(self.plotTableInsertRowAfter)
		self.plotTableMenu.addSeparator()
		self.plotTableMenu.addAction(self.plotTableDeleteRow)
		
		posH = self.tablePlots.mapToGlobal(pos).x()
		posV = self.tablePlots.mapToGlobal(pos).y() + \
		       self.plotTableMenu.actionGeometry(self.plotTableInsertRowBefore).height()
		newPos = QPoint(posH, int(posV))
		self.plotTableMenu.popup(newPos, self.plotTableInsertRowBefore)
	
	def contextMenuImageTable(self):
		"""
		Context menu for map table - right click on row number
		gives option to delete, insert before, insert after.

		:return: None
		"""
		
		self.tableImages.verticalHeader().setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
		self.tableImages.verticalHeader().customContextMenuRequested.connect(self.imageTableMenu)
	
	def imageTableMenu(self, pos):
		"""
		Prepare the context menu for the map table.

		:param pos: QPoint
		:return: None
		"""
		
		self.imageTableMenu = QMenu()
		self.imageTableInsertRowBefore = QAction("Insert Above", self.imageTableMenu)
		self.imageTableInsertRowAfter = QAction("Insert Below", self.imageTableMenu)
		self.imageTableDeleteRow = QAction("Delete", self.imageTableMenu)
		
		index = self.tableImages.rowAt(pos.y())
		self.imageTableInsertRowBefore.triggered.connect(lambda: self.insertImageRow(index, TuAnimationDialog.INSERT_BEFORE))
		self.imageTableInsertRowAfter.triggered.connect(lambda: self.insertImageRow(index, TuAnimationDialog.INSERT_AFTER))
		self.imageTableDeleteRow.triggered.connect(lambda: self.removeImages(index))
		
		self.imageTableMenu.addAction(self.imageTableInsertRowBefore)
		self.imageTableMenu.addAction(self.imageTableInsertRowAfter)
		self.imageTableMenu.addSeparator()
		self.imageTableMenu.addAction(self.imageTableDeleteRow)
		
		posH = self.tableImages.mapToGlobal(pos).x()
		posV = self.tableImages.mapToGlobal(pos).y() + \
		       self.imageTableMenu.actionGeometry(self.imageTableInsertRowBefore).height()
		newPos = QPoint(posH, int(posV))
		self.imageTableMenu.popup(newPos, self.imageTableInsertRowBefore)
		
	def check(self, event=None, preview=False):
		"""
		Checks input parameters before trying to run the tool and destroying the dialog.

		:return: void
		"""

		# General Tab
		if not self.cboResult.currentText():
			msg = 'No Result File Selected'
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error', msg)
			else:
				print(msg)
			return
		# if self.cboScalar.currentText() == '-None-' and self.cboVector.currentText() == '-None-':
		# 	msg = 'Must Choose at Least One Scalar or Vector Result Type'
		# 	if self.tuView.iface is not None:
		# 		QMessageBox.information(self, 'Input Error', msg)
		# 	else:
		# 		print(msg)
		# 	return
		if self.tuView.tuOptions.xAxisDates:
			startTimeConverted = self.tuView.tuPlot.convertDateToTime(self.cboStart.currentText(),
			                                                          unit=self.tuView.tuOptions.timeUnits)
			if startTimeConverted == -99999.:
				msg = 'Error converting input start date'
				if self.tuView.iface is not None:
					QMessageBox.information(self, 'Input Error', msg)
				else:
					print(msg)
				return
			endTimeConverted = self.tuView.tuPlot.convertDateToTime(self.cboEnd.currentText(),
			                                                        unit=self.tuView.tuOptions.timeUnits)
			if endTimeConverted == -99999.:
				msg = 'Error converting input end date'
				if self.tuView.iface is not None:
					QMessageBox.information(self, 'Input Error', msg)
				else:
					print(msg)
				return
		else:
			startTimeConverted = convertFormattedTimeToTime(self.cboStart.currentText(),
			                                                unit=self.tuView.tuOptions.timeUnits)
			endTimeConverted = convertFormattedTimeToTime(self.cboEnd.currentText(),
			                                              unit=self.tuView.tuOptions.timeUnits)

		if startTimeConverted >= endTimeConverted:
			msg = 'End Time Must Be Later Than Start Time'
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error', msg)
			else:
				print(msg)
			return
		if not self.editOutput.text() and not preview:
			msg = 'Must Specify Output File'
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error', msg)
			else:
				print(msg)
			return
		self.layer = coastalmeqgis_find_layer(self.cboResult.currentText())
		if self.layer is None and self.cboResult.currentText() not in self.tuView.tuResults.tuResults1D.results1d:
			msg = 'Cannot Find Result File in QGIS: {0}'.format(self.cboResult.currentText())
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error', msg)
			else:
				print(msg)
			return
		if self.layer and self.layer.type() != QgsMapLayer.MeshLayer and not isinstance(self.layer, NetCDFGrid):
			msg = 'Error finding Result Layer: {0}'.format(self.cboResult.currentText())
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error',  msg)
			else:
				print(msg)
			return
		if not os.path.exists(os.path.dirname(self.editOutput.text())) and not preview:
			msg = 'Could Not Find Output Folder:\n{0}'.format(self.editOutput.text())
			if self.tuView.iface is not None:
				QMessageBox.information(self, 'Input Error', msg)
			else:
				print(msg)
			return

		# Layout Tab
		for i in range(self.tableImages.rowCount()):
			if not os.path.exists(self.tableImages.item(i, 0).text()):
				msg = 'Cannot Find Image:\n{0}'.format(self.tableImages.cellWidget(i, 0).layout().itemAt(1).widget().text())
				if self.tuView.iface is not None:
					QMessageBox.information(self, 'Input Error', msg)
				else:
					print(msg)
				return
		if self.radLayoutCustom.isChecked():
			if not os.path.exists(self.editTemplate.text()):
				msg = 'Cannot Find Custom Layout Template:\n{0}'.format(self.editTemplate.text())
				if self.tuView.iface is not None:
					QMessageBox.information(self, 'Input Error', msg)
				else:
					print(msg)
				return
		if self.groupTime.isChecked():
			if self.le_time_format.text():
				try:
					_ = datetime.now().strftime(self.le_time_format.text())
				except Exception as e:
					if self.tuView.iface is not None:
						QMessageBox.information(self, 'Input Error', 'Invalid Time Format: error message - {0}'.format(e))
					else:
						print('Invalid Time Format: error message - {0}'.format(e))
					return

		# Video Tab
		if not preview:
			if self.radFfmpegSystem.isChecked():
				self.ffmpeg_bin = "ffmpeg"
				# debian systems use avconv (fork of ffmpeg)
				if which(self.ffmpeg_bin) is None:
					self.ffmpeg_bin = "avconv"
			else:
				self.ffmpeg_bin = self.editFfmpegPath.text()  # custom path
				if not self.ffmpeg_bin:
					msg = 'Missing FFmpeg exe Location'
					if self.tuView.iface is not None:
						QMessageBox.information(self, 'Input Error', msg)
					else:
						print(msg)
					return
				elif not os.path.exists(self.ffmpeg_bin):
					msg = 'Could Not Find FFmpeg exe:\n{0}'.format(self.ffmpeg_bin)
					if self.tuView.iface is not None:
						QMessageBox.information(self, 'Input Error', msg)
					else:
						print(msg)
					return

			if which(self.ffmpeg_bin) is None:
				QMessageBox.warning(self, "FFmpeg missing",
									"The tool for video creation (<a href=\"http://en.wikipedia.org/wiki/FFmpeg\">FFmpeg</a>) "
									"is missing. Please check your FFmpeg configuration in <i>Video</i> tab.<p>"
									"<b>Windows users:</b> Let the COASTALME plugin download FFmpeg automatically (by clicking OK).<p>"
									"<b>Linux users:</b> Make sure FFmpeg is installed in your system - usually a package named "
									"<tt>ffmpeg</tt>. On Debian/Ubuntu systems FFmpeg was replaced by Libav (fork of FFmpeg) "
									"- use <tt>libav-tools</tt> package.<p>"
									"<b>MacOS users:</b> Make sure FFmpeg is installed in your system <tt>brew install ffmpeg</tt>")

				if platform.system() != 'Windows':
					return

				# special treatment for Windows users!
				# offer automatic download and installation from Lutra web.
				# Official distribution is not used because:
				# 1. packages use 7zip compression (need extra software)
				# 2. packages contain extra binaries we do not need

				msg = "Would you like to download and auto-configure FFmpeg?\n\n" \
					  "The download may take some time (~70 MB).\n" \
					  "FFmpeg will be downloaded to the COASTALME plugin's directory."
				if self.tuView.iface is not None:
					reply = QMessageBox.question(self,
												 'Download FFmpeg',
												 msg,
												 QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO, QT_MESSAGE_BOX_YES)
				else:
					reply = input(f'{msg}\n(Y/N)\n')
					if reply.lower() == 'y':
						reply = QT_MESSAGE_BOX_YES
					else:
						reply = QT_MESSAGE_BOX_NO
				if reply != QT_MESSAGE_BOX_YES:
					return

				self.ffmpeg_bin = downloadFfmpeg(self)
				if not self.ffmpeg_bin:
					return

				# configure the path automatically
				self.radFfmpegCustom.setChecked(True)
				self.editFfmpegPath.setText(self.ffmpeg_bin)
				s = QSettings()
				s.setValue("COASTALME/animation_ffmpeg_switch", "custom")
				s.setValue("COASTALME/animation_ffmpeg", self.ffmpeg_bin)

		# check default on all cs / lp plots
		limits_not_set = [y for x, y in self.pbDialogs.items() if y.cboPlotType.text() == 'CS / LP' and not y.userSet]
		if limits_not_set and self.iface:
			answer = AxisLimitsMessage.warning(self)
			if answer == AxisLimitsMessage.Cancel:
				return
			elif answer == AxisLimitsMessage.UseTV:
				for plot_settings in limits_not_set:
					plot_settings.minmax_from_tv('x')
					plot_settings.minmax_from_tv('y')
					plot_settings.minmax_from_tv('y2')
					plot_settings.userSet = True
			elif answer == AxisLimitsMessage.Calc:
				pass  # default behaviour - do nothing
			else:
				return  # assume cancel

		self.run(preview)
	
	def updateProgress(self, i, cnt):
		""" callback from animation routine """
		self.progress.setMaximum(cnt)
		self.progress.setValue(i)
		qApp.processEvents()
	
	def quality(self):
		if self.radQualBest.isChecked():
			return 0
		elif self.radQualLow.isChecked():
			return 2
		else:  # high
			return 1
		
	def viewToolbar(self, plotType):
		if plotType == 'Time Series':
			return self.tuPlot.tuPlotToolbar.viewToolbarTimeSeries
		elif plotType == 'CS / LP':
			return self.tuPlot.tuPlotToolbar.viewToolbarLongPlot
		elif plotType == 'Cross Section':
			return self.tuPlot.tuPlotToolbar.viewToolbarCrossSection
		else:
			return None
		
	def plotAxisLimits(self, plotType, axis):
		if type == 'Time Series':
			plotNo = 0
		elif type == 'CS / LP':
			plotNo = 1
		else:
			return [], []
		
		parentLayout, figure, subplot, plotWidget, isSecondaryAxis, artists, labels, unit, yAxisLabelTypes, yAxisLabels, xAxisLabels, xAxisLimits, yAxisLimits = \
			self.tuView.tuPlot.plotEnumerator(plotNo)
		
		if axis == 'x':
			return subplot.get_xlim()
		elif axis == 'y1':
			return subplot.get_ylim()
		elif axis == 'y2':
			subplot2 = self.tuView.tuPlot.getSecondaryAxis()
			return subplot2.get_ylim()
		
	def getResultType(self, plotType, label):
		rt = label
		if plotType == 'Time Series':
			for resultType, userLabel in self.tuView.tuPlot.frozenTSProperties.items():
				if userLabel[0] == label:
					rt = resultType
					break
		elif plotType == 'CS / LP':
			for resultType, userLabel in self.tuView.tuPlot.frozenLPProperties.items():
				if userLabel[0] == label:
					rt = resultType
					break
		
		if plotType == 'Time Series':
			plotNo = 0
		elif plotType == 'CS / LP':
			plotNo = 1
		
		for t in self.tuView.tuPlot.tuPlotToolbar.getItemsFromPlotOptions(0):
			if t in rt:
				return t  # e.g. 'Water Level point 1' returns 'Water Level'
		
		
	def run(self, preview=False):
		"""
		Run tool to create animation
		
		:return: void
		"""

		qv = Qgis.QGIS_VERSION_INT

		if not preview:
			if self.tuView.iface is not None:
				self.buttonBox.setEnabled(False)  # disable button box so users know something is happening
				QApplication.setOverrideCursor(QT_CURSOR_WAIT)
		
		# save plot settings so line colours won't vary over time
		#self.tuView.tuPlot.setNewPlotProperties(0)
		#self.tuView.tuPlot.setNewPlotProperties(1)
		
		# get results
		asd = self.cboScalar.currentText()
		avd = self.cboVector.currentText()
		if asd == '-None-':
			asd = -1
		if avd == '-None-':
			avd = -1
		#for i in range(self.layer.dataProvider().datasetGroupCount()):
		#	if self.layer.dataProvider().datasetGroupMetadata(i).name() == asd:
		#		asd = i
		#	if self.layer.dataProvider().datasetGroupMetadata(i).name() == avd:
		#		avd = i
		nc_grid = False
		n = self.layer.name() if self.layer else self.cboResult.currentText()
		for resultType in self.tuView.tuResults.results[n]:
			if resultType == '_nc_grid':
				nc_grid = True
				asd = -1
				break
			if resultType == asd:
				for time in self.tuView.tuResults.results[self.layer.name()][resultType]['times']:
					asd = self.tuView.tuResults.results[self.layer.name()][resultType]['times'][time][-1].group()
			if resultType == avd:
				for time in self.tuView.tuResults.results[self.layer.name()][resultType]['times']:
					avd = self.tuView.tuResults.results[self.layer.name()][resultType]['times'][time][-1].group()
		ts_res = False
		if asd == -1 and avd == -1 and n in self.tuView.tuResults.tuResults1D.results1d:
			ts_res = True

		# particles
		ptm_res = []  # particles dataprovider
		# ptm = '{0}_ptm.nc'.format(self.layer.name())
		ptms = [x.name() for x in QgsProject.instance().layerTreeRoot().findLayers() if re.findall(r'_ptm\.nc', x.name(), flags=re.IGNORECASE)]
		for ptm in ptms:
			if ptm in self.tuView.tuResults.results:
				if ptm in self.tuView.tuResults.tuResultsParticles.resultsParticles:
					# ptm_res = self.tuView.tuResults.tuResultsParticles.resultsParticles[ptm]
					ptm_res.append(self.tuView.tuResults.tuResultsParticles.resultsParticles[ptm])

		# Get start and end time
		if qv >= 31600:
			if asd != -1:
				resultType = self.layer.dataProvider().datasetGroupMetadata(asd).name()
			elif avd != -1:
				resultType = self.layer.dataProvider().datasetGroupMetadata(avd).name()
			elif nc_grid:
				resultType = self.cboScalar.currentText()
			elif ts_res:
				resultType = None
			else:
				resultType = 'Bed Elevation'
		rt = self.tuView.tuResults.results[n][
			'referenceTime'] if 'referenceTime' in self.tuView.tuResults.results else self.tuView.tuOptions.zeroTime
		if qv < 31600:
			if self.tuView.tuOptions.xAxisDates:
				tStart = self.tuView.tuPlot.convertDateToTime(self.cboStart.currentText(),
				                                              unit=self.tuView.tuOptions.timeUnits)
				tEnd = self.tuView.tuPlot.convertDateToTime(self.cboEnd.currentText(),
				                                            unit=self.tuView.tuOptions.timeUnits)
			else:
				tStart = convertFormattedTimeToTime(self.cboStart.currentText(),
				                                    unit=self.tuView.tuOptions.timeUnits)
				tEnd = convertFormattedTimeToTime(self.cboEnd.currentText(),
				                                  unit=self.tuView.tuOptions.timeUnits)
		else:
			if self.tuView.tuOptions.xAxisDates:
				tStart = datetime.strptime(self.cboStart.currentText(), self.tuView.tuResults.dateFormat)
				tEnd = datetime.strptime(self.cboEnd.currentText(), self.tuView.tuResults.dateFormat)
			else:
				tStart = convertFormattedTimeToTime(self.cboStart.currentText(),
				                                    unit=self.tuView.tuOptions.timeUnits)
				tEnd = convertFormattedTimeToTime(self.cboEnd.currentText(),
				                                  unit=self.tuView.tuOptions.timeUnits)
				if self.tuView.tuOptions.timeUnits == 's':
					tStart = rt + timedelta(seconds=tStart)
					tEnd = rt + timedelta(seconds=tEnd)
				else:
					try:
						tStart = rt + timedelta(hours=tStart)
						tEnd = rt + timedelta(hours=tEnd)
					except OverflowError:
						tStart = rt + timedelta(seconds=tStart)
						tEnd = rt + timedelta(seconds=tEnd)
		#tStart = self.cboStart.currentText().split(':')
		#tStart = float(tStart[0]) + float(tStart[1]) / 60 + float(tStart[2]) / 3600
		#tStartKey = '{0:.4f}'.format(tStart)
		#tEnd = self.cboEnd.currentText().split(':')
		#tEnd = float(tEnd[0]) + float(tEnd[1]) / 60 + float(tEnd[2]) / 3600
		#tEndKey = '{0:.4f}'.format(tEnd)
		
		# Get video settings
		w = self.spinWidth.value()  # width
		h = self.spinHeight.value()  # height
		fps = self.spinSpeed.value()  # frames per second
		target_dur = self.sbTargetDur.value()  # target duration (sec)
		m1 = self.cbMethod1.isChecked()  # use method 1 (original method)
		
		# Get output directory for images
		tmpdir = tempfile.mkdtemp(prefix='coastalme')
		img_output_tpl = os.path.join(tmpdir, "%03d.png")
		tmpl = None  # path to template file to be used
		
		# get output for animation
		output_file = self.editOutput.text()
		QSettings().setValue('COASTALME/animation_outfolder', output_file)
		
		# Get Map Layout properties
		titleProp = {}
		if self.groupTitle.isChecked():
			titleProp['label'] = self.labelTitle.text()
			titleProp['font'] = self.fbtnTitle.currentFont()
			titleProp['font colour'] = self.colorTitleText.color()
			titleProp['background'] = self.cbTitleBackground.isChecked()
			titleProp['background color'] = self.colorTitleBackground.color()
			titleProp['frame'] = self.cbTitleFrame.isChecked()
			titleProp['frame color'] = self.colorTitleFrame.color()
			titleProp['position'] = self.cboPosTitle.currentIndex()
		timeProp = {}
		if self.groupTime.isChecked():
			timeProp['format'] = self.le_time_format.text()
			timeProp['label'] = self.labelTime.text()
			timeProp['font'] = self.fbtnTime.currentFont()
			timeProp['font colour'] = self.colorTimeText.color()
			timeProp['background'] = self.cbTimeBackground.isChecked()
			timeProp['background color'] = self.colorTimeBackground.color()
			timeProp['frame'] = self.cbTimeFrame.isChecked()
			timeProp['frame color'] = self.colorTimeFrame.color()
			timeProp['position'] = self.cboPosTime.currentIndex()
		legendProp = {}
		if self.groupLegend.isChecked():
			legendProp['label'] = self.labelLegend.text()
			legendProp['font'] = self.fbtnLegend.currentFont()
			legendProp['font colour'] = self.colorLegendText.color()
			legendProp['background'] = self.cbLegendBackground.isChecked()
			legendProp['background color'] = self.colorLegendBackground.color()
			legendProp['frame'] = self.cbLegendFrame.isChecked()
			legendProp['frame color'] = self.colorLegendFrame.color()
			legendProp['position'] = self.cboPosLegend.currentIndex()
		layout = {}
		if self.radLayoutDefault.isChecked():
			layout['type'] = 'default'
			layout['file'] = None
			if self.groupTitle.isChecked():
				layout['title'] = titleProp
			if self.groupTime.isChecked():
				layout['time'] = timeProp
			if self.groupLegend.isChecked():
				layout['legend'] = legendProp
		else:
			layout['type'] = 'file'
			layout['file'] = self.editTemplate.text()
			
		# Get Plot Data
		if self.groupPlot.isChecked():
			plot = {}
			plotCount = 0
			for i in range(self.tablePlots.rowCount()):
				plotDict = {}
				plotDict['labels'] = self.tablePlots.item(i, 1).text().split(';;')
				plotDict['type'] = self.tablePlots.item(i, 0).text()
				plotDict['position'] = self.tablePlots.item(i, 2).text()
				plotDict['properties'] = self.pbDialogs[self.tablePlots.cellWidget(i, 3)]
				plot[plotCount] = plotDict
				plotCount += 1
			if plot:
				layout['plots'] = plot
			graphics = {}
			for i in range(self.tableGraphics.rowCount()):
				cb = self.tableGraphics.item(i, 0)
				if cb.checkState() == QT_CHECKED:
					graphicDict = {}
					label = self.tableGraphics.item(i, 0)
					graphic = self.label2graphic[label.text()]
					userLabel = self.tableGraphics.item(i, 1).text()
					position = self.tableGraphics.item(i, 2).text()
					font = self.rowNo2fntDialog[i]
					graphicDict['id'] = label.text()
					graphicDict['user label'] = userLabel
					graphicDict['position'] = position
					graphicDict['font'] = font.fntButton.currentFont()
					graphicDict['font colour'] = font.fntColor.color()
					graphicDict['background'] = font.cbBackground.isChecked()
					graphicDict['background color'] = font.backgroundColor.color()
					graphicDict['frame'] = font.cbFrame.isChecked()
					graphicDict['frame color'] = font.frameColor.color()
					if 'TS' in label.text():
						graphicDict['type'] = 'marker'
					elif 'CS' in label.text():
						graphicDict['type'] = 'rubberband profile'
					elif 'Flow' in label.text():
						graphicDict['type'] = 'rubberband flow'
					elif 'Curtain' in label.text():
						graphicDict['type'] = 'curtain'
					elif 'Vert Profile' in label.text():
						graphicDict['type'] = 'marker'
					graphics[graphic] = graphicDict
			if graphics:
				layout['graphics'] = graphics
			
		# Get Image Data
		if self.groupImages.isChecked():
			image = {}
			imageCount = 0
			for i in range(self.tableImages.rowCount()):
				imageDict = {
					'source': self.tableImages.item(i, 0).text(),
					'position': self.tableImages.item(i, 1).text(),
					'properties': self.pbDialogsImage[self.tableImages.cellWidget(i, 2)]
				}
				image[imageCount] = imageDict
				imageCount += 1
			layout['images'] = image
		
		prog = lambda i, count: self.updateProgress(i, count)  # progress bar

		timesteps = []
		if qv < 31600:
			for i in range(self.cboStart.count()):
				if self.tuView.tuOptions.xAxisDates:
					timeconverted = self.tuView.tuPlot.convertDateToTime(self.cboStart.itemText(i),
					                                                          unit=self.tuView.tuOptions.timeUnits)
					if timeconverted == -99999.:
						QMessageBox.information(self, 'Input Error', 'Error converting input start date')
						return
				else:
					timeconverted = convertFormattedTimeToTime(self.cboStart.itemText(i),
					                                                unit=self.tuView.tuOptions.timeUnits)
					if timeconverted == -99999.:
						QMessageBox.information(self, 'Input Error', 'Error converting input start date')
						return
				timesteps.append(timeconverted)
		else:
			for i in range(self.cboStart.count()):
				if self.tuView.tuOptions.xAxisDates:
					date = datetime.strptime(self.cboStart.itemText(i), self.tuView.tuResults.dateFormat)
				else:
					timeconverted = convertFormattedTimeToTime(self.cboStart.itemText(i),
					                                           unit=self.tuView.tuOptions.timeUnits)
					if timeconverted == -99999.:
						QMessageBox.information(self, 'Input Error', 'Error converting input start date')
						return
					if self.tuView.tuOptions.timeUnits == 's':
						date = rt + timedelta(seconds=timeconverted)
					else:
						try:
							date = rt + timedelta(hours=timeconverted)
						except OverflowError:
							date = rt + timedelta(seconds=timeconverted)
				timesteps.append(date)

		# put collected data into dictionary for easy access later
		d = {'layer': self.layer,
			 'name': n,
			 'time': (tStart, tEnd),
			 'img_size': (w, h),
			 'tmp_imgfile': img_output_tpl,
			 # 'layers': self.canvas.layers(),
			 'layers': self.layers,
			 # 'extent': self.canvas.extent(),
			 'extent': self.extent,
			 # 'crs': self.canvas.mapSettings().destinationCrs(),
			 'crs': self.crs,
			 'layout': layout,
			 'nc_grid': nc_grid,
		     'scalar index': asd,
		     'vector index': avd,
		     'active scalar': self.cboScalar.currentText(),
		     'tmpdir': os.path.dirname(img_output_tpl),
		     'particles': ptm_res,
		     'turesults': self.tuView.tuResults,
		     'timesteps': timesteps,
		     'rendered': self.mesh_rendered,
			 }
		if qv >= 31600:
			d['reference_time'] = rt

		for pb, dialog in self.pbDialogs.items():
			dialog.setDefaults(self, self.dialog2Plot[dialog][0].text(), self.dialog2Plot[dialog][1].text().split(';;'),
			                   xAxisDates=self.tuView.tuOptions.xAxisDates)
		self.layout = animation(d, self.iface, prog, self, preview)
		self.tuView.tuPlot.updateCurrentPlot(0, retain_flow=True)
		self.tuView.tuPlot.updateCurrentPlot(1)
		
		if preview:
			self.iface.openLayoutDesigner(layout=self.layout)
		else:
			if m1:
				ffmpeg_res, logfile = images_to_video(img_output_tpl, output_file, fps, self.quality(), self.ffmpeg_bin)
			else:
				if os.path.splitext(output_file)[1].upper() == '.GIF':
					ffmpeg_res, logfile = images_to_video_gif(img_output_tpl, output_file, fps, self.quality(),
					                                          self.ffmpeg_bin, target_dur)
				else:
					# remove lossless - doesn't seem to work very well and doesn't support mp4
					ffmpeg_res, logfile = images_to_video2(img_output_tpl, output_file, fps, max(1, self.quality()), self.ffmpeg_bin,
					                                       target_dur)
			
			if ffmpeg_res:
				shutil.rmtree(tmpdir)

			if self.tuView.iface is not None:
				QApplication.restoreOverrideCursor()
			
			self.updateProgress(0, 1)

			if self.tuView.iface is not None:
				self.buttonBox.setEnabled(True)
			
			if ffmpeg_res:
				msg = "The export of animation was successful!"
				if self.tuView.iface is not None:
					QMessageBox.information(self, "Export", msg)
				else:
					print(msg)
			else:
				msg = "An error occurred when converting images to video. " \
				      "The images are still available in " + tmpdir + "\n\n" \
				      "This should not happen. Please email support@coastalme.com " \
				      "with the contents from the log file:\n" + logfile
				if self.tuView.iface is not None:
					QMessageBox.warning(self, "Export", msg)
				else:
					print(msg)
			
			self.storeDefaults()
			
			self.accept()
			
	def storeDefaults(self):
		"""
		Store inputs in project.
		
		:return: void
		"""
		
		# General Tab
		self.project.writeEntry("COASTALME", 'start_time', self.cboStart.currentText())
		self.project.writeEntry("COASTALME", 'end_time', self.cboEnd.currentText())
		self.project.writeEntry("COASTALME", 'result_name', self.cboResult.currentText())
		self.project.writeEntry("COASTALME", 'result_scalar', self.cboScalar.currentText())
		self.project.writeEntry("COASTALME", 'result_vector', self.cboVector.currentText())
		self.project.writeEntry("COASTALME", 'video_width', self.spinWidth.value())
		self.project.writeEntry("COASTALME", 'video_height', self.spinHeight.value())
		self.project.writeEntry("COASTALME", 'video_fps', self.spinSpeed.value())
		self.project.writeEntry("COASTALME", 'output_file', self.editOutput.text())
		
		# Layout
		layout_type = 'default' if self.radLayoutDefault.isChecked() else 'custom'
		self.project.writeEntry("COASTALME", 'layout_type', layout_type)
		self.project.writeEntry("COASTALME", 'custom_template_path', self.editTemplate.text())
		# title
		self.project.writeEntry("COASTALME", 'title_cb', self.groupTitle.isChecked())
		self.project.writeEntry("COASTALME", 'title_label', self.labelTitle.text())
		self.project.writeEntry("COASTALME", 'title_font_name', self.fbtnTitle.currentFont().family())
		self.project.writeEntry("COASTALME", 'title_font_size', self.fbtnTitle.currentFont().pointSize())
		self.project.writeEntry("COASTALME", 'title_font_bold', self.fbtnTitle.currentFont().bold())
		if is_qt6:
			self.project.writeEntry("COASTALME", 'title_font_italic', self.fbtnTitle.currentFont().style().value)
		else:
			self.project.writeEntry("COASTALME", 'title_font_italic', self.fbtnTitle.currentFont().style())
		self.project.writeEntry("COASTALME", 'title_font_strikeout', self.fbtnTitle.currentFont().strikeOut())
		self.project.writeEntry("COASTALME", 'title_font_underline', self.fbtnTitle.currentFont().underline())
		self.project.writeEntry("COASTALME", 'title_font_color', self.colorTitleText.color().name())
		self.project.writeEntry("COASTALME", 'title_background_cb', self.cbTitleBackground.isChecked())
		self.project.writeEntry("COASTALME", 'title_background_color', self.colorTitleBackground.color().name())
		self.project.writeEntry("COASTALME", 'title_background_position', self.cboPosTitle.currentIndex())
		self.project.writeEntry("COASTALME", 'title_border_cb', self.cbTitleFrame.isChecked())
		self.project.writeEntry("COASTALME", 'title_border_color', self.colorTitleFrame.color().name())
		
		# time
		self.project.writeEntry("COASTALME", 'time_cb', self.groupTime.isChecked())
		self.project.writeEntry("COASTALME", 'time_label', self.labelTime.text())
		self.project.writeEntry("COASTALME", 'time_font_name', self.fbtnTime.currentFont().family())
		self.project.writeEntry("COASTALME", 'time_font_size', self.fbtnTime.currentFont().pointSize())
		self.project.writeEntry("COASTALME", 'time_font_bold', self.fbtnTime.currentFont().bold())
		if is_qt6:
			self.project.writeEntry("COASTALME", 'time_font_italic', self.fbtnTime.currentFont().style().value)
		else:
			self.project.writeEntry("COASTALME", 'time_font_italic', self.fbtnTime.currentFont().style())
		self.project.writeEntry("COASTALME", 'time_font_strikeout', self.fbtnTime.currentFont().strikeOut())
		self.project.writeEntry("COASTALME", 'time_font_underline', self.fbtnTime.currentFont().underline())
		self.project.writeEntry("COASTALME", 'time_font_color', self.colorTimeText.color().name())
		self.project.writeEntry("COASTALME", 'time_background_cb', self.cbTimeBackground.isChecked())
		self.project.writeEntry("COASTALME", 'time_background_color', self.colorTimeBackground.color().name())
		self.project.writeEntry("COASTALME", 'time_background_position', self.cboPosTime.currentIndex())
		self.project.writeEntry("COASTALME", 'time_border_cb', self.cbTimeFrame.isChecked())
		self.project.writeEntry("COASTALME", 'time_border_color', self.colorTimeFrame.color().name())
		
		# legend
		self.project.writeEntry("COASTALME", 'legend_cb', self.groupLegend.isChecked())
		self.project.writeEntry("COASTALME", 'legend_label', self.labelLegend.text())
		self.project.writeEntry("COASTALME", 'legend_font_name', self.fbtnLegend.currentFont().family())
		self.project.writeEntry("COASTALME", 'legend_font_size', self.fbtnLegend.currentFont().pointSize())
		self.project.writeEntry("COASTALME", 'legend_font_bold', self.fbtnLegend.currentFont().bold())
		if is_qt6:
			self.project.writeEntry("COASTALME", 'legend_font_italic', self.fbtnLegend.currentFont().style().value)
		else:
			self.project.writeEntry("COASTALME", 'legend_font_italic', self.fbtnLegend.currentFont().style())
		self.project.writeEntry("COASTALME", 'legend_font_strikeout', self.fbtnLegend.currentFont().strikeOut())
		self.project.writeEntry("COASTALME", 'legend_font_underline', self.fbtnLegend.currentFont().underline())
		self.project.writeEntry("COASTALME", 'legend_font_color', self.colorLegendText.color().name())
		self.project.writeEntry("COASTALME", 'legend_background_cb', self.cbLegendBackground.isChecked())
		self.project.writeEntry("COASTALME", 'legend_background_color', self.colorLegendBackground.color().name())
		self.project.writeEntry("COASTALME", 'legend_background_position', self.cboPosLegend.currentIndex())
		self.project.writeEntry("COASTALME", 'legend_border_cb', self.cbLegendFrame.isChecked())
		self.project.writeEntry("COASTALME", 'legend_border_color', self.colorLegendFrame.color().name())
		
		# Plots
		self.project.writeEntry("COASTALME", 'plots_cb', self.groupPlot.isChecked())
		self.project.writeEntry("COASTALME", 'number_of_plots', self.tablePlots.rowCount())
		for i in range(self.tablePlots.rowCount()):
			self.project.writeEntry("COASTALME", 'plot_{0}_type'.format(i), self.tablePlots.item(i, 0).text())
			self.project.writeEntry("COASTALME", 'plot_{0}_items'.format(i), self.tablePlots.item(i, 1).text().split(';;'))
			self.project.writeEntry("COASTALME", 'plot_{0}_position'.format(i), self.tablePlots.item(i, 2).text())
			p = self.pbDialogs[self.tablePlots.cellWidget(i, 3)]
			self.project.writeEntry("COASTALME", 'plot_{0}_title'.format(i), p.leTitle.text())
			self.project.writeEntry("COASTALME", 'plot_{0}_xlabel'.format(i), p.leXLabel.text())
			self.project.writeEntry("COASTALME", 'plot_{0}_ylabel'.format(i), p.leYLabel.text())
			self.project.writeEntry("COASTALME", 'plot_{0}_y2label'.format(i), p.leY2Label.text())
			self.project.writeEntry("COASTALME", 'plot_{0}_xmin'.format(i), int(p.sbXmin.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_xmax'.format(i), int(p.sbXMax.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_year'.format(i), p.dteXmin.dateTime().date().year())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_month'.format(i), p.dteXmin.dateTime().date().month())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_day'.format(i), p.dteXmin.dateTime().date().day())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_hour'.format(i), p.dteXmin.dateTime().time().hour())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_minute'.format(i), p.dteXmin.dateTime().time().minute())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_second'.format(i), p.dteXmin.dateTime().time().second())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemin_msecond'.format(i), p.dteXmin.dateTime().time().msec())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_year'.format(i), p.dteXMax.dateTime().date().year())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_month'.format(i), p.dteXMax.dateTime().date().month())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_day'.format(i), p.dteXMax.dateTime().date().day())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_hour'.format(i), p.dteXMax.dateTime().time().hour())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_minute'.format(i), p.dteXMax.dateTime().time().minute())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_second'.format(i), p.dteXMax.dateTime().time().second())
			self.project.writeEntry("COASTALME", 'plot_{0}_xdatemax_msecond'.format(i), p.dteXMax.dateTime().time().msec())
			self.project.writeEntry("COASTALME", 'plot_{0}_xaxis_rotation'.format(i), p.sbXAxisRotation.value())
			self.project.writeEntry("COASTALME", 'plot_{0}_ymin'.format(i), int(p.sbYMin.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_ymax'.format(i), int(p.sbYMax.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_y2min'.format(i), int(p.sbY2Min.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_y2max'.format(i), int(p.sbY2Max.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_legend_cb'.format(i), p.cbLegend.isChecked())
			self.project.writeEntry("COASTALME", 'plot_{0}_legend_pos'.format(i), p.cboLegendPos.currentIndex())
			self.project.writeEntry("COASTALME", 'plot_{0}_ygrid'.format(i), p.cbGridY.isChecked())
			self.project.writeEntry("COASTALME", 'plot_{0}_xgrid'.format(i), p.cbGridX.isChecked())
			self.project.writeEntry("COASTALME", 'plot_{0}_xsize'.format(i), int(p.sbFigSizeX.value()))
			self.project.writeEntry("COASTALME", 'plot_{0}_ysize'.format(i), int(p.sbFigSizeY.value()))
			
		# Graphics
		self.project.writeEntry("COASTALME", "number_of_graphics", self.tableGraphics.rowCount())
		for i in range(self.tableGraphics.rowCount()):
			self.project.writeEntry("COASTALME", "graphic_{0}_cb".format(i), self.tableGraphics.item(i, 0).checkState())
			self.project.writeEntry("COASTALME", "graphic_{0}_user_label".format(i), self.tableGraphics.item(i, 1).text())
			self.project.writeEntry("COASTALME", "graphic_{0}_position".format(i), self.tableGraphics.item(i, 2).text())
			p = self.rowNo2fntDialog[i]
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_name'.format(i), p.fntButton.currentFont().family())
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_size'.format(i), p.fntButton.currentFont().pointSize())
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_bold'.format(i), p.fntButton.currentFont().bold())
			if is_qt6:
				self.project.writeEntry("COASTALME", 'graphic_{0}_font_italic'.format(i), p.fntButton.currentFont().style().value)
			else:
				self.project.writeEntry("COASTALME", 'graphic_{0}_font_italic'.format(i), p.fntButton.currentFont().style())
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_strikeout'.format(i), p.fntButton.currentFont().strikeOut())
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_underline'.format(i), p.fntButton.currentFont().underline())
			self.project.writeEntry("COASTALME", 'graphic_{0}_font_color'.format(i), p.fntColor.color().name())
			self.project.writeEntry("COASTALME", 'graphic_{0}_background_cb'.format(i), p.cbBackground.isChecked())
			self.project.writeEntry("COASTALME", 'graphic_{0}_background_color'.format(i), p.backgroundColor.color().name())
			
		# Images
		self.project.writeEntry("COASTALME", 'images_cb', self.groupImages.isChecked())
		self.project.writeEntry("COASTALME", 'number_of_images', self.tableImages.rowCount())
		for i in range(self.tableImages.rowCount()):
			self.project.writeEntry("COASTALME", 'image_{0}_source'.format(i), self.tableImages.item(i, 0).text())
			self.project.writeEntry("COASTALME", 'image_{0}_position'.format(i), self.tableImages.item(i, 1).text())
			p = self.pbDialogsImage[self.tableImages.cellWidget(i, 2)]
			self.project.writeEntry("COASTALME", 'image_{0}_use_original_size'.format(i), p.rbUseOriginalSize.isChecked())
			self.project.writeEntry("COASTALME", 'image_{0}_resize_image'.format(i), p.rbResizeImage.isChecked())
			self.project.writeEntry("COASTALME", 'image_{0}_xsize'.format(i), p.sbSizeX.value())
			self.project.writeEntry("COASTALME", 'image_{0}_ysize'.format(i), p.sbSizeY.value())
			self.project.writeEntry("COASTALME", 'image_{0}_maintain_aspect_ratio'.format(i), p.cbKeepAspectRatio.isChecked())
		
		# Video Tab
		if self.radQualBest.isChecked():
			quality = 'best'
		elif self.radQualHigh.isChecked():
			quality = 'high'
		else:
			quality = 'low'
		self.project.writeEntry("COASTALME", 'video_quality', quality)
		ffmpeg_path = 'default' if self.radFfmpegSystem.isChecked() else 'custom'
		QSettings().setValue("COASTALME/animation_ffmpeg_switch", ffmpeg_path)
		QSettings().setValue("COASTALME/animation_ffmpeg", self.ffmpeg_bin)
	
class PlotProperties(QDialog, Ui_PlotProperties):
	
	def __init__(self, animationDialog, cboPlotType, mcboPlotItems, datetime=False, caller='animation'):
		QDialog.__init__(self)
		self.setupUi(self)
		self.userSet = False  # once user has entered properties and left once, don't update anymore
		self.cross_section_y_axis1_limits_set = cboPlotType.text() != 'CS / LP'
		self.cross_section_y_axis2_limits_set = cboPlotType.text() != 'CS / LP'

		self.dynamicYAxis = False
		self.xUseMatplotLibDefault = False
		self.yUseMatplotLibDefault = False
		self.animationDialog = animationDialog
		self.cboPlotType = cboPlotType
		self.mcboPlotItems = mcboPlotItems
		self.caller = caller
		
		self.datetime = datetime
		if datetime:
			self.dteXmin.setVisible(True)
			self.dteXMax.setVisible(True)
			self.sbXmin.setVisible(False)
			self.sbXMax.setVisible(False)
			self.sbXAxisRotation.setVisible(True)
			self.label_17.setVisible(True)
			self.horizontalWidget.setVisible(True)
			self.sbXAxisRotation.setValue(animationDialog.tuView.tuOptions.xAxisLabelRotation)
		else:
			self.dteXmin.setVisible(False)
			self.dteXMax.setVisible(False)
			self.sbXmin.setVisible(True)
			self.sbXMax.setVisible(True)
			self.sbXAxisRotation.setVisible(False)
			self.label_17.setVisible(False)
			self.horizontalWidget.setVisible(False)
		self.resize(self.minimumSizeHint())
		
		self.pbAutoCalcXLim.clicked.connect(lambda event: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'x limits'))
		self.pbAutoCalcYLim.clicked.connect(lambda event: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'y limits'))
		self.pbAutoCalcY2Lim.clicked.connect(lambda event: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'y2 limits'))
		self.pbAutoCalcX2Lim.clicked.connect(lambda event: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'x2 limits'))
		self.buttonBox.accepted.connect(self.userSetTrue)

	def show_(self):
		b = self.cboPlotType.text() == 'Vert Profile'
		self.label_18.setVisible(b)
		self.label_19.setVisible(b)
		self.sbX2min.setVisible(b)
		self.label_20.setVisible(b)
		self.sbX2Max.setVisible(b)
		self.pbAutoCalcX2Lim.setVisible(b)

		b = not b
		self.label_14.setVisible(b)
		self.label_15.setVisible(b)
		self.sbY2Min.setVisible(b)
		self.label_16.setVisible(b)
		self.sbY2Max.setVisible(b)
		self.pbAutoCalcY2Lim.setVisible(b)

		try:
			self.pbAutoCalcXLim.clicked.disconnect()
		except:
			pass
		try:
			self.pbAutoCalcYLim.clicked.disconnect()
		except:
			pass
		try:
			self.pbAutoCalcY2Lim.clicked.disconnect()
		except:
			pass

		if self.cboPlotType.text() == 'CS / LP':
			self.pbAutoCalcXLim.setText('From TV Plot')
			self.pbAutoCalcYLim.setText('From TV Plot')
			self.pbAutoCalcY2Lim.setText('From TV Plot')
			self.pbAutoCalcXLim.clicked.connect(lambda: self.minmax_from_tv('x'))
			self.pbAutoCalcYLim.clicked.connect(lambda: self.minmax_from_tv('y'))
			self.pbAutoCalcY2Lim.clicked.connect(lambda: self.minmax_from_tv('y2'))
		else:
			self.pbAutoCalcXLim.setText('Auto Calc')
			self.pbAutoCalcYLim.setText('Auto Calc')
			self.pbAutoCalcY2Lim.setText('Auto Calc')
			self.pbAutoCalcXLim.clicked.connect(lambda: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'not cross sections', static=False))
			self.pbAutoCalcYLim.clicked.connect(lambda: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'not cross sections', static=False))
			self.pbAutoCalcY2Lim.clicked.connect(lambda: self.setDefaults(self.animationDialog, self.cboPlotType, self.mcboPlotItems, 'not cross sections', static=False))

		self.exec()

	def minmax_from_tv(self, axis):
		from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot import TuPlot

		tuplot = self.animationDialog.tuView.tuPlot
		ax = tuplot.plotEnumerator(TuPlot.CrossSection)[2]
		ax2 = tuplot.getSecondaryAxis(TuPlot.CrossSection, create=False)
		if axis == 'x':
			xmin, xmax = ax.get_xlim()
			self.sbXmin.setValue(xmin)
			self.sbXMax.setValue(xmax)
		elif axis == 'y':
			ymin, ymax = ax.get_ylim()
			self.sbYMin.setValue(ymin)
			self.sbYMax.setValue(ymax)
		elif axis == 'y2' and ax2 is not None:
			ymin, ymax = ax2.get_ylim()
			self.sbY2Min.setValue(ymin)
			self.sbY2Max.setValue(ymax)

	def setDateTime(self, bDt):
		self.datetime = bDt
		if self.datetime:
			self.dteXmin.setVisible(True)
			self.dteXMax.setVisible(True)
			self.sbXmin.setVisible(False)
			self.sbXMax.setVisible(False)
			self.sbXAxisRotation.setVisible(True)
			self.label_17.setVisible(True)
			self.horizontalWidget.setVisible(True)
			self.sbXAxisRotation.setValue(self.animationDialog.tuView.tuOptions.xAxisLabelRotation)
		else:
			self.dteXmin.setVisible(False)
			self.dteXMax.setVisible(False)
			self.sbXmin.setVisible(True)
			self.sbXMax.setVisible(True)
			self.sbXAxisRotation.setVisible(False)
			self.label_17.setVisible(False)
			self.horizontalWidget.setVisible(False)
		self.resize(self.minimumSizeHint())

	def userSetTrue(self):
		self.xUseMatplotLibDefault = False
		self.userSet = True
		
	def applyPrevious(self, prop=None):
		
		if prop is not None:
			self.leTitle.setText(prop.leTitle.text())
			self.leXLabel.setText(prop.leXLabel.text())
			self.leYLabel.setText(prop.leYLabel.text())
			self.leY2Label.setText(prop.leY2Label.text())
			self.sbXmin.setValue(prop.sbXmin.value())
			self.sbXMax.setValue(prop.sbXMax.value())
			self.sbYMin.setValue(prop.sbYMin.value())
			self.sbYMax.setValue(prop.sbYMax.value())
			self.sbY2Min.setValue(prop.sbY2Min.value())
			self.sbY2Max.setValue(prop.sbY2Max.value())
			self.cbLegend.setChecked(prop.cbLegend.isChecked())
			self.cboLegendPos.setCurrentIndex(prop.cboLegendPos.currentIndex())
			self.cbGridY.setChecked(prop.cbGridY.isChecked())
			self.cbGridX.setChecked(prop.cbGridX.isChecked())
			self.sbFigSizeX.setValue(prop.sbFigSizeX.value())
			self.sbFigSizeY.setValue(prop.sbFigSizeY.value())
	
	def setDefaults(self, animation, plotType, items, recalculate='', static=False, activeScalar=None, xAxisDates=False,
	                time=None):
		from ..coastalmeqgis_tuviewer.coastalmeqgis_tuplot import TuPlot

		qv = Qgis.QGIS_VERSION_INT

		if self.caller == 'maps':
			static = True

		if type(plotType) is not str:
			if type(plotType) is QTableWidgetItem:
				plotType = plotType.text()
			else:
				plotType = plotType.currentText()
		if type(items) is not list:
			if type(items) is QTableWidgetItem:
				items = items.text().split(';;')
			else:
				items = items.checkedItems()
		
		li, la, ax = animation.plotItems(plotType)
		lines, labels, axis = [], [], []
		for item in items:
			if item == 'Active Dataset':
				if plotType == 'Vert Profile':
					self.leXLabel.setText(activeScalar)
				else:
					self.leYLabel.setText(activeScalar)
				self.dynamicYAxis = True
				self.xUseMatplotLibDefault = True
				self.yUseMatplotLibDefault = True
			if item == 'Active Dataset [Water Level for Depth]':
				if activeScalar == 'Depth':
					self.leYLabel.setText('Water Level')
				elif activeScalar == 'D':
					self.leYLabel.setText('H')
				else:
					self.leYLabel.setText(activeScalar)
				self.dynamicYAxis = True
				self.xUseMatplotLibDefault = True
				self.yUseMatplotLibDefault = True
			i = la.index(item) if la.count(item) else -1
			if i > -1:
				lines.append(li[i])
				labels.append(la[i])
				axis.append(ax[i])
		
		# X Axis Label
		if plotType == 'Time Series':
			if self.leXLabel.text() == 'Chainage' or not self.userSet:  # sitting on default or user hasn't made changes
				if xAxisDates:
					self.leXLabel.setText('Date')
				else:
					self.leXLabel.setText('Time')
		elif plotType == 'CS / LP':
			if self.leXLabel.text() == 'Time' or not self.userSet:  # sitting on default or user hasn't made changes
				self.leXLabel.setText('Chainage')
		elif plotType == 'Vert Profile':
			self.leYLabel.setText('Elevation')

		if time is not None:
			if plotType == 'CS / LP':
				animation.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection, draw=False, time=time,
				                                          mesh_rendered=False)
				lines, labels, axis = animation.plotItems(plotType)
				labels = [TuResults.stripMaximumName(TuResults.stripMinimumName(x)) for x in labels]
			elif plotType == 'Vert Profile':
				animation.tuView.tuPlot.updateCurrentPlot(TuPlot.VerticalProfile, draw=False, time=time,
				                                          mesh_rendered=False)
				lines, labels, axis = animation.plotItems(plotType)
				labels = [TuResults.stripMaximumName(TuResults.stripMinimumName(x)) for x in labels]

		# X Axis Limits
		if plotType == 'Time Series':
			if not self.userSet or recalculate == 'x limits':
				xmin = 999999
				xmax = -999999
				for item in items:
					if item != 'Current Time' and item != 'Culverts and Pipes':
						i = labels.index(item) if labels.count(item) else -1
						if i > -1:
							if type(lines[i]) is PolyCollection:
								xmin2, xmax2 = getPolyCollectionExtents(lines[i], axis='x')
							elif type(lines[i]) is Quiver:
								xmin2, xmax2 = getQuiverExtents(lines[i], axis='y')
							else:
								x = lines[i].get_xdata()
								xmin2, xmax2 = np.nanmin(x), np.nanmax(x)
								if self.animationDialog.tuView.tuOptions.xAxisDates:
									# if xmin2 in self.animationDialog.tuView.tuResults.date2time:
									# 	xmin2 = self.animationDialog.tuView.tuResults.date2time[xmin2]
									# else:
									# 	xmin2 = 999999
									# if xmax2 in self.animationDialog.tuView.tuResults.date2time:
									# 	xmax2 = self.animationDialog.tuView.tuResults.date2time[xmax2]
									# else:
									# 	xmax2 = -999999
									xmin2 = convert_datetime_to_float(xmin2)
									xmax2 = convert_datetime_to_float(xmax2)
							xmin = min(xmin, xmin2)
							xmax = max(xmax, xmax2)
							margin = (xmax - xmin) * 0.05
							xmin = xmin - margin
							xmax = xmax + margin
							if not self.datetime:
								self.sbXmin.setValue(xmin)
								self.sbXMax.setValue(xmax)
							else:
								# xmin = convertTimeToDate(self.animationDialog.tuView.tuOptions.zeroTime, xmin,
								#                          self.animationDialog.tuView.tuOptions.timeUnits)
								# xmax = convertTimeToDate(self.animationDialog.tuView.tuOptions.zeroTime, xmax,
								#                          self.animationDialog.tuView.tuOptions.timeUnits)
								xmin = convert_float_to_datetime(xmin)
								xmax = convert_float_to_datetime(xmax)
								self.dteXmin.setDateTime(xmin)
								self.dteXMax.setDateTime(xmax)
							break
						self.sbXmin.setValue(0)
						self.sbXMax.setValue(1)
				if xmin == 99999 or xmax == -99999:
					self.xUseMatplotLibDefault = True
		elif static:
			if plotType == 'CS / LP':
				if not self.userSet or recalculate == 'x limits':
					xmin = 999999
					xmax = -999999
					for item in items:
						i = labels.index(item) if labels.count(item) else -1
						if i > -1:
							if type(lines[i]) is matplotlib.lines.Line2D:
								x = lines[i].get_xdata()
								xmin = min(xmin, np.nanmin(x))
								xmax = max(xmax, np.nanmax(x))
							elif isinstance(lines[i], matplotlib.patches.Polygon):
								xy = lines[i].line.get_xy()
								x = xy[:, 0]
								xmin = min(xmin, np.nanmin(x))
								xmax = max(xmax, np.nanmax(x))
							elif type(lines[i]) is PolyCollection:
								xmin_t, xmax_t, = getPolyCollectionExtents(lines[i], axis='x')
								xmin = min(xmin, xmin_t)
								xmax = max(xmax, xmax_t)
							elif type(lines[i]) is Quiver:
								xmin_t, xmax_t, = getQuiverExtents(lines[i], axis='x')
								xmin = min(xmin, xmin_t)
								xmax = max(xmax, xmax_t)
					if xmin == 99999 or xmax == -99999:
						self.xUseMatplotLibDefault = True
					else:
						# margin = (xmax - xmin) * 0.05
						margin = max((xmax - xmin) * 0.05, 0.01)
						xmin = xmin - margin
						xmax = xmax + margin
						self.sbXmin.setValue(xmin)
						self.sbXMax.setValue(xmax)
			else:
				if not self.userSet or recalculate == 'y limits':
					ymin = 999999
					ymax = -999999
					for item in items:
						i = labels.index(item) if labels.count(item) else -1
						if i > -1:
							if type(lines[i]) is matplotlib.lines.Line2D:
								y = lines[i].get_ydata()
								ymin = min(ymin, np.nanmin(y))
								ymax = max(ymax, np.nanmax(y))
					if ymin == 99999 or ymax == -99999:
						self.yUseMatplotLibDefault = True
					else:
						# margin = (xmax - xmin) * 0.05
						margin = max((ymax - ymin) * 0.05, 0.01)
						ymin = ymin - margin
						ymax = ymax + margin
						self.sbYMin.setValue(ymin)
						self.sbYMax.setValue(ymax)
				
		# Y Axis Label
		if not self.userSet and not self.dynamicYAxis:
			if items:
				if 'axis 1' in axis and 'axis 2' in axis:
					for item in items:
						i = labels.index(item) if labels.count(item) else -1
						if i > -1:
							if axis[i] == 'axis 1':
								if '[Curtain]' in item:
									self.leYLabel.setText('Elevation')
								elif plotType == 'Vert Profile':
									self.leXLabel.setText(item)
								else:
									self.leYLabel.setText(item)
								break
				else:
					if '[Curtain]' in items[0]:
						self.leYLabel.setText('Elevation')
					elif plotType == 'Vert Profile':
						self.leXLabel.setText(items[0])
					else:
						self.leYLabel.setText(items[0])
				
		# Y2 Axis Label
		userSetY2 = True
		#if 'axis 1' in axis and 'axis 2' in axis:
		#	if self.sbY2Min.value() == 0 and self.sbY2Max.value() == 0:
		#		userSetY2 = False
		if (not self.userSet or not userSetY2) and not self.dynamicYAxis:
			if items:
				if 'axis 1' in axis and 'axis 2' in axis:
					for item in items:
						i = labels.index(item) if labels.count(item) else -1
						if i > -1:
							if axis[i] == 'axis 2':
								if plotType == 'Vert Profile':
									self.leX2Label.setText(item)
									break
								else:
									self.leY2Label.setText(item)
									break
					
		# Y and Y2 Axis limits
		if ((not self.userSet or not userSetY2) or recalculate == 'y limits' or recalculate == 'y2 limits' or
		    (recalculate == 'x limits' and plotType == 'CS / LP') or
		    (recalculate == 'x limits' and plotType == 'Vert Profile') or
		    (recalculate == 'x2 limits' and plotType == 'Vert Profile')) and not self.dynamicYAxis:
			# set up progress bar since extracting from long sections can take some time
			maxProgress = 0
			maxProgress = animation.tuView.cboTime.count() * len(items)
			complete = 0
			if maxProgress:
				if animation.iface is not None:
					animation.iface.messageBar().clearWidgets()
					progressWidget = animation.iface.messageBar().createMessage("Tuview",
					                                                            " Calculating Plot Minimums and Maximums . . .")
					messageBar = animation.iface.messageBar()
					progress = QProgressBar()
					progress.setMaximum(100)
					progressWidget.layout().addWidget(progress)
					messageBar.pushWidget(progressWidget, duration=1)
					animation.iface.mainWindow().repaint()
				else:
					print("Calculating Plot Minimums and Maximums . . .")
				pComplete = 0
				complete = 0
			# static option is for maps so don't need to loop
			# through all iterations in cross section / long plots
			# to get max and min
			if plotType == 'Time Series' or (static == True and plotType != 'Vert Profile'):
				if items:
					ymin = 999999
					ymax = -999999
					if 'axis 1' in axis and 'axis 2' in axis:
						ymin2 = 999999
						ymax2 = -999999
						for item in items:
							if item != 'Current Time':
								i = labels.index(item) if labels.count(item) else -1
								if i > -1:
									if axis[i] == 'axis 1':
										y = lines[i].get_ydata()
										ymin = min(ymin, np.nanmin(y))
										ymax = max(ymax, np.nanmax(y))
									elif axis[i] == 'axis 2':
										y = lines[i].get_ydata()
										ymin2 = min(ymin2, np.nanmin(y))
										ymax2 = max(ymax2, np.nanmax(y))
							complete += 1 * animation.tuView.cboTime.count()
							if maxProgress:
								pComplete = int(complete / maxProgress * 100)
								if animation.iface is not None:
									progress.setValue(pComplete)
								else:
									print(f' {pComplete:.0f}', end="", flush=True)
						margin = max((ymax - ymin) * 0.15, 0.01)
						margin2 = max((ymax2 - ymin2) * 0.15, 0.01)
						if not self.userSet or recalculate == 'y limits':
							self.sbYMin.setValue(ymin - margin)
							self.sbYMax.setValue(ymax + margin)
						if recalculate != 'y limits':
							self.sbY2Min.setValue(ymin2 - margin2)
							self.sbY2Max.setValue(ymax2 + margin2)
					elif not self.userSet or recalculate == 'y limits':
						for item in items:
							if item != 'Current Time':
								i = labels.index(item) if labels.count(item) else -1
								if i > -1:
									if type(lines[i]) is matplotlib.lines.Line2D:
										y = lines[i].get_ydata()
										ymin = min(ymin, np.nanmin(y))
										ymax = max(ymax, np.nanmax(y))
									elif isinstance(lines[i], matplotlib.patches.Polygon):
										xy = lines[i].line.get_xy()
										y = xy[:, 1]
										ymin = min(ymin, np.nanmin(y))
										ymax = max(ymax, np.nanmax(y))
									elif type(lines[i]) is PolyCollection:
										ymin_t, ymax_t, = getPolyCollectionExtents(lines[i], axis='y')
										ymin = min(ymin, ymin_t)
										ymax = max(ymax, ymax_t)
									elif type(lines[i]) is Quiver:
										ymin_t, ymax_t = getQuiverExtents(lines[i], axis='y')
										ymin = min(ymin, ymin_t)
										ymax = max(ymax, ymax_t)
							complete += 1 * animation.tuView.cboTime.count()
							if maxProgress:
								pComplete = int(complete / maxProgress * 100)
								if animation.iface is not None:
									progress.setValue(pComplete)
								else:
									print(f' {pComplete:.0f}', end="", flush=True)
						margin = max((ymax - ymin) * 0.05, 0.01)
						self.sbYMin.setValue(ymin - margin)
						self.sbYMax.setValue(ymax + margin)
					if ymin == 99999 or ymax == -99999:
						self.yUseMatplotLibDefault = True
				else:
					self.sbYMin.setValue(0)
					self.sbYMax.setValue(1)
			elif static and plotType == 'Vert Profile':
				if items:
					xmin = 999999
					xmax = -999999
					if 'axis 1' in axis and 'axis 2' in axis:
						xmin2 = 999999
						xmax2 = -999999
						for item in items:
							i = labels.index(item) if labels.count(item) else -1
							if i > -1:
								if axis[i] == 'axis 1':
									x = lines[i].get_xdata()
									xmin = min(xmin, np.nanmin(x))
									xmax = max(xmax, np.nanmax(x))
								elif axis[i] == 'axis 2':
									x = lines[i].get_xdata()
									xmin2 = min(xmin2, np.nanmin(x))
									xmax2 = max(xmax2, np.nanmax(x))
							complete += 1 * animation.tuView.cboTime.count()
							if maxProgress:
								pComplete = int(complete / maxProgress * 100)
								if animation.iface is not None:
									progress.setValue(pComplete)
								else:
									print(f' {pComplete:.0f}', end="", flush=True)
						margin = max((xmax - xmin) * 0.15, 0.01)
						margin2 = max((xmax2 - xmin2) * 0.15, 0.01)
						if not self.userSet or recalculate == 'x limits':
							self.sbXmin.setValue(xmin - margin)
							self.sbXMax.setValue(xmax + margin)
						if recalculate != 'x limits':
							self.sbX2min.setValue(xmin2 - margin2)
							self.sbX2Max.setValue(xmax2 + margin2)
					elif not self.userSet or recalculate == 'x limits':
						for item in items:
							if item != 'Current Time':
								i = labels.index(item) if labels.count(item) else -1
								if i > -1:
									x = lines[i].get_xdata()
									xmin = min(xmin, np.nanmin(x))
									xmax = max(xmax, np.nanmax(x))
							complete += 1 * animation.tuView.cboTime.count()
							if maxProgress:
								pComplete = int(complete / maxProgress * 100)
								if animation.iface is not None:
									progress.setValue(pComplete)
								else:
									print(f' {pComplete:.0f}', end="", flush=True)
						margin = max((xmax - xmin) * 0.05, 0.01)
						self.sbXmin.setValue(xmin - margin)
						self.sbXMax.setValue(xmax + margin)
					if xmin == 99999 or xmax == -99999:
						self.xUseMatplotLibDefault = True
				else:
					self.sbXmin.setValue(0)
					self.sbXMax.setValue(1)
			else:  # long plot / cross section - so need to loop through all timesteps to get max
				if recalculate != 'not cross sections':
					if items:
						ymin = 999999
						ymax = -999999
						ymin2 = 999999
						ymax2 = -999999
						xmin = 999999
						xmax = -999999
						xmin2 = 999999
						xmax2 = -999999
						for i in range(animation.tuView.cboTime.count()):
							timeFormatted = animation.tuView.cboTime.itemText(i)
							unit = self.animationDialog.tuView.tuOptions.timeUnits
							# if self.animationDialog.tuView.tuOptions.xAxisDates:
							# 	time = convertFormattedDateToTime(timeFormatted,
							# 	                                  self.animationDialog.tuView.tuResults.dateFormat,
							# 	                                  self.animationDialog.tuView.tuResults.date2time)
							# else:
							# 	time = convertFormattedTimeToTime(timeFormatted, unit=unit)

							if qv < 31600:
								time = self.animationDialog.tuView.tuResults.timeFromString(timeFormatted)
							else:
								if self.animationDialog.tuView.tuOptions.xAxisDates:
									time = datetime.strptime(timeFormatted, self.animationDialog.tuView.tuResults.dateFormat)
								else:
									if timeFormatted in self.animationDialog.tuView.tuResults.cboTime2timekey:
										time = self.animationDialog.tuView.tuResults.cboTime2timekey[timeFormatted]
										time = self.animationDialog.tuView.tuResults.timekey2time[time]
										zt = self.animationDialog.tuView.tuOptions.zeroTime
										time = zt + timedelta(hours=time)
									else:
										time = convertFormattedTimeToTime(timeFormatted, unit=unit)

							if plotType == 'CS / LP':
								animation.tuView.tuPlot.updateCurrentPlot(TuPlot.CrossSection, draw=False, time=time,
																		  mesh_rendered=False)
							else:
								animation.tuView.tuPlot.updateCurrentPlot(TuPlot.VerticalProfile, draw=False, time=time,
																		  mesh_rendered=False)
							lines, labels, axis = animation.plotItems(plotType)
							if 'axis 1' in axis and 'axis 2' in axis:
								for item in items:
									if '[Curtain]' in item:
										is_ = []
										for i, label in enumerate(labels):
											if '[Curtain]' in label:
												rt = item.split('[Curtain]')[0].strip()
												if rt in label:
													is_.append(i)
									else:
										is_ = [labels.index(item)] if labels.count(item) else []
									for i in is_:
										if axis[i] == 'axis 1':
											if type(lines[i]) is matplotlib.lines.Line2D:
												y = lines[i].get_ydata()
												x = lines[i].get_xdata()
												ymin = min(ymin, np.nanmin(y))
												ymax = max(ymax, np.nanmax(y))
												xmin = min(xmin, np.nanmin(x))
												xmax = max(xmax, np.nanmax(x))
											elif isinstance(lines[i], matplotlib.patches.Polygon):
												xy = lines[i].line.get_xy()
												y = xy[:, 1]
												x = xy[:, 0]
												ymin = min(ymin, np.nanmin(y))
												ymax = max(ymax, np.nanmax(y))
												xmin = min(xmin, np.nanmin(x))
												xmax = max(xmax, np.nanmax(x))
											elif type(lines[i]) is PolyCollection:
												ymin_t, ymax_t, = getPolyCollectionExtents(lines[i], axis='y')
												xmin_t, xmax_t, = getPolyCollectionExtents(lines[i], axis='x')
												ymin = min(ymin, ymin_t)
												ymax = max(ymax, ymax_t)
												xmin = min(xmin, xmin_t)
												xmax = max(xmax, xmax_t)
											elif type(lines[i]) is Quiver:
												ymin_t, ymax_t = getQuiverExtents(lines[i], axis='y')
												xmin_t, xmax_t, = getQuiverExtents(lines[i], axis='x')
												ymin = min(ymin, ymin_t)
												ymax = max(ymax, ymax_t)
												xmin = min(xmin, xmin_t)
												xmax = max(xmax, xmax_t)
										elif axis[i] == 'axis 2':
											y = lines[i].get_ydata()
											x = lines[i].get_xdata()
											if plotType == 'Vert Profile':
												ymin = min(ymin, np.nanmin(y))
												ymax = max(ymax, np.nanmax(y))
												xmin2 = min(xmin, np.nanmin(x))
												xmax2 = max(xmax, np.nanmax(x))
											else:
												ymin2 = min(ymin2, np.nanmin(y))
												ymax2 = max(ymax2, np.nanmax(y))
												xmin = min(xmin, np.nanmin(x))
												xmax = max(xmax, np.nanmax(x))
									complete += 1
									if maxProgress:
										pComplete = int(complete / maxProgress * 100)
										if animation.iface is not None:
											progress.setValue(pComplete)
										else:
											print(f' {pComplete:.0f}', end="", flush=True)
							elif not self.userSet or recalculate == 'y limits' or recalculate == 'x limits':
								for item in items:
									if item != 'Current Time':
										if '[Curtain]' in item:
											is_ = []
											for i, label in enumerate(labels):
												if '[Curtain]' in label:
													rt = item.split('[Curtain]')[0].strip()
													if rt in label:
														is_.append(i)
										else:
											is_ = [labels.index(item)] if labels.count(item) else []
										for i in is_:
											if type(lines[i]) is matplotlib.lines.Line2D:
												y = lines[i].get_ydata()
												x = lines[i].get_xdata()
												ymin = min(ymin, np.nanmin(y))
												ymax = max(ymax, np.nanmax(y))
												xmin = min(xmin, np.nanmin(x))
												xmax = max(xmax, np.nanmax(x))
											elif isinstance(lines[i], matplotlib.patches.Polygon):
												xy = lines[i].get_xy()
												y = xy[:, 1]
												x = xy[:, 0]
												ymin = min(ymin, np.nanmin(y))
												ymax = max(ymax, np.nanmax(y))
												xmin = min(xmin, np.nanmin(x))
												xmax = max(xmax, np.nanmax(x))
											elif type(lines[i]) is PolyCollection:
												ymin_t, ymax_t = getPolyCollectionExtents(lines[i], axis='y')
												xmin_t, xmax_t, = getPolyCollectionExtents(lines[i], axis='x')
												ymin = min(ymin, ymin_t)
												ymax = max(ymax, ymax_t)
												xmin = min(xmin, xmin_t)
												xmax = max(xmax, xmax_t)
											elif type(lines[i]) is Quiver:
												ymin_t, ymax_t = getQuiverExtents(lines[i], axis='y')
												xmin_t, xmax_t, = getQuiverExtents(lines[i], axis='x')
												ymin = min(ymin, ymin_t)
												ymax = max(ymax, ymax_t)
												xmin = min(xmin, xmin_t)
												xmax = max(xmax, xmax_t)
									complete += 1
									if maxProgress:
										pComplete = int(complete / maxProgress * 100)
										if animation.iface is not None:
											progress.setValue(pComplete)
										else:
											print(f' {pComplete:.0f}', end="", flush=True)
						margin = max((ymax - ymin) * 0.05, 0.01)
						marginx = max((xmax - xmin) * 0.05, 0.01)
						if not self.userSet or recalculate == 'y limits':
							self.sbYMin.setValue(ymin - margin)
							self.sbYMax.setValue(ymax + margin)
							self.cross_section_y_axis1_limits_set = True
						if not self.userSet or recalculate == 'x limits':
							#if not self.datetime:
							self.sbXmin.setValue(xmin - marginx)
							self.sbXMax.setValue(xmax + marginx)
							#else:
							#	self.dteXmin.setDateTime(xmin - marginx)
							#	self.dteXMax.setDateTime(xmax + marginx)
						if ymin2 != 999999 and ymax2 != -999999:
							if not self.userSet or recalculate == 'y2 limits':
								margin2 = max((ymax2 - ymin2) * 0.05, 0.01)
								self.sbY2Min.setValue(ymin2 - margin2)
								self.sbY2Max.setValue(ymax2 + margin2)
								self.cross_section_y_axis2_limits_set = True
						if ymin == 999999 or ymax == -999999:
							self.yUseMatplotLibDefault = True
						if xmin2 != 999999 and xmax2 != -999999:
							if not self.userSet or recalculate == 'x2 limits':
								margin2 = max((xmax2 - xmin2) * 0.05, 0.01)
								self.sbX2min.setValue(xmin2 - margin2)
								self.sbX2Max.setValue(xmax2 + margin2)
					else:
						self.sbYMin.setValue(0)
						self.sbYMax.setValue(1)
		if animation.iface is None:
			print()
		self.userSet = True


class TextPropertiesDialog(QDialog, Ui_textPropertiesDialog):
	
	def __init__(self):
		QDialog.__init__(self)
		self.setupUi(self)
		self.cbBackground.setChecked(True)
		self.cbFrame.setChecked(True)
		self.buttonBox.accepted.connect(self.accept)
		
		
		
class ImagePropertiesDialog(QDialog, Ui_ImageProperties):
	
	def __init__(self):
		QDialog.__init__(self)
		self.setupUi(self)
		
		self.buttonBox.accepted.connect(self.accept)
		
	def applyPrevious(self, prop=None):
		if prop is not None:
			self.rbUseOriginalSize.setChecked(prop.rbUseOriginalSize.isChecked())
			self.rbResizeImage.setChecked(prop.rbResizeImage.isChecked())
			self.sbSizeX.setValue(prop.sbSizeX.value())
			self.sbSizeY.setValue(prop.sbSizeY.value())
			self.cbKeepAspectRatio.setChecked(prop.cbKeepAspectRatio.isChecked())


class AxisLimitsMessage(QDialog, Ui_animationPlotLimitsWarning):

	NoValue = -1
	Calc = 0
	UseTV = 1
	Cancel = 2

	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		self.returnValue = AxisLimitsMessage.NoValue
		self.pbCalc.clicked.connect(lambda: self.setReturnValue(AxisLimitsMessage.Calc))
		self.pbUseTV.clicked.connect(lambda: self.setReturnValue(AxisLimitsMessage.UseTV))
		self.pbCancel.clicked.connect(lambda: self.setReturnValue(AxisLimitsMessage.Cancel))

	def setReturnValue(self, value):
		self.returnValue = value
		self.accept()

	@staticmethod
	def warning(parent):
		dialog = AxisLimitsMessage(parent)
		dialog.exec()
		return dialog.returnValue

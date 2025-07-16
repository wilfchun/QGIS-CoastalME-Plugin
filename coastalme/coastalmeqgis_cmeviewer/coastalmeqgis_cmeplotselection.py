from qgis.core import QgsWkbTypes, QgsVectorLayer


class CmePlotSelection():
	"""
	Class for handling plotting selected vector layers.
	
	"""
	
	def __init__(self, CmePlot):
		self.cmePlot = CmePlot
		self.iface = CmePlot.iface
	
	def plotTimeSeries(self, layer, **kwargs):
		"""
		Plot time series from selected points

		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot
		
		self.cmePlot.cmePlot2D.plotSelectionPointFeat.clear()  # clear selected feacmere for plotting list
		
		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = int(self.cmePlot.cmeView.cmeOptions.iLabelField)
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				# self.cmePlot.clearPlot(0, retain_1d=True, retain_flow=True)  # clear plot
				self.cmePlot.clearPlot2(CmePlot.TimeSeries, CmePlot.DataTimeSeries2D)  # clear plot
				self.cmePlot.cmePlot2D.resetMultiPointCount()
				self.cmePlot.cmePlot2D.plotTimeSeriesFromMap(layer, f.geometry().asPoint(), bypass=multi,
				                                           featName=featName, markerNo=i+1, **kwargs)
			else:
				self.cmePlot.cmePlot2D.plotTimeSeriesFromMap(layer, f.geometry().asPoint(), bypass=multi,
				                                           featName=featName, markerNo=i+1, **kwargs)
			self.cmePlot.cmePlot2D.plotSelectionPointFeat.append(f)
		
		self.cmePlot.cmePlot2D.reduceMultiPointCount(1)  # have to minus 1 off to make it count properly
		self.cmePlot.holdTimeSeriesPlot = True
		self.cmePlot.timeSeriesPlotFirst = False
		
		# unpress button
		self.cmePlot.cmePlotToolbar.plotTSMenu.menuAction().setChecked(False)
		
		return True

	def plotTimeSeriesDepAv(self, layer, **kwargs):
		"""
		Plot time series from selected points

		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot3D.plotSelectionPointFeat.clear()  # clear selected feacmere for plotting list

		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = int(self.cmePlot.cmeView.cmeOptions.iLabelField)
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				# self.cmePlot.clearPlot(0, retain_1d=True, retain_flow=True)  # clear plot
				self.cmePlot.clearPlot2(CmePlot.TimeSeries, CmePlot.DataTimeSeriesDepAv)  # clear plot
				self.cmePlot.cmePlot3D.resetMultiPointCount()
				self.cmePlot.cmePlot3D.plotTimeSeriesFromMap(layer, f.geometry().asPoint(), bypass=multi,
				                                           featName=featName, markerNo=i + 1,
				                                           data_type=CmePlot.DataTimeSeriesDepAv, **kwargs)
			else:
				self.cmePlot.cmePlot3D.plotTimeSeriesFromMap(layer, f.geometry().asPoint(), bypass=multi,
				                                           featName=featName, markerNo=i + 1,
				                                            data_type=CmePlot.DataTimeSeriesDepAv, **kwargs)
			self.cmePlot.cmePlot3D.plotSelectionPointFeat.append(f)

		self.cmePlot.cmePlot3D.reduceMultiPointCount(1)  # have to minus 1 off to make it count properly
		self.cmePlot.holdTimeSeriesPlot = True
		self.cmePlot.timeSeriesPlotFirst = False

		# unpress button
		self.cmePlot.cmePlotToolbar.averageMethodTSMenu.menuAction().setChecked(False)

		return True
	
	def plotCrossSection(self, layer, **kwargs):
		"""
		Plot cross section or long profile from selected polyline

		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot2D.plotSelectionLineFeat.clear()  # clear selected feacmere for plotting list

		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = self.cmePlot.cmeView.cmeOptions.iLabelField
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				# self.cmePlot.clearPlot(1, retain_1d=True, retain_flow=True)  # clear plot
				self.cmePlot.clearPlot2(CmePlot.CrossSection, CmePlot.DataCrossSection2D)  # clear plot
				self.cmePlot.cmePlot2D.resetMultiLineCount()
				self.cmePlot.cmePlot2D.plotCrossSectionFromMap(layer, f, bypass=multi, featName=featName, lineNo=i+1, **kwargs)
			else:
				self.cmePlot.cmePlot2D.plotCrossSectionFromMap(layer, f, bypass=multi, featName=featName, lineNo=i+1, **kwargs)
			self.cmePlot.cmePlot2D.plotSelectionLineFeat.append(f)

		self.cmePlot.cmePlot2D.reduceMultiLineCount(1)  # have to minus 1 off to make it count properly
		self.cmePlot.profilePlotFirst = False

		# unpress button
		self.cmePlot.cmePlotToolbar.plotLPMenu.menuAction().setChecked(False)

		return True

	def plotCrossSectionDepAv(self, layer, **kwargs):
		"""
		Plot cross section or long profile from selected polyline

		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot3D.plotSelectionLineFeat.clear()  # clear selected feacmere for plotting list

		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = self.cmePlot.cmeView.cmeOptions.iLabelField
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				# self.cmePlot.clearPlot(1, retain_1d=True, retain_flow=True)  # clear plot
				self.cmePlot.clearPlot2(CmePlot.CrossSection, CmePlot.DataCrossSectionDepAv)  # clear plot
				self.cmePlot.cmePlot3D.resetMultiLineCount()
				self.cmePlot.cmePlot3D.plotCrossSectionFromMap(layer, f, bypass=multi, featName=featName, lineNo=i + 1,
				                                             data_type=CmePlot.DataCrossSectionDepAv, **kwargs)
			else:
				self.cmePlot.cmePlot3D.plotCrossSectionFromMap(layer, f, bypass=multi, featName=featName, lineNo=i + 1,
				                                             data_type=CmePlot.DataCrossSectionDepAv, **kwargs)
			self.cmePlot.cmePlot3D.plotSelectionLineFeat.append(f)

		self.cmePlot.cmePlot3D.reduceMultiLineCount(1)  # have to minus 1 off to make it count properly
		self.cmePlot.profilePlotFirst = False

		# unpress button
		self.cmePlot.cmePlotToolbar.averageMethodCSMenu.menuAction().setChecked(False)

		return True
	
	def plotFlow(self, layer, **kwargs):
		"""
		Plot flow from selected line.
		
		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot2D.plotSelectionFlowFeat.clear()
		
		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = self.cmePlot.cmeView.cmeOptions.iLabelField
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				if self.cmePlot.timeSeriesPlotFirst:  # first plot so need to remove test line
					self.cmePlot.clearPlot2(CmePlot.TimeSeries, CmePlot.DataFlow2D)
					self.cmePlot.timeSeriesPlotFirst = False
				else:
					# self.cmePlot.clearPlot(0, retain_1d=True, retain_2d=True)  # clear plot
					self.cmePlot.clearPlot2(CmePlot.TimeSeries, CmePlot.DataFlow2D)
				self.cmePlot.cmePlot2D.resetMultiFlowLineCount()
				self.cmePlot.cmePlot2D.plotFlowFromMap(layer, f, bypass=multi, featName=featName, **kwargs)
			else:
				self.cmePlot.cmePlot2D.plotFlowFromMap(layer, f, bypass=multi, featName=featName, **kwargs)
			self.cmePlot.cmePlot2D.plotSelectionFlowFeat.append(f)
		
		self.cmePlot.cmePlot2D.reduceMultiFlowLineCount(1)  # have to minus 1 off to make it count properly
		self.cmePlot.profilePlotFirst = False
		
		# unpress button
		self.cmePlot.cmePlotToolbar.plotFluxButton.setChecked(False)
		
		return True

	def plotCurtain(self, layer, **kwargs):
		"""
		Plot flow from selected line.

		:param layer: QgsVectorLayer
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot3D.plotSelectionCurtainFeat.clear()

		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = self.cmePlot.cmeView.cmeOptions.iLabelField
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				self.cmePlot.clearPlot2(CmePlot.TimeSeries, CmePlot.DataFlow2D)

			self.cmePlot.cmePlot3D.plotCurtainFromMap(layer, f, bypass=multi, featName=featName, **kwargs)
			self.cmePlot.cmePlot3D.plotSelectionCurtainFeat.append(f)

		self.cmePlot.profilePlotFirst = False

		# unpress button
		self.cmePlot.cmePlotToolbar.curtainPlotMenu.menuAction().setChecked(False)

		return True

	def plotVerticalProfile(self, layer, **kwargs):
		"""

		"""

		from .coastalmeqgis_cmeplot import CmePlot

		self.cmePlot.cmePlot3D.plotSelectionVPFeat.clear()

		sel = layer.selectedFeatures()
		multi = False
		if len(sel) > 1:
			multi = True
		for i, f in enumerate(sel):
			# get feacmere name from attribute
			iFeatName = self.cmePlot.cmeView.cmeOptions.iLabelField
			if len(f.attributes()) > iFeatName:
				featName = f.attributes()[iFeatName]
			else:
				featName = None

			if i == 0:
				self.cmePlot.clearPlot2(CmePlot.VerticalProfile, CmePlot.DataVerticalProfile)

			self.cmePlot.cmePlot3D.plotVerticalProfileFromMap(layer, f, bypass=multi, featName=featName, **kwargs)
			self.cmePlot.cmePlot3D.plotSelectionVPFeat.append(f)

		self.cmePlot.verticalProfileFirst = False

		# unpress button
		self.cmePlot.cmePlotToolbar.plotVPMenu.menuAction().setChecked(False)
	
	def useSelection(self, dataType, **kwargs):
		"""
		Use selected feacmeres for plotting.
		
		:param kwargs: -> dict key word arguments
		:return: bool -> True for successful, False for unsuccessful
		"""

		from .coastalmeqgis_cmeplot import CmePlot
		
		plotType = kwargs['type'] if 'type' in kwargs.keys() else 'standard'
		layer = kwargs['layer'] if 'layer' in kwargs else None
		
		plot = False

		if layer is None:
			if self.iface is not None:
				layer = self.iface.activeLayer()

		if 'layer' in kwargs:  # otherwise doubling up layer arguments
			del kwargs['layer']

		# check that there is an active layer
		if layer is not None:
			
			# check that layer is vector type
			if isinstance(layer, QgsVectorLayer):
				
				# check geometry type i.e. point, line
				if dataType == CmePlot.DataTimeSeries2D:
					if layer.geometryType() == QgsWkbTypes.PointGeometry:
						plot = self.plotTimeSeries(layer, **kwargs)
				elif dataType == CmePlot.DataCrossSection2D:
					if layer.geometryType() == QgsWkbTypes.LineGeometry:
						plot = self.plotCrossSection(layer, **kwargs)
				elif dataType == CmePlot.DataFlow2D:
					if layer.geometryType() == QgsWkbTypes.LineGeometry:
						plot = self.plotFlow(layer, **kwargs)
				elif dataType == CmePlot.DataCurtainPlot:
					if layer.geometryType() == QgsWkbTypes.LineGeometry:
						plot = self.plotCurtain(layer, **kwargs)
				elif dataType == CmePlot.DataTimeSeriesDepAv:
					if layer.geometryType() == QgsWkbTypes.PointGeometry:
						plot = self.plotTimeSeriesDepAv(layer, **kwargs)
				elif dataType == CmePlot.DataCrossSectionDepAv:
					if layer.geometryType() == QgsWkbTypes.LineGeometry:
						plot = self.plotCrossSectionDepAv(layer, **kwargs)
				elif dataType == CmePlot.DataVerticalProfile:
					if layer.geometryType() == QgsWkbTypes.PointGeometry:
						plot = self.plotVerticalProfile(layer, **kwargs)
		
		self.cmePlot.plotSelectionPoint = True
		
		return plot

	def clearSelection(self, dataType):
		"""

		"""

		from .coastalmeqgis_cmeplot import CmePlot

		for dataType in self.cmePlot.plotDataPlottingTypes:
			if self.cmePlot.plotDataToSelection[dataType] is not None: self.cmePlot.plotDataToSelection[dataType].clear()

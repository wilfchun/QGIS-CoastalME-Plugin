# Viewer System Implementation

## Overview

The viewer system is the core visualization component of the plugin, currently implemented as the "TuView" system. This document details how the viewer works, its components, and how it can be adapted for CoastalME.

## Main Viewer Component (`coastalmeqgis_tuview.py`)

### Class Structure

```python
class TuView(QDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()
        
        # Core components
        self.tuResults = TuResults(self)          # Results management
        self.tuPlot = TuPlot(self)               # Plotting system
        self.tuMenuBar = TuMenuBar(self)         # Menu system
        self.tuOptions = TuOptions()             # User preferences
        
        # UI state management
        self.connected = False
        self.currentLayer = None
        self.lock2DTimesteps = False
```

### Key UI Components

The viewer provides several key interface elements:

#### 1. Results List (`OpenResults`)
- **Purpose**: Shows all loaded results
- **Type**: `QListWidget`
- **Interaction**: User can select/deselect results to control visibility

```python
def resultsChanged(self):
    """Handle result selection changes"""
    # Update active mesh layers
    self.tuResults.tuResults2D.updateActiveMeshLayers()
    
    # Update result types
    self.tuResults.updateResultTypes()
    
    # Re-render map
    self.renderMap()
```

#### 2. Result Types Tree (`OpenResultTypes`)
- **Purpose**: Shows available result types (depth, velocity, etc.)
- **Type**: Custom tree widget with checkboxes
- **Features**: Primary/secondary axis selection, min/max toggles

```python
def resultTypesChanged(self, event):
    """Handle result type selection changes"""
    if event['button'] == QT_LEFT_BUTTON:
        self.tuResults.updateActiveResultTypes(event['modelIndex'])
```

#### 3. Time Control
- **Time Slider**: Navigate through time steps
- **Time Combo Box**: Select specific time
- **Play Controls**: Animate through time steps

```python
def timeSliderChanged(self):
    """Handle time step changes"""
    self.tuResults.updateActiveTime()
    self.renderMap()
    
    # Update plots
    if self.cbShowCurrentTime.isChecked():
        self.tuPlot.clearPlot2(TuPlot.TimeSeries, TuPlot.DataCurrentTime)
```

#### 4. Plot Tabs
- **Time Series**: Time-based plots
- **Cross Section**: Cross-sectional views
- **Vertical Profile**: Vertical data profiles

## Results Management System (`coastalmeqgis_turesults.py`)

### Core Data Structures

```python
class TuResults:
    def __init__(self, TuView):
        # Main results registry
        self.results = {}                    # All loaded results
        self.activeResults = []              # Currently selected results
        self.activeResultsIndexes = []       # UI indexes for active results
        
        # Time management
        self.activeTime = None               # Current time step
        self.timekey2time = {}              # Time key to time value mapping
        self.timekey2date = {}              # Time key to date mapping
        
        # Component handlers
        self.tuResults2D = TuResults2D(self)
        self.tuResults1D = TuResults1D(self)
        self.tuResultsParticles = TuResultsParticles(self)
```

### Result Loading Process

```python
def loadResults(self, filepath):
    """Load results from file"""
    
    # 1. Determine file type
    if filepath.endswith('.xmdf'):
        provider = XMDFDataProvider()
    elif filepath.endswith('.tpc'):
        provider = TPCDataProvider()
    
    # 2. Load data
    success = provider.Load(filepath)
    
    # 3. Create QGIS layer
    if success:
        layer = self.createQGISLayer(provider)
        
        # 4. Add to registry
        self.results[layer.name()] = {
            'provider': provider,
            'layer': layer,
            'times': provider.getTimes()
        }
        
        # 5. Update UI
        self.updateResultTypes()
```

## 2D Results System (`coastalmeqgis_turesults2d.py`)

### Mesh Layer Management

```python
class TuResults2D:
    def __init__(self, TuResults):
        self.results2d = {}               # 2D result datasets
        self.activeMeshLayers = []        # Currently active mesh layers
        self.activeScalar = None          # Current scalar dataset
        self.activeVector = None          # Current vector dataset
        
    def loadOpenMeshLayers(self, **kwargs):
        """Load mesh layers into QGIS"""
        
        # Get mesh files
        meshLayer = kwargs.get('layer')
        if meshLayer:
            # Load specific layer
            self.loadMeshLayer(meshLayer)
        else:
            # Load all available mesh layers
            self.loadAllMeshLayers()
```

### Dataset Management

```python
def updateActiveMeshLayers(self):
    """Update which mesh layers are active"""
    
    # Get selected results
    selectedResults = self.getSelectedResults()
    
    # Update active layers
    self.activeMeshLayers = []
    for result in selectedResults:
        if result in self.results2d:
            layer = self.results2d[result]['layer']
            self.activeMeshLayers.append(layer)
    
    # Update dataset assignments
    self.updateDatasetAssignments()
```

### Map Rendering

```python
def renderMap(self):
    """Update map visualization"""
    
    for layer in self.activeMeshLayers:
        # Set active scalar dataset
        if self.activeScalar:
            layer.setStaticScalarDatasetIndex(self.activeScalar)
        
        # Set active vector dataset
        if self.activeVector:
            layer.setStaticVectorDatasetIndex(self.activeVector)
        
        # Trigger repaint
        layer.triggerRepaint()
```

## 1D Results System (`coastalmeqgis_turesults1d.py`)

### Time Series Data

```python
class TuResults1D:
    def __init__(self, TuResults):
        self.results1d = {}              # 1D result datasets
        self.activeType = None           # Current geometry type (0=point, 1=line, 2=region)
        self.selectedResults = []        # Selected features
        
    def loadTSResults(self, layer):
        """Load time series results"""
        
        # Determine if this is a time series layer
        if not isTSLayer(layer):
            return False
            
        # Load data provider
        provider = self.createTSProvider(layer)
        
        # Add to results
        self.results1d[layer.name()] = {
            'provider': provider,
            'layer': layer,
            'geometry_type': layer.geometryType()
        }
        
        return True
```

### Plot Data Generation

```python
def plot1dResults(self):
    """Generate 1D plot data"""
    
    # Get selected features
    selectedFeatures = self.getSelectedFeatures()
    
    # Prepare plot data
    plotData = []
    for feature in selectedFeatures:
        # Get time series data for this feature
        data = self.getTimeSeriesData(feature)
        plotData.append(data)
    
    # Update plots
    self.tuView.tuPlot.updateTimeSeriesPlot(plotData)
```

## Plotting System (`coastalmeqgis_tuplot.py`)

### Plot Types

```python
class TuPlot:
    # Plot type constants
    TimeSeries = 0
    CrossSection = 1
    VerticalProfile = 2
    
    def __init__(self, TuView):
        self.tuView = TuView
        self.figures = {}           # Matplotlib figures
        self.axes = {}             # Plot axes
        self.toolbar = None        # Plot toolbar
        
    def drawPlot(self, plotType, data, **kwargs):
        """Draw plot using matplotlib"""
        
        if plotType == self.TimeSeries:
            self.drawTimeSeriesPlot(data, **kwargs)
        elif plotType == self.CrossSection:
            self.drawCrossSectionPlot(data, **kwargs)
        elif plotType == self.VerticalProfile:
            self.drawVerticalProfilePlot(data, **kwargs)
```

### Time Series Plotting

```python
def drawTimeSeriesPlot(self, data, **kwargs):
    """Draw time series plot"""
    
    # Get or create figure
    fig = self.figures.get('timeseries')
    if not fig:
        fig = plt.figure()
        self.figures['timeseries'] = fig
    
    # Clear previous plot
    fig.clear()
    ax = fig.add_subplot(111)
    
    # Plot data
    for series in data:
        ax.plot(series['times'], series['values'], 
                label=series['label'])
    
    # Configure plot
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    ax.grid(True)
    
    # Update display
    fig.canvas.draw()
```

## User Interface Integration

### Dock Widget Layout

```python
def setupUI(self):
    """Set up the dock widget UI"""
    
    # Main layout
    self.mainLayout = QVBoxLayout()
    
    # Results section
    self.resultsWidget = QWidget()
    self.resultsLayout = QVBoxLayout(self.resultsWidget)
    
    # Add results list
    self.OpenResults = QListWidget()
    self.resultsLayout.addWidget(self.OpenResults)
    
    # Add result types tree
    self.OpenResultTypes = DataSetTreeView()
    self.resultsLayout.addWidget(self.OpenResultTypes)
    
    # Time control section
    self.timeWidget = QWidget()
    self.timeLayout = QHBoxLayout(self.timeWidget)
    
    # Add time slider
    self.sliderTime = QSlider(Qt.Horizontal)
    self.timeLayout.addWidget(self.sliderTime)
    
    # Add time combo
    self.cboTime = QComboBox()
    self.timeLayout.addWidget(self.cboTime)
    
    # Plot section
    self.plotWidget = QWidget()
    self.plotLayout = QVBoxLayout(self.plotWidget)
    
    # Add plot tabs
    self.tabWidget = QTabWidget()
    self.plotLayout.addWidget(self.tabWidget)
    
    # Assemble main layout
    self.mainLayout.addWidget(self.resultsWidget)
    self.mainLayout.addWidget(self.timeWidget)
    self.mainLayout.addWidget(self.plotWidget)
    
    # Set main widget
    self.setWidget(QWidget())
    self.widget().setLayout(self.mainLayout)
```

### Signal Connections

```python
def qgisConnect(self):
    """Connect QGIS signals"""
    
    # Results changed
    self.OpenResults.itemSelectionChanged.connect(self.resultsChanged)
    
    # Result types changed
    self.OpenResultTypes.leftClicked.connect(self.resultTypesChanged)
    
    # Time changed
    self.cboTime.currentIndexChanged.connect(self.timeSliderChanged)
    self.sliderTime.valueChanged.connect(self.timeComboChanged)
    
    # Layer changed
    self.iface.currentLayerChanged.connect(self.currentLayerChanged)
    
    # Project events
    self.project.layersAdded.connect(self.layersAdded)
    self.project.layersWillBeRemoved.connect(self.layersRemoved)
```

## Data Synchronization

### Time Synchronization

```python
def updateActiveTime(self):
    """Update active time across all components"""
    
    # Get current time from UI
    currentIndex = self.cboTime.currentIndex()
    if currentIndex >= 0:
        timeText = self.cboTime.itemText(currentIndex)
        self.activeTime = self.parseTimeText(timeText)
        
        # Update all result types
        self.tuResults2D.updateActiveTime(self.activeTime)
        self.tuResults1D.updateActiveTime(self.activeTime)
        self.tuResultsParticles.updateActiveTime(self.activeTime)
```

### Result Type Synchronization

```python
def updateActiveResultTypes(self, modelIndex):
    """Update active result types"""
    
    # Get selected result types from UI
    selectedTypes = self.getSelectedResultTypes()
    
    # Update 2D results
    self.tuResults2D.updateActiveResultTypes(selectedTypes)
    
    # Update plots
    self.tuPlot.updateCurrentPlot()
    
    # Re-render map
    self.renderMap()
```

## Animation System

### Time Animation

```python
def playThroughTimesteps(self):
    """Auto-play through time steps"""
    
    if self.btnTimePlay.isChecked():
        # Set up timer
        self.timer = QTimer()
        self.timer.setInterval(int(self.tuOptions.playDelay * 1000))
        self.timer.timeout.connect(self.nextTimestep)
        self.timer.start()
    else:
        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()

def nextTimestep(self):
    """Move to next time step"""
    
    currentIndex = self.cboTime.currentIndex()
    nextIndex = currentIndex + 1
    
    if nextIndex < self.cboTime.count():
        self.cboTime.setCurrentIndex(nextIndex)
    else:
        # Stop at end
        self.timer.stop()
        self.btnTimePlay.setChecked(False)
```

## Customization Points

### For CoastalME Adaptation

1. **Result Type Names**: Change result type labels from TUFLOW to CoastalME conventions
2. **File Format Support**: Modify data providers for CoastalME file formats
3. **Visualization Styling**: Update default styling for CoastalME results
4. **Plot Types**: Customize plots for CoastalME-specific visualizations
5. **Time Format**: Adjust time handling for CoastalME conventions

### Extension Points

```python
# Custom result type handling
def addCustomResultType(self, name, handler):
    """Add custom result type"""
    self.customResultTypes[name] = handler

# Custom plot type
def addCustomPlotType(self, name, plotter):
    """Add custom plot type"""
    self.customPlotTypes[name] = plotter

# Custom data provider
def registerDataProvider(self, extension, provider):
    """Register custom data provider"""
    self.dataProviders[extension] = provider
```

## Performance Considerations

### Memory Management
- Results are cached but can be cleared
- Large datasets are loaded on-demand
- Temporary visualizations are cleaned up

### Rendering Optimization
- Only active layers are rendered
- Time steps are loaded incrementally
- Plot updates are batched

### Threading
- Data loading uses background threads
- UI updates happen on main thread
- Long operations show progress indicators

## Next Steps

To understand the data structures that power this system:
- Read `04_data_structures.md`

To learn how to adapt this for CoastalME:
- Read `05_migration_guide.md`
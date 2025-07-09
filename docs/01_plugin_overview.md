# QGIS Plugin Development Overview

## Introduction

This document provides a comprehensive guide to understanding the QGIS-CoastalME-Plugin architecture for developers with no QGIS plugin experience. The plugin is currently based on TUFLOW viewer technology and is being repurposed for CoastalME visualization.

## What is a QGIS Plugin?

QGIS plugins are Python extensions that add functionality to the QGIS desktop GIS application. They can:

- Add new tools and processing algorithms
- Create custom user interfaces (docks, dialogs, toolbars)
- Handle specific data formats
- Provide visualization capabilities
- Integrate with external libraries and services

## Core QGIS Plugin Structure

### Essential Files

Every QGIS plugin must have these core files:

1. **`__init__.py`** - Plugin initialization and entry point
2. **`metadata.txt`** - Plugin metadata (name, version, dependencies)
3. **Main plugin class** - Core functionality implementation

### Plugin Lifecycle

```python
# 1. Plugin Loading
def classFactory(iface):
    return MyPlugin(iface)

# 2. Plugin Initialization
def initGui(self):
    # Create menus, toolbars, dock widgets
    
# 3. Plugin Cleanup
def unload(self):
    # Remove UI elements, disconnect signals
```

## QGIS API Key Concepts

### QgsInterface (iface)
The main interface to QGIS application:
```python
self.iface.activeLayer()        # Get current layer
self.iface.mapCanvas()          # Access map view
self.iface.addDockWidget()      # Add dock panels
self.iface.messageBar()         # Show messages
```

### Layers and Data
- **QgsVectorLayer** - Points, lines, polygons
- **QgsRasterLayer** - Grid/image data  
- **QgsMeshLayer** - Unstructured mesh data (key for modeling results)

### UI Components
- **QDockWidget** - Dockable panels (like our results viewer)
- **QAction** - Menu items and toolbar buttons
- **QDialog** - Modal dialog windows

## Signal/Slot System

QGIS uses Qt's signal/slot mechanism for event handling:

```python
# Connect a signal to a slot (function)
self.button.clicked.connect(self.on_button_clicked)

# Layer selection changed
self.iface.currentLayerChanged.connect(self.layer_changed)

# Disconnect signals (important for cleanup)
self.button.clicked.disconnect()
```

## Plugin Architecture Patterns

### 1. Menu-Based Tools
Simple tools that appear in QGIS menus:
```python
def initGui(self):
    self.action = QAction("My Tool", self.iface.mainWindow())
    self.action.triggered.connect(self.run_tool)
    self.iface.addPluginToMenu("My Plugin", self.action)
```

### 2. Dock Widgets
Persistent panels for ongoing interaction:
```python
def initGui(self):
    self.dock = MyDockWidget()
    self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
```

### 3. Processing Algorithms
Tools that appear in Processing Toolbox:
```python
class MyAlgorithm(QgsProcessingAlgorithm):
    def processAlgorithm(self, parameters, context, feedback):
        # Your algorithm logic here
        return {}
```

## Data Handling in QGIS

### Layer Management
```python
# Add layer to project
QgsProject.instance().addMapLayer(layer)

# Get all layers
layers = QgsProject.instance().mapLayers()

# Find specific layer
layer = QgsProject.instance().mapLayersByName("Layer Name")[0]
```

### Feature Access
```python
# Get selected features
selected = layer.selectedFeatures()

# Iterate through all features
for feature in layer.getFeatures():
    geometry = feature.geometry()
    attributes = feature.attributes()
```

### Time-Based Data
QGIS has temporal capabilities for time-varying data:
```python
# Set temporal properties
temporal_props = layer.temporalProperties()
temporal_props.setIsActive(True)
temporal_props.setFixedTemporalRange(start_time, end_time)
```

## Plugin Development Best Practices

### 1. Resource Management
- Always disconnect signals in `unload()`
- Clean up temporary files and layers
- Handle memory carefully with large datasets

### 2. Error Handling
```python
try:
    # Risky operation
    layer.loadData()
except Exception as e:
    self.iface.messageBar().pushMessage("Error", str(e), level=Qgis.Critical)
```

### 3. User Feedback
```python
# Progress bars for long operations
progress = QProgressBar()
self.iface.statusBarIface().addWidget(progress)

# Message bar notifications
self.iface.messageBar().pushMessage("Success", "Operation completed")
```

### 4. Settings Storage
```python
# Store user preferences
settings = QSettings()
settings.setValue("myplugin/setting", value)

# Retrieve settings
value = settings.value("myplugin/setting", default_value)
```

## Threading and Performance

For long-running operations, use QgsTask:
```python
class MyTask(QgsTask):
    def run(self):
        # Long operation here
        return True
    
    def finished(self, result):
        # Called when task completes
        pass

# Run task
QgsApplication.taskManager().addTask(MyTask())
```

## Common QGIS Plugin Patterns

### Result Visualization Plugin
This is what our CoastalME plugin implements:

1. **Data Loading** - Read model results from files
2. **Layer Creation** - Convert data to QGIS layers
3. **Time Management** - Handle temporal datasets
4. **Visualization** - Render results with styling
5. **User Interaction** - Provide controls for exploration

### Key Components:
- **Data Providers** - Handle specific file formats
- **Result Management** - Track loaded results
- **Time Controller** - Manage temporal data
- **Plot Integration** - Matplotlib integration for graphs
- **UI Dock** - Main interface panel

## Next Steps

To understand this specific plugin:

1. Read `02_plugin_architecture.md` - Overall structure
2. Read `03_viewer_system.md` - Visualization components  
3. Read `04_data_structures.md` - Data handling
4. Read `05_migration_guide.md` - TUFLOW to CoastalME conversion

## Resources

- [QGIS API Documentation](https://qgis.org/pyqgis/)
- [PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [Qt Documentation](https://doc.qt.io/) - For UI components
# Data Structures and File Formats

## Overview

This document details the data structures used in the plugin and the file formats it supports. Understanding these is crucial for adapting the plugin to work with CoastalME results.

## Core Data Structures

### 1. Results Registry (`TuResults.results`)

The main data structure that tracks all loaded results:

```python
self.results = {
    'result_name': {
        # 2D mesh results
        'times': ['0.000000', '0.500000', '1.000000'],
        'types': ['Depth', 'Velocity', 'WSE'],
        'referenceTime': datetime(2023, 1, 1, 0, 0, 0),
        
        # 1D time series results
        'H': TimeSeries_Data(),          # Water levels
        'Q': TimeSeries_Data(),          # Flows
        'V': TimeSeries_Data(),          # Velocities
        
        # Particle results
        '_particles': [timesteps_list],
        
        # NetCDF grid results
        '_nc_grid': {
            'times': {'0.000000': [0.0]},
            'referenceTime': datetime(2023, 1, 1, 0, 0, 0)
        }
    }
}
```

### 2. Time Management

Time is handled through several interconnected dictionaries:

```python
class TuResults:
    def __init__(self):
        # Core time mappings
        self.timekey2time = {}       # '0.000000' -> 0.0
        self.timekey2date = {}       # '0.000000' -> datetime
        self.time2date = {}          # 0.0 -> datetime
        self.date2timekey = {}       # datetime -> '0.000000'
        self.date2time = {}          # datetime -> 0.0
        
        # Time specification handling (QGIS 3.16+)
        self.timekey2date_tspec = {}
        self.time2date_tspec = {}
        self.date_tspec2timekey = {}
        self.date_tspec2time = {}
        
        # Reference time
        self.zeroTime = datetime(2023, 1, 1, 0, 0, 0)
        self.timeSpec = 1  # Qt.TimeSpec
```

**Time Key Format**: Times are stored as formatted strings with 6 decimal places (e.g., "0.000000", "1.500000")

### 3. Result Type Structure

Result types are organized hierarchically:

```python
# Map Outputs (2D Results)
map_outputs = [
    ("Depth", 0, True, False),           # (name, index, enabled, selected)
    ("Velocity", 1, True, False),
    ("Water Surface Elevation", 2, True, False),
    ("Bed Elevation", 3, True, False)
]

# Time Series (1D Results)
time_series = [
    ("Water Level", 4, True, False),
    ("Flow", 5, True, False),
    ("Velocity", 6, True, False),
    ("Energy Level", 7, True, False)
]
```

## File Format Support

### 1. 2D Mesh Results

#### XMDF Format (`.xmdf`)
HDF5-based format for mesh results:

```python
class XMDFDataProvider:
    def Load(self, filename):
        # Open HDF5 file
        import h5py
        with h5py.File(filename, 'r') as f:
            # Read mesh geometry
            self.loadMeshGeometry(f)
            
            # Read datasets
            self.loadDatasets(f)
            
            # Read time information
            self.loadTimeInfo(f)
```

**Structure**:
- `/Geometry/2D Mesh/` - Mesh nodes and elements
- `/Datasets/` - Result datasets organized by type
- `/Time/` - Time step information

#### DAT Format (`.dat`)
ASCII format for TUFLOW results:

```python
class DATDataProvider:
    def Load(self, filename):
        with open(filename, 'r') as f:
            # Read header
            header = self.readHeader(f)
            
            # Read time steps
            while True:
                timestep = self.readTimestep(f)
                if timestep is None:
                    break
                self.timesteps.append(timestep)
```

**Structure**:
```
TUFLOW_DAT_FILE_VERSION_1.0
NUMELEMS 1000
NUMPTS 500
TIMESTEP 0.0
<data values>
TIMESTEP 0.5
<data values>
...
```

### 2. 1D Network Results

#### TPC Format (`.tpc`)
Time series data for 1D networks:

```python
class TPCDataProvider:
    def Load(self, filename):
        # Read header information
        self.readHeader(filename)
        
        # Read node/channel data
        self.readNetworkData(filename)
        
        # Read time series data
        self.readTimeSeriesData(filename)
```

**Structure**:
- Header: Version, units, reference time
- Network: Node and channel definitions
- Time series: Values at each time step

#### CSV Format (`.csv`)
Comma-separated values for time series:

```python
class CSVDataProvider:
    def Load(self, filename):
        import csv
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            for row in reader:
                self.processRow(row)
```

### 3. Particle Results

#### NetCDF Format (`.nc`)
NetCDF format for particle tracking:

```python
class ParticleDataProvider:
    def load_file(self, filename):
        import netCDF4
        self.nc = netCDF4.Dataset(filename, 'r')
        
        # Read particle variables
        self.x = self.nc.variables['x']
        self.y = self.nc.variables['y']
        self.z = self.nc.variables['z']
        self.status = self.nc.variables['status']
        
        # Read time information
        self.time = self.nc.variables['time']
```

**Variables**:
- `x`, `y`, `z`: Particle positions
- `status`: Particle status (active/inactive)
- `age`: Particle age
- `mass`: Particle mass
- `group_id`: Particle group identifier

### 4. Mesh Geometry

#### 2DM Format (`.2dm`)
SMS 2D mesh format:

```python
class MeshGeometry:
    def load2DM(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('ND'):
                    # Node definition
                    self.addNode(line)
                elif line.startswith('E3T') or line.startswith('E4Q'):
                    # Element definition
                    self.addElement(line)
```

**Format**:
```
MESH2D
ND 1 X Y Z
ND 2 X Y Z
...
E3T 1 N1 N2 N3 MAT
E4Q 2 N1 N2 N3 N4 MAT
```

## CoastalME-Specific Data Structures

### 1. CoastalME Result Types

Based on the analysis, CoastalME supports these result types:

#### 2D Results
```python
coastalme_2d_results = {
    'H': 'Water Level/Depth',
    'V': 'Velocity',
    'Q': 'Flow Rate',
    'GL': 'Ground Level',
    'QA': 'Flow Area',
    'Vx': 'Velocity X',
    'Vy': 'Velocity Y',
    'VA': 'Velocity Angle',
    'D': 'Depth',
    'HMax': 'Maximum Water Level',
    'Vol': 'Volume'
}
```

#### 1D Results
```python
coastalme_1d_results = {
    'H': 'Water Level',
    'E': 'Energy Level',
    'V': 'Velocity',
    'Q': 'Flow Rate',
    'A': 'Area',
    'Vol': 'Volume',
    'QI': 'Flow Input',
    'MB': 'Mass Balance',
    'NF': 'Node Flow Regime',
    'CF': 'Channel Flow Regime',
    'CL': 'Channel Losses'
}
```

### 2. CoastalME File Formats

#### Control Files
```python
coastalme_control_files = {
    '.tcf': 'TUFLOW Control File',
    '.ecf': 'Event Control File',
    '.tgc': 'Geometry Control File',
    '.tbc': 'Boundary Control File',
    '.tef': 'Time Event File',
    '.toc': 'Table of Contents File'
}
```

#### Result Files
```python
coastalme_result_files = {
    '.xmdf': '2D Mesh Results',
    '.dat': '2D Grid Results',
    '.nc': 'NetCDF Results',
    '.tpc': '1D Time Series Results',
    '.csv': 'CSV Time Series Results'
}
```

## Data Provider Architecture

### Base Data Provider

```python
class DataProvider:
    def __init__(self):
        self.loaded = False
        self.filename = None
        self.displayName = None
        self.formatVersion = None
        
    def Load(self, filename):
        """Load data from file"""
        raise NotImplementedError
        
    def getTimes(self):
        """Get available time steps"""
        raise NotImplementedError
        
    def getResultTypes(self):
        """Get available result types"""
        raise NotImplementedError
        
    def getData(self, result_type, time_step):
        """Get data for specific result type and time"""
        raise NotImplementedError
```

### Specialized Providers

#### 2D Mesh Provider
```python
class MeshDataProvider(DataProvider):
    def __init__(self):
        super().__init__()
        self.mesh_geometry = None
        self.datasets = {}
        self.times = []
        
    def loadMeshGeometry(self, source):
        """Load mesh geometry from 2DM file"""
        pass
        
    def loadDatasets(self, source):
        """Load result datasets"""
        pass
```

#### 1D Network Provider
```python
class NetworkDataProvider(DataProvider):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.channels = []
        self.time_series = {}
        
    def loadNetworkGeometry(self, source):
        """Load network geometry"""
        pass
        
    def loadTimeSeries(self, source):
        """Load time series data"""
        pass
```

## Time Series Data Structure

### Core Time Series Class

```python
class TimeSeries:
    def __init__(self):
        self.Header = []        # Column headers
        self.ID = []           # Location IDs
        self.Values = None     # NumPy array of values
        self.nLocs = 0         # Number of locations
        self.nVals = 0         # Number of time steps
        self.loaded = False
        
    def Load(self, source, format_type):
        """Load time series from source"""
        if format_type == 'tpc':
            self.loadTPC(source)
        elif format_type == 'csv':
            self.loadCSV(source)
            
    def getValue(self, location, time_index):
        """Get value at specific location and time"""
        if location in self.ID:
            loc_index = self.ID.index(location)
            return self.Values[time_index, loc_index + 2]  # +2 for timestep and time columns
        return None
```

### Time Series Data Format

The `Values` array has this structure:
```
[
    [timestep, time, location1_value, location2_value, ...],
    [timestep, time, location1_value, location2_value, ...],
    ...
]
```

## Cross-Section Data

### Cross-Section Structure

```python
class CrossSection:
    def __init__(self):
        self.source = None      # Source identifier
        self.type = 'XZ'        # Cross-section type
        self.x = []            # X coordinates
        self.z = []            # Z elevations
        self.np = 0            # Number of points
        self.loaded = False
        
    def load(self, source, x_data, z_data):
        """Load cross-section data"""
        self.source = source
        self.x = x_data
        self.z = z_data
        self.np = len(x_data)
        self.loaded = True
```

## Particle Data Structure

### Particle Data Provider

```python
class ParticleDataProvider:
    def __init__(self):
        self.nc = None              # NetCDF dataset
        self.times = []             # Time steps
        self.reference_time = None  # Reference time
        self.variables = {}         # Available variables
        
    def read_data_at_time(self, time_index):
        """Read particle data at specific time"""
        if time_index is None:
            return None
            
        data = {}
        data['x'] = self.nc.variables['x'][time_index, :]
        data['y'] = self.nc.variables['y'][time_index, :]
        data['z'] = self.nc.variables['z'][time_index, :]
        data['stat'] = self.nc.variables['stat'][time_index, :]
        
        # Read additional variables
        for var_name in self.variables:
            if var_name in self.nc.variables:
                data[var_name] = self.nc.variables[var_name][time_index, :]
                
        return data
```

## Data Conversion Utilities

### Time Conversion

```python
def convertTimeToFormattedTime(time_value, unit='h'):
    """Convert time value to formatted string"""
    if unit == 'h':
        hours = int(time_value)
        minutes = int((time_value - hours) * 60)
        seconds = int(((time_value - hours) * 60 - minutes) * 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif unit == 's':
        return f"{time_value:.2f}s"
    else:
        return str(time_value)

def timeStringToFloat(time_string):
    """Convert time string to float value"""
    try:
        if ':' in time_string:
            parts = time_string.split(':')
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0
            seconds = float(parts[2]) if len(parts) > 2 else 0
            return hours + minutes/60 + seconds/3600
        else:
            return float(time_string)
    except ValueError:
        return 0.0
```

### Coordinate Transformation

```python
def transformCoordinates(x, y, source_crs, target_crs):
    """Transform coordinates between CRS"""
    transformer = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
    point = QgsPointXY(x, y)
    transformed = transformer.transform(point)
    return transformed.x(), transformed.y()
```

## Data Validation

### Result Data Validation

```python
class DataValidator:
    @staticmethod
    def validateTimeSteps(times):
        """Validate time step data"""
        if not times:
            return False, "No time steps found"
            
        # Check for monotonic increasing
        for i in range(1, len(times)):
            if times[i] <= times[i-1]:
                return False, f"Time steps not monotonic at index {i}"
                
        return True, "Valid"
        
    @staticmethod
    def validateResultType(result_type, available_types):
        """Validate result type"""
        if result_type not in available_types:
            return False, f"Result type '{result_type}' not available"
        return True, "Valid"
```

## Memory Management

### Data Caching

```python
class DataCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
        
    def get(self, key):
        """Get data from cache"""
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
        
    def put(self, key, data):
        """Put data in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
            
        self.cache[key] = data
        self.access_order.append(key)
```

## Integration with QGIS

### Layer Creation

```python
def createQGISMeshLayer(mesh_file, result_file, display_name):
    """Create QGIS mesh layer"""
    # Create mesh layer
    mesh_layer = QgsMeshLayer(mesh_file, display_name, "mdal")
    
    # Add result datasets
    if result_file:
        mesh_layer.dataProvider().addDataset(result_file)
    
    # Configure temporal properties
    temporal_props = mesh_layer.temporalProperties()
    temporal_props.setIsActive(True)
    temporal_props.setReferenceTime(QDateTime.currentDateTime())
    
    return mesh_layer

def createQGISVectorLayer(geometry_type, display_name, crs=None):
    """Create QGIS vector layer"""
    if crs is None:
        crs = QgsProject.instance().crs()
        
    uri = f"{geometry_type}?crs={crs.authid()}"
    vector_layer = QgsVectorLayer(uri, display_name, "memory")
    
    return vector_layer
```

## Next Steps

To learn how to adapt these structures for CoastalME:
- Read `05_migration_guide.md`

To understand the broader plugin architecture:
- Review `02_plugin_architecture.md`
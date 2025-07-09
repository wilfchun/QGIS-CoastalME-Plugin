# Migration Guide: TUFLOW to CoastalME

## Overview

This guide provides a comprehensive plan for migrating the TUFLOW-based viewer to a CoastalME-focused results viewer. The migration involves systematic renaming, code refactoring, and adaptation of data structures while preserving all visualization functionality.

## Migration Strategy

### Phase 1: Analysis and Planning ✓
- [x] Identify all TUFLOW references in codebase
- [x] Map CoastalME-specific requirements
- [x] Document current architecture
- [x] Plan migration approach

### Phase 2: File and Directory Restructure
- [ ] Rename viewer directory
- [ ] Rename core files
- [ ] Update import statements
- [ ] Restructure documentation

### Phase 3: Code Refactoring
- [ ] Class and function renaming
- [ ] Variable and constant updates
- [ ] String literal updates
- [ ] Comment and documentation updates

### Phase 4: Data Structure Adaptation
- [ ] Result type mapping
- [ ] File format handling
- [ ] Time management updates
- [ ] Visualization styling

### Phase 5: Testing and Validation
- [ ] Unit test updates
- [ ] Integration testing
- [ ] Performance validation
- [ ] User acceptance testing

## Detailed Migration Plan

### 1. Directory and File Renaming

#### Primary Directory Structure
```bash
# Main viewer directory
coastalme/coastalmeqgis_tuviewer/ → coastalme/coastalmeqgis_cmeviewer/

# Utility directories
coastalme/convert_coastalme_model_gis_format/conv_tf_gis_format/ → 
coastalme/convert_coastalme_model_gis_format/conv_cme_gis_format/

coastalme/utils/tf_command.py → coastalme/utils/cme_command.py
coastalme/utils/tf_empty.py → coastalme/utils/cme_empty.py
```

#### Core Viewer Files (29 files to rename)
```python
# File renaming mapping
file_renames = {
    'coastalmeqgis_tuview.py': 'coastalmeqgis_cmeview.py',
    'coastalmeqgis_turesults.py': 'coastalmeqgis_cmeresults.py',
    'coastalmeqgis_turesults2d.py': 'coastalmeqgis_cmeresults2d.py',
    'coastalmeqgis_turesults1d.py': 'coastalmeqgis_cmeresults1d.py',
    'coastalmeqgis_turesultsParticles.py': 'coastalmeqgis_cmeresultsParticles.py',
    'coastalmeqgis_tuplot.py': 'coastalmeqgis_cmeplot.py',
    'coastalmeqgis_tuplot1d.py': 'coastalmeqgis_cmeplot1d.py',
    'coastalmeqgis_tuplot2d.py': 'coastalmeqgis_cmeplot2d.py',
    'coastalmeqgis_tuplot3d.py': 'coastalmeqgis_cmeplot3d.py',
    'coastalmeqgis_tuanimation.py': 'coastalmeqgis_cmeanimation.py',
    'coastalmeqgis_tumap.py': 'coastalmeqgis_cmemap.py',
    'coastalmeqgis_tumenubar.py': 'coastalmeqgis_cmemenubar.py',
    'coastalmeqgis_tumenufunctions.py': 'coastalmeqgis_cmemenufunctions.py',
    'coastalmeqgis_tumenucontext.py': 'coastalmeqgis_cmemenucontext.py',
    'coastalmeqgis_tuoptions.py': 'coastalmeqgis_cmeoptions.py',
    'coastalmeqgis_tuproject.py': 'coastalmeqgis_cmeproject.py',
    'coastalmeqgis_turubberband.py': 'coastalmeqgis_cmerubberband.py',
    'coastalmeqgis_tuuserplotdata.py': 'coastalmeqgis_cmeuserplotdata.py',
    'tuResultsNcGrid.py': 'cmeResultsNcGrid.py'
}
```

#### Migration Script for File Renaming
```python
#!/usr/bin/env python3
"""
File renaming migration script
"""
import os
import shutil
import re

def rename_files(base_dir, file_mapping):
    """Rename files according to mapping"""
    for old_name, new_name in file_mapping.items():
        old_path = os.path.join(base_dir, old_name)
        new_path = os.path.join(base_dir, new_name)
        
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")
        else:
            print(f"Warning: {old_name} not found")

def update_imports(file_path, import_mapping):
    """Update import statements in file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_import, new_import in import_mapping.items():
        content = content.replace(old_import, new_import)
    
    with open(file_path, 'w') as f:
        f.write(content)
```

### 2. Class and Function Renaming

#### Core Classes
```python
# Class renaming mapping
class_renames = {
    'TuView': 'CmeView',
    'TuResults': 'CmeResults',
    'TuResults2D': 'CmeResults2D',
    'TuResults1D': 'CmeResults1D',
    'TuResultsParticles': 'CmeResultsParticles',
    'TuResultsIndex': 'CmeResultsIndex',
    'TuPlot': 'CmePlot',
    'TuPlot1D': 'CmePlot1D',
    'TuPlot2D': 'CmePlot2D',
    'TuPlot3D': 'CmePlot3D',
    'TuMap': 'CmeMap',
    'TuProject': 'CmeProject',
    'TuAnimation': 'CmeAnimation',
    'TuOptions': 'CmeOptions',
    'TuMenuBar': 'CmeMenuBar',
    'TuRubberBand': 'CmeRubberBand',
    'TuUserPlotData': 'CmeUserPlotData'
}

# Function renaming patterns
function_patterns = {
    r'tuflow_': 'coastalme_',
    r'tu_': 'cme_',
    r'tuResults': 'cmeResults',
    r'tuPlot': 'cmePlot',
    r'tuView': 'cmeView',
    r'tuOptions': 'cmeOptions'
}
```

#### Migration Script for Class Renaming
```python
def update_class_names(file_path, class_mapping):
    """Update class names in file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_class, new_class in class_mapping.items():
        # Update class definitions
        content = re.sub(rf'\bclass {old_class}\b', f'class {new_class}', content)
        
        # Update class instantiations
        content = re.sub(rf'\b{old_class}\s*\(', f'{new_class}(', content)
        
        # Update type hints
        content = re.sub(rf': {old_class}\b', f': {new_class}', content)
        
        # Update comments
        content = re.sub(rf'# {old_class}', f'# {new_class}', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
```

### 3. User Interface Updates

#### Window and Dialog Titles
```python
# UI text updates
ui_text_updates = {
    'TUFLOW Viewer': 'CoastalME Viewer',
    'TUFLOW Results': 'CoastalME Results',
    'TUFLOW Plot': 'CoastalME Plot',
    'TUFLOW Animation': 'CoastalME Animation',
    'TUFLOW Options': 'CoastalME Options',
    'TUFLOW Utility Error': 'CoastalME Utility Error',
    'Load TUFLOW Results': 'Load CoastalME Results',
    'TUFLOW': 'CoastalME'
}
```

#### Menu Item Updates
```python
def update_menu_items(file_path):
    """Update menu items in UI files"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update menu text
    content = content.replace('TUFLOW', 'CoastalME')
    content = content.replace('TuView', 'CoastalME Viewer')
    content = content.replace('Tu_View', 'CoastalME_Viewer')
    
    # Update tooltips
    content = content.replace('TUFLOW viewer', 'CoastalME viewer')
    content = content.replace('TUFLOW results', 'CoastalME results')
    
    with open(file_path, 'w') as f:
        f.write(content)
```

### 4. Configuration and Settings Updates

#### QSettings Keys
```python
# Settings key updates
settings_updates = {
    'TUFLOW/tuview_': 'COASTALME/cmeview_',
    'TUFLOW/tu_': 'COASTALME/cme_',
    'tuflow_': 'coastalme_',
    'TUVIEW/': 'CMEVIEW/'
}

def update_settings_keys(file_path):
    """Update QSettings keys"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_key, new_key in settings_updates.items():
        content = content.replace(f'"{old_key}', f'"{new_key}')
        content = content.replace(f"'{old_key}", f"'{new_key}")
    
    with open(file_path, 'w') as f:
        f.write(content)
```

#### Project Settings
```python
# Project-specific settings
project_settings = {
    'TUFLOW/tuview_dock_opened': 'COASTALME/cmeview_dock_opened',
    'TUFLOW/tuview_defaultlayout': 'COASTALME/cmeview_defaultlayout',
    'TUFLOW/tuview_previouslayout': 'COASTALME/cmeview_previouslayout'
}
```

### 5. Data Structure Adaptation

#### Result Type Mapping
```python
# Map TUFLOW result types to CoastalME equivalents
result_type_mapping = {
    # 2D Results
    'Depth': 'Water Depth',
    'Velocity': 'Velocity',
    'Water Level': 'Water Surface Elevation',
    'Bed Elevation': 'Bed Level',
    'Unit Flow': 'Unit Flow',
    'Hazard': 'Flood Hazard',
    
    # 1D Results
    'Flow': 'Flow Rate',
    'Level': 'Water Level',
    'Velocity': 'Velocity',
    'Energy Level': 'Energy Level',
    'Volume': 'Volume'
}

def update_result_types(file_path):
    """Update result type references"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_type, new_type in result_type_mapping.items():
        content = content.replace(f'"{old_type}"', f'"{new_type}"')
        content = content.replace(f"'{old_type}'", f"'{new_type}'")
    
    with open(file_path, 'w') as f:
        f.write(content)
```

#### File Format Updates
```python
# File format extensions that may need updating
file_format_mapping = {
    '.sup': '.sup',    # Keep as is
    '.xmdf': '.xmdf',  # Keep as is
    '.dat': '.dat',    # Keep as is
    '.2dm': '.2dm',    # Keep as is
    '.nc': '.nc',      # Keep as is
    '.tpc': '.tpc',    # Keep as is
    '.csv': '.csv'     # Keep as is
}
# Note: File formats are largely compatible
```

### 6. Visualization and Styling Updates

#### Default Styling
```python
# Update default color schemes and styling
def update_default_styles():
    """Update default visualization styles for CoastalME"""
    
    # Color schemes
    coastalme_colors = {
        'depth': ['#0000FF', '#00FFFF', '#FFFF00', '#FF0000'],
        'velocity': ['#000080', '#0080FF', '#80FF00', '#FF8000'],
        'elevation': ['#8B4513', '#DAA520', '#FFFF00', '#90EE90']
    }
    
    # Update style files
    style_files = [
        'coastalme/QGIS_Styles/grad/Depth.json',
        'coastalme/QGIS_Styles/grad/Velocity.json',
        'coastalme/QGIS_Styles/grad/Flow.json'
    ]
    
    for style_file in style_files:
        update_style_file(style_file, coastalme_colors)
```

#### Icon Updates
```python
# Update plugin icons
icon_updates = {
    'tuview.png': 'cmeview.png',
    'results.png': 'cme_results.png',
    'TuPLOT_External.PNG': 'CmePLOT_External.PNG'
}
```

### 7. Testing Strategy

#### Unit Test Updates
```python
# Update test files
test_file_updates = {
    'test_tuflow_': 'test_coastalme_',
    'test_tu_': 'test_cme_',
    'TestTuflow': 'TestCoastalME',
    'TestTu': 'TestCme'
}

def update_test_files(test_dir):
    """Update test files for CoastalME"""
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_test_file(file_path)

def update_test_file(file_path):
    """Update individual test file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update test class names
    content = re.sub(r'class Test(\w*?)Tu(\w*?)\(', r'class Test\1Cme\2(', content)
    
    # Update test method names
    content = re.sub(r'def test_tuflow_', 'def test_coastalme_', content)
    
    # Update assertions
    content = content.replace('tuflow', 'coastalme')
    content = content.replace('TUFLOW', 'CoastalME')
    
    with open(file_path, 'w') as f:
        f.write(content)
```

#### Integration Testing
```python
# Integration test plan
integration_tests = [
    'test_cme_viewer_loading',
    'test_cme_result_display',
    'test_cme_time_navigation',
    'test_cme_plot_generation',
    'test_cme_animation_export',
    'test_cme_file_format_support'
]
```

### 8. Documentation Updates

#### README Updates
```python
def update_readme():
    """Update README.md file"""
    readme_updates = {
        'TUFLOW': 'CoastalME',
        'TuView': 'CoastalME Viewer',
        'tuflow': 'coastalme',
        'TUFLOW viewer': 'CoastalME viewer',
        'TUFLOW results': 'CoastalME results',
        'TUFLOW models': 'CoastalME models'
    }
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    for old_text, new_text in readme_updates.items():
        content = content.replace(old_text, new_text)
    
    with open('README.md', 'w') as f:
        f.write(content)
```

#### Help Documentation
```python
# Update help files
help_file_updates = {
    'tuflow': 'coastalme',
    'TUFLOW': 'CoastalME',
    'Tuflow': 'CoastalME',
    'TuView': 'CoastalME Viewer'
}
```

### 9. Complete Migration Script

```python
#!/usr/bin/env python3
"""
Complete migration script for TUFLOW to CoastalME
"""
import os
import shutil
import re
import glob

class TuflowToCoastalMEMigrator:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.backup_dir = os.path.join(base_dir, 'backup_tuflow')
        
    def create_backup(self):
        """Create backup of original files"""
        print("Creating backup...")
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
        shutil.copytree(self.base_dir, self.backup_dir, 
                       ignore=shutil.ignore_patterns('backup_*'))
        print("Backup created successfully")
    
    def migrate_directories(self):
        """Migrate directory structure"""
        print("Migrating directories...")
        
        # Rename main viewer directory
        old_dir = os.path.join(self.base_dir, 'coastalme', 'coastalmeqgis_tuviewer')
        new_dir = os.path.join(self.base_dir, 'coastalme', 'coastalmeqgis_cmeviewer')
        
        if os.path.exists(old_dir):
            shutil.move(old_dir, new_dir)
            print(f"Renamed: {old_dir} -> {new_dir}")
    
    def migrate_files(self):
        """Migrate individual files"""
        print("Migrating files...")
        
        # Get all Python files
        python_files = glob.glob(os.path.join(self.base_dir, '**/*.py'), recursive=True)
        
        for file_path in python_files:
            self.migrate_file(file_path)
    
    def migrate_file(self, file_path):
        """Migrate a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply all transformations
            content = self.update_imports(content)
            content = self.update_class_names(content)
            content = self.update_function_names(content)
            content = self.update_variables(content)
            content = self.update_strings(content)
            content = self.update_comments(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error migrating {file_path}: {e}")
    
    def update_imports(self, content):
        """Update import statements"""
        import_mapping = {
            'from .coastalmeqgis_tuviewer': 'from .coastalmeqgis_cmeviewer',
            'from coastalmeqgis_tuviewer': 'from coastalmeqgis_cmeviewer',
            'import coastalmeqgis_tuviewer': 'import coastalmeqgis_cmeviewer',
            'coastalmeqgis_tuviewer.': 'coastalmeqgis_cmeviewer.'
        }
        
        for old_import, new_import in import_mapping.items():
            content = content.replace(old_import, new_import)
        
        return content
    
    def update_class_names(self, content):
        """Update class names"""
        class_mapping = {
            'TuView': 'CmeView',
            'TuResults': 'CmeResults',
            'TuPlot': 'CmePlot',
            'TuOptions': 'CmeOptions',
            'TuProject': 'CmeProject',
            'TuAnimation': 'CmeAnimation'
        }
        
        for old_class, new_class in class_mapping.items():
            content = re.sub(rf'\b{old_class}\b', new_class, content)
        
        return content
    
    def update_function_names(self, content):
        """Update function names"""
        function_patterns = [
            (r'\btuflow_(\w+)', r'coastalme_\1'),
            (r'\btu_(\w+)', r'cme_\1'),
            (r'\btuResults(\w*)', r'cmeResults\1'),
            (r'\btuPlot(\w*)', r'cmePlot\1')
        ]
        
        for pattern, replacement in function_patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def update_variables(self, content):
        """Update variable names"""
        var_mapping = {
            'tuView': 'cmeView',
            'tuResults': 'cmeResults',
            'tuPlot': 'cmePlot',
            'tuOptions': 'cmeOptions'
        }
        
        for old_var, new_var in var_mapping.items():
            content = re.sub(rf'\b{old_var}\b', new_var, content)
        
        return content
    
    def update_strings(self, content):
        """Update string literals"""
        string_mapping = {
            'TUFLOW': 'CoastalME',
            'TuView': 'CoastalME Viewer',
            'TUFLOW Viewer': 'CoastalME Viewer',
            'TUFLOW Results': 'CoastalME Results',
            'TUFLOW Plot': 'CoastalME Plot'
        }
        
        for old_string, new_string in string_mapping.items():
            content = content.replace(f'"{old_string}"', f'"{new_string}"')
            content = content.replace(f"'{old_string}'", f"'{new_string}'")
        
        return content
    
    def update_comments(self, content):
        """Update comments"""
        comment_mapping = {
            'TUFLOW': 'CoastalME',
            'TuView': 'CoastalME Viewer',
            'tuflow': 'coastalme'
        }
        
        for old_comment, new_comment in comment_mapping.items():
            content = re.sub(rf'# (.*?){old_comment}(.*?)$', rf'# \1{new_comment}\2', content, flags=re.MULTILINE)
        
        return content
    
    def migrate_metadata(self):
        """Update metadata.txt"""
        metadata_path = os.path.join(self.base_dir, 'coastalme', 'metadata.txt')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                content = f.read()
            
            # Update metadata fields
            content = content.replace('TUFLOW', 'CoastalME')
            content = content.replace('flood and coastal simulation', 'coastal and flood simulation')
            content = re.sub(r'name=.*', 'name=CoastalME', content)
            
            with open(metadata_path, 'w') as f:
                f.write(content)
            
            print("Updated metadata.txt")
    
    def run_migration(self):
        """Run complete migration"""
        print("Starting TUFLOW to CoastalME migration...")
        
        self.create_backup()
        self.migrate_directories()
        self.migrate_files()
        self.migrate_metadata()
        
        print("Migration completed successfully!")
        print(f"Backup stored in: {self.backup_dir}")

# Usage
if __name__ == '__main__':
    migrator = TuflowToCoastalMEMigrator('/path/to/plugin')
    migrator.run_migration()
```

### 10. Post-Migration Checklist

#### Validation Steps
```python
validation_checklist = [
    'Plugin loads without errors',
    'All menus and toolbars appear correctly',
    'Result loading works for all supported formats',
    'Time navigation functions properly',
    'Plot generation works for all plot types',
    'Animation export functions correctly',
    'Settings are saved and loaded properly',
    'No TUFLOW references remain in UI',
    'All help documentation updated',
    'Tests pass successfully'
]
```

#### Performance Testing
```python
performance_tests = [
    'Large result file loading',
    'Time step navigation speed',
    'Plot rendering performance',
    'Memory usage during animation',
    'Multi-result display performance'
]
```

### 11. Rollback Strategy

```python
def rollback_migration(base_dir):
    """Rollback migration if needed"""
    backup_dir = os.path.join(base_dir, 'backup_tuflow')
    
    if os.path.exists(backup_dir):
        print("Rolling back migration...")
        
        # Remove current files
        coastalme_dir = os.path.join(base_dir, 'coastalme')
        if os.path.exists(coastalme_dir):
            shutil.rmtree(coastalme_dir)
        
        # Restore backup
        shutil.copytree(backup_dir, base_dir)
        
        print("Rollback completed successfully")
    else:
        print("No backup found - cannot rollback")
```

## Success Criteria

The migration is considered successful when:

1. **Functionality Preserved**: All original features work exactly as before
2. **No TUFLOW References**: No user-visible TUFLOW references remain
3. **Code Quality**: Code maintains same structure and quality
4. **Performance**: No performance degradation
5. **Documentation**: All documentation updated consistently
6. **Testing**: All tests pass with new naming conventions

## Risk Mitigation

1. **Complete Backup**: Always create full backup before starting
2. **Incremental Migration**: Migrate in phases with testing between each
3. **Version Control**: Use git branches for migration work
4. **Testing**: Comprehensive testing after each phase
5. **Rollback Plan**: Clear rollback strategy if issues arise

## Timeline Estimate

- **Phase 1 (Analysis)**: 1-2 days ✓
- **Phase 2 (File Structure)**: 2-3 days
- **Phase 3 (Code Refactoring)**: 5-7 days
- **Phase 4 (Data Adaptation)**: 3-4 days
- **Phase 5 (Testing)**: 3-5 days

**Total Estimated Time**: 14-21 days

## Conclusion

This migration guide provides a systematic approach to converting the TUFLOW-based viewer to a CoastalME-focused system. The key is to preserve all functionality while completely removing TUFLOW branding and terminology.

The migration script provided can automate most of the work, but manual review and testing are essential to ensure quality and correctness.
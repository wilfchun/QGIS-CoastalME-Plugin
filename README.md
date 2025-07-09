# QGIS-CoastalME-Plugin

## CoastalME related QGIS Plugins

The QGIS-CoastalME plugin is a collection of tools to assist with the building and visualisation of [CoastalME](https://github.com/coastalme/coastalme) models.  These plugins can be used with [Crayfish](http://www.lutraconsulting.co.uk/products/crayfish/) to enable the visualisation the 2D timeseries output from CoastalME.

### Repository Contents:

- Readme.md - You're here
- /qgis_plugin/tuflow - contains the main core of the plugin.

- /utilities/ - location for functionality / libraries that can be re-used elsewhere (e.g. a python lib that's also a script).

### QGIS Version

  These plugins are currently only available for QGIS 2.0 and above.  We are no longer supporting a CoastalME plugin for 1.8. As part of the QGIS install python should already be installed on your machine.


### To install:  

  To enable please save the .zip file to your QGIS plugin directory and then unzip.  This zip folder will contain a number folders as outlined above.

The tuflow folder from QGIS-CoastalME-Plugin-master.zip\QGIS-CoastalME-Plugin-master\qgis_plugin\tuflow should sit directly plugin folder i.e.

	C:\Users\<username>\.qgis2\python\plugins\tuflow\


Alternatively you can clone the repository from github, although you will need to unpack into the directory structure above.

  
### To use:
  When you open QGIS the plugin should load itself. If not, you can enable it from Plugin > Manage and Install plugins window.  This can be found under 

	Plugins >> CoastalME

  To check you have the required dependencies please run the following tool:

    Plugins >> CoastalME >> About >> Check Python Dependencies Installed.

  If additional dependencies are required, these should be listed in the dialogue.  The main dependencies are:

- matplotlib

  You can download matplotlib from [here](http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.win32-py2.7.exe/download) and install it in the usual way.
  
- numpy

  You can download numpy from [here](http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python2.7.exe/download) and install it in the usual way.

  Alternatively, you can install them from OSGeo4W package manager.

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 coastalmeqgis_menu
                                 A QGIS plugin
 Initialises the COASTALME menu system
                              -------------------
        begin                : 2013-08-27
        copyright            : (C) 2013 by Phillip Ryan
        email                : support@coastalme.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# import setuptools

# Import the PyQt and QGIS libraries
# from qgis.PyQt.QtWidgets  import ( QMenu )

# Import the code for the dialog
from .coastalmeqgis_dialog import *
from .coastalmeqgis_library import about

# Import the code for the 1D results viewer
# from coastalmeqgis_TuPlot import *
# from TuPLOT_external import *

# Import the code for the 1D results viewer
from .coastalmeqgis_tuviewer.coastalmeqgis_tuview import TuView

from .provider import TuflowAlgorithmProvider

import tempfile
import shutil
import os
import glob
import sys

from subprocess import Popen, PIPE

if sys.platform == 'win32':
    from subprocess import DETACHED_PROCESS
else:
    DETACHED_PROCESS = None

try:
    from .swangis.swangis.ui import *

    swangisSupported = True
except ImportError:
    swangisSupported = False
except Exception as e:
    swangisSupported = False
    QMessageBox.warning(None, 'COASTALME Plugin', 'Error loading swangis tools: {0}'.format(e))

# clean up previous tempfiles
for_deleting = glob.glob(os.path.join(tempfile.gettempdir(), "coastalme_refh2*"))
for f in for_deleting:
    try:
        shutil.rmtree(f)
    except:
        continue

refh2dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ReFH2")
pyds = glob.glob(os.path.join(refh2dir, "*.pyd"))
if os.path.exists(os.path.join(refh2dir, 'refh2.py')):
    try:
        from .ReFH2.refh2 import Refh2Dock
    except ImportError as e:
        refh2_errmsg = str(e)
        Refh2Dock = None
elif pyds and sys.platform == 'win32':
    pyd = None
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        pyd = [x for x in pyds if "cp312" in x]
        if pyd:
            pyd = pyd[0]
    elif sys.version_info.major == 3 and sys.version_info.minor == 9:
        pyd = [x for x in pyds if "cp39" in x]
        if pyd:
            pyd = pyd[0]
    if pyd:
        tmpdir = tempfile.mkdtemp(prefix='coastalme_refh2')
        shutil.copy(pyd, tmpdir)
        sys.path.append(tmpdir)
        # try:
        from refh2 import Refh2Dock
        # except Exception as e:
        #     refh2_errmsg = str(e)
        #     Refh2Dock = None
    else:
        refh2_errmsg = 'Unsupported Python version installed with QGIS for ReFH2 tool.\nSupported versions: Python 3.9, Python 3.12'
        Refh2Dock = None
else:
    refh2_errmsg = 'ReFH2 tool not found or not supported on this platform.'
    Refh2Dock = None

# from coastalme.ReFH2.refh2 import Refh2Dock

from .SCS.scs import SCSDock

# import for integrity tool
from .integrity_tool.IntegrityTool import IntegrityToolDock

# par
from .coastalmeqgis_library import coastalmeqgis_apply_check_tf, resetQgisSettings

from .bridge_editor.BridgeEditor import ArchBridgeDock

from .menu_provider import TuflowContextMenuProvider

from .gui import Logging
from .gui.coastalmedrophandler import TuflowDropHandler

from .toc.toc import toc_selected_layers

# remote debugging
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2020.3.1\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2020.3.1\plugins\python\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\plugins\python\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2023.1.3\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\plugins\python\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\plugins\python-ce\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2023.1.3\plugins\python-ce\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2023.2.1\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2023.2.1\plugins\python\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\plugins\python\helpers\pydev')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\debug-eggs')
sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\plugins\python-ce\helpers\pydev')



from .compatibility_routines import QT_MESSAGE_BOX_CANCEL, QT_DOCK_WIDGET_AREA_RIGHT, QT_MESSAGE_BOX_YES, QT_TOOLBUTTIN_INSTANT_POPUP, QT_MESSAGE_BOX_NO, QT_DIALOG_TYPE, QT_DOCK_WIDGET_AREA_BOTTOM


class coastalmeqgis_menu:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = Path(os.path.realpath(__file__)).parent
        self.resultsPlottingDockOpened = False
        self.archBridgeDockOpen = False
        self.tpOpen = 'not open'
        self.intFile = ''
        self.cLayer = None
        self.tpExternal = None
        self.refh2DockOpen = False
        self.scsDockOpen = False
        self.defaultPath = 'C:\\'
        self.integrityToolOpened = False
        self.lambdaConnections = []
        self.icons = {}

        self.dropHandler = TuflowDropHandler(iface)
        self.provider = TuflowAlgorithmProvider()
        self.menu_provider = TuflowContextMenuProvider(self.iface)
        Logging.init_logging(iface)

    def icon(self, icon_name: str) -> QIcon:
        """Get icon."""
        if icon_name in self.icons:
            return self.icons[icon_name]
        p = self.plugin_dir / 'icons'
        for p_ in p.glob(f'{icon_name}.*'):
            icon = QIcon(str(p_))
            self.icons[icon_name] = icon
            return icon
        icon = QIcon()
        for p_ in p.glob(f'{icon_name}*'):
            regex = icon_name + r'_\d{2}$'
            if re.findall(regex, p_.stem):
                size = int(p_.stem[-2:])
                icon.addFile(str(p_), QSize(size, size))
        self.icons[icon_name] = icon
        return icon

    def initProcessing(self):
        """Create the Processing provider"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        self.menu_provider.init_menu()
        self.menu_provider.register_menu()
        for layer in QgsProject.instance().mapLayers().values():
            self.menu_provider.register_layer(layer)
        QgsProject.instance().layersAdded.connect(self.menu_provider.register_layers)

        self.iface.registerCustomDropHandler(self.dropHandler)

        dir = os.path.dirname(__file__)
        icon = QIcon(os.path.join(dir, "coastalme.png"))
        self.coastalmeMenu = self.iface.pluginMenu().addMenu(icon, "&COASTALME")

        # About Submenu
        self.about_menu = QMenu(QCoreApplication.translate("COASTALME", "&About"))
        self.coastalmeMenu.addMenu(self.about_menu)

        icon = QIcon(os.path.join(dir, "icons", "info.png"))
        self.about_action = QAction(icon, "About", self.iface.mainWindow())
        # QObject.connect(self.about_action, SIGNAL("triggered()"), self.about_coastalmeqgis)
        self.about_action.triggered.connect(self.about_coastalmeqgis)
        self.about_menu.addAction(self.about_action)

        icon = QIcon(os.path.join(dir, "icons", "check_dependancy.png"))
        self.check_dependancy_action = QAction(icon, "Check Python Dependencies Installed", self.iface.mainWindow())
        # QObject.connect(self.check_dependancy_action, SIGNAL("triggered()"), self.check_dependencies)
        self.check_dependancy_action.triggered.connect(self.check_dependencies)
        self.about_menu.addAction(self.check_dependancy_action)

        # Help
        self.about_menu.addSeparator()
        self.help_action = QAction(QgsApplication.getThemeIcon('/mActionHelpContents.svg'), '&Help', self.iface.mainWindow())
        self.help_action.triggered.connect(goto_plugin_help)
        self.about_menu.addAction(self.help_action)

        # Changelog
        self.changelog_action = QAction('&Changelog', self.iface.mainWindow())
        self.changelog_action.triggered.connect(goto_plugin_changelog)
        self.about_menu.addAction(self.changelog_action)

        self.about_menu.addSeparator()
        self.coastalme_downloads_page_action = QAction('COASTALME Downloads Webpage', self.iface.mainWindow())
        self.coastalme_downloads_page_action.triggered.connect(goto_coastalme_downloads)
        self.about_menu.addAction(self.coastalme_downloads_page_action)
        self.download_dev_version_action = QAction("Download Latest Development Version of COASTALME Plugin",
                                                   self.iface.mainWindow())
        self.download_dev_version_action.triggered.connect(lambda: download_latest_dev_plugin(self.iface))
        self.about_menu.addAction(self.download_dev_version_action)

        # Editing Submenu
        self.editing_menu = QMenu(QCoreApplication.translate("COASTALME", "&Editing"))
        self.coastalmeMenu.addMenu(self.editing_menu)

        # icon = QIcon(os.path.dirname(__file__) + "/icons/coastalme_increment_24px.png")
        # icon = QIcon(os.path.join(dir, "icons", "coastalme.png"))
        icon = QIcon()
        for size in [16, 24, 32, 48, 64]:
            icon.addFile(os.path.join(dir, "icons", "config_proj_{0}".format(size)), QSize(size, size))
        self.configure_tf_action = QAction(icon, "Configure / Create COASTALME Project", self.iface.mainWindow())
        # QObject.connect(self.configure_tf_action, SIGNAL("triggered()"), self.configure_tf)
        self.configure_tf_action.triggered.connect(self.configure_tf)
        self.editing_menu.addAction(self.configure_tf_action)

        icon = QIcon(os.path.join(dir, "icons", " coastalme_import.png"))
        self.import_empty_tf_action = QAction(icon, "Import Empty File", self.iface.mainWindow())
        # QObject.connect(self.import_empty_tf_action, SIGNAL("triggered()"), self.import_empty_tf)
        self.import_empty_tf_action.triggered.connect(self.import_empty_tf)
        self.editing_menu.addAction(self.import_empty_tf_action)

        # Add COASTALME attribute fields to existing GIS layer Added ES 23/02/2018
        icon = QIcon(os.path.join(dir, "icons", "insert_coastalme_attributes.png"))
        self.insert_COASTALME_attributes_action = QAction(icon, "Insert COASTALME Attributes to existing GIS layer",
                                                       self.iface.mainWindow())
        # QObject.connect(self.insert_COASTALME_attributes_action, SIGNAL("triggered()"), self.insert_COASTALME_attributes)
        self.insert_COASTALME_attributes_action.triggered.connect(self.insert_COASTALME_attributes)
        self.editing_menu.addAction(self.insert_COASTALME_attributes_action)

        icon = QIcon(os.path.join(dir, "icons", "coastalme_increment_24px.png"))
        self.increment_action = QAction(icon, "Increment Selected Layer", self.iface.mainWindow())
        # QObject.connect(self.increment_action, SIGNAL("triggered()"), self.increment_layer)
        self.increment_action.triggered.connect(self.increment_layer)
        self.editing_menu.addAction(self.increment_action)

        """Removed split_MI beta tool for now"""
        # icon = QIcon(os.path.dirname(__file__) + "/icons/mif_2_shp.png")
        # self.splitMI_action = QAction(icon, "Convert MapInfo file to Shapefile (beta)", self.iface.mainWindow())
        ##QObject.connect(self.splitMI_action, SIGNAL("triggered()"), self.split_MI)
        # self.splitMI_action.triggered.connect(self.split_MI)
        # self.editing_menu.addAction(self.splitMI_action)

        """Removed split_MI_folder tool for now"""
        # icon = QIcon(os.path.dirname(__file__) + "/icons/mif_2_shp.png")
        # self.splitMI_folder_action = QAction(icon, "Convert MapInfo files in folder Shapefile (beta)", self.iface.mainWindow())
        ##QObject.connect(self.splitMI_folder_action, SIGNAL("triggered()"), self.split_MI_folder)
        # self.splitMI_folder_action.triggered.connect(self.split_MI_folder)
        # self.editing_menu.addAction(self.splitMI_folder_action)

        """Not tested enough to include"""
        # icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        # self.points_to_lines_action = QAction(icon, "Convert Points to Lines (survey to breaklines) ALPHA", self.iface.mainWindow())
        # QObject.connect(self.points_to_lines_action, SIGNAL("triggered()"), self.points_to_lines)
        # self.editing_menu.addAction(self.points_to_lines_action)

        # RUN Submenu
        self.run_menu = QMenu(QCoreApplication.translate("COASTALME", "&Run"))
        self.coastalmeMenu.addMenu(self.run_menu)

        icon = QIcon(os.path.join(dir, "icons", "Run_COASTALME.png"))
        self.run_coastalme_action = QAction(icon, "Run COASTALME Simulation", self.iface.mainWindow())
        # QObject.connect(self.run_coastalme_action, SIGNAL("triggered()"), self.run_coastalme)
        self.run_coastalme_action.triggered.connect(self.run_coastalme)
        self.run_menu.addAction(self.run_coastalme_action)

        icon = QIcon(os.path.join(dir, "runner\\coastalme-runner\\icons\\runner", "icons8-exercise.ico"))
        self.launch_runner_action = QAction(icon, "Launch COASTALME Runner", self.iface.mainWindow())
        # QObject.connect(self.run_coastalme_action, SIGNAL("triggered()"), self.run_coastalme)
        self.launch_runner_action.triggered.connect(self.launch_runner)
        self.run_menu.addAction(self.launch_runner_action)

        # CLEAR Submenu
        self.clear_menu = QMenu(QCoreApplication.translate("COASTALME", "&Clear"))
        self.coastalmeMenu.addMenu(self.clear_menu)
        self.clearGlobalSettingsAction = QAction("Clear COASTALME Global Settings", self.iface.mainWindow())
        self.clearProjectSettingsAction = QAction("Clear COASTALME Project Settings", self.iface.mainWindow())
        self.removeTuviewAction = QAction("Close COASTALME Viewer Completely", self.iface.mainWindow())
        self.reloadTuviewAction = QAction("Reload COASTALME Viewer", self.iface.mainWindow())
        self.clear_menu.addAction(self.clearGlobalSettingsAction)
        self.clear_menu.addAction(self.clearProjectSettingsAction)
        self.clear_menu.addAction(self.removeTuviewAction)
        self.clear_menu.addAction(self.reloadTuviewAction)
        self.clearGlobalSettingsAction.triggered.connect(lambda: resetQgisSettings(scope='Global'))
        self.clearProjectSettingsAction.triggered.connect(lambda: resetQgisSettings(scope='Project'))
        self.removeTuviewAction.triggered.connect(self.removeTuview)
        self.reloadTuviewAction.triggered.connect(self.reloadTuview)

        # top level in menu

        # Reload Data Added ES 16/07/18
        icon = QIcon(os.path.join(dir, "icons", "Reload_Data.PNG"))
        self.reload_data_action = QAction(icon, "Reload Data", self.iface.mainWindow())
        self.reload_data_action.triggered.connect(self.reload_data)
        self.iface.addToolBarIcon(self.reload_data_action)
        self.coastalmeMenu.addAction(self.reload_data_action)

        # TuPlot
        icon = QIcon(os.path.join(dir, "icons", "tuview.png"))
        self.view_results_action = QAction(icon, "COASTALME Viewer", self.iface.mainWindow())
        self.view_results_action.triggered.connect(self.openResultsPlottingWindow)
        self.iface.addToolBarIcon(self.view_results_action)
        self.coastalmeMenu.addAction(self.view_results_action)

        # Integrity Tool
        icon = QIcon(os.path.join(dir, "icons", "IntegrityTool.png"))
        self.integrity_tool_action = QAction(icon, "1D Integrity Tool", self.iface.mainWindow())
        self.integrity_tool_action.triggered.connect(self.integrityToolWindow)
        self.iface.addToolBarIcon(self.integrity_tool_action)
        self.coastalmeMenu.addAction(self.integrity_tool_action)

        # configure project in toolbar
        self.iface.addToolBarIcon(self.configure_tf_action)

        # bridges
        # code for icon with menu - preserved when we have more bridge editors
        iconArch = QIcon(os.path.join(dir, "icons", "ArchBridge.png"))
        iconClearSpan = QIcon(os.path.join(dir, "icons", "ClearSpanBridge.png"))
        self.archBridgeAction = QAction(iconArch, "Arch Bridge", self.iface.mainWindow())
        self.archBridgeAction.setToolTip(r'Arch Bridge Editor &#40;beta&#41;')
        self.archBridgeAction.triggered.connect(self.archBrideEditor)
        # clearSpanAction = QAction(iconClearSpan, "Clear Span Bridge", self.iface.mainWindow())
        # clearSpanAction.triggered.connect(self.clearSpanBridgeEditor)
        # toolButton = QToolButton()
        # toolButton.setIcon(iconArch)
        # toolButton.setToolTip("Bridge Editor")
        # menu = QMenu()
        # menu.addAction(archBridgeAction)
        # menu.addAction(clearSpanAction)
        # toolButton.setMenu(menu)
        # toolButton.setPopupMode(QT_TOOLBUTTIN_INSTANT_POPUP)
        # self.iface.addToolBarWidget(toolButton)
        self.iface.addToolBarIcon(self.archBridgeAction)
        self.coastalmeMenu.addAction(self.archBridgeAction)

        # TuPLOT External Added ES 2017/11
        # icon = QIcon(os.path.dirname(__file__) + "/icons/TuPLOT_External.PNG")
        # self.open_tuplot_external_action = QAction(icon, "TuPlot_Ext", self.iface.mainWindow())
        ##QObject.connect(self.open_tuplot_external_action, SIGNAL("triggered()"), self.open_tuplot_ext)
        # self.open_tuplot_external_action.triggered.connect(self.open_tuplot_ext)
        # self.iface.addToolBarIcon(self.open_tuplot_external_action)
        # self.iface.addPluginToMenu("&COASTALME", self.open_tuplot_external_action)

        # Added MJS 24/11
        icon = QIcon(os.path.join(dir, "icons", "coastalme_import.png"))
        self.import_empty_tf_action = QAction(icon, "Import Empty File", self.iface.mainWindow())
        # QObject.connect(self.import_empty_tf_action, SIGNAL("triggered()"), self.import_empty_tf)
        self.import_empty_tf_action.triggered.connect(self.import_empty_tf)
        self.iface.addToolBarIcon(self.import_empty_tf_action)
        self.coastalmeMenu.addAction(self.import_empty_tf_action)

        # insert COASTALME attributes to existing GIS layer
        self.coastalmeMenu.addAction(self.insert_COASTALME_attributes_action)
        self.iface.addToolBarIcon(self.insert_COASTALME_attributes_action)

        # ES 2018/05 Load input files from TCF
        icon = QIcon(os.path.join(dir, "icons", "Load_from_TCF.PNG"))
        self.load_coastalmeFiles_from_TCF_action = QAction(icon, "Load COASTALME Layers from TCF", self.iface.mainWindow())
        self.load_coastalmeFiles_from_TCF_action.triggered.connect(self.loadTuflowLayersFromTCF)
        self.coastalmeMenu.addAction(self.load_coastalmeFiles_from_TCF_action)
        self.iface.addToolBarIcon(self.load_coastalmeFiles_from_TCF_action)

        # ES 2019/01 Filter and Sort COASTALME Layers in Map Window
        icon = QIcon(os.path.join(dir, "icons", "filter_sort_layers.png"))
        self.filterAndSortLayersAction = QAction(icon, "Filter and Sort COASTALME Layers in Map Window",
                                                 self.iface.mainWindow())
        self.filterAndSortLayersAction.triggered.connect(self.filterAndSortLayers)
        self.coastalmeMenu.addAction(self.filterAndSortLayersAction)
        self.iface.addToolBarIcon(self.filterAndSortLayersAction)

        # Added MJS 24/11
        icon = QIcon(os.path.join(dir, "icons", "coastalme_increment_24px.png"))
        self.increment_action = QAction(icon, "Increment Selected Layer", self.iface.mainWindow())
        # QObject.connect(self.increment_action, SIGNAL("triggered()"), self.increment_layer)
        self.increment_action.triggered.connect(self.increment_layer)
        self.iface.addToolBarIcon(self.increment_action)
        self.coastalmeMenu.addAction(self.increment_action)

        # Added MJS 11/02
        icon = QIcon(os.path.join(dir, "icons", "check_files_folder.png"))
        self.import_chk_action = QAction(icon, "Import Check Files from Folder", self.iface.mainWindow())
        # QObject.connect(self.import_chk_action, SIGNAL("triggered()"), self.import_check)
        self.import_chk_action.triggered.connect(self.import_check)
        self.iface.addToolBarIcon(self.import_chk_action)
        self.coastalmeMenu.addAction(self.import_chk_action)

        # PAR 2016/02/12
        icon = QIcon(os.path.join(dir, "icons", "check_files_open.png"))
        self.apply_chk_action = QAction(icon, "Apply COASTALME Styles to Open Layers", self.iface.mainWindow())
        # Object.connect(self.apply_chk_action, SIGNAL("triggered()"), self.apply_check)
        self.apply_chk_action.triggered.connect(self.apply_check)
        self.iface.addToolBarIcon(self.apply_chk_action)
        self.iface.addToolBarIcon(self.apply_chk_action)

        # PAR 2016/02/15
        icon = QIcon(os.path.join(dir, "icons", "check_files_currentlayer.png"))
        self.apply_chk_cLayer_action = QAction(icon, "Apply COASTALME Styles to Current Layer", self.iface.mainWindow())
        # QObject.connect(self.apply_chk_cLayer_action, SIGNAL("triggered()"), self.apply_check_cLayer)
        self.apply_chk_cLayer_action.triggered.connect(self.apply_check_cLayer)
        # self.iface.addToolBarIcon(self.apply_chk_cLayer_action)
        # self.iface.addPluginToMenu("&COASTALME", self.apply_chk_cLayer_action)
        self.apply_stability_style_clayer_action = QAction(QIcon(os.path.join(dir, "icons", "style_stability.png")),
                                                           "Apply Stability Checking Style to Current Layer",
                                                           self.iface.mainWindow())
        self.apply_stability_style_clayer_action.triggered.connect(self.apply_stability_styling_clayer)

        self.apply_style_clayer_menu = QMenu()
        self.apply_style_clayer_menu.addAction(self.apply_chk_cLayer_action)
        self.apply_style_clayer_menu.addAction(self.apply_stability_style_clayer_action)
        self.apply_style_clayer_menu.setIcon(icon)
        self.apply_style_clayer_menu.menuAction().setToolTip("Apply COASTALME Styles to Current Layer")
        self.apply_style_clayer_menu.setDefaultAction(self.apply_chk_cLayer_action)
        self.style_menu_connection = self.apply_style_clayer_menu.menuAction().triggered.connect(
            self.apply_check_cLayer)
        self.iface.addToolBarIcon(self.apply_style_clayer_menu.menuAction())

        # self.toolButton = QToolButton()
        # self.toolButton.setIcon(icon)
        # self.toolButton.setToolTip("Apply COASTALME Styles to Current Layer")
        # menu = QMenu()
        # menu.addAction(self.apply_chk_cLayer_action)
        # menu.addAction(self.apply_stability_style_clayer_action)
        # self.toolButton.setMenu(menu)
        # self.toolButton.setPopupMode(QT_TOOLBUTTIN_INSTANT_POPUP)
        # self.iface.addToolBarWidget(self.toolButton)

        if spatial_database_option:
            icon = QIcon(os.path.join(dir, "icons", "geopackage.jpg"))
            self.apply_gpkg_layernames_action = QAction(icon, "Apply GPKG Layer Names", self.iface.mainWindow())
            self.apply_gpkg_layernames_action.triggered.connect(self.apply_gpkg_layername)
            self.iface.addToolBarIcon(self.apply_gpkg_layernames_action)

        # Auto label generator ES 8/03/2018
        icon = QIcon(os.path.join(dir, "icons", "Label_icon.PNG"))
        # self.apply_auto_label_action = QAction(icon, "Apply Label to Current Layer", self.iface.mainWindow())
        # self.apply_auto_label_action.triggered.connect(self.apply_label_cLayer)
        # self.iface.addToolBarIcon(self.apply_auto_label_action)
        # self.tbAutoLabel = QToolButton()
        # self.tbAutoLabel.setIcon(icon)
        # self.tbAutoLabel.setToolTip("Apply Label to Current Layer")
        self.autoLabelMenu = QMenu()
        self.autoLabelMenu.menuAction().triggered.connect(self.apply_label_cLayer)
        self.autoLabelMenu.setIcon(icon)
        self.autoLabelMenu.menuAction().setToolTip("Apply Label to Current Layer")
        self.autoLabelSettingLocAction = QAction("Open Label Settings", self.autoLabelMenu)
        self.autoLabelSettingLocAction.triggered.connect(self.openLabelSettingLoc)
        self.autoLabelMenu.addAction(self.autoLabelSettingLocAction)
        # self.iface.addPluginToMenu("&COASTALME", self.apply_auto_label_action)
        # self.tbAutoLabel.setMenu(self.autoLabelMenu)
        self.iface.addToolBarIcon(self.autoLabelMenu.menuAction())

        # ES 2018/01 ARR2016 Beta
        icon = QIcon(os.path.join(dir, "icons", "arr2016.PNG"))
        self.extract_arr2016_action = QAction(icon, "Extract ARR2019 for COASTALME", self.iface.mainWindow())
        # QObject.connect(self.extract_arr2016_action, SIGNAL("triggered()"), self.extract_arr2016)
        self.extract_arr2016_action.triggered.connect(self.extract_arr2016)
        self.coastalmeMenu.addAction(self.extract_arr2016_action)
        self.iface.addToolBarIcon(self.extract_arr2016_action)

        # ReFH2
        icon = QIcon(os.path.join(dir, "icons", "ReFH2icon.png"))
        self.extractRefh2Action = QAction(icon, "Extract ReFH 2 for COASTALME", self.iface.mainWindow())
        self.extractRefh2Action.triggered.connect(self.extractRefh2)
        self.coastalmeMenu.addAction(self.extractRefh2Action)
        self.iface.addToolBarIcon(self.extractRefh2Action)

        # SCS
        icon = QIcon(os.path.join(dir, "icons", "CNicon.png"))
        self.extractSCSAction = QAction(icon, "Extract SCS for COASTALME (beta)", self.iface.mainWindow())
        self.extractSCSAction.triggered.connect(self.extractSCS)
        self.coastalmeMenu.addAction(self.extractSCSAction)
        self.iface.addToolBarIcon(self.extractSCSAction)

        # ES 2019/01 COASTALME Utilities
        icon = QgsApplication.getThemeIcon('mActionTerminal.svg')
        self.coastalmeUtilitiesAction = QAction(icon, "COASTALME Utilities", self.iface.mainWindow())
        self.coastalmeUtilitiesAction.triggered.connect(self.coastalmeUtilities)
        self.coastalmeMenu.addAction(self.coastalmeUtilitiesAction)
        self.iface.addToolBarIcon(self.coastalmeUtilitiesAction)

        # Init classes variables
        self.dockOpened = False  # remember for not reopening dock if there's already one opened
        self.resdockOpened = False
        self.selectionmethod = 0  # The selection method defined in option
        self.saveTool = self.iface.mapCanvas().mapTool()  # Save the standard mapttool for restoring it at the end
        self.layerindex = None  # for selection mode
        self.previousLayer = None  # for selection mode
        self.plotlibrary = None  # The plotting library to use
        self.textquit0 = "Click for polyline and double click to end (right click to cancel then quit)"
        self.textquit1 = "Select the polyline in a vector layer (Right click to quit)"

        # SWMM tools - all in processing tools for now
        # self.swmmMenu = QMenu(QCoreApplication.translate("COASTALME", "SWMM"))
        # self.swmmAction = QAction("SWMM Tools", self.iface.mainWindow())
        # self.iface.addPluginToMenu('&COASTALME', self.swmmAction)

        # swangis
        self.builderUI = None
        self.processingUI = None
        self.swanMenu = QMenu()
        self.builderAction = QAction("Model Builder", self.iface.mainWindow())
        self.builderAction.triggered.connect(self.runBuilderUI)
        self.processingAction = QAction("Post Processing", self.iface.mainWindow())
        self.processingAction.triggered.connect(self.runProcessingUI)
        self.swanMenu.addAction(self.builderAction)
        self.swanMenu.addAction(self.processingAction)
        self.swanAction = QAction("SWAN GIS Tools (beta)", self.iface.mainWindow())
        self.swanAction.setMenu(self.swanMenu)
        self.coastalmeMenu.addAction(self.swanAction)
        QgsProject.instance().cleared.connect(self.clearBuilderUI)

    def unload(self):
        self.menu_provider.unregister_menu()

        # coastalme viewer
        self.removeTuview(no_popup=True)

        # integrity tool
        try:
            self.integrityTool.qgisDisconnect()
        except:
            pass
        try:
            self.integrityTool.close()
            self.iface.removeDockWidget(self.integrityTool)
            del self.integrityTool
        except:
            pass
        # refh2
        try:
            self.refh2Dock.qgisDisconnect()
        except:
            pass
        try:
            self.refh2Dock.close()
            self.iface.removeDockWidget(self.refh2Dock)
            del self.refh2Dock
        except:
            pass
        # SCS
        try:
            self.scsDock.close()
            self.iface.removeDockWidget(self.scsDock)
            del self.scsDock
        except:
            pass
        # SWAN
        try:
            self.clearBuilderUI()
        except:
            pass
        try:
            self.clearProcessingUI()
        except:
            pass
        # BRIDGE EDITOR
        try:
            self.archBridgeDock.close()
            self.iface.removeDockWidget(self.archBridgeDock)
            del self.archBridgeDock
        except:
            pass

        self.qgisDisconnect()

        self.coastalmeMenu.clear()
        self.iface.pluginMenu().removeAction(self.coastalmeMenu.menuAction())

        self.iface.removeToolBarIcon(self.reload_data_action)
        self.iface.removeToolBarIcon(self.view_results_action)
        self.iface.removeToolBarIcon(self.integrity_tool_action)
        self.iface.removeToolBarIcon(self.import_empty_tf_action)
        self.iface.removeToolBarIcon(self.insert_COASTALME_attributes_action)
        self.iface.removeToolBarIcon(self.load_coastalmeFiles_from_TCF_action)
        self.iface.removeToolBarIcon(self.filterAndSortLayersAction)
        self.iface.removeToolBarIcon(self.increment_action)
        self.iface.removeToolBarIcon(self.import_chk_action)
        self.iface.removeToolBarIcon(self.apply_chk_action)
        self.iface.removeToolBarIcon(self.apply_style_clayer_menu.menuAction())
        self.iface.removeToolBarIcon(self.autoLabelMenu.menuAction())
        self.iface.removeToolBarIcon(self.extract_arr2016_action)
        self.iface.removeToolBarIcon(self.extractRefh2Action)
        self.iface.removeToolBarIcon(self.extractSCSAction)
        self.iface.removeToolBarIcon(self.coastalmeUtilitiesAction)
        if spatial_database_option:
            self.iface.removeToolBarIcon(self.apply_gpkg_layernames_action)
        self.iface.removeToolBarIcon(self.archBridgeAction)
        self.iface.removeToolBarIcon(self.configure_tf_action)

    def configure_tf(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_configure_tf_dialog(self.iface, project, self.iface.mainWindow())
        dialog.exec()

    def create_tf_dir(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_create_tf_dir_dialog(self.iface, project)
        dialog.exec()

    def import_empty_tf(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_import_empty_tf_dialog(self.iface, project)
        dialog.exec()

    def increment_layer(self):
        dialog = coastalmeqgis_increment_dialog(self.iface)
        dialog.exec()

    def flow_trace(self):
        dialog = coastalmeqgis_flowtrace_dialog(self.iface)
        dialog.exec()

    def points_to_lines(self):
        # QMessageBox.information(self.iface.mainWindow(), "debug", "points to lines")
        dialog = coastalmeqgis_line_from_points(self.iface)
        dialog.exec()

    def split_MI(self):
        # QMessageBox.information(self.iface.mainWindow(), "debug", "points to lines")
        dialog = coastalmeqgis_splitMI_dialog(self.iface)
        dialog.exec()

    def split_MI_folder(self):
        # QMessageBox.information(self.iface.mainWindow(), "debug", "points to lines")
        QMessageBox.information(self.iface.mainWindow(), "debug", "starting")
        dialog = coastalmeqgis_splitMI_folder_dialog(self.iface)
        dialog.exec()

    #### external viewer interface
    #	def results_1d_ext(self):
    #		if self.dockOpened == False:
    #			self.dock = COASTALMEifaceDock(self.iface)
    #			self.iface.addDockWidget( QT_DOCK_WIDGET_AREA_RIGHT, self.dock )
    #			self.dockOpened = True

    def openResultsPlottingWindow(self, showmessage=True):
        qv = Qgis.QGIS_VERSION_INT
        if self.resultsPlottingDockOpened:
            if not self.resultsPlottingDock.isVisible():
                self.resultsPlottingDock.show()
                self.resultsPlottingDock.qgisConnect()
            elif showmessage:
                bRedock = QMessageBox.question(self.iface.mainWindow(), "COASTALME Viewer",
                                               "Would you like to redock COASTALME Viewer?",
                                               QT_MESSAGE_BOX_YES | QT_MESSAGE_BOX_NO | QT_MESSAGE_BOX_CANCEL)
                if bRedock == QT_MESSAGE_BOX_YES:
                    self.resultsPlottingDock.setFloating(False)
        else:
            try:
                self.resultsPlottingDock = TuView(self.iface, removeTuview=self.removeTuviewAction,
                                                  reloadTuview=self.reloadTuviewAction)
            except:
                self.resultsPlottingDock = TuView(self.iface)
            dockArea = QT_DOCK_WIDGET_AREA_BOTTOM
            isTabified = False
            tabifiedWith = []
            if QSettings().value("COASTALME/tuview_defaultlayout", "previous_state") == "narrow" or \
                    (QSettings().value("COASTALME/tuview_defaultlayout", "previous_state") == 'previous_state' and
                     QSettings().value("COASTALME/tuview_previouslayout", "plot") == "narrow"):
                dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                if QSettings().contains("COASTALME/tuview_docklocation"):
                    dockArea = QSettings().value("COASTALME/tuview_docklocation", QT_DOCK_WIDGET_AREA_RIGHT)
                    if type(dockArea) is str:
                        try:
                            dockArea = int(dockArea)
                        except ValueError:
                            dockArea = QT_DOCK_WIDGET_AREA_RIGHT
                isTabified = QSettings().value("COASTALME/tuview_isdocktabified", False)
                if type(isTabified) is str:
                    try:
                        isTabified = bool(isTabified)
                    except ValueError:
                        isTabified = False
                if isTabified:
                    tabifiedWith = QSettings().value("COASTALME/tuview_tabifiedwith", [])
                    if type(isTabified) is str:
                        tabifiedWith = tabifiedWith.split(",")
                    if not tabifiedWith:
                        isTabified = False

            if isTabified and qv >= 31400:
                self.iface.addTabifiedDockWidget(dockArea, self.resultsPlottingDock, tabifiedWith, True)
            else:
                self.iface.addDockWidget(dockArea, self.resultsPlottingDock)
            self.resultsPlottingDockOpened = True

    def removeTuview(self, **kwargs):
        no_popup = kwargs['no_popup'] if 'no_popup' in kwargs else False
        resetQgisSettings(scope='Project', tuviewer=True, feedback=False)
        try:
            self.resultsPlottingDock.tuPlot.clearAllPlots()
            self.resultsPlottingDock.qgisDisconnect(completely_remove=True)
            self.resultsPlottingDock.close()
            self.iface.removeDockWidget(self.resultsPlottingDock)
            del self.resultsPlottingDock
            self.resultsPlottingDockOpened = False
            if 'feedback' in kwargs:
                if not kwargs['feedback']:
                    return
            if not no_popup:
                QMessageBox.information(self.iface.mainWindow(), "COASTALME", "Completely Closed COASTALME Viewer")
        except:
            if 'feedback' in kwargs:
                if not kwargs['feedback']:
                    return
            if not no_popup:
                QMessageBox.information(self.iface.mainWindow(), "COASTALME",
                                        "ERROR closing COASTALME Viewer. Please email support@coastalme.com")

    def reloadTuview(self):
        self.removeTuview(feedback=False)
        self.openResultsPlottingWindow()

    # def open_tuplot_ext(self):
    #	"""TuPLOT external function."""
    #
    #	# initiate External TuPLOT library
    #	self.tpExternal = TuPLOT(self.iface)
    #
    #	# below try statement just checks if TuPLOT is already open
    #	try:
    #		poll = self.tpOpen.poll()
    #		if poll == None: # TuPLOT is open
    #			self.tpOpen, self.intFile, self.defaultPath = self.tpExternal.open(self.tpOpen, self.intFile, self.defaultPath)
    #			self.cLayer = self.iface.mapCanvas().currentLayer()
    #		else: # TuPLOT is not already open
    #			self.tpOpen, self.intFile, self.defaultPath = self.tpExternal.open('not open', self.intFile, self.defaultPath)
    #			self.cLayer = self.iface.mapCanvas().currentLayer()
    #	except: # first time TuPLOT has been initiated so must not be open
    #		self.tpOpen, self.intFile, self.defaultPath = self.tpExternal.open('not open', self.intFile, self.defaultPath)
    #		self.cLayer = self.iface.mapCanvas().currentLayer()
    #
    #	# connect external TuPLOT to signals
    #	try:
    #		poll = self.tpOpen.poll()
    #		if poll == None: # TuPLOT is running so connect
    #			if self.cLayer is not None: # there is a current layer selected so connect both selection change and layer change
    #				#QObject.connect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
    #				self.cLayer.selectionChanged.connect(self.select_changed)
    #				#QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.layer_changed)
    #				self.iface.currentLayerChanged.connect(self.layer_changed)
    #			else: # there is no current layer selected so connect layer change only
    #				#QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.layer_changed)
    #				self.iface.currentLayerChanged.connect(self.layer_changed)
    #		else: # TuPLOT is not running so disconnect
    #			#QObject.disconnect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
    #			self.cLayer.selectionChanged.disconnect(self.select_changed)
    #			#QObject.disconnect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.layer_changed)
    #			self.iface.currentLayerChanged.disconnect(self.layer_changed)
    #	except:
    #		None

    def select_changed(self):
        """Used with TuPLOT external function. Is called when current selection changes."""

        # check to see if TuPLOT is open
        poll = self.tpOpen.poll()
        if poll == None:  # TuPLOT is open so update .int file
            self.tpOpen, self.intFile, self.defaultPath = self.tpExternal.open(self.tpOpen, self.intFile,
                                                                               self.defaultPath)
        else:  # TuPLOT is not open so disconnect signals
            # QObject.disconnect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
            self.cLayer.selectionChanged.disconnect(self.select_changed)
            # QObject.disconnect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.layer_changed)
            self.iface.currentLayerChanged.disconnect(self.layer_changed)

    def layer_changed(self):
        """Used with TuPLOT external function. Is called when current layer changes."""

        self.cLayer = self.iface.mapCanvas().currentLayer()
        if self.cLayer is not None:
            # QObject.connect(self.cLayer,SIGNAL("selectionChanged()"),self.select_changed)
            self.cLayer.selectionChanged.connect(self.select_changed)

    def cleaning_res(self):
        QMessageBox.information(self.iface.mainWindow(), "debug", "Dock Closed")
        self.dockOpened = False

    def run_coastalme(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_run_tf_simple_dialog(self.iface, project)
        dialog.exec()

    def launch_runner(self):
        if sys.platform != 'win32':
            QMessageBox.warning(self.iface.mainWindow(), "Not Supported",
                                "The COASTALME Runner is currently only supported on Windows")
            return
        dir = os.path.dirname(__file__)
        script_with_path = os.path.join(dir, "runner\\coastalme-runner\\runner\\main.py")
        if not os.path.isfile(script_with_path):
            QMessageBox.critical(self.iface.mainWindow(), "Not Found",
                                 f'The COASTALME runner script not found at {script_with_path}')
            return
        command = ['python3', script_with_path]
        # https://stackoverflow.com/questions/70543646/module-does-not-have-the-attribute-subprocess-detached-process
        process = Popen(command, creationflags=DETACHED_PROCESS, start_new_session=True)

    def check_dependencies(self):
        # QMessageBox.critical(self.iface.mainWindow(), "Info", "Not yet implemented!")
        from .coastalmeqgis_library import check_python_lib
        error = check_python_lib(self.iface)
        if error != None:
            QMessageBox.critical(self.iface.mainWindow(), "Error", "Not all dependencies installed.")
        else:
            QMessageBox.information(self.iface.mainWindow(), "Information", "All dependencies installed :)")

    def about_coastalmeqgis(self):
        # QMessageBox.information(self.iface.mainWindow(), "About COASTALME QGIS", 'This is a developmental version of the COASTALME QGIS utitlity, build: '+build_vers)
        # QMessageBox.information(self.iface.mainWindow(), "About COASTALME QGIS", "This is a {0} version of the COASTALME QGIS utility\nBuild: {1}".format(build_type,build_vers))
        about(self.iface.mainWindow())

    # Added MJS 11/02
    def import_check(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_import_check_dialog(self.iface, project)
        dialog.exec()

    def apply_check(self):
        error, message = coastalmeqgis_apply_check_tf(self.iface)
        if error:
            QMessageBox.critical(self.iface.mainWindow(), "Error", message)

    def apply_check_cLayer(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "check_files_currentlayer.png"))
        self.apply_style_clayer_menu.setIcon(icon)
        self.apply_style_clayer_menu.menuAction().setToolTip("Apply COASTALME Styles to Current Layer")
        self.apply_style_clayer_menu.setDefaultAction(self.apply_chk_cLayer_action)
        self.apply_style_clayer_menu.menuAction().triggered.disconnect(self.style_menu_connection)
        self.style_menu_connection = self.apply_style_clayer_menu.menuAction().triggered.connect(
            self.apply_check_cLayer)
        error, message = coastalmeqgis_apply_check_tf_clayer(self.iface)
        if error:
            QMessageBox.critical(self.iface.mainWindow(), "Error", message)

    def apply_stability_styling_clayer(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "style_stability.png"))
        self.apply_style_clayer_menu.setIcon(icon)
        self.apply_style_clayer_menu.menuAction().setToolTip("Apply Stability Styling to Current Layer")
        self.apply_style_clayer_menu.setDefaultAction(self.apply_stability_style_clayer_action)
        self.apply_style_clayer_menu.menuAction().triggered.disconnect(self.style_menu_connection)
        self.style_menu_connection = self.apply_style_clayer_menu.menuAction().triggered.connect(
            self.apply_stability_styling_clayer)
        error, message = coastalmeqgis_apply_stability_style_clayer(self.iface)
        if error:
            QMessageBox.critical(self.iface.mainWindow(), "Error", message)

    def apply_gpkg_layername(self):
        coastalmeqgis_apply_gpkg_layername(self.iface)

    def extract_arr2016(self):
        dialog = coastalmeqgis_extract_arr2016_dialog(self.iface)
        dialog.exec()

    def insert_COASTALME_attributes(self):
        project = QgsProject.instance()
        dialog = coastalmeqgis_insert_coastalme_attributes_dialog(self.iface, project)
        dialog.exec()

    def apply_label_cLayer(self):
        error, message = coastalmeqgis_apply_autoLabel_clayer(self.iface)
        if error:
            QMessageBox.critical(self.iface.mainWindow(), "Error", message)

    def openLabelSettingLoc(self):
        dir = os.path.dirname(__file__)
        p = os.path.join(dir, "layer_labelling")
        os.startfile(p)

    def loadTuflowLayersFromTCF(self):
        settings = QSettings()
        lastFolder = str(settings.value("COASTALME/load_TCF_last_folder", os.sep))
        if (len(lastFolder) > 0):  # use last folder if stored
            fpath = lastFolder
        else:
            cLayer = self.iface.mapCanvas.currentLayer()
            if cLayer:  # if layer selected use the path to this
                dp = cLayer.dataProvider()
                ds = dp.dataSourceUri()
                fpath = os.path.dirname(unicode(ds))
            else:  # final resort to current working directory
                fpath = os.getcwd()

        old_method = sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 9)
        inFileName, _ = QFileDialog.getOpenFileName(self.iface.mainWindow(), 'Open COASTALME Control File', fpath,
                                                    "All control files (*.tcf *.ecf *.tgc *.tbc *.tef *.toc *.qcf *.trfc *.trfcf *.trd *.escf *.adcf *.tscf);;"
                                                    "TCF (*.tcf);;ECF (*.ecf);;TGC (*.tgc);;TBC (*.tbc);;TEF (*.tef);;TOC (*.toc);;QCF (.qcf);;TRFC (*.trfc *.trfcf);;TRD (*.trd);;ESCF (*.escf);;ADCF (*.adcf);;TSCF (*.tscf)")
        if inFileName:
            if old_method:
                load_rasters = LoadRasterMessageBox(self.iface.mainWindow(), 'Load Rasters',
                                                    'Load raster layers into workspace (large raster layers can be slow to load)?')
        options_called = False
        # for inFileName in inFileNames[0]:
        #	if not inFileNames or len(inFileName) < 1:  # empty list
        if not inFileName:  # empty list
            return
        else:
            fpath, fname = os.path.split(inFileName)
            if fpath != os.sep and fpath.lower() != 'c://' and fpath != '':
                settings.setValue("COASTALME/load_TCF_last_folder", fpath)
            # if os.path.splitext(inFileName)[1].lower() != '.tcf':
            if False:
                QMessageBox.information(self.iface.mainWindow(), "Message", 'Must select TCF')
                return
            else:
                if old_method:
                    error, message, scenarios = getScenariosFromTcf(inFileName)
                    events = []
                else:
                    error, message = False, ''
                    scenarios, events = [], []
                    try:
                        getScenariosFromTCF_v2(inFileName, scenarios, events)
                    except Exception:
                        error = True
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        message = ''.join(traceback.extract_tb(exc_traceback).format()) + '{0}{1}'.format(exc_type,
                                                                                                          exc_value)
                if error:
                    if message:
                        QMessageBox.information(self.iface.mainWindow(), "Message", message)
                    return
                if scenarios or events:
                    self.dialog = coastalmeqgis_scenarioSelection_dialog(self.iface, inFileName, scenarios, events)
                    if not old_method:
                        self.dialog.setOptionsVisible(True)
                    self.dialog.exec()
                    if not self.dialog.status:
                        return
                    scenarios = self.dialog.scenarios[:]
                    events = self.dialog.events[:]
                else:
                    scenarios, events = [], []
                    if not options_called:
                        result = LoadTCFOptionsMessageBox(self.iface.mainWindow(), 'Load Layers from Control File')
                        options_called = True
                        if result != 'ok':
                            return

                if old_method:
                    openGisFromTcf(inFileName, self.iface, scenarios, load_rasters)
                else:
                    self.prog_dialog = QWidget(self.iface.mainWindow(), QT_DIALOG_TYPE)
                    self.prog_dialog.setWindowTitle('Loading Control File Layers')
                    self.prog_label = QLabel()
                    self.prog_bar = QProgressBar()
                    self.prog_bar.setRange(0, 0)
                    layout = QVBoxLayout()
                    layout.addWidget(self.prog_label)
                    layout.addWidget(self.prog_bar)
                    self.prog_dialog.setLayout(layout)
                    self.prog_dialog.setFixedSize(QSize(500, 75))
                    self.prog_dialog.show()
                    self.model_file_layers = ModelFileLayers()
                    self.load_gis = LoadGisFromControlFile(self.model_file_layers, inFileName, None, scenarios, events)
                    self.thread = QThread()
                    self.load_gis.moveToThread(self.thread)
                    self.thread.started.connect(self.load_gis.loadGisFromControlFile_v2)
                    self.model_file_layers.layer_added.connect(self.layer_added)
                    self.load_gis.finished.connect(self.load_gis_files)
                    self.load_gis.error.connect(self.on_error)
                    self.thread.start()
                # loadGisFromControlFile_v2(model_file_layers, inFileName, None, scenarios)
                # err, errmsg = loadGisFiles(model_file_layers)
                # if err:
                # 	QMessageBox.warning(self.iface.mainWindow(), 'Failed Load', errmsg)
                # else:
                # 	QMessageBox.information(self.iface.mainWindow(), 'Completed Load', 'Successfully loaded all layers')

    def on_error(self, err_msg):
        self.thread.terminate()
        self.thread.wait()
        self.prog_dialog.close()
        QMessageBox.warning(self.iface.mainWindow(), 'Load from TCF',
                            'Unexpected error loading GIS from TCF: {0}'.format(err_msg))

    def load_gis_files(self):
        self.thread.terminate()
        self.thread.wait()
        # self.thread = QThread()
        self.prog_bar.setRange(0, self.model_file_layers.count())
        self.prog_bar.setValue(0)
        self.prog_label.setText('Loading Layers')
        QgsApplication.processEvents()
        self.load_files = LoadGisFiles(self.model_file_layers, self.prog_dialog)
        # self.load_files.moveToThread(self.thread)
        # self.thread.started.connect(self.load_files.loadGisFiles)
        self.load_files.loadGisFiles()
        # self.load_files.start_layer_load.connect(self.layer_loading)
        # self.load_files.finished.connect(self.finished_load_gis_files)
        self.finished_load_gis_files()

    def finished_load_gis_files(self):
        # self.thread.terminate()
        # self.thread.wait()
        self.prog_dialog.close()
        msg = ''
        if self.load_gis.settings.no_files_copied:
            msg = 'No files were loaded for the following commands:\n{0}'.format(
                '"\n- '.join([': '.join(x) for x in self.load_gis.settings.no_files_copied]))
        if self.load_files.err:
            msg = '{0}\n\nError importing file into QGIS:\n{1}'.format(msg, self.load_files.msg)
        if msg:
            QMessageBox.critical(self.iface.mainWindow(), 'Load from TCF', msg)

    def layer_added(self, e):
        self.prog_label.setText('Found Layer: {0}'.format(e))

    def reload_data(self):
        for layer in toc_selected_layers(self.iface):
            reload_data(layer)

    def filterAndSortLayers(self):
        self.filterSortLayerDialog = FilterSortLayersDialog(self.iface)
        self.filterSortLayerDialog.exec()

    def coastalmeUtilities(self):
        self.coastalmeUtilitiesDialog = TuflowUtilitiesDialog(self.iface)
        self.coastalmeUtilitiesDialog.exec()

    def archBrideEditor(self):
        if self.archBridgeDockOpen:
            self.archBridgeDock.show()
        else:
            self.archBridgeDock = ArchBridgeDock(self.iface)
            self.iface.addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.archBridgeDock)
            self.archBridgeDockOpen = True

    def clearSpanBridgeEditor(self):
        pass

    def integrityToolWindow(self):
        if self.integrityToolOpened:
            self.integrityTool.show()
        else:
            self.integrityTool = IntegrityToolDock(self.iface)
            self.iface.addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.integrityTool)
            self.integrityToolOpened = True

    def extractRefh2(self):
        if sys.platform != 'win32':
            QMessageBox.critical(self.iface.mainWindow(), "ReFH2", "ReFH2 tool is only available in Windows")
            return

        if Refh2Dock is None:
            QMessageBox.critical(self.iface.mainWindow(), "ReFH2",
                                 "A problem occurred loading ReFH2 tool. Please contact support@coastalme.com")
            return

        if self.refh2DockOpen:
            self.refh2Dock.show()
        else:
            # test if checksum.pyd can be imported
            # try:
            # 	from coastalme.ReFH2.checksum import checkSum
            # except ImportError:
            # 	QMessageBox.critical(self.iface.mainWindow(), "ReFH2",
            # 	                     "Could not import checksum from checksum.pyd. This can be caused by an "
            # 	                     "organisation's 'Group Policy' as part of IT security. "
            # 	                     "Please contact your system administrator.")
            # 	return

            self.refh2Dock = Refh2Dock(self.iface)
            self.iface.addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.refh2Dock)
            self.refh2DockOpen = True

    def extractSCS(self):
        if self.scsDockOpen:
            self.scsDock.show()
        else:
            self.scsDock = SCSDock(self.iface)
            self.iface.addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.scsDock)
            self.scsDockOpen = True

    # swangis
    def runBuilderUI(self):
        if swangisSupported:
            if self.builderUI is None:
                self.builderUI = BuilderUI()
                self.iface.mainWindow().addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.builderUI.dockWidget)
            else:
                self.builderUI.dockWidget.setVisible(True)
        else:
            QMessageBox.information(self.iface.mainWindow(), 'COASTALME Plugin',
                                    'Unable to load SWAN GIS Tools. Please ensure you have '
                                    'the netCDF4 Python library installed.')

    # swangis
    def runProcessingUI(self):
        if swangisSupported:
            if self.processingUI is None:
                self.processingUI = PostProcessingUI()
                self.iface.mainWindow().addDockWidget(QT_DOCK_WIDGET_AREA_RIGHT, self.processingUI.dockWidget)
            else:
                self.processingUI.dockWidget.setVisible(True)
        else:
            QMessageBox.information(self.iface.mainWindow(), 'COASTALME Plugin',
                                    'Unable to load SWAN GIS Tools. Please ensure you have '
                                    'the netCDF4 Python library installed.')

    # swangis
    def clearBuilderUI(self):
        # remove the builder UI if active and save project
        if self.builderUI is not None:
            self.iface.removeDockWidget(self.builderUI.dockWidget)
            self.builderUI.dockWidget.setParent(None)
            self.builderUI.gridLayerUI.setLayer(None)
            self.builderUI = None

    # swangis
    def clearProcessingUI(self):
        # remove the processing UI if active
        if self.processingUI is not None:
            self.processingUI.dockWidget.close()
            self.iface.removeDockWidget(self.processingUI.dockWidget)
            self.processingUI = None

    def addLambdaConnection(self, conn):
        self.lambdaConnections.append(conn)

    def qgisDisconnect(self):
        for conn in self.lambdaConnections:
            try:
                QgsProject.instance().readProject.disconnect(conn)
            except:
                pass
        try:
            self.about_action.triggered.disconnect(self.about_coastalmeqgis)
        except:
            pass
        try:
            self.check_dependancy_action.triggered.disconnect(self.check_dependencies)
        except:
            pass
        try:
            self.configure_tf_action.triggered.disconnect(self.configure_tf)
        except:
            pass
        try:
            self.import_empty_tf_action.triggered.disconnect(self.import_empty_tf)
        except:
            pass
        try:
            self.insert_COASTALME_attributes_action.triggered.disconnect(self.insert_COASTALME_attributes)
        except:
            pass
        try:
            self.increment_action.triggered.disconnect(self.increment_layer)
        except:
            pass
        try:
            self.run_coastalme_action.triggered.disconnect(self.run_coastalme)
        except:
            pass
        try:
            self.launch_runner_action.triggered.disconnect(self.launch_runner)
        except:
            pass
        try:
            self.clearGlobalSettingsAction.triggered.disconnect()
        except:
            pass
        try:
            self.clearProjectSettingsAction.triggered.disconnect()
        except:
            pass
        try:
            self.removeTuviewAction.triggered.disconnect(self.removeTuview)
        except:
            pass
        try:
            self.reloadTuviewAction.triggered.disconnect(self.reloadTuview)
        except:
            pass
        try:
            self.reload_data_action.triggered.disconnect(self.reload_data)
        except:
            pass
        try:
            self.view_results_action.triggered.disconnect(self.openResultsPlottingWindow)
        except:
            pass
        try:
            self.integrity_tool_action.triggered.disconnect(self.integrityToolWindow)
        except:
            pass
        try:
            self.import_empty_tf_action.triggered.disconnect(self.import_empty_tf)
        except:
            pass
        try:
            self.load_coastalmeFiles_from_TCF_action.triggered.disconnect(self.loadTuflowLayersFromTCF)
        except:
            pass
        try:
            self.filterAndSortLayersAction.triggered.disconnect(self.filterAndSortLayers)
        except:
            pass
        try:
            self.increment_action.triggered.disconnect(self.increment_layer)
        except:
            pass
        try:
            self.import_chk_action.triggered.disconnect(self.import_check)
        except:
            pass
        try:
            self.apply_chk_action.triggered.disconnect(self.apply_check)
        except:
            pass
        try:
            self.apply_chk_cLayer_action.triggered.disconnect(self.apply_check_cLayer)
        except:
            pass
        try:
            self.autoLabelMenu.menuAction().triggered.disconnect(self.apply_label_cLayer)
        except:
            pass
        try:
            self.autoLabelSettingLocAction.triggered.disconnect(self.openLabelSettingLoc)
        except:
            pass
        try:
            self.extract_arr2016_action.triggered.disconnect(self.extract_arr2016)
        except:
            pass
        try:
            self.extractRefh2Action.triggered.disconnect(self.extractRefh2)
        except:
            pass
        try:
            self.coastalmeUtilitiesAction.triggered.disconnect(self.coastalmeUtilities)
        except:
            pass
        if spatial_database_option:
            try:
                self.apply_gpkg_layernames_action.triggered.disconnect(self.apply_gpkg_layername)
            except:
                pass
        try:
            QgsProject.instance().cleared.disconnect(self.clearBuilderUI)
        except:
            pass

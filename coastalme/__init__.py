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
 This script initializes the plugin, making it known to QGIS.
"""
import re

from qgis.core import *
import sys


def name():
    return "COASTALME"


def description():
    return "A collection of the QGIS plugins for COASTALME modelling."


def version():
    return "Version 2018-02-AB"


def icon():
    return "coastalme.png"


def qgisMinimumVersion():
    return "3.4"


def author():
    return "Phillip Ryan, Ellis Symons"


def email():
    return "support@coastalme.com"


def openTuview(event, coastalmeqgis):
    if Qgis.QGIS_VERSION_INT >= 30400:
        tuviewOpen = QgsProject().instance().readEntry("TUVIEW", "dock_opened")[0]
        if tuviewOpen == 'Open':
            coastalmeqgis.openResultsPlottingWindow(showmessage=False)
            for lyrid, lyr in QgsProject.instance().mapLayers().items():
                if re.findall('_PLOT_[PLR]$', lyr.name(), re.IGNORECASE):
                    coastalmeqgis.resultsPlottingDock.currentLayer = lyr
            coastalmeqgis.resultsPlottingDock.loadProject()
            coastalmeqgis.resultsPlottingDock.canvas.mapCanvasRefreshed.connect(
                coastalmeqgis.resultsPlottingDock.tuResults.tuResults2D.renderMap)
            coastalmeqgis.resultsPlottingDock.canvas.mapCanvasRefreshed.connect(
                coastalmeqgis.resultsPlottingDock.tuPlot.updateCurrentPlot)
        elif tuviewOpen == 'Close':
            coastalmeqgis.openResultsPlottingWindow(showmessage=False)
            coastalmeqgis.resultsPlottingDock.setVisible(False)
            coastalmeqgis.resultsPlottingDock.loadProject()
            coastalmeqgis.resultsPlottingDock.canvas.mapCanvasRefreshed.connect(
                coastalmeqgis.resultsPlottingDock.tuResults.tuResults2D.renderMap)
            coastalmeqgis.resultsPlottingDock.canvas.mapCanvasRefreshed.connect(
                coastalmeqgis.resultsPlottingDock.tuPlot.updateCurrentPlot)


def classFactory(iface):
    # from .editor_functions import editor_swmm_links_conduits

    # load coastalmeqgis_menu class from file coastalmeqgis_menu
    from .coastalmeqgis_menu import coastalmeqgis_menu

    menu = coastalmeqgis_menu(iface)

    # check if tuview should be opened
    openTuview(None, menu)

    # setup signal to capture project opens so tuview can be opened if needed
    conn = QgsProject.instance().readProject.connect(lambda event: openTuview(event, menu))

    menu.addLambdaConnection(conn)

    return menu

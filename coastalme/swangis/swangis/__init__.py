try: # Running in QGIS
    if __name__ != 'coastalme.swangis.swangis':  # not being called from coastalme plugin
        from swangis.ui import PluginMenuUI

    def name():
        return "SWAN GIS Tools"


    def description():
        return "Tools for building SWAN models"


    def version():
        return "0.0.5"


    def icon():
        return ""


    def qgisMinimumVersion():
        return "3.6"


    def author():
        return "COASTALME Support"


    def email():
        return ""


    def classFactory(iface):
        """Entry point for QGIS"""
        if __name__ != 'coastalme.swangis.swangis':  # not being called from coastalme plugin
            return PluginMenuUI(iface)

except ModuleNotFoundError:
    # Running outside QGIS
    from swan import *
    from plotting import *
    # from downloads import *

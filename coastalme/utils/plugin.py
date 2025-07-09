from qgis.utils import plugins


def coastalme_plugin():
    """Returns the COASTALME Plugin instance."""
    return plugins.get('coastalme')

from qgis._core import QgsMapLayer

from coastalme.toc.toc import coastalmeqgis_find_layer, findAllVectorLyrsWithGroups
from coastalme.utils import file_from_data_source, layer_name_from_data_source
from coastalme.coastalme_swmm.swmm_io import is_coastalme_swmm_file

def find_swmm_gpkgs():
    gpkgs = set()

    mapLayerNamesIds = findAllVectorLyrsWithGroups()

    for layer_name, layer_id in mapLayerNamesIds:
        layer = coastalmeqgis_find_layer(layer_id, search_type='layerid')
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            if layer.storageType() == 'GPKG':
                db = file_from_data_source(layer.dataProvider().dataSourceUri())
                try:
                    if is_coastalme_swmm_file(db):
                        gpkgs.add(db)
                except:
                    pass

    return list(gpkgs)

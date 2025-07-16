from qgis.PyQt.QtCore import Qt
from qgis._core import QgsProject
from qgis.core import Qgis

from ..nc_grid_data_provider import NetCDFGrid, LoadError
from ..coastalmeqgis_dialog import coastalmeqgis_scenarioSelection_dialog
from .tmp_result import TmpResult
from ..gui import Logging

try:
    from pathlib import Path
except ImportError:
    from pathlib_ import Path_ as Path



from ..compatibility_routines import QT_MATCH_RECURSIVE


class CmeResultsNcGrid:

    def __init__(self, cmeView=None):
        self.cmeView = cmeView
        self.iface = cmeView.iface
        self.results = {}
        self.copied_results = {}

    def importResults(self, inFileNames, **kwargs):
        qv = Qgis.QGIS_VERSION_INT
        if qv < 31600:
            print('Not supported for earlier QGIS versions before version 3.16')
            return

        # disconnect incoming signals for load step
        skipConnect = False
        try:
            self.cmeView.project.layersAdded.disconnect(self.cmeView.layersAdded)
        except:
            skipConnect = True

        copy_res = self.cmeView.cmeOptions.copy_mesh
        errors = []
        for j, f in enumerate(inFileNames):
            # copy result scmeff
            if j == 0 and self.cmeView.cmeOptions.show_copy_mesh_dlg and NetCDFGrid.capable():
                copy_res = TmpResult.ask_copy_res_dlg(self.cmeView, self.cmeView.cmeOptions)
            if copy_res:
                tmp_res = TmpResult(f)
                if tmp_res.valid:
                    try:
                        f = tmp_res.copy(self.cmeView)
                    except RuntimeError as e:
                        Logging.error('Error copying result file to temporary directory', 'Python error: {0}'.format(e))
                        return
                else:
                    Logging.error('Could not create temporary directory for result file',
                                  'Temporary directory: {0}'.format(tmp_res.tmp_dir))
                    return

            if 'layers' in kwargs:
                selected_layers = kwargs['layers']
            else:
                layers = [x for x in NetCDFGrid.nc_grid_layers(f)]
                if not layers:
                    if not NetCDFGrid.capable():
                        raise LoadError(
                            'NetCDF4 Python library not installed. Please see the following wiki page for more information:<p>'
                            '<a href="https://wiki.coastalme.com/index.php?title=COASTALME_Viewer_-_Load_Results_-_NetCDF_Grid"'
                            '<span style=" text-decoration: underline; color:#0000ff;">wiki.coastalme.com/index.php?title=COASTALME_Viewer_-_Load_Results_-_NetCDF_Grid'
                            '</span></a>')
                    if not NetCDFGrid.is_nc_grid(f):
                        raise LoadError('Format is not recognised as a NetCDF raster.')
                dlg = coastalmeqgis_scenarioSelection_dialog(self.iface, f, layers)
                dlg.setWindowTitle('Layer Selection')
                dlg.exec()
                if not dlg.stacmes:
                    return
                selected_layers = dlg.scenarios

            for layer in selected_layers:
                # Load
                mLayer, name = self._load_file(f, layer, **kwargs)
                if mLayer is None:
                    errors.append(name)
                    continue

                if copy_res:
                    self.copied_results[mLayer] = tmp_res

                self.cmeView.cmeResults.updateDateTimes()

                if mLayer is None or name is None:
                    if not skipConnect:
                        self.cmeView.project.layersAdded.connect(self.cmeView.layersAdded)
                    return False

                # Open layer in map
                if kwargs.get('add_map_layer') is None or kwargs.get('add_map_layer'):
                    self.cmeView.project.addMapLayer(mLayer)
                mLayer.nameChanged.connect(lambda: self.cmeView.cmeResults.cmeResults2D.layerNameChanged(mLayer, name,
                                                                         mLayer.name()))  # if name is changed can capcmere this in indexing

                # add to result list widget
                names = []
                for i in range(self.cmeView.OpenResults.count()):
                    if self.cmeView.OpenResults.item(i).text() not in names:
                        names.append(self.cmeView.OpenResults.item(i).text())
                if name not in names:
                    self.cmeView.OpenResults.addItem(name)  # add to widget
                k = self.cmeView.OpenResults.findItems(name, QT_MATCH_RECURSIVE)[0]
                k.setSelected(True)
                self.cmeView.resultChangeSignalCount = 0  # reset signal count back to 0

        # connect load signals
        if not skipConnect:
            self.cmeView.project.layersAdded.connect(self.cmeView.layersAdded)

        if errors:
            raise Exception('\n'.join(errors))
        return True

    def _load_file(self, filename, layer_name, **kwargs):

        display_name = '{0} - {1}'.format(Path(filename).stem, layer_name)
        uri = 'NetCDF:{0}:{1}'.format(filename, layer_name)
        try:
            nc_grid = NetCDFGrid(uri, display_name, default_reference_time=self.cmeView.cmeOptions.zeroTime, **kwargs)
        except LoadError as e:
            return None, str(e)

        self.getResultMetaData(display_name, nc_grid)

        # load first step
        self.updateActiveTime()

        return nc_grid, display_name

    def getResultMetaData(self, display_name, nc_grid):
        if display_name not in self.cmeView.cmeResults.results:
            self.cmeView.cmeResults.results[display_name] = {}

        # populate resdata
        timekey2time = self.cmeView.cmeResults.timekey2time  # dict
        zeroTime = nc_grid.reference_time
        if self.cmeView.OpenResults.count() == 0:
            self.cmeView.cmeOptions.zeroTime = zeroTime
            if self.iface is not None:
                self.cmeView.cmeOptions.timeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
                self.cmeView.cmeResults.loadedTimeSpec = self.iface.mapCanvas().temporalRange().begin().timeSpec()
            else:
                self.cmeView.cmeOptions.timeSpec = 1
                self.cmeView.cmeResults.loadedTimeSpec = 1

        timesteps = nc_grid.times  # relative time
        for t in timesteps:
            timekey2time['{0:.6f}'.format(t)] = t

        self.cmeView.cmeResults.results[display_name]["_nc_grid"] = \
        {
            'times': {'{0:.6f}'.format(x): [x] for x in timesteps},
            'referenceTime': nc_grid.reference_time
        }

        # add to internal storage
        self.results[display_name] = [nc_grid, timesteps]

    def layerReloaded(self, layer):
        if layer is None and hasattr(self.cmeView, 'timer') and self.cmeView.timer is not None:  # start timer to reload results
            self.cmeView.timer.start(300)
            return

        results = self.cmeView.cmeResults.results
        display_name = layer.name()
        if display_name in results:
            if '_nc_grid' in results[display_name]:
                del results[display_name]['_nc_grid']

        self.getResultMetaData(display_name, layer)
        self.cmeView.cmeResults.updateResultTypes()
        self.cmeView.resultsChanged()

    def layerNameChanged(self, old_name, new_name):
        if old_name in self.results:
            self.results[new_name] = self.results[old_name]
            del self.results[old_name]

    def updateActiveTime(self, date=None):
        if date is None:
            active_date = self.cmeView.cmeResults.activeTime
        else:
            active_date = date

        nc_grid = None
        selectedResults = [x.text() for x in self.cmeView.OpenResults.selectedItems()]
        for res_name, data in self.results.items():
            nc_grid = data[0]
            if nc_grid.static:
                continue

            if res_name not in selectedResults or active_date is None:
                time_index = None
            else:
                # find closest
                for time_index, date in enumerate(nc_grid.timesteps('absolute')):
                    if date == active_date:
                        break
                    if date > active_date:
                        if time_index == 0:
                            break
                        else:
                            diff = abs((date - active_date).total_seconds())
                            if diff > 0.01:
                                time_index -= 1
                            break

            # update nc grid band
            if nc_grid is not None:
                legint = QgsProject.instance().layerTreeRoot()
                node = legint.findLayer(nc_grid.id())
                band = time_index + 1 if time_index is not None else None
                if band is None and node is not None:
                    node.setItemVisibilityChecked(False)
                else:
                    if node is not None:
                        node.setItemVisibilityChecked(True)
                    nc_grid.update_band(band)
                nc_grid.triggerRepaint()

    def removeResults(self, resList, **kwargs):
        """
        Removes the Particles results from the indexed results and ui.

        :param resList: list -> str result name e.g. M01_5m_001
        :return: bool -> True for successful, False for unsuccessful
        """

        remove_layer = kwargs['remove_layer'] if 'remove_layer' in kwargs else True

        results = self.cmeView.cmeResults.results

        try:
            self.cmeView.project.layersWillBeRemoved.disconnect(self.cmeView.layersRemoved)
        except:
            pass

        for res in resList:
            if res in self.results:
                if res in results:
                    del results[res]
                layer = self.results[res][0]
                if remove_layer:
                    try:
                        self.cmeView.project.removeMapLayer(layer.id())
                        del layer
                    except:
                        pass

                del self.results[res]

            for i in range(self.cmeView.OpenResults.count()):
                item = self.cmeView.OpenResults.item(i)
                if item is not None and item.text() == res:
                    if res not in results:
                        self.cmeView.OpenResults.takeItem(i)

        if self.cmeView.canvas is not None:
            self.cmeView.canvas.refresh()
        self.cmeView.cmeResults.updateResultTypes()
        self.cmeView.project.layersWillBeRemoved.connect(self.cmeView.layersRemoved)

        return True

    def active_grids(self):
        selectedResults = [x.text() for x in self.cmeView.OpenResults.selectedItems()]
        for res_name, data in self.results.items():
            if res_name in selectedResults:
                yield data[0]

    def grids(self):
        for res_name, data in self.results.items():
            yield data[0]

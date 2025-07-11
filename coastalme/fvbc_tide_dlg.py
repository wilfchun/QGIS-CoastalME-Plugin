from qgis.PyQt.QtWidgets import QDialog

from coastalme.forms.fv_bc_tide_nc import Ui_ImportFVBCTideDlg
from coastalme.coastalmeqgis_library import browse
from coastalme.compatibility_routines import Path

try:
    from netCDF4 import Dataset
except ImportError:
    from coastalme.netCDF4_ import Dataset_ as Dataset


class ImportFVBCTideDlg(QDialog, Ui_ImportFVBCTideDlg):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btnNS.clicked.connect(lambda: browse(self, 'existing file', 'COASTALME_Viewer/FVBC_Tide', 'Node String Layer',
                                                  'Shapefile (*.shp *.SHP)', self.leNS))
        self.btnNC.clicked.connect(lambda: browse(self, 'existing file', 'COASTALME_Viewer/FVBC_Tide', 'NetCDF File',
                                                  'NetCDF (*.nc *.NC)', self.leNC))

    @property
    def node_string_fpath(self):
        return self.leNS.text()

    @property
    def nc_fpath(self):
        return self.leNC.text()

    @property
    def use_local_time(self):
        return self.cbUseLocalTime.isChecked()

    def accept(self):
        if not self.node_string_fpath:
            self.leNS.setFocus()
            return
        if not self.nc_fpath:
            self.leNC.setFocus()
            return
        super().accept()

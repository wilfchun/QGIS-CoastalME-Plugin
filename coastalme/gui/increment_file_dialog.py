import os.path
from pathlib import Path
from typing import Generator, Union

from qgis.core import QgsVectorLayer, QgsProject, QgsMapLayer, QgsVectorFileWriter
from qgis.PyQt.QtWidgets import (QDialog, QWidget, QFileDialog, QLineEdit, QTableWidgetItem, QTableWidget, QMenu,
                             QApplication)
from qgis.PyQt.QtGui import QResizeEvent
from qgis.PyQt.QtCore import QSettings, QDir, Qt, QPoint

from ..compatibility_routines import QT_ITEM_FLAG_ITEM_IS_ENABLED, QT_ITEM_FLAG_ITEM_IS_SELECTABLE, is_qt6, QT_CHECKED, QT_CUSTOM_CONTEXT_MENU, QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE, QT_UNCHECKED
from ..ui import Ui_IncrementFileDialog, Ui_IncrementDbLyrDialog, Ui_IncrementLayerDialog
from ..utils import coastalme_plugin

if is_qt6:
    from qgis.PyQt.QtGui import QAction
else:
    from qgis.PyQt.QtWidgets import QAction


class IncrementLayerDialogBase(QDialog):

    def __init__(self, parent: QWidget, layer: QgsVectorLayer):
        super().__init__(parent)
        self.layer = layer
        self.add_to_canvas = True

    def setup_ui(self):
        self.dlg_size_from_save()
        self.splitter_pos_from_save()
        self.splitter.splitterMoved.connect(self.splitter_moved)
        self.setWindowTitle(f'Increment Layer: {self.layer.name()}')
        self.setWindowIcon(coastalme_plugin().icon('increment_layer'))
        self.html_help.setHtml(self.short_help_string())
        self.output_folder_err_txt.hide()
        self.output_name_err_txt.hide()
        self.error = False
        self.warning = False
        for line_edit in self.findChildren(QLineEdit):
            line_edit.textChanged.connect(self.validate)
        for table in self.findChildren(QTableWidget):
            table.itemChanged.connect(self.validate)
        QgsProject.instance().layersRemoved.connect(self.validate)
        self.check_for_warnings()

    def iter(self) -> Generator['IncrementLayerDialogBase', None, None]:
        yield self

    def accept(self) -> None:
        self.validate(about_to_run=True)
        if self.error:
            return
        super().accept()

    def dlg_size_from_save(self) -> None:
        if QSettings().contains('coastalme_plugin/increment_dlg_size'):
            w, h = QSettings().value('coastalme_plugin/increment_dlg_size').split(',')
            w, h = int(w), int(h)
            self.resize(int(w), int(h))

    def splitter_pos_from_save(self) -> None:
        if QSettings().contains('coastalme_plugin/increment_dlg_splitter_sizes'):
            sizes = QSettings().value('coastalme_plugin/increment_dlg_splitter_sizes').split(',')
            sizes = [int(x) for x in sizes]
            self.splitter.setSizes(sizes)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        super().resizeEvent(a0)
        QSettings().setValue('coastalme_plugin/increment_dlg_size', '{0},{1}'.format(self.width(), self.height()))

    def splitter_moved(self, pos: int, index: int) -> None:
        sizes = ','.join([str(x) for x in self.splitter.sizes()])
        QSettings().setValue('coastalme_plugin/increment_dlg_splitter_sizes', sizes)

    def error_text_creator(self, text: str) -> str:
        return f'<font color="red">{text}</font>'

    def warning_text_creator(self, text: str) -> str:
        return f'<font color="darkorange">{text}</font>'

    def validate(self, new_text: str = '', about_to_run: bool = False) -> None:
        self.warning = False
        self.output_name_err_txt.hide()
        self.check_for_warnings()
        if about_to_run or self.error:  # only show red text when trying to run the tool (clear up red text immediately)
            self.error = False
            self.validate_output_folder()
            self.validate_output_name()

    def driver_name(self) -> str:
        from ..utils import get_driver_name_from_extension
        return get_driver_name_from_extension('vector', self.out_file().suffix)

    def clone_layer(self) -> QgsVectorLayer:
        return self.layer

    def save_rem_layer_selection(self, checked: bool) -> None:
        QSettings().setValue('coastalme_plugin/increment_dlg_rem_layer', checked)

    @property
    def remove_old_layer(self) -> bool:
        if hasattr(self, 'remove_old_layer_rb'):
            return self.remove_old_layer_rb.isChecked()
        return True

    @remove_old_layer.setter
    def remove_old_layer(self, value: bool) -> None:
        if not hasattr(self, 'remove_old_layer_rb'):
            return
        if value:
            self.remove_old_layer_rb.setChecked(True)
        else:
            self.keep_old_layer_rb.setChecked(True)

    @property
    def output_folder(self) -> str:
        return ''

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        pass

    @property
    def output_name(self) -> str:
        return ''

    @output_name.setter
    def output_name(self, value: str) -> None:
        pass

    @property
    def action_on_existing(self) -> int:
        return 0

    def out_file(self) -> Path:
        return Path()

    def out_data_source(self) -> str:
        return ''

    def open_layer_data_sources(self) -> Union[str, Path]:
        pass

    def short_help_string(self) -> str:
        return ''

    def validate_output_folder(self):
        pass

    def validate_output_name(self):
        pass

    def check_for_warnings(self):
        pass


class IncrementFileDialog(IncrementLayerDialogBase, Ui_IncrementFileDialog):

    def __init__(self, parent: QWidget, layer: QgsVectorLayer):
        from ..utils import increment_name, clean_data_source
        super().__init__(parent, layer)
        self.setupUi(self)
        self.data_source = Path(clean_data_source(layer.dataProvider().dataSourceUri()))
        self.output_folder_line_edit.setText(str(self.data_source.parent))
        self.output_name_line_edit.setText(increment_name(self.data_source.stem))

        # browse
        self.output_folder_browse_btn.clicked.connect(self.browse_output_folder)

        # remove old layer
        b = QSettings().value('coastalme_plugin/increment_dlg_rem_layer', True)
        if isinstance(b, str):
            b = True if b.lower() == 'true' else False
        self.remove_old_layer_rb.setChecked(b)
        self.keep_old_layer_rb.setChecked(not b)
        self.remove_old_layer_rb.toggled.connect(self.save_rem_layer_selection)

        self.setup_ui()

    @property
    def output_folder(self) -> str:
        return self.output_folder_line_edit.text()

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        self.output_folder_line_edit.setText(value)

    @property
    def output_name(self) -> str:
        return self.output_name_line_edit.text()

    @output_name.setter
    def output_name(self, value: str) -> None:
        self.output_name_line_edit.setText(value)

    @property
    def action_on_existing(self) -> int:
        return QgsVectorFileWriter.CreateOrOverwriteFile

    def out_file(self) -> Path:
        output_folder = Path(self.output_folder)
        output_file = output_folder / f'{self.output_name}{self.data_source.suffix}'
        return output_file

    def out_data_source(self) -> str:
        return str(self.out_file())

    def browse_output_folder(self) -> None:
        start_dir = self.output_folder
        if not start_dir:
            start_dir = QDir.homePath()
        folder = QFileDialog.getExistingDirectory(self, 'Output Folder', start_dir)
        if folder:
            self.output_folder = folder

    def short_help_string(self) -> str:
        folder = Path(os.path.realpath(__file__)).parent.parent / 'alg'
        help_filename = folder / 'help' / 'html' / 'increment_file.html'
        return help_filename.open().read()

    def open_layer_data_sources(self) -> list[Path]:
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                yield Path(layer.dataProvider().dataSourceUri().split('|')[0])

    def validate_output_folder(self):
        if not self.output_folder:
            self.output_folder_err_txt.setText(self.error_text_creator('Output folder cannot be empty'))
            self.output_folder_err_txt.show()
            self.error = True
            return

        self.output_folder_err_txt.hide()

    def validate_output_name(self):
        if not self.output_name:
            self.output_name_err_txt.setText(self.error_text_creator('Output name cannot be empty'))
            self.output_name_err_txt.show()
            self.error = True
            return
        if self.data_source == self.out_file():
            self.output_name_err_txt.setText(self.error_text_creator('Output file cannot be the same as the input file'))
            self.output_name_err_txt.show()
            self.error = True
            return
        if self.out_file() in [x for x in self.open_layer_data_sources()]:
            self.output_name_err_txt.setText(self.error_text_creator('Output file is open in QGIS. '
                                                                     'Please close before overwriting.'))
            self.output_name_err_txt.show()
            self.error = True
            return

        if not self.warning:
            self.output_name_err_txt.hide()

    def check_for_warnings(self):
        if self.out_file().exists():
            self.output_name_err_txt.setText(self.warning_text_creator('Warning: Output file already exists'))
            self.output_name_err_txt.show()
            self.warning = True
            return


class IncrementDbLyrDialog(IncrementLayerDialogBase, Ui_IncrementDbLyrDialog):

    def __init__(self, parent: QWidget, layer: QgsVectorLayer):
        from ..utils import GPKG, increment_name, clean_data_source, file_from_data_source, layer_name_from_data_source
        super().__init__(parent, layer)
        self.setupUi(self)
        self.data_source = clean_data_source(layer.dataProvider().dataSourceUri())
        self._layer_name = layer_name_from_data_source(self.data_source)
        self._active_file = file_from_data_source(self.data_source)
        self.gpkg = GPKG(self._active_file)
        self.gpkg_layers = self.gpkg.layers()
        self.output_database = str(self._active_file.parent / increment_name(self._active_file.name))
        self.output_layer_table.setHorizontalHeaderLabels(['Original Layer', 'Incremented Layer'])
        width = self.output_layer_table.sizeHint().width()
        self.output_layer_table.setColumnWidth(0, int(width * 0.5))
        self.output_layer_table.setColumnWidth(1, int(width * 0.5))
        self.output_layer_table.setRowCount(len(self.gpkg_layers))
        for i, layer in enumerate(self.gpkg_layers):
            item = QTableWidgetItem(layer)
            item.setCheckState(QT_CHECKED)
            item.setFlags(QT_ITEM_FLAG_ITEM_IS_SELECTABLE | QT_ITEM_FLAG_ITEM_IS_ENABLED | QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE)
            self.output_layer_table.setItem(i, 0, item)
            if layer == self._layer_name:
                self.output_layer_table.setItem(i, 1, QTableWidgetItem(increment_name(layer)))
        self.output_layer_table.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)
        self.output_layer_table.customContextMenuRequested.connect(self.output_layer_table_context_menu)
        self._add_as_new_layer = False

        # browse
        self.output_database_browse_btn.clicked.connect(self.browse_output_database)

        # remove old layer
        b = QSettings().value('coastalme_plugin/increment_dlg_rem_layer', True)
        if isinstance(b, str):
            b = True if b.lower() == 'true' else False
        self.remove_old_layer_rb.setChecked(b)
        self.keep_old_layer_rb.setChecked(not b)
        self.remove_old_layer_rb.toggled.connect(self.save_rem_layer_selection)

        self.setup_ui()
        self.setWindowTitle(f'Increment Layer and Database: {self._layer_name}')

    @property
    def remove_old_layer(self) -> bool:
        if hasattr(self, 'remove_old_layer_rb'):
            return self.remove_old_layer_rb.isChecked() or not self._add_as_new_layer
        return True

    @property
    def layer(self) -> QgsVectorLayer:
        return self._layer

    @layer.setter
    def layer(self, layer: QgsVectorLayer) -> None:
        self._layer = layer

    @property
    def output_folder(self) -> str:
        return str(Path(self.output_database_line_edit.text()).parent)

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        raise AttributeError('Cannot set output_folder')

    @property
    def output_name(self) -> str:
        return self._layer_name

    @output_name.setter
    def output_name(self, name) -> None:
        raise AttributeError('Cannot set output_name')

    @property
    def output_database(self) -> str:
        return self.output_database_line_edit.text()

    @output_database.setter
    def output_database(self, value: str) -> None:
        self.output_database_line_edit.setText(value)

    @property
    def action_on_existing(self) -> int:
        if Path(self._active_file).exists():
            return QgsVectorFileWriter.CreateOrOverwriteLayer
        return QgsVectorFileWriter.CreateOrOverwriteFile

    def output_layer_table_context_menu(self, pos: QPoint) -> None:
        item = self.output_layer_table.itemAt(pos)
        if not item or item.row() == -1 or item.column() != 0:
            return
        menu = QMenu(self.output_layer_table)
        action_copy_text = QAction('Copy Text', menu)
        action_copy_text.triggered.connect(lambda: self.copy_text(item.text()))
        menu.addAction(action_copy_text)
        action_increment_layer = QAction('Increment Layer', menu)
        action_increment_layer.triggered.connect(lambda: self.increment_layer_name_at_row(item.row()))
        menu.addAction(action_increment_layer)
        menu.popup(self.output_layer_table.viewport().mapToGlobal(pos))

    def iter(self) -> Generator['IncrementDbLyrDialog', None, None]:
        from ..utils import file_from_data_source, layer_name_from_data_source
        open_layers = list(QgsProject.instance().mapLayers().values())
        open_data_sources = list(self.open_layer_data_sources())
        for i in range(self.output_layer_table.rowCount()):
            out_data_source = self._output_data_source(i)
            input_data_source = self._input_data_source(i)
            if not out_data_source:
                continue
            self._add_as_new_layer = bool(self.output_layer_table.item(i, 1))
            self._active_file = file_from_data_source(out_data_source)
            self._layer_name = layer_name_from_data_source(out_data_source)
            if input_data_source.replace('\\', '/') in open_data_sources:
                self._layer = open_layers[open_data_sources.index(input_data_source)]
            else:
                self._layer = QgsVectorLayer(input_data_source, self._layer_name, 'ogr')
            yield self

    def out_file(self) -> Path:
        return self._active_file

    def out_data_source(self) -> str:
        return f'{self.out_file()}|layername={self.output_name}'

    def open_layer_data_sources(self) -> list[str]:
        from ..utils import clean_data_source
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                yield clean_data_source(layer.dataProvider().dataSourceUri()).replace('\\', '/')
            else:
                yield ''  # for non-vector layers, return empty string - shouldn't ever be used as a data source but needs to match length of map layers

    def short_help_string(self) -> str:
        folder = Path(os.path.realpath(__file__)).parent.parent / 'alg'
        help_filename = folder / 'help' / 'html' / 'increment_db_and_lyr.html'
        return help_filename.open().read()

    def browse_output_database(self) -> None:
        start_dir = self.output_database
        if not start_dir:
            start_dir = QDir.homePath()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Output Database',
            start_dir,
            'GeoPackage (*.gpkg *.GPKG)',
            options=QFileDialog.DontConfirmOverwrite
        )
        if file_name:
            self.output_database = file_name

    def validate_output_folder(self):
        pass

    def validate_output_name(self):
        from ..utils import layer_name_from_data_source
        open_data_sources = [x for x in self.open_layer_data_sources()]
        if Path(self.output_database).exists():
            for i in range(self.output_layer_table.rowCount()):
                out_data_source = self._output_data_source(i)
                if out_data_source is None:
                    continue
                if out_data_source in open_data_sources:
                    self.output_name_err_txt.setText(
                        self.error_text_creator(
                            f'At least one output layer is open in QGIS: {layer_name_from_data_source(out_data_source)}'
                        )
                    )
                    self.output_name_err_txt.show()
                    self.error = True
                    return

    def check_for_warnings(self):
        from ..utils import GPKG, layer_name_from_data_source
        existing_layers = GPKG(self.output_database).layers()
        if Path(self.output_database).exists():
            for i in range(self.output_layer_table.rowCount()):
                out_data_source = self._output_data_source(i)
                if out_data_source is None:
                    continue
                layer_name = layer_name_from_data_source(out_data_source)
                if layer_name in existing_layers:
                    self.output_name_err_txt.setText(
                        self.warning_text_creator(
                            f'Warning: At least one output layer already exists in database: {layer_name}'
                        )
                    )
                    self.output_name_err_txt.show()
                    self.warning = True
                    break

    def _input_data_source(self, row: int) -> str:
        from ..utils import file_from_data_source
        src = self.output_layer_table.item(row, 0)
        if src.checkState() == QT_CHECKED:
            return f'{Path(file_from_data_source(self.data_source)).as_posix()}|layername={src.text()}'

    def _output_data_source(self, row: int) -> str:
        src = self.output_layer_table.item(row, 0)
        if not src or not src.checkState() == QT_CHECKED:
            return
        dst = self.output_layer_table.item(row, 1)
        dst = dst.text() if dst is not None else src.text()
        return f'{Path(self.output_database).as_posix()}|layername={dst}'

    def copy_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def increment_layer_name_at_row(self, row: int) -> None:
        from ..utils import increment_name
        self.output_layer_table.setItem(
            row, 1, QTableWidgetItem(increment_name(self.output_layer_table.item(row, 0).text()))
        )


class IncrementLayerDialog(IncrementLayerDialogBase, Ui_IncrementLayerDialog):

    def __init__(self, parent: QWidget, layer: QgsVectorLayer):
        from ..utils import increment_name, clean_data_source, layer_name_from_data_source, file_from_data_source
        super().__init__(parent, layer)
        self.setupUi(self)

        self.data_source = clean_data_source(layer.dataProvider().dataSourceUri())
        self.database = file_from_data_source(self.data_source)
        self.layername = layer_name_from_data_source(self.data_source)
        self.increment_layer_name = increment_name(layer_name_from_data_source(self.data_source))
        self.superseded_folder = Path(self.data_source).parent / 'ss'
        self.supersede_database = str(self.superseded_folder / f'{layer_name_from_data_source(self.data_source)}.gpkg')
        self.supersede_layer_name = layer_name_from_data_source(self.data_source)

        self.increment_layer_name_cb.toggled.connect(self.update_active_widgets)
        self.supersede_src_cb.toggled.connect(self.update_active_widgets)

        # load prev settings
        self.increment_layer_name_cb.setChecked(QSettings().value('coastalme_plugin/increment_layer_dlg_inc_lyr_cb', False, type=bool))
        self.supersede_src_cb.setChecked(QSettings().value('coastalme_plugin/increment_layer_dlg_supersede_src_cb', False, type=bool))
        self.keep_old_layer_rb.setChecked(QSettings().value('coastalme_plugin/increment_layer_dlg_keep_old_layer_rb', True, type=bool))
        self.cb_rename_layer.setChecked(QSettings().value('coastalme_plugin/increment_layer_dlg_cb_rename_layer', False, type=bool))

        self.increment_layer_name_cb.toggled.connect(lambda x: QSettings().setValue('coastalme_plugin/increment_layer_dlg_inc_lyr_cb', x))
        self.supersede_src_cb.toggled.connect(lambda x: QSettings().setValue('coastalme_plugin/increment_layer_dlg_supersede_src_cb', x))
        self.keep_old_layer_rb.toggled.connect(lambda x: QSettings().setValue('coastalme_plugin/increment_layer_dlg_keep_old_layer_rb', x))
        self.cb_rename_layer.toggled.connect(lambda x: QSettings().setValue('coastalme_plugin/increment_layer_dlg_cb_rename_layer', x))

        # browse
        self.supersede_database_browse_btn.clicked.connect(self.browse_supersede_database)

        self.setup_ui()
        self.update_active_widgets()

    @property
    def rename_layer(self) -> bool:
        return self.cb_rename_layer.isChecked()

    @rename_layer.setter
    def rename_layer(self, value: bool) -> None:
        self.cb_rename_layer.setChecked(value)

    @property
    def add_to_canvas(self) -> bool:
        return not self.b_supersede_source

    @add_to_canvas.setter
    def add_to_canvas(self, value: bool) -> None:
        pass

    @property
    def output_folder(self) -> str:
        return str(Path(self.supersede_database).parent)

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        raise AttributeError('Cannot set output_folder')

    @property
    def output_name(self) -> str:
        if self.b_increment_layer_name:
            return self.increment_layer_name
        else:
            return self.supersede_layer_name

    @output_name.setter
    def output_name(self, value: str) -> None:
        self.supersede_layer_name = value

    @property
    def action_on_existing(self) -> int:
        if self.b_supersede_source:
            if Path(self.supersede_database).exists():
                return QgsVectorFileWriter.CreateOrOverwriteLayer
            return QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            return QgsVectorFileWriter.CreateOrOverwriteLayer

    @property
    def b_supersede_source(self) -> bool:
        return self.supersede_src_cb.isChecked()

    @b_supersede_source.setter
    def b_supersede_source(self, value: bool) -> None:
        self.supersede_src_cb.setChecked(value)

    @property
    def b_increment_layer_name(self) -> bool:
        return self.increment_layer_name_cb.isChecked()

    @b_increment_layer_name.setter
    def b_increment_layer_name(self, value: bool) -> None:
        self.increment_layer_name_cb.setChecked(value)

    @property
    def increment_layer_name(self) -> str:
        return self.increment_layer_name_line_edit.text()

    @increment_layer_name.setter
    def increment_layer_name(self, value: str) -> None:
        self.increment_layer_name_line_edit.setText(value)

    @property
    def supersede_database(self) -> str:
        return self.supersede_database_line_edit.text()

    @supersede_database.setter
    def supersede_database(self, value: str) -> None:
        self.supersede_database_line_edit.setText(value)

    @property
    def supersede_layer_name(self) -> str:
        return self.supersede_layer_line_edit.text()

    @supersede_layer_name.setter
    def supersede_layer_name(self, value: str) -> None:
        self.supersede_layer_line_edit.setText(value)

    @property
    def supersede_datasource(self) -> str:
        return f'{self.supersede_database}|layername={self.supersede_layer_name}'

    @supersede_datasource.setter
    def supersede_datasource(self, value: str) -> None:
        pass

    @property
    def new_data_source(self):
        from ..utils import file_from_data_source
        if self.b_increment_layer_name:
            return f'{Path(file_from_data_source(self.data_source)).as_posix()}|layername={self.increment_layer_name}'

    @property
    def target_name(self) -> str:
        if self.b_increment_layer_name and self.b_supersede_source:
            return self.increment_layer_name

    def clone_layer(self) -> QgsVectorLayer:
        if self.b_supersede_source:
            return self.layer
        return self.layer.clone()

    def out_file(self) -> Path:
        return Path(self.database)

    def out_data_source(self) -> str:
        return f'{self.out_file()}|layername={self.output_name}'

    def open_layer_data_sources(self) -> Union[str, Path]:
        from ..utils import clean_data_source
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                yield clean_data_source(layer.dataProvider().dataSourceUri())

    def short_help_string(self) -> str:
        folder = Path(os.path.realpath(__file__)).parent.parent / 'alg'
        help_filename = folder / 'help' / 'html' / 'increment_layer.html'
        return help_filename.open().read()

    def browse_supersede_database(self) -> None:
        start_dir = self.supersede_database
        if not start_dir:
            start_dir = QDir.homePath()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Database to Supersede Into',
            start_dir,
            'GeoPackage (*.gpkg *.GPKG)',
            options=QFileDialog.DontConfirmOverwrite
        )
        if file_name:
            self.supersede_database = file_name

    def validate_output_folder(self):
        data_source = f'{Path(self.supersede_database).as_posix()}|layername={self.supersede_layer_name}'
        if data_source in [x for x in self.open_layer_data_sources()]:
            self.output_folder_err_txt.setText(
                self.error_text_creator(
                    f'Output layer is open in QGIS: {self.supersede_layer_name}'
                )
            )
            self.output_folder_err_txt.show()
            self.error = True
            return

    def validate_output_name(self):
        if self.b_increment_layer_name:
            if self.new_data_source in [x for x in self.open_layer_data_sources()]:
                self.output_name_err_txt.setText(
                    self.error_text_creator(
                        f'Output layer is open in QGIS: {self.increment_layer_name}'
                    )
                )
                self.output_name_err_txt.show()
                self.error = True
                return

    def check_for_warnings(self):
        from ..utils import GPKG, file_from_data_source
        if self.b_increment_layer_name and self.increment_layer_name in GPKG(file_from_data_source(self.data_source)).layers():
            self.output_name_err_txt.setText(
                self.warning_text_creator(
                    f'Warning: Incremented layer already exists in current database: {self.increment_layer_name}'
                )
            )
            self.output_name_err_txt.show()
            self.warning = True
        if Path(self.supersede_database).exists():
            if self.supersede_layer_name in GPKG(self.supersede_database).layers():
                self.output_folder_err_txt.setText(
                    self.warning_text_creator(
                        f'Warning: Supersede layer already exists in database: {self.supersede_layer_name}'
                    )
                )
                self.output_folder_err_txt.show()
                self.warning = True

    def update_active_widgets(self, e: bool = False) -> None:
        self.increment_layer_name_line_edit.setEnabled(self.increment_layer_name_cb.isChecked())
        self.cb_rename_layer.setEnabled(self.increment_layer_name_cb.isChecked())
        self.supersede_database_line_edit.setEnabled(self.supersede_src_cb.isChecked())
        self.supersede_layer_line_edit.setEnabled(self.supersede_src_cb.isChecked())
        self.supersede_database_browse_btn.setEnabled(self.supersede_src_cb.isChecked())


import json
import os
from collections import OrderedDict
from pathlib import Path
from qgis.utils import plugins, pluginDirectory

from qgis.PyQt.QtCore import QCoreApplication, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingUtils
from qgis.core import QgsVectorLayer

# processing
import processing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterEnum
from qgis.core import QgsProcessingParameterString
from qgis.core import Qgis, QgsCoordinateReferenceSystem
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.gui.wrappers import WidgetWrapper

from ..utils import ProjectConfig, coastalme_plugin
from coastalme.gui.alg.custom_file_select_parameter import CustomFileSelectParameter
from coastalme.gui.alg.domain_setup_parameter import DomainSetupParameter
from coastalme.gui.alg.settings_table_parameter import SettingsTableParameter
from coastalme.gui.alg.output_format_parameter import OutputFormatParameter


if Qgis.QGIS_VERSION_INT >= 33600:
    FILE_BEHAVIOUR = Qgis.ProcessingFileParameterBehavior.File
    FOLDER_BEHAVIOUR = Qgis.ProcessingFileParameterBehavior.Folder
else:
    FILE_BEHAVIOUR = QgsProcessingParameterFile.File
    FOLDER_BEHAVIOUR = QgsProcessingParameterFile.Folder


class CreateTuflowCatchProject_CustomDialog(AlgorithmDialog):
    """
    Custom dialog. Updates parameters dynamically if a new project folder is selected and it contains an
    existing tcsettings.json file.
    """

    def __init__(self, *args):
        self.project_folder = ''
        super().__init__(*args)

    def changeEvent(self,  *args, **kwargs):
        super().changeEvent(*args, **kwargs)
        self.event_handler()

    def keyReleaseEvent(self, *args, **kwargs):
        super().keyReleaseEvent(*args, **kwargs)
        self.event_handler()

    def event_handler(self):
        if self.mainWidget() is None:
            return
        if not hasattr(self.mainWidget(), 'wrappers'):
            return
        if 'project_folder' not in self.mainWidget().wrappers or not self.mainWidget().wrappers['project_folder'].widgetValue():
            return
        folder = self.mainWidget().wrappers['project_folder'].widgetValue()
        if folder == self.project_folder:
            return
        self.project_folder = folder
        folder = Path(folder)
        settings = folder / 'tfsettings.json'
        if not settings.exists():
            return
        try:
            with settings.open() as f:
                project = ProjectConfig.from_json(f)
        except Exception:
            return
        if 'coastalme_executable' in self.mainWidget().wrappers:
            wrapper = self.mainWidget().wrappers['coastalme_executable']
            is_python_wrapper = issubclass(wrapper.__class__, WidgetWrapper)
            if not is_python_wrapper:
                widget = wrapper.wrappedWidget()
                widget.setFilePath(str(project.hpcexe))
            else:
                widget = wrapper.widget
                widget.setText(str(project.hpcexe))
        if 'coastalme_fv_executable' in self.mainWidget().wrappers:
            wrapper = self.mainWidget().wrappers['coastalme_fv_executable']
            is_python_wrapper = issubclass(wrapper.__class__, WidgetWrapper)
            if not is_python_wrapper:
                widget = wrapper.wrappedWidget()
                widget.setFilePath(str(project.fvexe))
            else:
                widget = wrapper.widget
                widget.setText(str(project.fvexe))
        if 'project_crs' in self.mainWidget().wrappers:
            wrapper = self.mainWidget().wrappers['project_crs']
            wrapper.setParameterValue(project.crs, self.processingContext())
        if 'default_gis_format' in self.mainWidget().wrappers:
            cbo = self.mainWidget().wrappers['default_gis_format'].wrappedWidget()
            cbo.setCurrentIndex(project.gis_extension_to_enum(project.gis_format))


# QGIS_VERSION>=32800
class CreateTuflowProject(QgsProcessingAlgorithm):
    """Setup and create a COASTALME Catch project with the option to create empty files and folder structure."""

    def initAlgorithm(self, config=None):
        """Adds inputs and outputs which define what is displayed in the dialog."""
        # Project Name input
        self.addParameter(
            QgsProcessingParameterString(
                'project_name',
                'Project Name',
                defaultValue=None
            )
        )

        # Project Folder input
        self.addParameter(
            CustomFileSelectParameter(
                'project_folder',
                'Project Folder',
                behavior=FOLDER_BEHAVIOUR,
                fileFilter='All files (*.*)',
                defaultValue=None,
                dirSettingsKey='/coastalme/create_project/project_folder'
            )
        )

        # HPC Executable input
        default_hpc_exe = QSettings().value('/coastalme/create_project/project_exe', None)
        self.addParameter(
            CustomFileSelectParameter(
                'coastalme_executable',
                'COASTALME Executable',
                behavior=FILE_BEHAVIOUR,
                fileFilter='EXE (*.exe *.EXE)',
                defaultValue=default_hpc_exe,
                dirSettingsKey='/coastalme/create_project/project_exe'
            )
        )

        # COASTALME Settings
        table_params_fpath = Path(__file__).parent / 'data' / 'create_coastalme_settings.json'
        with table_params_fpath.open() as f:
            d = json.load(f)
        table_params = d['command settings']
        default_value = QSettings().value('/coastalme/create_project/coastalme_settings', None)
        if not default_value:
            default_value = json.dumps({k2: v2.get('default', '') for k, v in table_params.items() for k2, v2 in v.items()})
        self.addParameter(
            SettingsTableParameter(
                'settings',
                'COASTALME Settings',
                defaultValue=default_value,
                optional=False,
                table_params=table_params
            )
        )

        # domain setup
        self.addParameter(
            DomainSetupParameter(
                'domain',
                'Domain Setup',
                defaultValue=None,
                optional=True
            )
        )

        # output formats
        default_value = OrderedDict({
            'XMDF': {
                'result_types': ['Water Level', 'Depth', 'Velocity'], 'interval': 300.
            },
            'TIF': {
                'result_types': ['Water Level', 'Depth', 'Velocity'], 'interval': 0.
            }
        })
        default_value = QSettings().value('/coastalme/create_project/output_formats', default_value)
        self.addParameter(
            OutputFormatParameter(
                'output_formats',
                'Output Formats',
                defaultValue=default_value,
                optional=True
            )
        )

        # checkbox to create empty files
        default_create_empty_files = True if QSettings().value('/coastalme/create_project/create_empty_files', False) in ['true', 'True', True] else False
        self.addParameter(
            QgsProcessingParameterBoolean(
                'create_empty_files', 'Create Empty Files',
                optional=True,
                defaultValue=default_create_empty_files)
        )

        # checkbox to create folder structure
        default_create_folder_structure = True if QSettings().value('/coastalme/create_project/create_folder_structure', False) in ['true', 'True', True] else False
        self.addParameter(
            QgsProcessingParameterBoolean(
                'create_folder_structure',
                'Create Folder Structure',
                optional=True,
                defaultValue=default_create_folder_structure
            )
        )

        # checkbox to setup coastalme control file templates
        default_setup_cf_templates = True if QSettings().value('/coastalme/create_project/setup_cf_templates', False) in ['true', 'True', True] else False
        self.addParameter(
            QgsProcessingParameterBoolean(
                'setup_cf_templates',
                'Setup Control File Templates',
                optional=True,
                defaultValue=default_setup_cf_templates
            )
        )

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}
        feedback.setCurrentStep(0)

        d = json.loads(self.parameterAsString(parameters, 'settings', context), object_pairs_hook=OrderedDict)
        crs = QgsCoordinateReferenceSystem(d['Projection'].split(' - ')[0])
        gis_format = d['GIS Format']
        del d['Projection']
        del d['GIS Format']

        res_fmts = json.loads(self.parameterAsString(parameters, 'output_formats', context), object_pairs_hook=OrderedDict)

        if self.parameterAsBool(parameters, 'create_empty_files', context):
            if not self.parameterAsBool(parameters, 'create_folder_structure', context):
                feedback.reportError('Cannot create empty files without creating folder structure.', True)
                return {}

        if self.parameterAsBool(parameters, 'setup_cf_templates', context):
            if not self.parameterAsBool(parameters, 'create_folder_structure', context):
                feedback.reportError('Cannot setup control file templates without creating folder structure.', True)
                return {}

        domain = self.parameterAsString(parameters, 'domain', context)

        project = ProjectConfig(
            self.parameterAsString(parameters, 'project_name', context),
            self.parameterAsFile(parameters, 'project_folder', context),
            crs,
            gis_format,
            self.parameterAsFile(parameters, 'coastalme_executable', context),
            None,
            domain,
            d,
            res_fmts
        )
        # save settings
        feedback.pushInfo('Saving settings...')
        project.save_settings()
        feedback.setCurrentStep(1)

        # settings for next time tool is run
        QSettings().setValue('/coastalme/create_project/crs', project.crs.authid())
        QSettings().setValue('/coastalme/create_project/default_gis_format', gis_format)
        QSettings().setValue('/coastalme/create_project/create_empty_files', self.parameterAsBool(parameters, 'create_empty_files', context))
        QSettings().setValue('/coastalme/create_project/create_folder_structure', self.parameterAsBool(parameters, 'create_folder_structure', context))
        QSettings().setValue('/coastalme/create_project/setup_cf_templates', self.parameterAsBool(parameters, 'setup_cf_templates', context))
        QSettings().setValue('/coastalme/create_project/coastalme_settings', self.parameterAsString(parameters, 'settings', context))
        QSettings().setValue('/coastalme/create_project/output_formats', res_fmts)

        # folder structure
        if self.parameterAsBool(parameters, 'create_folder_structure', context):
            feedback.pushInfo('Creating folder structure...')
            project.create_folders()
        feedback.setCurrentStep(2)

        # domain check file - if domain has been specified
        if domain:
            feedback.pushInfo('Creating domain check file...')
            dom_check = project.create_domain_check_file(domain, crs.toWkt())
            if dom_check.startswith('ERROR:'):
                feedback.pushWarning(dom_check)
            else:
                feedback.pushInfo(dom_check)
                alg_params = {
                    'INPUT': dom_check,
                    'NAME': Path(dom_check).stem
                }
                outputs['LoadLayer'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback,
                                                      is_child_algorithm=True)
                if plugins and plugins.get('coastalme'):
                    stylefile = Path(pluginDirectory('coastalme'))  / 'QGIS_Styles' / '_dom_check_R.qml'
                    if stylefile.exists():
                        alg_params = {
                            'INPUT': outputs['LoadLayer']['OUTPUT'],
                            'STYLE': str(stylefile)
                        }
                        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context,
                                                                  feedback=feedback, is_child_algorithm=True)
                    else:
                        feedback.reportWarning(f'Cannot find style file: {stylefile}')

        # empty files
        if self.parameterAsBool(parameters, 'create_empty_files', context):
            project.create_proj_gis_file(project.folder / 'model' / 'gis', False)
            feedback.pushInfo('Creating HPC empty files...')
            project.create_hpc_empties()
            feedback.setCurrentStep(3)
        feedback.setCurrentStep(4)
        # setup template control files
        if self.parameterAsBool(parameters, 'setup_cf_templates', context):
            feedback.pushInfo('Setting up control file templates...')
            project.setup_cf_templates()
        feedback.setCurrentStep(5)

        return results

    def createCustomParametersWidget(self, parent=None):
        """Custom parameters widget so events can dynamically update gui."""
        return CreateTuflowCatchProject_CustomDialog(self, False, parent)

    def shortHelpString(self) -> str:
        folder = Path(os.path.realpath(__file__)).parent
        help_filename = folder / 'help' / 'html' / 'create_project.html'
        with help_filename.open() as f:
            return self.tr(f.read().replace('\n', '<p>'))

    def name(self):
        return 'create_coastalme_project'

    def displayName(self):
        return 'Create COASTALME Project'

    def icon(self) -> QIcon:
        if coastalme_plugin():
            return coastalme_plugin().icon('config_proj')
        return QIcon()

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return CreateTuflowProject()

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

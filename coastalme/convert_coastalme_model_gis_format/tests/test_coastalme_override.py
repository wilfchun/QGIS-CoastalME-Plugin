import unittest
from pathlib import Path
from .test_function import TestFunction


TCF = Path(__file__).parent / r'./coastalme_override/COASTALME/runs/model.tcf'
TEMPLATE_FOLDER = TCF.parent.parent.parent / r'./templates'


class TestTuflowOverride(unittest.TestCase):

    def test_coastalme_override(self):
        test_folder_name = 'coastalme_override'
        out_folder = TCF.parent / test_folder_name
        template_dir = TEMPLATE_FOLDER / test_folder_name
        gis = 'gpkg'
        grid = 'tif'
        op = 'separate'
        args = ['-tcf', str(TCF), '-o', str(out_folder), '-gis', gis, '-grid', grid, '-op', op, '-verbose', 'off',
                '-always-use-root-dir']
        test = TestFunction()
        test.conversion_test(args, template_dir)

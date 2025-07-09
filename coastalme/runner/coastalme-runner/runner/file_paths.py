import os
from pathlib import Path


def get_runner_absolute_path(relative_path):
    """
    Get the absolute path for a relative path
    :param relative_path: path from this folder
    :return: absolute path (pathlib Path)
    """
    script_path = Path(os.path.dirname(os.path.realpath(__file__)))

    return str((script_path / relative_path).resolve())

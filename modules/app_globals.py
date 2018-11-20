import os

UI_PATH = 'ui'
UI_PATHS_FILE = 'gui_resource_paths.json'

LOG_FILE_NAME = 'tiffy.log'

SETTINGS_FILE = 'settings.json'
SETTINGS_DIR_NAME = 'tiffy'

EXIFTOOL_BINARY = 'bin/exiftool.exe'


def get_current_modules_dir():
    """ Return path to this app modules directory """
    # Path to this module
    current_path = os.path.dirname(__file__)

    # Traverse one directoy up
    current_path = os.path.abspath(os.path.join(current_path, '../'))

    return current_path


def get_settings_dir() -> str:
    _app_data = os.getenv('APPDATA')

    _knecht_settings_dir = os.path.join(_app_data, SETTINGS_DIR_NAME)

    if not os.path.exists(_knecht_settings_dir):
        try:
            os.mkdir(_knecht_settings_dir)
        except Exception as e:
            print('Error creating settings directory', e)
            return ''

    return _knecht_settings_dir


class Resource:
    """
        Qt resource paths for ui files and icons.
        Will be loaded from json dict on startup.

        create_gui_resource.py will create the json file for us.
        ui_path[filename] = relative path to ui file
        icon_path[filename] = Qt resource path
    """
    ui_paths = dict()
    icon_paths = dict()

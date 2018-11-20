import logging

from pathlib import Path

from PyQt5 import QtCore
from PyQt5.uic import loadUi

from modules.app_globals import UI_PATH
from modules.log import init_logging

LOGGER = init_logging(__name__)


class SetupWidget:
    @staticmethod
    def from_ui_file(widget_cls, ui_file):
        """ Load a Qt .ui file to setup the provided widget """
        # Store current log level and set it to ERROR for Ui load
        current_log_level = logging.root.getEffectiveLevel()
        logging.root.setLevel(logging.ERROR)

        # Load the Ui file
        ui_file = Path(UI_PATH + '/' + ui_file)
        loadUi(ui_file, widget_cls)

        # Restore previous log level
        logging.root.setLevel(current_log_level)


class ConnectCall(QtCore.QObject):
    def __init__(self, *args, target=None, parent=None):
        super(ConnectCall, self).__init__(parent=parent)
        self.args = args
        self.target = target

    def call(self):
        self.target(*self.args)

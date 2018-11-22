from PyQt5 import QtCore, QtWidgets

from modules.widgets.menu_file import FileMenu
from modules.widgets.menu_info import InfoMenu
from modules.widgets.menu_language import LanguageMenu
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainWindowMenu(QtCore.QObject):
    def __init__(self, ui: QtWidgets.QMainWindow):
        super(MainWindowMenu, self).__init__(parent=ui)
        self.ui = ui

        # File menu already added through UI definition file
        self.file_menu = FileMenu(ui)

        self.lang_menu = LanguageMenu(ui)
        self.info_menu = InfoMenu(ui)

        self.ui.menuBar().addMenu(self.lang_menu)
        self.ui.menuBar().addMenu(self.info_menu)

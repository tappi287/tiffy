import time
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from modules import TiffySettings
from modules.app_read_excel import OpenExcel
from modules.gui.gui_utils import ConnectCall
from modules.gui.icon_resource import IconRsc
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class FileMenu(QtCore.QObject):

    def __init__(self, ui: QtWidgets.QMainWindow, menu: QtWidgets.QMenu=None):
        super(FileMenu, self).__init__(parent=ui)
        self.ui = ui
        self.img_viewer = None
        self.menu = menu or ui.menuDatei
        self.recent_menu = QtWidgets.QMenu(_('Zuletzt geöffnet'), self.menu)

        self.open_xlsx = OpenExcel(ui, self)

        self.setup_file_menu()

    def setup_file_menu(self):
        # ---- Open ----
        open_xlsx_action = QtWidgets.QAction(IconRsc.get_icon('folder'), _('Excel Tabelle öffnen'), self.menu)
        open_xlsx_action.triggered.connect(self.open_xlsx.open_excel)
        self.menu.addAction(open_xlsx_action)

        self.menu.addSeparator()

        # ---- Recent files menu ----
        self.recent_menu.aboutToShow.connect(self.update_recent_files_menu)
        self.menu.addMenu(self.recent_menu)

        # ---- Exit ----
        action_exit = QtWidgets.QAction(IconRsc.get_icon('close'), _("Beenden"), self)
        action_exit.triggered.connect(self.ui.close)
        self.menu.addAction(action_exit)

    def enable_menus(self, enabled: bool=True):
        for a in self.menu.actions():
            a.setEnabled(enabled)

        self.recent_menu.setEnabled(enabled)

    def update_recent_files_menu(self):
        self.recent_menu.clear()

        if not len(TiffySettings.app['recent_files']):
            no_entries_dummy = QtWidgets.QAction(_("Keine Einträge vorhanden"), self.recent_menu)
            no_entries_dummy.setEnabled(False)
            self.recent_menu.addAction(no_entries_dummy)

        for idx, entry in enumerate(TiffySettings.app['recent_files']):
            file, file_type = entry
            file_name = Path(file).name

            if not Path(file).exists():
                # Skip and remove non existing files
                TiffySettings.app['recent_files'].pop(idx)
                continue

            recent_action = QtWidgets.QAction(f'{file_name} - {file_type}', self.recent_menu)
            recent_action.setIcon(IconRsc.get_icon('preset_ref'))

            if file_type == 'xlsx':
                call = ConnectCall(Path(file).as_posix(), target=self.open_xlsx.open_excel, parent=recent_action)
                recent_action.triggered.connect(call.call)

            self.recent_menu.addAction(recent_action)

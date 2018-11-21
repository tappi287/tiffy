import time
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from modules import TiffySettings
from modules.exiftool import ReadExcel, Exif
from modules.gui.gui_utils import ConnectCall
from modules.gui.icon_resource import IconRsc
from modules.widgets.file_dialog import FileDialog
from modules.widgets.message_box import ExcelLoadFailedMsgBox
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

        self.setup_file_menu()

    def setup_file_menu(self):
        # ---- Open ----
        open_xlsx_action = QtWidgets.QAction(IconRsc.get_icon('folder'), _('Öffnen'), self.menu)
        open_xlsx_action.triggered.connect(self.open_excel)
        self.menu.addAction(open_xlsx_action)

        self.menu.addSeparator()

        # ---- Recent files menu ----
        self.recent_menu.aboutToShow.connect(self.update_recent_files_menu)
        self.menu.addMenu(self.recent_menu)

        # ---- Exit ----
        action_exit = QtWidgets.QAction(IconRsc.get_icon('close'), _("Beenden"), self)
        action_exit.triggered.connect(self.ui.close)
        self.menu.addAction(action_exit)

    def open_excel(self, file: str=None) -> None:
        self.enable_menus(False)

        if not file:
            file = FileDialog.open(self.ui, None, 'xlsx')

        if not file:
            LOGGER.info('Open Xlsx File dialog canceled.')
            self.enable_menus(True)
            return

        excel_data = ReadExcel.get_data(Path(file).as_posix())
        self.ui.treeWidget.clear()

        for data in excel_data.items():
            file, file_dict = data
            item_list = [f'{file}']

            for tag, value in zip(Exif.exiftool_tags, file_dict.values()):
                if not value:
                    value = ''
                item_list.append(value)

            item = QtWidgets.QTreeWidgetItem(item_list)
            self.ui.treeWidget.addTopLevelItem(item)

        TiffySettings.add_recent_file(file, 'xlsx')

        # Store excel data in Exif class
        Exif.excel_data = excel_data

        # Output load info
        self.ui.statusBar().showMessage(_('{0} in {1:.3}s geladen.').format(Path(file).name, 0.0))
        self.enable_menus(True)

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
                call = ConnectCall(Path(file).as_posix(), target=self.open_excel, parent=recent_action)
                recent_action.triggered.connect(call.call)

            self.recent_menu.addAction(recent_action)

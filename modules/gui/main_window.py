from pathlib import Path

from PyQt5 import QtWidgets

from modules import TiffySettings
from modules.exiftool import Exif
from modules.gui.gui_utils import SetupWidget
from modules.gui.main_menu import MainWindowMenu
from modules.gui.path_util import SetDirectoryPath
from modules.app_globals import Resource
from modules.gui.icon_resource import IconRsc
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app: QtWidgets.QApplication):
        super(MainWindow, self).__init__()
        self.app = app
        SetupWidget.from_ui_file(self, Resource.ui_paths['tiffy'])

        self.rk_icon = IconRsc.get_icon('RK_Icon')
        self.setWindowIcon(self.rk_icon)

        # Set version window title
        self.setWindowTitle(
            f'{_("Tiffy")} - v{self.app.version}'
            )

        # Prepare translations
        self.translations()

        # ---- Setup Main Menu ----
        self.main_menu = MainWindowMenu(self)

        # ---- Setup path dialogs ----
        dialog_args = (_('Tiff Datei auswaehlen'),  # Title
                       _('Tif (*.tif;*.tiff)')      # Filter
                       )

        self.img_dir = SetDirectoryPath(app, self, mode='file', line_edit=self.imgLineEdit, tool_button=self.imgBtn,
                                        dialog_args=dialog_args, reject_invalid_path_edits=True, parent=self)
        self.img_dir.path_changed.connect(self.update_img_path)

        self.startBtn.pressed.connect(self.read_meta)

        # self.system_tray = QtWidgets.QSystemTrayIcon(self.rk_icon, self)
        # self.system_tray.hide()

    def read_meta(self):
        if not self.img_dir.path:
            return

        exif = Exif(self, self.img_dir.path)
        exif.result.connect(self.meta_result)
        exif.read_meta_data()

    def meta_result(self, metadata: dict):
        LOGGER.debug('%s', metadata)

        for file in metadata:
            self.add_list_widget_item(f'File: {file["SourceFile"]}')

            for tags in file.items():
                key, value = tags
                self.add_list_widget_item(f'{key}: {value}')

    def add_list_widget_item(self, item_text):
        item = QtWidgets.QListWidgetItem(item_text)
        self.listWidget.addItem(item)

    def update_img_path(self, img_path: Path):
        if not img_path.is_file():
            # Only update on chosen files
            return

        if img_path.exists():
            TiffySettings.app['current_path'] = img_path.parent.as_posix()
            TiffySettings.add_recent_file(img_path, img_path.suffix)

        self.img_dir.set_path_text(img_path.parent)
        self.img_dir.path = img_path.parent

    def show_tray_notification(self,
                               title=_('RenderKnecht'),
                               message=_('Keine Nachricht angegeben.')):
        self.system_tray.show()
        self.system_tray.showMessage(title, message, self.rk_icon)
        self.system_tray.hide()

    def tree_with_focus(self):
        """ Return the current QTreeView in focus """
        widget_in_focus = self.focusWidget()

        if widget_in_focus in self.tree_view_list:
            return widget_in_focus

        return False

    def closeEvent(self, close_event):
        close_event.ignore()
        self.app.quit()

    def translations(self):
        self.menuDatei.setTitle(_("Datei"))

from PyQt5 import QtWidgets

from modules.app_update_meta import ImgMetaDataApp
from modules.gui.gui_utils import SetupWidget
from modules.gui.main_menu import MainWindowMenu
from modules.gui.path_util import SetDirectoryPath
from modules.app_globals import Resource
from modules.gui.icon_resource import IconRsc
from modules.detect_language import get_translation
from modules.log import init_logging
from modules.widgets.progress_overlay import ProgressOverlay

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

        self.img_dir = SetDirectoryPath(app, self, mode='file2dir', line_edit=self.imgLineEdit, tool_button=self.imgBtn,
                                        dialog_args=dialog_args, reject_invalid_path_edits=False, parent=self)

        # ---- Setup overlay progress widget ----
        self.progress_widget = ProgressOverlay(self.treeWidget)

        # --- App will bind itself to start btn ---
        self.img_app = ImgMetaDataApp(self)

        self.system_tray = QtWidgets.QSystemTrayIcon(self.rk_icon, self)
        self.system_tray.hide()

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

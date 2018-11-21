import sys

from PyQt5 import QtWidgets

from modules.detect_language import get_translation
from modules.gui.gui_utils import GuiExceptionHook
from modules.gui.main_window import MainWindow
from modules.widgets.message_box import GenericMsgBox
from modules.log import init_logging
from modules.widgets.splash_screen import show_splash_screen_movie

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainApp(QtWidgets.QApplication):
    def __init__(self, version, exception_hook: GuiExceptionHook=None):
        super(MainApp, self).__init__(sys.argv)

        if exception_hook:
            exception_hook.app = self
            exception_hook.setup_signal_destination(self.app_exception)

        splash = show_splash_screen_movie(self)

        self.version = version

        self.ui = MainWindow(self)
        self.ui.show()

        splash.finish(self.ui)

    def app_exception(self, msg):
        msg = _("Ausnahme aufgetreten: <br><br>") + msg.replace('\n', '<br>')
        GenericMsgBox.warning(self.ui, _("Schwerwiegender Fehler"), msg)

    def about_to_quit(self):
        pass

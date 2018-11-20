import sys

from PyQt5 import QtWidgets

from modules.gui.main_window import MainWindow
from modules.log import init_logging
from modules.widgets.splash_screen import show_splash_screen_movie

LOGGER = init_logging(__name__)


class MainApp(QtWidgets.QApplication):
    def __init__(self, version):
        super(MainApp, self).__init__(sys.argv)

        splash = show_splash_screen_movie(self)

        self.version = version

        self.ui = MainWindow(self)
        self.ui.show()

        splash.finish(self.ui)

    def about_to_quit(self):
        pass

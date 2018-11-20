from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QKeySequence

from modules.log import init_logging
from modules.detect_language import get_translation

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class TreeContextMenu(QtWidgets.QMenu):
    def __init__(self, view, ui: QtWidgets.QMainWindow, menu_name: str = _('Baum Kontextmenü')):
        super(TreeContextMenu, self).__init__(menu_name, view)
        self.view, self.ui, self.status_bar = view, ui, ui.statusBar()

        # ---- Prepare Actions ----
        self.insert_row_action = QtWidgets.QAction(_('Zeile einfügen'))
        self.insert_row_action.triggered.connect(self.editor.insert_rows)
        self.addAction(self.insert_row_action)

        self.remove_row_action = QtWidgets.QAction(_('Zeile entfernen\tEntf'))
        self.remove_row_action.triggered.connect(self.editor.remove_rows)
        self.addAction(self.remove_row_action)

        self.addSeparator()

        # ---- Add main menu > edit -----
        self.addMenu(self.ui.main_menu.edit_menu)
        # ---- Add main menu > create -----
        if self.view is self.ui.presetTree:
            self.addMenu(self.ui.main_menu.create_menu)

        # Install context menu event filter
        self.view.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is not self.view:
            return False

        if event.type() == QtCore.QEvent.ContextMenu:
            self.popup(event.globalPos())
            return True

        return False

    def update_actions(self):
        pass

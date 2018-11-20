from PyQt5 import QtWidgets, QtCore

from modules.log import init_logging

LOGGER = init_logging(__name__)


class ProgressOverlay(QtWidgets.QWidget):
    """ Displays a progress bar on top of the provided parent QWidget """
    progress_bar_width_factor = 0.5

    def __init__(self, parent):
        super(ProgressOverlay, self).__init__(parent)

        self.parent = parent

        try:
            self.header_height = self.parent.header().height()
        except AttributeError:
            self.header_height = 0

        height = parent.frameGeometry().height() - self.header_height
        self.setGeometry(0, 0, parent.frameGeometry().width(), height)

        # Make widget transparent
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # Setup widget Layout
        self.box_layout = QtWidgets.QHBoxLayout(self.parent)
        self.box_layout.setContentsMargins(0, self.header_height, 0, 0)
        self.box_layout.setSpacing(0)

        self.progress = QtWidgets.QProgressBar(parent=self)
        self.progress.setFormat('%v/%m')
        self.progress.setAlignment(QtCore.Qt.AlignCenter)
        self.progress.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Hide this widget if progress bar is hidden/shown
        self.progress.hideEvent = self._progress_show_hide_event_wrapper
        self.progress.showEvent = self._progress_show_hide_event_wrapper

        self.box_layout.addWidget(self.progress, 0, QtCore.Qt.AlignCenter)

        # Install parent resize wrapper
        self.org_parent_resize_event = self.parent.resizeEvent
        self.parent.resizeEvent = self._parent_resize_wrapper

        self.progress.hide()
        self.hide()

    def _progress_show_hide_event_wrapper(self, event):
        if event.type() == QtCore.QEvent.Hide:
            self.hide()
        elif event.type() == QtCore.QEvent.Show:
            self.show()

    def _parent_resize_wrapper(self, event):
        self.org_parent_resize_event(event)
        self.resize(self.parent.size())
        self.progress.setMinimumWidth(round(self.width() * self.progress_bar_width_factor))

        event.accept()

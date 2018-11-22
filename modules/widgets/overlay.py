from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPalette, QMovie

from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class _OverlayWidget(QtWidgets.QWidget):
    def __init__(self, widget):
        super(_OverlayWidget, self).__init__(widget)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)

        self.widget = widget

        self.setPalette(palette)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        try:
            height = widget.frameGeometry().height() + widget.header().height()
        except AttributeError:
            LOGGER.error('Overlay Parent has no attribute "header". Using frame height.')
            # Parent has no header
            height = widget.frameGeometry().height()

        self.setGeometry(0, 0, widget.frameGeometry().width(), height)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Add the QMovie object to the label
        self.movie_screen = QtWidgets.QLabel(self)
        self.movie_screen.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.movie_screen, alignment=QtCore.Qt.AlignHCenter)

        self.org_resize_event = self.widget.resizeEvent
        self.widget.resizeEvent = self.resizeEvent

    def move_to_center(self, current_mov):
        """ Move Screen to center """
        mr = current_mov.currentPixmap().rect()
        w, h = mr.width(), mr.height()

        r = self.widget.rect()
        x, y = r.width() / 2, r.height() / 2

        x, y = x - (w / 2), y - (h / 2)

        self.movie_screen.setGeometry(x, y, w, h)

    def generic_center(self):
        """ Moves Movie to Center of parent """
        w, h = 64, 64
        r = self.widget.rect()
        x, y = r.width() / 2, r.height() / 2

        x, y = x - (w / 2), y - (h / 2)
        self.movie_screen.setGeometry(x, y, w, h)

    def update_position(self, pos):
        """ Receives position of drop events """
        self.movie_screen.setGeometry(pos.x() - 32, pos.y(), 64, 64)

    def resizeEvent(self, QResizeEvent):
        self.org_resize_event(QResizeEvent)
        self.resize(QResizeEvent.size())


class IntroOverlay(_OverlayWidget):
    opaque_timer = QtCore.QTimer()
    opaque_timer.setSingleShot(True)

    finished_signal = QtCore.pyqtSignal()

    def __init__(self, widget):
        super(IntroOverlay, self).__init__(widget=widget)
        self.widget = widget

        self.check_mov = QMovie(':/anim/check_anim.gif')
        self.check_mov.setCacheMode(QMovie.CacheAll)
        self.check_mov.finished.connect(self.finished)

        self.intro_mov = QMovie(':/anim/drop_anim.gif')
        self.intro_mov.setCacheMode(QMovie.CacheAll)
        self.intro_mov.finished.connect(self.finished)
        self.opaque_timer.timeout.connect(self.set_opaque_for_mouse_events)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is None or event is None:
            return False

        if obj is self:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.mouse_click()
                return True

        return False

    def set_opaque_for_mouse_events(self):
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

    def intro(self):
        self.intro_mov.jumpToFrame(0)
        self.movie_screen.setMovie(self.intro_mov)

        LOGGER.info('Playing introduction in %sx %sy %spx %spx',
                    self.movie_screen.rect().x(), self.movie_screen.rect().y(),
                    self.movie_screen.rect().width(), self.movie_screen.rect().height())

        self.opaque_timer.start(1000)
        self.movie_screen.show()
        self.show()

        self.intro_mov.start()

    def checkmark(self):
        self.check_mov.jumpToFrame(0)
        self.movie_screen.setMovie(self.check_mov)
        self.opaque_timer.start(1000)
        self.movie_screen.show()
        self.show()

        self.check_mov.start()

    def mouse_click(self):
        self.intro_mov.stop()
        self.finished()

    def finished(self):
        self.movie_screen.hide()
        self.hide()
        self.finished_signal.emit()

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from modules.widgets.message_box import GenericMsgBox
from modules.exiftool import Exif
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class ImgMetaDataApp(QObject):
    def __init__(self, ui):
        super(ImgMetaDataApp, self).__init__(ui)
        self.ui = ui

        self.exif_worker = ImgMetaDataWorker(ui)
        self.setup_exif_app()

    def setup_exif_app(self):
        self.exif_worker.num_items.connect(self.setup_progress)
        self.exif_worker.result.connect(self.update_progress)
        self.exif_worker.finished.connect(self.finish_exif_worker)

        self.ui.startBtn.pressed.connect(self.start_exif_worker)

    def setup_progress(self, value):
        self.ui.progress_widget.progress.show()
        self.ui.progress_widget.progress.setValue(0)
        self.ui.progress_widget.progress.setMaximum(value)

    def update_progress(self, file_name, msg):
        v = self.ui.progress_widget.progress.value() + 1
        self.ui.progress_widget.progress.setValue(v)

        item = QTreeWidgetItem((file_name, msg))
        self.ui.treeWidget.addTopLevelItem(item)

    def start_exif_worker(self):
        self.exif_worker.start()
        self.ui.treeWidget.clear()

    def finish_exif_worker(self):
        self.ui.progress_widget.progress.hide()


class ImgMetaDataWorker(QObject):
    result = pyqtSignal(str, str)
    num_items = pyqtSignal(int)
    finished = pyqtSignal()

    work_timer = QTimer()
    work_timer.setInterval(50)

    def __init__(self, ui):
        super(ImgMetaDataWorker, self).__init__(ui)
        self.ui = ui

        self.exif = None
        self.img_work_queue = list()
        self.missing_imgs = list()
        self.cmd_list = list()
        self.work_timer.timeout.connect(self.work)

    def start(self):
        if not self.ui.img_dir.path or not self.ui.img_dir.path.exists():
            LOGGER.error('Can not start img process. Missing images path.')
            self.finished.emit()
            self.msg(_('Kein Pfad zu Bilddaten angegeben.'))
            return

        self.exif = Exif(self.ui, self.ui.img_dir.path)
        self.exif.result.connect(self.exif_result)

        if not self.exif.excel_data:
            LOGGER.error('Can not start img process. No excel data.')
            self.finished.emit()
            self.msg(_('Keine Excel Daten geladen.'))
            return

        for img_file in self.exif.get_img_files():
            if img_file.stem in self.exif.excel_data.keys():
                self.img_work_queue.append(
                    (img_file, self.exif.excel_data[img_file.stem])
                                      )
            else:
                self.missing_imgs.append(img_file)

        self.num_items.emit(len(self.img_work_queue))
        self.work_timer.start()

    def work(self):
        if not len(self.img_work_queue):
            self.finish()
            return

        img_file, img_dict = self.img_work_queue.pop(0)
        command = list()

        for tag, dict_value in zip(self.exif.exiftool_tags, img_dict.values()):
            if not dict_value:
                continue

            command.append(f'{tag}={dict_value}')

        command.append(f'{img_file.as_posix()}')

        LOGGER.debug('Appending command: %s', command)
        self.exif.update_meta_data(command, img_file.name)

    def finish(self):
        self.work_timer.stop()

        for img in self.missing_imgs:
            self.result.emit(img.name, _("ACHTUNG! Bilddatei -NICHT- in Excel gefunden!"))

        self.finished.emit()

    def exif_result(self, *result):
        self.result.emit(*result)

    def msg(self, msg):
        msg_box = GenericMsgBox(self.ui, _("Bildprozessor"), msg)
        msg_box.exec()
        self.ui.statusBar().showMessage(msg)

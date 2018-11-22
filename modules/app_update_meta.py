import fnmatch
from typing import Union
from pathlib import Path
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QThread

from modules.widgets.message_box import GenericMsgBox
from modules.exif_worker import Exif
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

        self.exif_worker = None

        self.ui.startBtn.pressed.connect(self.start_exif_worker)

    def start_exif_worker(self):
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.startBtn.setEnabled(False)
        self.run_exif_app()

    def finish_exif_worker(self):
        self.ui.tabWidget.setCurrentIndex(1)
        self.exif_worker.exit()
        self.ui.startBtn.setEnabled(True)
        self.ui.progress_widget.progress.hide()

    def run_exif_app(self):
        self.exif_worker = ImgMetaDataWorker(self.ui.img_dir.path, self.ui.excel_data)

        self.exif_worker.num_items.connect(self.setup_progress)
        self.exif_worker.result.connect(self.update_progress)
        self.exif_worker.finish_process.connect(self.finish_exif_worker)
        self.exif_worker.msg.connect(self.message)

        self.exif_worker.start()

    def setup_progress(self, value):
        self.ui.treeWidgetImg.clear()
        self.ui.progress_widget.progress.show()
        self.ui.progress_widget.progress.setValue(0)
        self.ui.progress_widget.progress.setMaximum(value)

    def update_progress(self, file_name, msg):
        v = self.ui.progress_widget.progress.value() + 1
        self.ui.progress_widget.progress.setValue(v)

        item = QTreeWidgetItem((file_name, msg))
        self.ui.treeWidgetImg.addTopLevelItem(item)

    def message(self, msg):
        msg_box = GenericMsgBox(self.ui, _("Bildprozessor"), msg)
        msg_box.exec()
        self.ui.statusBar().showMessage(msg, 8000)


class ImgMetaDataWorker(QThread):
    result = pyqtSignal(str, str)
    num_items = pyqtSignal(int)
    msg = pyqtSignal(str)
    finish_process = pyqtSignal()

    def __init__(self, path: Union[Path, None], excel_data):
        super(ImgMetaDataWorker, self).__init__()
        self.path = path
        self.excel_data = excel_data

        self.exif = Exif(self.path, self.idealThreadCount())
        self.exif.result.connect(self.exif_result)

        self.img_work_queue = list()
        self.missing_imgs = list()
        self.cmd_list = list()

        self.exif_timeout = QTimer()
        self.exif_timeout.setSingleShot(True)
        self.exif_timeout.setInterval(500)
        self.exif_timeout.timeout.connect(self.work)

        self.started.connect(self.init_process)

    def run(self):
        self.exec()
        LOGGER.debug('Img Worker Thread ended.')

    def init_process(self):
        if not self.check_data():
            return

        for img_file in self.exif.get_img_files():
            # Last two digits of file name indicate page number and are ignored
            file_match = fnmatch.filter(self.excel_data.keys(), f'{img_file.stem[:-2]}??')

            if file_match:
                file_match = file_match[0]

                self.img_work_queue.append(
                    (img_file, self.excel_data[file_match])
                                      )
            else:
                self.missing_imgs.append(img_file)

        self.num_items.emit(len(self.img_work_queue))
        self.work()

    def check_data(self):
        if not self.path or not self.path.exists():
            LOGGER.error('Can not start img process. Missing images path.')
            self.msg.emit(_('Kein Pfad zu Bilddaten angegeben.'))
            self.finish_process.emit()
            return False

        if not self.excel_data:
            LOGGER.error('Can not start img process. No excel data.')
            self.msg.emit(_('Keine Excel Daten geladen.'))
            self.finish_process.emit()
            return False

        return True

    def work(self):
        if not len(self.img_work_queue):
            self.finish_work()
            return

        img_file, img_dict = self.img_work_queue.pop(0)
        command = list()

        for tag, dict_value in zip(Exif.exiftool_tags, img_dict.values()):
            if not dict_value:
                continue

            command.append(f'{tag}={dict_value}')

        # Do not back up files
        command.append('-overwrite_original')
        command.append(f'{img_file.as_posix()}')

        LOGGER.debug('Appending command: %s', command)
        self.exif.update_meta_data(command, img_file.name)
        self.exif_timeout.start()

    def finish_work(self):
        if self.exif.thread_pool.activeThreadCount():
            self.exif_timeout.start()
            return

        self.exif_timeout.stop()

        for img in self.missing_imgs:
            self.result.emit(img.name, _("ACHTUNG! Bilddatei -NICHT- in Excel gefunden!"))

        self.finish_process.emit()

    def exif_result(self, *result):
        self.result.emit(*result)
        self.work()

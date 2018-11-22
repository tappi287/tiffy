import exiftool
from collections import OrderedDict
from pathlib import Path
from PyQt5 import QtCore, QtWidgets

from modules.app_globals import EXIFTOOL_BINARY
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class Exif(QtCore.QObject):
    result = QtCore.pyqtSignal(str, str)
    file_types = ['.tif', '.tiff', '.jpg', '.jpeg']

    xmp_keys = ['XMP:Title', 'XMP:Creator', 'XMP:Description', 'XMP:Subject', 'XMP:Rights']
    iptc_keys = ['IPTC:ObjectName', 'IPTC:By-line', 'IPTC:Caption-Abstract', 'IPTC:Keywords', 'IPTC:CopyrightNotice']
    exif_keys = [None, 'EXIF:Artist', 'EXIF:ImageDescription', None, 'EXIF:Copyright']

    # Actual Exiftool tag names
    exiftool_tags = ['-Title', '-Creator', '-Description', '-Subject', '-Rights']

    spreadsheet_map = OrderedDict()
    spreadsheet_map.update({
        'file': 'B', 'title': 'K', 'author': None, 'description': None, 'keywords': 'B', 'copyright': 'EG'})

    # Maximum number of concurrent exiftool instances (running in QThreadPool)
    # Note that performance is mainly influenced by network/drive read and write speed
    # Having to many instances read and write may greatly reduces performance
    max_threads = 4

    def __init__(self, img_path: Path, ideal_thread_count: int=2):
        super(Exif, self).__init__()
        self.img_path = img_path
        self.current_file_name = None

        self.thread_pool = QtCore.QThreadPool(parent=self)
        thread_count = max(1, min(self.max_threads, round(ideal_thread_count * 0.75)))
        self.thread_pool.setMaxThreadCount(thread_count)
        self.thread_pool.setExpiryTimeout(90000)
        self.thread_pool.clear()

    def update_meta_data(self, cmd_list, file_name):
        self.current_file_name = file_name

        exif_runner = ExifRunner(cmd_list, file_name, self.update_result)
        self.thread_pool.start(exif_runner)
        LOGGER.debug('Started Exif Runner %s/%s', self.thread_pool.activeThreadCount(), self.max_threads)

    def update_result(self, file_name, result):
        self.result.emit(file_name, result)

    def read_meta_data(self):
        with exiftool.ExifTool(executable_=EXIFTOOL_BINARY) as et:
            metadata = et.get_metadata_batch(self.get_img_files().as_posix())

        if not metadata:
            return

        self.result.emit(metadata)

    def get_img_files(self):
        for img_file in self.img_path.glob('*.*'):
            if f'{img_file.suffix}'.casefold() in self.file_types:
                yield img_file


class ExifRunnerSignals(QtCore.QObject):
    result = QtCore.pyqtSignal(str, str)


class ExifRunner(QtCore.QRunnable):
    def __init__(self, cmd_list, current_file, result_callback):
        super(ExifRunner, self).__init__()
        self.cmd_list = cmd_list
        self.current_file = current_file

        self.signals = ExifRunnerSignals()
        self.signals.result.connect(result_callback)

    def run(self):
        with exiftool.ExifTool(executable_=EXIFTOOL_BINARY) as et:
            LOGGER.debug('Sending commands %s', self.cmd_list)

            params = map(exiftool.fsencode, self.cmd_list)
            result = et.execute(*params).decode('UTF-8')

            LOGGER.debug('Exiftool result: %s %s', self.current_file, result)
            self.signals.result.emit(self.current_file, result)

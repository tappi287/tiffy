import exiftool

from modules.app_globals import EXIFTOOL_BINARY
from pathlib import Path
from PyQt5 import QtCore, QtWidgets


class Exif(QtCore.QObject):
    result = QtCore.pyqtSignal(object)
    file_types = ['.tif', '.tiff']

    xmp_keys = ['XMP:Title', 'XMP:Creator', 'XMP:Description', 'XMP:Subject', 'XMP:Rights']
    iptc_keys = ['IPTC:ObjectName', 'IPTC:By-line', 'IPTC:Caption-Abstract', 'IPTC:Keywords', 'IPTC:CopyrightNotice']
    exif_keys = [None, 'EXIF:Artist', 'EXIF:ImageDescription', None, 'EXIF:Copyright']

    spreadsheet_map = {
        'title': 'K',
        'author': None,
        'keywords': 'B',
        'copyright': 'EG'
        }

    def __init__(self, ui: QtWidgets.QMainWindow, img_path: Path):
        super(Exif, self).__init__(ui)
        self.ui, self.img_path = ui, img_path

    def read_meta_data(self):
        with exiftool.ExifTool(executable_=EXIFTOOL_BINARY) as et:
            metadata = et.get_metadata_batch(self.get_img_files())

        if not metadata:
            return

        self.result.emit(metadata)

    def get_img_files(self):
        for img_file in self.img_path.glob('*.*'):
            if f'{img_file.suffix}'.casefold() in self.file_types:
                yield img_file.as_posix()

import fnmatch
import re
from typing import Union
from pathlib import Path
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QThread

from modules.widgets.message_box import GenericMsgBox, QuestionBox
from modules.exif_worker import Exif
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class ImgMetaDataApp(QObject):
    update_dpi = False
    dpi_res_x = '300.0'
    dpi_res_y = '300.0'
    dpi_unit = '2'  # 3=cm 2=inches
    dpi_tags = ['-ResolutionUnit', '-XResolution', '-YResolution']

    ignored_name_patterns = ('_VERSO?$', '_RECTO?$')
    ignore_last_digits = True

    def __init__(self, ui):
        super(ImgMetaDataApp, self).__init__(ui)
        self.ui = ui

        self.exif_worker = None
        self.update_from_excel = True

        self.ui.startBtn.pressed.connect(self.start_exif_worker)

    def start_exif_worker(self):
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.startBtn.setEnabled(False)

        if not self.check_data():
            self.finish_exif_worker()
            return

        self.run_exif_app()

    def finish_exif_worker(self):
        self.ui.tabWidget.setCurrentIndex(1)

        if self.exif_worker:
            self.exif_worker.exit()

        self.ui.startBtn.setEnabled(True)
        self.ui.progress_widget.progress.hide()

    def check_data(self):
        if not self.ui.img_dir.path or not self.ui.img_dir.path.exists():
            LOGGER.error('Can not start img process. Missing images path.')
            self.message(_('Kein Pfad zu Bilddaten angegeben.'))
            return False

        self.update_from_excel = True
        if not self.ui.excel_data:
            question = self.ask_proceed_without_excel(self.ui)
            if question:
                # User wants to proceed without excel data
                self.update_from_excel = False
                if not self.update_dpi:
                    self.message(_('Weder DPI noch Excel Daten zum aktualisieren ausgewählt.<br><br>'
                                   'Der Vorgang wird abgebrochen.'))
                    return False

                LOGGER.error('No excel data. But user wants to continue.')
                return True

            LOGGER.error('Can not start img process. No excel data.')
            return False

        if not self.verify_excel_data(self.ui.excel_data):
            LOGGER.error('Excel contained invalid keys only. Could not associate image files. Aborting.')
            self.message(_('Der Tabelle fehlen Daten in der Spalte für die korrespondierenden Dateinamen.<br><br>'
                            'Konnte keine Einträge mit gültigen Dateinamen finden. Überprüfe in den Einstellungen '
                            'ob die Spalte für die Dateinamen korrekt eingestellt ist.'))
            return False

        return True

    def run_exif_app(self):
        self.exif_worker = ImgMetaDataWorker(self, self.ui.img_dir.path, self.ui.excel_data, self.update_from_excel)

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

    @staticmethod
    def ask_proceed_without_excel(ui):
        question = QuestionBox.ask(parent=ui, title_txt=_('Bilddaten aktualisieren'),
                                   message=_('Es wurden keine Exceldaten geladen. '
                                             'Es werden keine Metadaten aktualisiert!'
                                             '<br><br>Möchtest du trotzedem fortfahren?'), ok_btn_txt=_('Fortfahren'),
                                   abort_btn_txt=_('Abbrechen'))
        return question

    @staticmethod
    def verify_excel_data(excel_data: dict):
        invalid_keys = set()

        for k in excel_data.keys():
            if not k:
                invalid_keys.add(k)

        for k in invalid_keys:
            excel_data.pop(k)

        if not excel_data:
            return False

        return True


class ImgMetaDataWorker(QThread):
    result = pyqtSignal(str, str)
    num_items = pyqtSignal(int)
    msg = pyqtSignal(str)
    finish_process = pyqtSignal()

    def __init__(self, parent_app: ImgMetaDataApp, path: Union[Path, None], excel_data, update_from_excel: bool):
        super(ImgMetaDataWorker, self).__init__()

        # Store dpi settings
        self.update_dpi = parent_app.update_dpi
        self.dpi_tags = parent_app.dpi_tags
        self.dpi_unit = parent_app.dpi_unit
        self.dpi_res_x = parent_app.dpi_res_x
        self.dpi_res_y = parent_app.dpi_res_y

        # Name settings
        self.ignored_name_patterns = parent_app.ignored_name_patterns
        self.ignore_last_digits = parent_app.ignore_last_digits

        self.path = path
        self.excel_data = excel_data
        self.update_from_excel = update_from_excel

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
        for img_file in self.exif.get_img_files():
            if not self.update_from_excel:
                # No excel data to update
                self.img_work_queue.append((img_file, None))
                continue

            file_match = self.match_file_name(img_file.stem, self.excel_data.keys())

            if file_match:
                file_match = file_match[0]

                self.img_work_queue.append(
                    (img_file, self.excel_data[file_match])
                                      )
            else:
                self.missing_imgs.append(img_file)

        self.num_items.emit(len(self.img_work_queue))
        self.work()

    def match_file_name(self, name, excel_keys):
        # Create search pattern for ignored name parts
        pattern = ''
        for pattern_part in self.ignored_name_patterns:
            pattern += f'{pattern_part}|'

        # Remove Name parts to ignore eg. _RECTO
        file_name = re.sub(pattern, '', name)

        if self.ignore_last_digits:
            # Last two digits of file name indicate page number and are ignored
            file_name = re.sub(r'\d\d$', '', file_name)

        # Match name against excel row entries
        file_match = fnmatch.filter(excel_keys, f'{file_name}*')

        return file_match

    def work(self):
        if not len(self.img_work_queue):
            self.finish_work()
            return

        img_file, img_dict = self.img_work_queue.pop(0)
        command = list()

        if self.update_dpi:
            # Update units from user settings and update resolution, eg 300dpi or 118,11 ppc
            for tag, value in zip(self.dpi_tags, (self.dpi_unit, self.dpi_res_x, self.dpi_res_y)):
                command.append(f'{tag}={value}')

        if self.update_from_excel:
            # Update image tags from excel data
            for tag, dict_value in zip(Exif.exiftool_tags, img_dict.values()):
                if not dict_value:
                    continue
                command.append(f'{tag}={dict_value}')

        # command.append('-v3')
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

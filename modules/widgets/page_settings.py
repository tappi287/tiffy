from PyQt5.QtCore import QObject, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator

from openpyxl.utils import column_index_from_string, get_column_letter
from modules.exif_worker import Exif
from modules.detect_language import get_translation
from modules.gui.gui_utils import ConnectCall
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class SettingsPage(QObject):
    def __init__(self, ui):
        super(SettingsPage, self).__init__(ui)
        self.ui = ui

        self.labels = [self.ui.fileLabel, self.ui.titleLabel, self.ui.authorLabel,
                       self.ui.descLabel, self.ui.keyLabel, self.ui.rightLabel]
        self.inputs = [self.ui.fileInput, self.ui.titleInput, self.ui.authorInput,
                       self.ui.descInput, self.ui.keyInput, self.ui.rightInput]
        self.fields = [self.ui.fileDesc, self.ui.titleDesc, self.ui.authorDesc,
                       self.ui.descDesc, self.ui.keyDesc, self.ui.rightDesc]
        self.boxes = [self.ui.fileBox, self.ui.titleBox, self.ui.authorBox,
                      self.ui.descBox, self.ui.keyBox, self.ui.rightBox]

        self.ui.threadCountSlider.sliderReleased.connect(self.update_thread_count)

        self.column_keys = list(Exif.spreadsheet_map.keys())
        self.default_columns = list(Exif.spreadsheet_map.values())
        self.translations()
        self.setup_widgets()

    def setup_widgets(self):
        regex = QRegExp('^[A-Z]?[A-Z]?[A-Z]?$')
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        validator = QRegExpValidator(regex)

        for idx, (input_field, box) in enumerate(zip(self.inputs, self.boxes)):
            input_field.setValidator(validator)
            input_call = ConnectCall(input_field, box, idx, target=self.update_column_field, parent=self)
            input_field.textChanged.connect(input_call.call)

            box_call = ConnectCall(input_field, box, idx, target=self.update_column_box, parent=self)
            box.valueChanged.connect(box_call.call)

        self.ui.restoreBtn.released.connect(self.restore_defaults)

    def update_column_field(self, input_field, input_box, idx: int):
        column = input_field.text().upper()
        input_field.setText(column)

        if column:
            input_box.setValue(column_index_from_string(column))
        else:
            input_box.setValue(0)

    def update_column_box(self, input_field, input_box, idx: int):
        """
            Called from line edit changed -and- box set value.
            Therefore safe to update spreadsheet map from here.
        """
        column_idx = input_box.value()
        column = None

        if column_idx:
            column = get_column_letter(column_idx)
            input_field.setText(column)
        else:
            input_field.setText('')

        self.update_excel_column(column, idx)

    def update_excel_column(self, column: str, idx: int):
        if not column:
            column = None

        if self.ui.excel_data:
            # Clear existing excel data
            self.ui.excel_data = None
            self.ui.treeWidget.clear()
            LOGGER.info('Spreadsheet mapping changed. Excel data cleared.')

        column_key = self.column_keys[idx]
        Exif.spreadsheet_map[column_key] = column
        LOGGER.debug('Updated spreadsheet mapping:\n%s', Exif.spreadsheet_map)

    def update_thread_count(self):
        Exif.max_threads = self.ui.threadCountSlider.value()

    def restore_defaults(self):
        for idx, (input_field, box) in enumerate(zip(self.inputs, self.boxes)):
            column = self.default_columns[idx]

            if column:
                input_field.setText(column)
            else:
                box.setValue(0)

    def translations(self):
        titles = _('Dateiname;Titel;Author;Beschreibung;Stichwörter;Copyright').split(';')
        desc = _('<b>Diese Spalte MUSS befüllt sein.</b> Leere Zeilen werden übersprungen. Enthält den Dateinamen ohne '
                 'Dateierweiterung.;'
                 'Enthält den korrespondierenden Titel;'
                 'Enthält den korrespondierenden Author;'
                 'Enthält die korrespondierende Beschreibung;'
                 'Enthält die korrespondierenden Stichwörter;'
                 'Enthält den korrespondierenden Rechtshinweis').split(';')
        values = list(Exif.spreadsheet_map.values())

        for idx, (label, input_field, field, box) in enumerate(zip(self.labels, self.inputs, self.fields, self.boxes)):
            label.setText(titles[idx])
            input_field.setText(values[idx])

            if values[idx]:
                box.setValue(column_index_from_string(values[idx]))

            field.setText(desc[idx])

        self.ui.groupBox.setTitle(_('Excel Tabellenzuordnungen'))
        self.ui.excelDesc.setText(_('Legt fest welche Spalte der Tabelle für die '
                                    'entsprechenden Metadaten verwendet wird. Leere Felder und Spalten mit Nummer 0 '
                                    'werden nicht berücksichtigt.'))
        self.ui.appSettings.setTitle(_('Anwendung'))
        self.ui.appSettingDesc.setText(_('Erweiterte Anwendungseinstellungen. Unerfahrenen Benutzern '
                                         'wird empfohlen diese Einstellungen nicht zu ändern.'))
        self.ui.restoreBtn.setText(_('Standard wiederherstellen'))

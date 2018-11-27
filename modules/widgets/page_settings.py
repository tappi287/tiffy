from PyQt5.QtCore import QObject, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator

from openpyxl.utils import column_index_from_string, get_column_letter

from modules.app_update_meta import ImgMetaDataApp
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

        # Dpi Settings
        self.ui.dpiBox.toggled.connect(self.enable_dpi_setting)
        self.ui.dpiSpinBox.valueChanged.connect(self.update_dpi_resolution)
        self.ui.dpiComboBox.currentIndexChanged.connect(self.update_dpi_unit)

        # File Name Pattern Settings
        self.ui.ignoreInput.editingFinished.connect(self.set_ignore_pattern)
        self.ui.ignoreNum.toggled.connect(self.set_ignore_last_digits)

    # ---- Filename - Excel association ----
    def set_ignore_pattern(self):
        value = self.ui.ignoreInput.text()
        pattern = value.split(';')
        LOGGER.debug('Setting file name ignore pattern: %s', pattern)
        ImgMetaDataApp.ignored_name_patterns = pattern

    def set_ignore_last_digits(self, enabled):
        LOGGER.debug('Setting Ignore last digits in file name: %s', enabled)
        ImgMetaDataApp.ignore_last_digits = enabled

    # ---- Excel associations ----
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

    # ---- DPI Settings ----
    @staticmethod
    def enable_dpi_setting(enabled: bool):
        LOGGER.debug('Updated dpi setting, update dpi: %s', enabled)
        ImgMetaDataApp.update_dpi = enabled

    def update_dpi_resolution(self, value):
        LOGGER.debug(f'Updated dpi setting, unit: {value:.2f}')
        ImgMetaDataApp.dpi_res_x = f'{value:.2f}'
        ImgMetaDataApp.dpi_res_y = f'{value:.2f}'

    def update_dpi_unit(self, index):
        if index == 0:
            ImgMetaDataApp.dpi_unit = '2'  # Inches
            LOGGER.debug('Updated dpi setting, unit: Inches')
        elif index == 1:
            ImgMetaDataApp.dpi_unit = '3'  # Centimeter
            LOGGER.debug('Updated dpi setting, unit: Centimeter')

    def restore_defaults(self):
        for idx, (input_field, box) in enumerate(zip(self.inputs, self.boxes)):
            column = self.default_columns[idx]

            if column:
                input_field.setText(column)
            else:
                box.setValue(0)

        self.ui.ignoreInput.setText('_VERSO?$;_RECTO?$')
        self.ui.ignoreNum.setChecked(True)

        self.ui.dpiBox.setChecked(False)
        self.ui.dpiComboBox.setCurrentIndex(0)
        self.ui.dpiSpinBox.setValue(300.0)

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

        # Excel settings
        self.ui.groupBox.setTitle(_('Excel Tabellenzuordnungen'))
        self.ui.excelDesc.setText(_('Legt fest welche Spalte der Tabelle für die '
                                    'entsprechenden Metadaten verwendet wird. Leere Felder und Spalten mit Nummer 0 '
                                    'werden nicht berücksichtigt.'))
        self.ui.appSettings.setTitle(_('Anwendung'))
        self.ui.appSettingDesc.setText(_('Erweiterte Anwendungseinstellungen. Unerfahrenen Benutzern '
                                         'wird empfohlen diese Einstellungen nicht zu ändern.'))
        self.ui.restoreBtn.setText(_('Standard wiederherstellen'))

        # DPI Tag Settings
        self.ui.dpiBox.setTitle(_('Auflösungs Meta Daten verändern'))
        self.ui.dpiLabel.setText(_('Auflösung pro Einheit'))

        for i, v in enumerate([_('DPI - Pixel pro Zoll'), _('PPCM - Pixel pro Centimeter')]):
            self.ui.dpiComboBox.setCurrentIndex(i)
            self.ui.dpiComboBox.setCurrentText(v)
        self.ui.dpiComboBox.setCurrentIndex(0)

        self.ui.dpiDesc.setText(_('Beschreibt die physikalische Bildgröße in angegebener Anzahl Pixel pro Einheit'))

        # Filename - Excel association
        self.ui.nameBox.setTitle(_('Dateinamen Zeilenzuordnung'))
        self.ui.ignoreLabel.setText(_('Ignoriert:'))
        self.ui.ignoreDesc.setText(_('RegEx für zu ignorienrende Teile des Dateinamens mit Semikolon ; getrennt. '
                                     'zB. <i>Name01_VERSO</i> entspricht Zeile <i>Name01</i>'))
        self.ui.ignoreNumDesc.setText(_('Ignoriert Zahlen am Namensende. zB. <i>Name08</i> '
                                        'entspricht Zeile <i>Name01</i>'))
        self.ui.ignoreNum.setText(_('Letzte 2 Stellen ignorieren'))

from PyQt5.QtCore import QObject

from modules.exif_worker import Exif
from modules.detect_language import get_translation
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

        self.translations()

    def setup_widgets(self):
        pass

    def translations(self):
        titles = _('Datei;Titel;Author;Beschreibung;Stichwörter;Copyright').split(';')
        desc = _('Enthält den korrespondierenden Dateinamen;'
                 'Enthält den korrespondierenden Titel;'
                 'Enthält den korrespondierenden Author;'
                 'Enthält die korrespondierende Beschreibung;'
                 'Enthält die korrespondierenden Stichwörter;'
                 'Enthält den korrespondierenden Rechtshinweis').split(';')
        values = list(Exif.spreadsheet_map.values())

        for idx, (label, input_field, field) in enumerate(zip(self.labels, self.inputs, self.fields)):
            label.setText(titles[idx])
            input_field.setText(values[idx])
            field.setText(desc[idx])

        self.ui.groupBox.setTitle(_('Excel Tabellenzuordnungen'))
        self.ui.excelDesc.setText(_('Legt fest welche Spalte der Tabelle für die '
                                    'entsprechenden Metadaten verwendet wird.'))
        self.ui.appSettings.setTitle(_('Anwendung'))
        self.ui.appSettingDesc.setText(_('Erweiterte Anwendungseinstellungen. Unerfahrenen Benutzern '
                                         'wird empfohlen diese Einstellungen nicht zu ändern.'))

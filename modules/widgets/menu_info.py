from PyQt5.QtWidgets import QMenu, QMessageBox, QAction

from modules.gui.icon_resource import IconRsc
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class InfoMenu(QMenu):
    def __init__(self, ui):
        super(InfoMenu, self).__init__('?', ui)
        self.ui = ui
        self.about_title = _("Über Tiffy v{} GPLv3").format(self.ui.app.version)

        icon = IconRsc.get_icon('help')
        info = QAction(icon, self.about_title, self)
        info.triggered.connect(self.show_about_box)
        self.addAction(info)

    def show_about_box(self):
        txt = _('{0}<br>Copyright (C) 2017 Stefan Tapper, All rights reserved.<br><br>'
                'Visit the <a href="https://github.com/tappi287/tiffy">source code@github</a> of this software!<br><br>'
                'Tiffy is free software: you can redistribute it and/or modify '
                'it under the terms of the GNU General Public License as published by '
                'the Free Software Foundation, either version 3 of the License, or '
                '(at your option) any later version.<br><br>'
                'Tiffy is distributed in the hope that it will be useful, '
                'but WITHOUT ANY WARRANTY; without even the implied warranty of '
                'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the '
                'GNU General Public License for more details.<br><br>'
                'You should have received a copy of the GNU General Public License '
                'along with Tiffy. If not, see '
                '<a href="http://www.gnu.org/licenses/">here</a>.').format(self.about_title)

        txt = _('{0}<br>Copyright (C) 2018 Stefan Tapper<br><br>'
                'Besuche den <a href="https://github.com/tappi287/tiffy">Quelltext@github</a> dieser Software!<br><br>'
                'Dieses Programm ist Freie Software: Sie können es unter den Bedingungen '
                'der GNU General Public License, wie von der Free Software Foundation, '
                'Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren '
                'veröffentlichten Version, weiter verteilen und/oder modifizieren.<br><br>'
                'Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird, jedoch '
                'OHNE JEDE GEWÄHR,; sogar ohne die implizite '
                'Gewähr der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. '
                'Siehe die GNU General Public License für weitere Einzelheiten.<br><br>'
                'Sie sollten eine Kopie der GNU General Public License zusammen mit diesem'
                'Programm erhalten haben. Wenn nicht, siehe '
                '<a href="http://www.gnu.org/licenses/">hier</a>.').format(self.about_title)

        about_box = QMessageBox.about(self.ui, self.about_title, txt)

from PyQt5.QtGui import QIcon, QPixmap
from modules.app_globals import Resource


class IconRsc:
    # Store loaded icons here
    icon_storage = {
        'example_key': QIcon()
        }

    @classmethod
    def get_icon(cls, icon_key: str):
        if icon_key not in cls.icon_storage.keys():

            if icon_key in Resource.icon_paths.keys():
                icon = QIcon(QPixmap(Resource.icon_paths[icon_key]))
            else:
                icon = QIcon()

            cls.icon_storage[icon_key] = icon

        return cls.icon_storage[icon_key]

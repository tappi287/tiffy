"""
    This setup should be imported before any application modules are imported.

    Imported only -ONCE- from main.
"""
from multiprocessing import Queue
from modules.settings import TiffySettings
from modules.log import init_logging, setup_logging

logging_queue = Queue(-1)
setup_logging(logging_queue)
LOGGER = init_logging('knecht_init')

TiffySettings.log_queue = logging_queue
TiffySettings.load_ui_resources()

try:
    TiffySettings.load()
except Exception as e:
    LOGGER.error('Error loading settings from file!\n%s', e)

LOGGER.info('Knecht modules initialisation method finished.')

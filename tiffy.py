import sys
import logging

from ui import gui_resource
from multiprocessing import Queue
from modules.gui.gui_utils import GuiExceptionHook
from modules.log import init_logging, setup_log_queue_listener
from modules.settings import TiffySettings
from modules.gui.main_app import MainApp

VERSION = '0.62'

# Prepare exception handling
sys.excepthook = GuiExceptionHook.exception_hook


def initialize_log_listener():
    global LOGGER
    LOGGER = init_logging('knecht_main')

    try:
        log_queue = TiffySettings.log_queue
    except AttributeError:
        LOGGER.fatal('Could not get logging queue from TiffySettings!')
        log_queue = Queue(-1)

    # This will move all handlers from LOGGER to the queue listener
    log_listener = setup_log_queue_listener(LOGGER, log_queue)

    return log_listener


def shutdown(log_listener):
    #
    # ---- CleanUp ----
    # We do this just to prevent the IDE from deleting the imports
    gui_resource.qCleanupResources()

    # Shutdown logging and remove handlers
    LOGGER.info('Shutting down log queue listener and logging module.')
    log_listener.stop()
    logging.shutdown()
    sys.exit()


def main():
    #
    # ---- StartUp ----
    # Start log queue listener in it's own thread
    log_listener = initialize_log_listener()
    log_listener.start()

    LOGGER.debug('---------------------------------------')
    LOGGER.debug('Application start.')

    # Update version in settings
    TiffySettings.app['version'] = VERSION

    # Load GUI resource paths
    if not TiffySettings.load_ui_resources():
        LOGGER.fatal('Can not locate UI resource files! Shutting down application.')
        shutdown(log_listener)

    #
    #
    # ---- Start application ----
    app = MainApp(VERSION, GuiExceptionHook)
    result = app.exec_()
    #
    #

    #
    #
    # ---- Application Result ----
    LOGGER.debug('---------------------------------------')
    LOGGER.debug('Qt application finished with exitcode %s', result)
    TiffySettings.save()
    #
    #
    shutdown(log_listener)


if __name__ == '__main__':
    main()

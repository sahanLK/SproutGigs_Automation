import os
import sys
import logging
import database
from PyQt5.QtGui import QIcon
from functions.fns import get_file_logger, get_syslogger
from keycapture import key_listener
from livecontrols import LiveControls
from screens.loginscreen import LoginScreen
from screens.mainscreen import MainScreen
from PyQt5.QtWidgets import QApplication
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/main.log", 'w+')
sys_logger = get_syslogger()

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    sys_logger.error("Import error when generating app id")
    pass

basedir = os.path.dirname(__file__)


# Setting up the database stuff
database.main()


if __name__ == "__main__":
    # Activate Keylogger
    if not key_listener():
        sys.exit()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, 'icons/app-icon.ico')))

    # Creating screens for only one time
    login_screen = LoginScreen()
    main_screen = MainScreen()

    # Screens will be universally accessed across the programme from LiveControls class
    LiveControls.screens['login_screen'] = login_screen
    LiveControls.screens['main_screen'] = main_screen

    login_screen.show()
    app.exec_()

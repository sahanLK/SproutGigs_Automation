import os
import sys
import logging
from PyQt5.QtGui import QIcon
from functions.fns import get_file_logger, get_syslogger
from keycapture import key_listener
from livecontrols import LiveControls
from picoconstants import db_handler
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


def __database_ok():
    # Check the existence of all the required tables.
    if not db_handler.tb_exists('accounts'):
        cols = {
            "email": "Varchar(255)",
            "password": "Varchar(255)",
            "device": "int(2)"
        }
        db_handler.create_tb('accounts', cols, 'email')

    if not db_handler.tb_exists('blogs'):
        cols = {
            "blog_domain": "Varchar(255)",
            "blog_links": "MEDIUMTEXT",
            "post_titles": "MEDIUMTEXT",
            "last_words": "MEDIUMTEXT",
            "last_sentences": "MEDIUMTEXT",
            "last_paragraphs": "MEDIUMTEXT",
        }
        db_handler.create_tb('blogs', cols, 'blog_domain')

    if not db_handler.tb_exists('ad_sites'):
        cols = {
            "domain": "Varchar(255)",
            "first_url": "MEDIUMTEXT",
            "about_url": "MEDIUMTEXT",
            "contact_url": "MEDIUMTEXT",
            "links": "MEDIUMTEXT",
        }
        db_handler.create_tb('ad_sites', cols, 'domain')

    if not db_handler.tb_exists('current_blog_and_ad_data'):
        cols = {
            "blog_links": "MEDIUMTEXT",
            "titles": "MEDIUMTEXT",
            "last_paragraphs": "MEDIUMTEXT",
            "last_sentences": "MEDIUMTEXT",
            "last_words": "MEDIUMTEXT",
            "ad_first_opened": "MEDIUMTEXT",
            "ad_contact_url": "MEDIUMTEXT",
            "ad_about_url": "MEDIUMTEXT",
            "ad_links": "MEDIUMTEXT",
        }
        db_handler.create_tb('current_blog_and_ad_data', cols)

    if not db_handler.tb_exists('current_job_data'):
        cols = {
            "job_id": "Varchar(255)",
            "ji_section": "Mediumtext",
            "rp_section": "Mediumtext",
            "ap_section": "Mediumtext",
        }
        db_handler.create_tb('current_job_data', cols, "job_id")

    if not db_handler.tb_exists('login_info'):
        cols = {
            "ip_address": "Varchar(255)",
            "email": "Varchar(255)",
            "datetime": "DATETIME",
        }
        db_handler.create_tb('login_info', cols, "ip_address")

    if not db_handler.tb_exists('ai_success'):
        cols = {
            "text": "VARCHAR(255)",
            "decision": "int(2)",
        }
        db_handler.create_tb('ai_success', cols, 'text')

    if not db_handler.tb_exists('ai_failed'):
        cols = {
            "text": "VARCHAR(255)",
            "decisions": "Varchar(255)",
        }
        db_handler.create_tb('ai_failed', cols, 'text')

    if not db_handler.tb_exists('earnings'):
        cols = {
            "date": "DATE",
            "tasks": "INT",
            "usd": "FLOAT",
        }
        db_handler.create_tb('earnings', cols, 'date')

    if not db_handler.tb_exists('test_steps'):
        cols = {
            "step": "VARCHAR(255)",
        }
        db_handler.create_tb('test_steps', cols, 'step')
    return True


__database_ok()

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

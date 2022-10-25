import sys
import logging
from selenium.webdriver.common.by import By

from functions.driverfns import open_url
from functions.fns import get_file_logger, get_syslogger
from picoconstants import *
from concurrent.futures import ThreadPoolExecutor
from livecontrols import LiveControls
from devices import device
import pathlib

base_dir = pathlib.Path(__file__).parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/picosetup.log", 'w+')
sys_logger = get_syslogger()


class SetupPico:
    driver = None

    def __init__(self):
        self.allowed_browsers = ['chrome', 'edge', 'firefox']

    def init_setup(self, email: str, password: str, browser: str):
        """
        Login to Picoworkers.
        :return:
        """
        if browser.lower() not in self.allowed_browsers:
            logger.critical("Using Invalid Browser.")
            return False
        with ThreadPoolExecutor() as executor:
            logger.info('Launching driver')
            executor.submit(self.__launch_driver, [email, password, browser.lower()])

    def __launch_driver(self, args):
        """
        Launch the webdriver.

        Device No. 0 is nothing but a normal webdriver instance except that disabled
        the javascript -> navigator.webdriver
        """
        email, pwd, browser = args[0], args[1], args[2]
        LiveControls.browser = browser  # Will be useful when capturing screenshots.

        device_record = db_handler.select_filtered('accounts', ['device'], f'email="{email}"')
        if device_record:
            device_no = device_record[0][0]
            logger.debug(f"Device No: {device_no}")
        else:
            sys_logger.critical("Device number could not be taken from database")
            return

        # if browser == 'chrome':
        #     user_data_dir = os.path.join(PICO_LOCATION, email)
        #     dev = device.DeviceWithChrome(device_no=device_no, udd=user_data_dir)
        #     self.driver = dev.get_driver()
        #     LiveControls.driver = self.driver
        if browser == 'edge':
            dev = device.DeviceWithEdge(device_no=device_no, pd=email)
            self.driver = dev.get_driver()
            LiveControls.driver = self.driver
        else:
            logger.error(f"No proper browser implementation. Given {browser}")
            return

        self.__adjust_window()

        self.accept_cookies()
        if not device_no == 0:
            self.driver.switch_to.new_window(type_hint='tab')
        open_url(LOGIN_URL, '_self', self.driver)
        self.driver.find_element(By.ID, EMAIL_FIELD_ID).send_keys(email)
        self.driver.find_element(By.ID, PASSWD_FIELD_ID).send_keys(pwd)
        if device_no == 0:
            self.driver.find_element(By.XPATH, LOGIN_BUT_X_PATH).click()

    def __adjust_window(self):
        self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.driver.set_window_position(POSITION_X, POSITION_Y)

    def accept_cookies(self):
        try:
            self.driver.find_element(By.XPATH, COOKIE_ACC_BUT_X_PATH).click()
        except Exception as e:
            logger.info(f"Error when accepting cookies.")
            pass

    def exit(self, close_driver=True):
        if close_driver:
            self.driver.quit()
        sys.exit()

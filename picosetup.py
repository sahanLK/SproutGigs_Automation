import sys
import logging
from selenium.webdriver.common.by import By
from functions.fns import get_file_logger, get_syslogger
from constants import *
from concurrent.futures import ThreadPoolExecutor
from livecontrols import LiveControls
from devices import device
import pathlib
from database import get_session, User

base_dir = pathlib.Path(__file__).parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/picosetup.log", 'w+')
sys_logger = get_syslogger()

session = get_session()


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

        device_no = session.query(User.device).filter(
            User.email.__eq__(email)).first()[0]

        if not device_no or not isinstance(device_no, int):
            sys_logger.critical(f"Invalid Device No: {device_no}")
            return
        sys_logger.debug(f"Device No: {device_no}")


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
        self.driver.open_url(LOGIN_URL, '_self', force_chk_config=True)
        self.driver.find_element(By.ID, EMAIL_FIELD_ID).send_keys(email)
        self.driver.find_element(By.ID, PASSWD_FIELD_ID).send_keys(pwd)
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

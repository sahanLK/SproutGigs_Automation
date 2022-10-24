import json
import os
import pathlib
import logging
from subprocess import CREATE_NO_WINDOW
from typing import Union

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from functions.fns import get_file_logger
from selenium.webdriver.remote.command import Command
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/device.log", 'w+')


class Edge(webdriver.Edge):

    def __init__(self, device_no: int, udd: Union[str, None], pd: Union[str, None]):
        # Configuration object that handles all the configurations.
        self.configs = _Configs(device_no=device_no, udd=udd, pd=pd)
        if not self.configs.configOk:
            logger.critical("Configuration error. Not initializing webdriver")
            return

        if not self.configs.htmlGenerated:
            logger.critical("Html file generate error. Not initializing webdriver")
            return

        # Looking Good. Initialize the webdriver.
        super(Edge, self).__init__(options=self.configs.options, service=self.configs.service)

    def __repr__(self):
        """
        When __init__ method did not execute the parent initialization (super) because of return
        statements in the __init__, this class becomes not representable or printable and generates errors.
        To prevent those errors, keep this always here.
        Errors are prevented by putting a fake session_id as 0.
        :return:
        """
        try:
            # Instance has created properly
            return '<{0.__module__}.{0.__name__} (session="{1}")>'.format(
                type(self), self.session_id)
        except AttributeError:
            return "0"

    def get(self, url: str) -> None:
        logger.debug("Method <get> is out of service. Use <open_url> instead.")
        return

    def open_url(self, url: str, target: str) -> None:
        if target == "_blank":
            self.switch_to.new_window(type_hint='tab')

        if 'sproutgigs' in url:  # Spoof for sproutgigs.com
            self.configs.exec_spoof_js(self)
            if self.configs.load_config_page(self):
                if self.configs.is_config_equal(self):
                    self.execute(Command.GET, {'url': url})
                else:
                    logger.critical(f"Configuration mismatch found. Not opening: {url}")
        else:
            self.execute(Command.GET, {'url': url})


class _Configs:
    common_options = ['--no-sandbox', '--start-maximized',
                      '--disable-blink-features=AutomationControlled', 'disable-infobars']

    def __init__(self, device_no: int, udd: Union[str, None], pd: Union[str, None]):
        self.device_no = device_no
        self.udd = udd
        self.pd = pd

        self.configOk = False
        self.htmlGenerated = False

        # If the device number is 0, nothing special will happen,
        # Device 0 is a normal selenium webdriver instance without any modification except
        # the javascript -> navigator.webdriver is set to false.
        if device_no == 0:
            logger.info("Device 0 requested. Nothing special will happen.")
            return

        logger.info(f"Creating device {device_no}\n{'=' * 50}\n")
        try:
            with open(f'{base_dir}/devices/devices-json/device{device_no}.json') as f:
                self.json_configs: dict = json.load(f)
        except FileNotFoundError:
            logger.error(f"device{device_no}.json not found. aborting ...")
            return

        self.browserInfo: dict = self.json_configs['browser']
        self.deviceInfo: dict = self.json_configs['device']

        # Web browser information
        # self.browserName = self.browserInfo['name']     # Possible values: [chrome, firefox, edge]
        # self.appCodeName = self.browserInfo['appCodeName']
        # self.browserVersion = self.browserInfo['version']

        # self.flashEnabled = self.browserInfo['flash']
        self.webGlEnabled = self.browserInfo['webGL']  # Option

        # Device information
        self.platform = self.deviceInfo['platform']  # Multiple JS

        # Width properties
        self.screenWidth = self.deviceInfo['screenWidth']  # JS
        self.screenAvailWidth = self.deviceInfo['screenAvailWidth']  # JS
        self.windowOuterWidth = self.deviceInfo['windowOuterWidth']  # JS
        self.windowInnerWidth = self.deviceInfo['windowInnerWidth']  # JS

        # Height properties
        self.screenHeight = self.deviceInfo['screenHeight']  # JS
        self.screenAvailHeight = self.deviceInfo['screenAvailHeight']  # JS
        self.windowOuterHeight = self.deviceInfo['windowOuterHeight']  # JS
        self.windowInnerHeight = self.deviceInfo['windowInnerHeight']  # JS

        self.screenColorDepth = self.deviceInfo['screenColorDepth']  # JS
        self.screenPixelDepth = self.deviceInfo['screenPixelDepth']  # JS

        self.navigatorUserAgent = self.browserInfo['navigatorUserAgent']  # JS
        self.navigatorCookieEnabled = self.browserInfo['navigatorCookies']  # JS
        self.navigatorDeviceMemory = self.deviceInfo['navigatorDeviceMemory']  # JS

        self.language = self.deviceInfo['language']  # Experimental Option
        self.gpu = self.deviceInfo['gpu']  # Option

        self._chk_req_configs()
        self.generate_html()

    def _chk_req_configs(self):
        # Check browser configs
        configs = [key for key in self.browserInfo.keys()]
        for key in configs:
            if self.browserInfo[key] == '':
                logger.error(f"Browser Config <{key}> not set")
                return
            else:
                logger.info(f"Browser Config for <{key}> set")

        # Check device configs
        configs = [key for key in self.deviceInfo.keys()]
        for key in configs:
            if self.deviceInfo[key] == '':
                logger.error(f"Device Config <{key}> not set")
                return
            else:
                logger.info(f"Device Config for <{key}> set")
        self.configOk = True

    def generate_html(self):
        header = open(f'{base_dir}/devices/config-page/header.txt').read()
        footer = open(f'{base_dir}/devices/config-page/footer.txt').read()
        logger.info("Page header and footer ready.")

        all_settings = [
            {'property': 'navigator.platform', 'value': self.platform, 'id': 'platform'},
            {'property': 'screen.width', 'value': self.screenWidth, 'id': 'width'},
            {'property': 'screen.availWidth', 'value': self.screenAvailWidth, 'id': 'availwidth'},
            {'property': 'window.outerWidth', 'value': self.windowOuterWidth, 'id': 'outerwidth'},
            {'property': 'window.innerWidth', 'value': self.windowInnerWidth, 'id': 'innerwidth'},
            {'property': 'screen.height', 'value': self.screenHeight, 'id': 'height'},
            {'property': 'screen.availHeight', 'value': self.screenAvailHeight, 'id': 'availheight'},
            {'property': 'window.outerHeight', 'value': self.windowOuterHeight, 'id': 'outerheight'},
            {'property': 'window.innerHeight', 'value': self.windowInnerHeight, 'id': 'innerheight'},
            {'property': 'screen.colorDepth', 'value': self.screenColorDepth, 'id': 'colordepth'},
            {'property': 'screen.pixelDepth', 'value': self.screenPixelDepth, 'id': 'pixeldepth'},
            {'property': 'navigator.userAgent', 'value': self.navigatorUserAgent, 'id': 'useragent'},
            {'property': 'navigator.cookieEnabled', 'value': self.navigatorCookieEnabled, 'id': 'cookieenabled'},
            {'property': 'navigator.deviceMemory', 'value': self.navigatorDeviceMemory, 'id': 'devicememory'},
        ]

        tb_rows = ''
        for setting in all_settings:
            tb_rows += f"<tr id='config-row'>\n" \
                       f"\t<td class='property'>{setting['property']}</td>\n" \
                       f"\t<td class='configured'>{setting['value']}</td>\n" \
                       f"\t<td class='actual' id='{setting['id']}'></td>\n" \
                       f"</tr>\n"

        body = f"""
                <div class="intro">
                    <h2 class="text-center device-no">Javascript Configuration For Device {self.device_no}</h2>
                </div>
                <div class="content">
                    <table class="table table-striped table-bordered" id="config-table">
                        <thead class="thead-dark">
                            <tr><th scope="col">Property</th>
                                <th scope="col">Configured To:</th>
                                <th scope="col">Actual</th>
                            </tr>
                        </thead>
                        {tb_rows}
                    </table>
                </div>
                """
        try:
            with open(f'{base_dir}/devices/configs.html', 'w+') as f:
                f.write("{}\n{}\n{}".format(header, body, footer))
                print("Generated configuration html file")
                self.htmlGenerated = True
                return True
        except Exception as e:
            print(f"Configuration html file generate error: {e}")
        # footer.txt file also contains some js code to display browser actual settings.

    def exec_spoof_js(self, driver: Union[Edge]):
        script = """
                (function(platform, screenWidth, screenAvailWidth, windowOuterWidth, windowInnerWidth,
                screenHeight, screenAvailHeight, windowOuterHeight, windowInnerHeight,screenColorDepth,
                 screenPixelDepth, navigatorUserAgent,navigatorCookieEnabled, navigatorDeviceMemory) {

                console.log("Executing device configuration");

                /* Width properties */
                Object.defineProperty(window.screen, 'width', {value: screenWidth});
                Object.defineProperty(window.screen, 'availWidth', {value: screenAvailWidth});

                Object.defineProperty(window, 'outerWidth', {value: windowOuterWidth});
                Object.defineProperty(window, 'innerWidth', {value: windowInnerWidth});

                /* Height properties */
                Object.defineProperty(window.screen, 'height', {value: screenHeight});
                Object.defineProperty(window.screen, 'availHeight', {value: screenAvailHeight});

                Object.defineProperty(window, 'outerHeight', {value: windowOuterHeight});
                Object.defineProperty(window, 'innerHeight', {value: windowInnerHeight});

                /* Other windows.screen properties */
                Object.defineProperty(window.screen, 'colorDepth', {value: screenColorDepth});
                Object.defineProperty(window.screen, 'pixelDepth', {value: screenPixelDepth});

                /* Other navigator properties */
                Object.defineProperty(window.navigator, 'platform', {value: platform});
                Object.defineProperty(window.navigator, 'cookieEnabled', {value: navigatorCookieEnabled});
                Object.defineProperty(window.navigator, 'deviceMemory', {value: navigatorDeviceMemory});

                /* Spoofing navigator.userAgentData object */
                var userAgentDataClone = Object;
                Object.assign(userAgentDataClone, JSON.parse(JSON.stringify(window.navigator.userAgentData)));
                userAgentDataClone.platform = platform;

                Object.defineProperty( window.navigator, 'userAgentData', {
                    value: userAgentDataClone,
                    writable: true,
                    enumerable: true,
                    configurable: true,
                });
                console.log("Executed device configuration successfully");
                })("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")
                """ % (self.platform,
                       self.screenWidth,
                       self.screenAvailWidth,
                       self.windowOuterWidth,
                       self.windowInnerWidth,
                       self.screenHeight,
                       self.screenAvailHeight,
                       self.windowOuterHeight,
                       self.windowInnerHeight,
                       self.screenColorDepth,
                       self.screenPixelDepth,
                       self.navigatorUserAgent,
                       self.navigatorCookieEnabled,
                       self.navigatorDeviceMemory)

        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script})
        logger.debug(f"CDP spoofing js executed. Since this doesn't give any output,"
                     f" successful execution not guaranteed.")

    @staticmethod
    def load_config_page(driver: Union[Edge]):
        """
        Loads the generated html file into the browser.
        :param driver:
        :return:
        """
        try:
            file = os.path.abspath(f"{base_dir}/devices/configs.html")
            if not os.path.isfile(file):
                raise FileNotFoundError
            # Do not use <open_url> method below. It will be an infinite loop
            driver.execute(Command.GET, {'url': file})
            logger.info("Configuration html file loaded")
            return True
        except FileNotFoundError:
            logger.critical("configs.html not found.")
        except Exception as e:
            logger.critical(f"Html file loading error: {e}")

    @staticmethod
    def is_config_equal(driver: Union[Edge]):
        """
        This is used to check if all the actual values and configured values are
        equal or not. If any of them are not equal, do not open any url.
        Use this method to check all the configurations whenever you are going to open an url.
        :param driver:
        :return:
        """
        html = driver.page_source
        soup = BeautifulSoup(str(html), 'lxml')

        for tr in soup.find_all('tr', {'id': 'config-row'}):
            config_to = tr.find('td', {'class': 'configured'}).text.strip()
            actual = tr.find('td', {'class': 'actual'}).text.strip()
            if config_to != actual:
                logger.error(f"Configuration mismatch:\t[{config_to} != {actual}]")
                return False
        return True

    @property
    def options(self) -> Union[EdgeOptions, ChromeOptions]:
        options = EdgeOptions()

        # Update common_options with few other values based on json data
        if not self.gpu:
            self.common_options.append("--disable-gpu")  # Change the canvas fingerprint
        if not self.webGlEnabled:
            self.common_options.append("--disable-webgl")  # Disabling WebGl
        self.common_options.append(f'--user-agent={self.navigatorUserAgent}')

        for option in self.common_options:
            options.add_argument(option)
            logger.info(f"Option applied ->\t{option}")

        # For device 0, common options will be applied
        if self.device_no == 0:
            return options

        options.add_experimental_option('prefs', {'intl.accept_languages': self.language})
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Browser specific options
        options.use_chromium = True  # For edge only

        # Here you set the path of the profile ending with User Data not the profile folder
        if self.udd:
            if os.path.exists(self.udd):
                options.add_argument(f"--user-data-dir={self.udd}")
                logger.debug(f"UDD applied -> {self.udd}")
            else:
                logger.debug("UDD path not available")

        # Here you specify the actual profile folder
        if self.pd:
            options.add_argument(f"profile-directory={self.pd}")
            logger.debug(f"PD applied for MS Edge driver -> {self.pd}")
        return options

    @property
    def service(self):
        service = EdgeService()
        service.creationflags = CREATE_NO_WINDOW
        logger.debug("Services applied")
        return service


class DeviceWithEdge:
    def __init__(self, device_no: int, udd: str = None, pd: str = None):
        self.device_no = device_no
        self.udd = udd
        self.pd = pd

    def get_driver(self) -> Union[Edge, None]:
        driver = Edge(device_no=self.device_no, udd=None, pd=None)
        try:
            # If this does not generate an error, driver is properly initialized.
            session = driver.session_id
            return driver
        except AttributeError:
            return None


if __name__ == "__main__":
    device = DeviceWithEdge(device_no=1)
    drv = device.get_driver()

    drv.open_url("http://localhost", target="_self")
    for _ in range(3):
        drv.open_url("http://localhost/", target='_blank')

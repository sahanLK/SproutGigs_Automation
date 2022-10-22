# Creates the given device with related json data
import json
import logging
import os.path
from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
import pathlib
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from functions.fns import get_file_logger, get_syslogger

base_dir = pathlib.Path(__file__).parent.parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/device.log", 'w+')
sys_logger = get_syslogger()


class _BaseDevice:
    """
    Create the Device
    """

    """
    Common options
    """
    common_options = ['--no-sandbox', '--start-maximized',
                      '--disable-blink-features=AutomationControlled', 'disable-infobars']

    def __init__(self, device_no: int):
        self.device_no = device_no

        self.configOk = False
        self.driver = None
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
        if self.configOk:
            self.store_common_options()
        else:
            logger.error("Configuration error")

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

    def store_common_options(self):
        """
        The options that require prior modification or checking, are appended into
        [common_options] with this method.
        :return:
        """
        if not self.gpu:
            self.common_options.append("--disable-gpu")  # Change the canvas fingerprint
        if not self.webGlEnabled:
            self.common_options.append("--disable-webgl")  # Disabling WebGl
        self.common_options.append(f'--user-agent={self.navigatorUserAgent}')

    def execute_spoofing_cdp_js(self) -> bool:
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

        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script})
            logger.info(f"Successfully executed cdp spoofing js")
            return True
        except Exception as e:
            logger.error(f"Error when executing cdp js: {e}")
        return False

    def _generate_html(self):
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
            tb_rows += f"<tr>\n" \
                       f"\t<td>{setting['property']}</td>\n" \
                       f"\t<td>{setting['value']}</td>\n" \
                       f"\t<td id='{setting['id']}'></td>\n" \
                       f"</tr>\n"

        body = f"""
        <div class="intro">
            <h2 class="text-center device-no">Javascript Configuration For Device {self.device_no}</h2>
        </div>
        <div class="content">
            <table class="table table-striped table-bordered">
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
                logger.info("Generated configuration html file")
                return True
        except Exception as e:
            logger.error(f"Configuration html file generate error: {e}")
        # footer.txt file also contains some js code to display browser actual settings.

    def _load_config_page(self):
        """
        Loads the generated js config html page into the current active tab.
        :return:
        """
        logger.info("Loading html file")
        try:
            file = os.path.abspath(f"{base_dir}/devices/configs.html")
            if not os.path.isfile(file):
                raise FileNotFoundError
            self.driver.get(f"file://{file}")
            logger.info("Html file loaded")
            return True
        except FileNotFoundError:
            logger.error("configs.html not found.")
        except Exception as e:
            logger.error(f"Html file loading error: {e}")


class DeviceWithEdge(_BaseDevice):
    def __init__(self, device_no: int, udd: str = None, pd: str = None):
        """
        Get a device with microsoft edge browser
        :param device_no: Used to identify the correct json file.
        :param udd: User data directory
        :param pd: Profile directory. Unique to the edge browser.
        """
        super(DeviceWithEdge, self).__init__(device_no=device_no)
        self.udd = udd
        self.pd = pd  # A unique option only for Microsoft Edge.

        # Don't need to do anything if configuration is not ok.
        if self.configOk:
            self.options = webdriver.EdgeOptions()
            self.service = EdgeService()

            self.service.creationflags = CREATE_NO_WINDOW
            self.apply_common_options()

    def apply_common_options(self):
        logger.info("Applying options.")
        for option in self.common_options:
            self.options.add_argument(option)
            logger.info(f'Option applied -> [{option}]')

        self.options.add_experimental_option('prefs', {'intl.accept_languages': self.language})
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Browser specific options
        self.options.use_chromium = True
        self.options = self.__apply_edge_udd_and_pd(options=self.options)

        # self.options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        logger.info("Options applied.")

    def __apply_edge_udd_and_pd(self, options: [webdriver.EdgeOptions]):
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

    def get_driver(self):
        logger.debug("Getting driver")
        if self.device_no == 0:
            logger.debug("Creating Device 0")
            options = webdriver.EdgeOptions()
            options = self.__apply_edge_udd_and_pd(options=options)
            options.add_argument('--disable-blink-features=AutomationControlled')
            self.driver = webdriver.Edge(
                options=options,
                executable_path='msedgedriver.exe')
            return self.driver

        if not self.configOk:
            logger.error("Configuration error, Not returning driver.")
            return
        logger.info("Configurations ok.")

        self.driver = webdriver.Edge(
            options=self.options,
            service=self.service,
            executable_path='msedgedriver.exe')
        logger.info("Executing Spoofing CDP js")
        self.execute_spoofing_cdp_js()

        if not self._generate_html():
            return
        if not self._load_config_page():
            return
        return self.driver


class DeviceWithChrome(_BaseDevice):
    def __init__(self, device_no: int, udd: str):
        """
        :param device_no:
        :param udd: User Data Directory
        """
        super(DeviceWithChrome, self).__init__(device_no=device_no)
        # Don't need to do anything if configuration is not ok.
        if self.configOk:
            self.udd = udd

            self.options = webdriver.ChromeOptions()
            self.service = ChromeService()

            self.service.creationflags = CREATE_NO_WINDOW
            self.apply_common_options()

    def apply_common_options(self):
        for option in self.common_options:
            self.options.add_argument(option)
            logger.info(f'Option applied -> [{option}]')

        self.options.add_experimental_option('prefs', {'intl.accept_languages': self.language})
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        prefs = {'disk-cache-size': 1073741824}
        self.options.add_experimental_option('prefs', prefs)

        if not os.path.exists(self.udd):
            os.makedirs(self.udd)
        self.options.add_argument(f"--user-data-dir={self.udd}")

    def get_driver(self):
        if not self.configOk:
            print("Configuration error, Not returning driver.")
            return

        self.driver = webdriver.Chrome(
            options=self.options,
            service=self.service,
            executable_path='msedgedriver.exe')
        logger.info("Executing Spoofing CDP js")
        self.execute_spoofing_cdp_js()

        if not self._generate_html():
            return
        if not self._load_config_page():
            return
        return self.driver


if __name__ == "__main__":
    device = DeviceWithEdge(device_no=0)
    driver = device.get_driver()
    print(driver)

from typing import Union
from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException, WebDriverException, NoSuchWindowException
from functions.fns import get_from_db
from picoconstants import (MARKETING_TEST_URL,
                           CHROME_HISTORY_URL,
                           EDGE_HISTORY_URL,
                           SNAPSHOT_LOC,
                           MAX_BLOG_URLS_REQ,
                           MAX_AD_URLS_REQ)
from livecontrols import LiveControls
import logging
import pathlib

base_dir = pathlib.Path(__file__).parent.parent.absolute()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] [%(filename)s %(funcName)s] line %(lineno)d:  %(message)s')
file_handler = logging.FileHandler(f"{base_dir}/logs/driverfns.log", 'w+')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def open_url(url: str, target: str, driver: Union[webdriver.Chrome, webdriver.Edge] = None) -> None:
    """
    Opens a given url with a given webdriver.
    :param url: str url to be opened.
    :param target: str _self or _blank in html.
    :param driver: Selenium Webdriver instance
    :return:
    """
    allowed_targets = ['_self', '_blank']
    if target not in allowed_targets:
        logger.critical(f"Invalid target parameter was passed in: {target}. Not opening: {url}")
        return
    if not driver:
        driver = LiveControls.driver
    try:
        if target == '_blank':
            driver.switch_to.new_window(type_hint='tab')
        driver.execute_cdp_cmd()
        driver.execute_script('''window.open("{}");'''.format(url))
    except Exception as e:
        logger.error(f'Error opening link : {url}: {e}')


def filter_mt():
    """
    Filter jobs for marketing test.
    :return: None
    """
    open_url(MARKETING_TEST_URL, "_self")
    logger.debug("Filtered for Marketing test jobs")


def snap_history():
    """
    Capture screenshot of an browser history page.
    :return:
    """
    from tabshandler import TabsHandler
    driver = get_driver()
    # Get links from database.
    blog_links = get_from_db('Blog_Links', get_all=True)
    if not blog_links:
        logger.debug("No blog links")
        return
    blog_links = blog_links[0:MAX_BLOG_URLS_REQ]

    ad_links = get_from_db('Ad_Links', get_all=True)
    ad_links = ad_links[0:MAX_AD_URLS_REQ]
    total_links = blog_links + ad_links

    # Open necessary links if not already opened.
    opened = 0
    for link in total_links:
        # Open the links if keylogger has not requested to stop
        if LiveControls.stop_link_open:
            logger.debug("Stopped snapshot:\tOpened: {}".format(opened))
            break
        open_url(link, '_blank')
        opened += 1
        if TabsHandler.switch_to_tab_by_url(link):
            TabsHandler.close_active_tab()
        continue

    # Stop link opening if user has opened them earlier.
    if opened == len(total_links):
        LiveControls.snap_links_opened = True

    # Do not capture the screenshot if user is forced to stop the link opening process or,
    # enough urls are not present in the database.
    if LiveControls.stop_link_open:
        logger.debug("Snapshot stopped: Keylogger stopped link opening")
        return
    if not len(blog_links) >= MAX_BLOG_URLS_REQ:
        logger.debug("Snapshot stopped: Insufficient blog data ({0}/{1}).".format(len(blog_links), MAX_BLOG_URLS_REQ))
        return
    if not len(ad_links) >= MAX_AD_URLS_REQ:
        logger.debug("Snapshot stopped: Insufficient ad data ({0}/{1})".format(len(ad_links), MAX_AD_URLS_REQ))
        return

    driver = LiveControls.driver
    if not driver:
        logger.error("Webdriver instance could not be taken from LiveControls.")
        return

    try:
        driver.switch_to.new_window(type_hint="tab")    # Switch to a new empty tab
    except NoSuchWindowException:
        logger.error("Failed to open a new tab")
        return
    browser = LiveControls.browser
    logger.info(f"Browser Detected: {browser}")
    if browser == 'chrome':
        history_url = CHROME_HISTORY_URL
    elif browser == 'edge':
        history_url = EDGE_HISTORY_URL
    else:
        logger.error('Could not detect proper history url type')
        return

    driver.get(history_url)
    try:
        driver.save_screenshot(SNAPSHOT_LOC)
        TabsHandler.close_active_tab()
        logger.debug("Screenshot captured.")
        TabsHandler.go_to_doing_job_tab()
    except NoSuchWindowException:
        pass


def get_driver() -> Union[webdriver.Chrome, webdriver.Edge]:
    """
    Returns the current active webdriver
    :return:
    """
    driver = LiveControls.driver
    if driver:
        return driver
    logger.error("No active webdriver found.")


def get_current_url(driver) -> str:
    """
    Get the current tab url
    :param driver:
    :return:
    """
    if driver:
        try:
            current_url = driver.current_url
            return current_url
        except (UnexpectedAlertPresentException,
                WebDriverException):
            pass
    return ''


def switch_to_any_tab():
    """
    Just used to switch any active window. Use whenever you close the active tab by JS.
    :return:
    """
    driver = get_driver()
    switched = False
    for handle in driver.window_handles:
        try:
            driver.switch_to.window(handle)
            switched = True
            break
        except Exception as e:
            continue
    if not switched:
        logger.debug("Could not switch to any random tab")


def modify_doing_job_page():
    """
    Apply all the modifications for doing job page executing Js.
    :return:
    """
    js_file = open("js/job-page.js").read()
    driver = get_driver()
    driver.execute_script(js_file)
    logger.debug("Page Modified.")

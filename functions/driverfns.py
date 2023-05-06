from typing import Union
from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException, WebDriverException, NoSuchWindowException

from devices.device import Edge
from constants import (MARKETING_TEST_URL,
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


def filter_mt():
    """
    Filter jobs for marketing test.
    :return: None
    """
    driver = get_driver()
    driver.open_url(MARKETING_TEST_URL, "_self")
    logger.debug("Filtered for Marketing test jobs")


def get_driver() -> Edge:
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
    driver = get_driver()
    driver.execute_script(open("js/job-page.js").read())
    logger.debug("Page Modified.")

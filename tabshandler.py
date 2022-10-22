from selenium.common import NoSuchWindowException

from functions.fns import get_file_logger, get_syslogger
from picoconstants import DOING_JOB_PAGE_INITIALS, MARKETING_TEST_URL
from functions.driverfns import get_driver, get_current_url, switch_to_any_tab
import logging
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/tabshandler.log", 'w+')
sys_logger = get_syslogger()


class TabsHandler:
    """
    Provide all the browser tab related functions and services across the programme.
    """

    """
    All the active tabs with urls: NOT CURRENTLY WORKING
    Use only one method to open and close tabs and update this dict inside those methods appropriately.
    """
    active_tabs = {"tab_id": "url"}

    @staticmethod
    def go_to_doing_job_tab():
        """
        Switch to the current proceeding job tab.
        :return:
        """
        driver = get_driver()
        if driver:
            try:
                if get_current_url(driver).startswith(DOING_JOB_PAGE_INITIALS):
                    driver.switch_to.window(driver.current_window_handle)
                    logger.info("Switched To: Doing Job Tab")
                    return True
            except AttributeError:
                pass

            # Try switching to a tab by tab
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if get_current_url(driver).startswith(DOING_JOB_PAGE_INITIALS):
                    logger.info("Switched To: Doing Job Tab")
                    return True
            logger.warning("Failed To Switch: Doing Job Tab")

    @staticmethod
    def go_to_jobs_tab():
        """
        Switch to the jobs tab.
        :return:
        """
        driver = get_driver()
        if driver:
            if get_current_url(driver) == MARKETING_TEST_URL:
                driver.switch_to.window(driver.current_window_handle)
                logger.info("Switched to: Jobs Tab")
                return True

            # Try switching to a tab by tab
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if get_current_url(driver) == MARKETING_TEST_URL:
                    logger.info("Switched To: Jobs Tab")
                    return True
            logger.warning("Failed To Switch: Jobs Tab")

    @staticmethod
    def switch_to_tab_by_url(url: str):
        """
        Switch to a tab by using an url.
        :param url:
        :return:
        """
        driver = get_driver()
        if driver:
            try:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    if get_current_url(driver) == url:
                        logger.info("Switched To: {}".format(url))
                        return True
                logger.debug("Failed To Switch: {}".format(url))
            except NoSuchWindowException:
                pass

    @staticmethod
    def switched_to_any_tab():
        """
        Switch to a random tab.
        This will prevent errors after closing active tab.
        :return:
        """
        switch_to_any_tab()

    @staticmethod
    def close_active_tab():
        """
        Closes the current active tab. Make sure you have switched to the desired tab before using.
        :return:
        """
        driver = get_driver()
        try:
            driver.execute_script('''window.close()''')
            switch_to_any_tab()
        except NoSuchWindowException:
            pass

    @staticmethod
    def close_junk_tabs():
        """
        Close all the tabs except ne
        :return:
        """
        driver = get_driver()
        closed = 0
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            current = get_current_url(driver)
            try:
                if current == MARKETING_TEST_URL:
                    continue
                elif current.startswith(DOING_JOB_PAGE_INITIALS):
                    continue
                else:
                    if len(driver.window_handles) == 2:
                        continue
                    driver.execute_script('''window.close()''')
                    closed += 1
            except (AttributeError, NoSuchWindowException):
                pass
        logger.info("Closed Junk Tabs: {}".format(closed))

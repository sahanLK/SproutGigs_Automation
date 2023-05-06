import logging
from selenium.webdriver.common.by import By
from livecontrols import LiveControls as Lc
from functions.fns import get_file_logger, get_syslogger
from functions.driverfns import get_driver, modify_doing_job_page
from jobshandler import JobsHandler
from tabshandler import TabsHandler
import pathlib

base_dir = pathlib.Path(__file__).parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/keyfunctions.log", 'w+')
sys_logger = get_syslogger()

jobs_handler = JobsHandler()
th = TabsHandler()


class KeyFunctions:

    @staticmethod
    def __get_submit_field():
        driver = get_driver()
        if driver and th.go_to_doing_job_tab():
            field = driver.find_element(By.ID, 'submission-data')
            if field:
                field.clear()
                return field
            else:
                logger.critical("Could not find common submit field")

    @staticmethod
    def select_textarea():
        driver = get_driver()
        if driver and th.go_to_doing_job_tab():
            try:
                driver.execute_script(open('js/change-textarea-no.js').read())
            except Exception as e:
                logger.warning("Error when changing textarea: {}".format(e))
        else:
            print("Field changed.")

    @staticmethod
    def clear_textarea(field_id: str = None):
        driver = get_driver()
        if driver and th.go_to_doing_job_tab():
            try:
                # If textarea id is given, find the field with the given id and clear it. Otherwise,
                # clear get the textarea number from the job page and clear it appropriately.
                driver.execute_script(open('js/clear-textarea.js').read(), field_id)
                logger.info("textarea cleared !")
            except Exception as e:
                logger.warning(f"Failed to clear the textarea: {e}")
        else:
            logger.warning("Driver not initialized.")

    @staticmethod
    def clear_already_submitted():
        """
        Clear the all submitted items.
        :return:
        """
        try:
            Ps.clear_already_submitted()
            sys_logger.debug("Submission data cache cleared")
        except Exception as e:
            sys_logger.error(f"Cache clearing failed: {e}")

    @staticmethod
    def stop_snapshot_process():
        Lc.stop_link_open = True

    @staticmethod
    def modify_page():
        try:
            th.go_to_doing_job_tab()
            modify_doing_job_page()
        except Exception as e:
            print("Page modify error: ", e)

    @staticmethod
    def submit_job():
        try:
            th.go_to_doing_job_tab()
            jobs_handler.submit_job()
        except Exception as e:
            logger.warning(f"Job submission failed: {e}")

    @staticmethod
    def skip_job():
        try:
            th.go_to_doing_job_tab()
            jobs_handler.select_a_job()
        except Exception as e:
            logger.warning(f"Job skipping failed: {e}")

    @staticmethod
    def hide_job():
        try:
            th.go_to_doing_job_tab()
            jobs_handler.hide_job()
        except Exception as e:
            logger.warning(f"Job hiding failed: {e}")
        finally:
            jobs_handler.select_a_job()

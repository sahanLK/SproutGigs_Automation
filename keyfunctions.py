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

    def submit_blog_link(self, field_id: str = None):
        val = Ps.get_blog_post_link()
        if val and th.go_to_doing_job_tab():
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Blog post link submitted.")
                else:
                    print("No driver")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_post_title(self, field_id: str = None):
        val = Ps.get_post_title()
        if val and th.go_to_doing_job_tab():
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Title submitted.")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_last_sentence(self, field_id: str = None):
        val = Ps.get_last_sentence()
        if val and th.go_to_doing_job_tab():
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Last sentence submitted.")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_last_word(self, field_id: str = None):
        val = Ps.get_last_word()
        print("Val is: ", val)
        if val and th.go_to_doing_job_tab():
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Last word submitted.")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_last_paragraph(self, field_id: str = None):
        val = Ps.get_last_para()
        if val and th.go_to_doing_job_tab():
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Last paragraph submitted.")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_ad_first(self, field_id: str = None):
        ad_first_url = Ps.get_ad_first_link()
        driver = get_driver()
        if driver and th.go_to_doing_job_tab() and ad_first_url:
            try:
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if ad_first_url:
                    field.send_keys(f"\n{ad_first_url}")
                    driver.find_element(By.TAG_NAME, 'body').click()
            except Exception as e:
                logger.warning(f"Could not submit: {e}")

    def submit_ad_inside(self, field_id: str = None):
        val = Ps.get_ad_inside_link()
        if val and th.go_to_doing_job_tab() and val:
            try:
                driver = get_driver()
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if field and driver:
                    field.send_keys(f"\n{val}")
                    driver.find_element(By.TAG_NAME, 'body').click()
                    print("Ad link submitted.")
            except Exception as e:
                logger.warning("submit failed: {}".format(e))

    def submit_ad_about(self, field_id: str = None):
        ad_about_url = Ps.get_ad_about_link()
        driver = get_driver()
        if driver and th.go_to_doing_job_tab() and ad_about_url:
            try:
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if ad_about_url:
                    field.send_keys(f"\n{ad_about_url}")
                    driver.find_element(By.TAG_NAME, 'body').click()
            except Exception as e:
                logger.warning(f"Could not submit: {e}")

    def submit_ad_contact(self, field_id: str = None):
        ad_contact = Ps.get_ad_contact_link()
        driver = get_driver()
        if driver and th.go_to_doing_job_tab():
            try:
                if field_id:
                    field = driver.find_element(By.ID, field_id)
                else:
                    field = self.__get_submit_field()
                if ad_contact:
                    field.send_keys(f"\n{ad_contact}")
                    driver.find_element(By.TAG_NAME, 'body').click()
            except Exception as e:
                logger.warning(f"Could not submit: {e}")

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

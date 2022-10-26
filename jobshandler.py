import re
import time
import logging
import settings
from datetime import datetime
from ai import BooleanCheck
from functions.fns import list_to_str, str_cleaner, get_file_logger, get_syslogger, get_ascii
from functions.driverfns import filter_mt, get_driver, modify_doing_job_page
from livecontrols import LiveControls
from picoconstants import DOING_JOB_PAGE_INITIALS, HIDE_JOB_CLSNAME
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from regexes import RE_HTTP_LINK, RE_NO_HTTP_LINK
from tabshandler import TabsHandler
from functions import easyjson
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException
from picoconstants import db_handler
from submitter import ProofsSubmitter
from widgetshandler import MainScreenWidgetsHandler
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/jobshandler.log", 'w+')
sys_logger = get_syslogger()


Ps = ProofsSubmitter()


class JobsHandler(TabsHandler):
    """
    Handler for all the job related tasks.
    """

    """
    The IDs of the jobs to use for building the job page url.
    """
    jobs_pool = iter

    def __init__(self):
        super(JobsHandler, self).__init__()
        self.driver = None
        self.actions = None
        self.current_job_id = None

    def update_jobs(self):
        """
        Updates the active job list.
        :return:
        """
        sys_logger.info("Updating jobs")
        self.driver = get_driver()
        job_ids = []
        skipped = 0
        filter_mt()
        if self.go_to_jobs_tab():
            soup = BeautifulSoup(str(self.driver.page_source), 'lxml')
            job_bars = soup.find_all('a', {"class": "job-bar"})
            for bar in job_bars:
                danger = bar.find('div', {"class": "bg-danger"})
                if not danger:
                    job_ids.append(bar['data-job-id'])
                    continue
                skipped += 1
        else:
            logger.error("Failed to update jobs")
        self.store_job_ids(job_ids)
        sys_logger.debug(f"Jobs Updated\t\t->\tStored: {len(job_ids)}\t\tSkipped: {skipped} jobs.")

    @classmethod
    def store_job_ids(cls, job_ids: list):
        cls.jobs_pool = iter(job_ids)

    def select_a_job(self):
        """
        Selects the job from the <jobs_pool> list, referring to the given index.
        :return: HTML source of the job page.
        """
        if not LiveControls.jobs_running:
            sys_logger.debug("Please click the run button in main screen before handling jobs.")
            return

        self.skip_job()
        sys_logger.info("Selecting a new job")
        try:
            self.current_job_id = self.jobs_pool.__next__()
            sys_logger.debug(f"Job ID: {self.current_job_id}")
        except (IndexError, StopIteration):
            self.update_jobs()
            return False
        except Exception as e:
            sys_logger.critical(f"Unexpected error while getting a Job ID: {e}")

        job_url = f'{DOING_JOB_PAGE_INITIALS}{self.current_job_id}'
        driver = get_driver()
        driver.open_url(job_url, target='_blank', force_chk_config=False)

        # If the current job has expired, select another job
        if not self.go_to_doing_job_tab():
            self.select_a_job()
            return False

        logger.info(f"\n\nJob selected: {job_url}")
        sys_logger.info(f"Job selected: {job_url}")

        job_page_source = self.__get_job_page_source()
        if job_page_source:
            modify_doing_job_page()
            if self.store_job_page_data(job_page_source):
                if BooleanCheck.code_submit_req():
                    if settings.CODE_SUBMIT_JOBS == 'hide':
                        self.hide_job()
                    self.select_a_job()
                    return False
                else:
                    self.open_req_urls()
                return True
            else:
                self.select_a_job()
                return False
        return False

    @staticmethod
    def open_req_urls():
        """
        Open the urls found in the job info section.
        :return:
        """
        sys_logger.debug("Opening urls in JI section")
        ji = db_handler.select_filtered('current_job_data', ['ji_section'], '', 1)
        links_http = {link.group(0) for link in RE_HTTP_LINK.finditer(str(ji))}
        sys_logger.debug(f"Found Http Links: {len(links_http)} from Ji_section")
        links_no_http = [f"https://{url.group(0).strip()}" for url in RE_NO_HTTP_LINK.finditer(str(ji))]
        sys_logger.debug(f"Found Non-Http Links: {len(links_no_http)} from Ji_section")
        if (len(links_http) >= 8) or (len(links_no_http) >= 8):
            sys_logger.debug("Too many urls found. Not opening anything.")
            return

        links_http.update(links_no_http)
        sys_logger.debug(f"Total links from ji_section: {len(links_http)}")
        for url in links_http:
            driver = get_driver()
            driver.open_url(url, target="_blank")

    def __get_job_page_source(self):
        try:
            self.go_to_doing_job_tab()
            driver = get_driver()
            if driver.current_url.startswith(DOING_JOB_PAGE_INITIALS):
                job_page_source = driver.page_source
                sys_logger.debug("Current job page source returned")
                return job_page_source
        except Exception as e:
            logger.error(f"Error when getting current job page source: {e}")
            sys_logger.error(f"Error when getting current job page source: {e}")

    def store_job_page_data(self, page_source):
        """
        Saving job page source and sections appropriately into a jason file.
        :param page_source:
        :return:
        """
        job_data_saver = _JobDataSaver(str(page_source))
        ji_section = job_data_saver.get_ji_section()
        ap_section = job_data_saver.get_ap_section()
        job_data_saver.store_submission_fields()

        try:
            db_handler.clear_tb('current_job_data')
            db_handler.add_record('current_job_data', ['self.current_job_id', ji_section, '', ap_section])
            logger.debug("Successfully stored current job page data.")
            sys_logger.debug("Successfully stored current job page data.")
            return True
        except Exception as e:
            logger.error(f'Storing job page data failed: {e}')
            sys_logger.error(f'Storing job page data failed: {e}')

    def skip_job(self):
        """
        Apply protocols when user needs to skip the current task.
        :return:
        """
        if not LiveControls.driver:
            return

        self.close_junk_tabs()
        self.go_to_doing_job_tab()
        self.close_active_tab()
        self.clear_active_job_data()
        Ps.clear_cache()
        LiveControls.set_default()

        self.clear_submission_widgets()

        wh = MainScreenWidgetsHandler()
        wh.clear_blog_url_field()  # Clear all url input field
        wh.but_miner_submit_set_default()
        wh.but_miner_submit_set_default()
        logger.info("Job skipped.")
        sys_logger.info("Job skipped\n\n")

    @staticmethod
    def clear_submission_widgets():
        LiveControls.submission_widgets.clear()  # clear the dict
        main_screen_wh = MainScreenWidgetsHandler()
        main_screen_wh.clear_submission_widgets()   # remove the widgets from scroll area

    def hide_job(self):
        """
        Hide the current active job, clicking the "Hide this job"
        link in the job page.
        :return:
        """
        if not LiveControls.driver:
            return

        self.go_to_doing_job_tab()
        try:
            self.driver = LiveControls.driver
            hide_link = self.driver.find_element(By.CLASS_NAME, HIDE_JOB_CLSNAME)
            self.actions = ActionChains(self.driver)
            self.actions.move_to_element(hide_link).perform()
            hide_link.click()
            time.sleep(1)

            self.close_active_tab()
            self.close_junk_tabs()
            self.clear_active_job_data()
            self.clear_submission_widgets()
            logger.info('Job Hiding Successful.')
            sys_logger.info('Job Hiding Successful.')
        except (NoSuchElementException,
                ElementClickInterceptedException,
                NoSuchWindowException):
            logger.warning("Job hiding failed.")
            pass

    def submit_job(self):
        """
        Clicks the submit button.
        WARNING: Should only use after filling all the proofs successfully.
        :return:
        """
        if self.go_to_doing_job_tab():
            driver = get_driver()
            try:
                driver.execute_script(open('js/click-submit-button.js').read())
                sys_logger.error(f"Job submitted")
            except Exception as e:
                sys_logger.error(f"Job submission failed: {e}")

            # Try to update the database for calculating the earni1ng.
            today = str(datetime.now()).split()[0]
            record = db_handler.select_filtered('earnings', ['date', 'tasks', 'usd'], f'date="{today}"')
            if record:
                # This is not the first job submitting today.
                # This should be a database record update. But because of an update method error in
                # the ezmysqlpy module, this is done by deleting the existing record as an alternative.
                db_handler.delete_records('earnings', f'date="{today}"')
                tasks, usd = int(record[0][1]) + 1, float(record[0][2]) + 0.03
                db_handler.add_record('earnings', [today, tasks, usd])
            else:
                db_handler.add_record('earnings', [today, 1, 0.03])

    @staticmethod
    def clear_active_job_data():
        db_handler.clear_tb('current_job_data')
        db_handler.clear_tb('current_blog_and_ad_data')


class _JobDataSaver:
    def __init__(self, job_html: str):
        super(_JobDataSaver, self).__init__()
        self.html = self.__get_no_br_html(get_ascii(job_html))

    @staticmethod
    def __get_no_br_html(html: str):
        """
        Replace all the <br> tags from the whole html page. This is done to prevent
        matching wrong urls form the Ji_section. If this method did not use before
        storing data into table[current_job_data], wrong and invalid urls will be opened
        by [JobsHandler.open_req_urls()]
        :param html:
        :return:
        """
        try:
            rm_br = re.sub(r"<br>|</br>|<br/>", " ", html)
            return rm_br
        except Exception as e:
            sys_logger.error(f"Error when removing <br> from source: {e}")

    def get_ji_section(self):
        """
        Stores Job Info Section into the json file.
        :return:
        """
        soup = BeautifulSoup(self.html, 'lxml')
        steps = [str_cleaner(step.text) for step in soup.find('div', {"id": "job-instructions"}).find_all('li')]
        if not steps:
            logger.warning("Job Info could not be determined.")
        merged = list_to_str(steps)
        return merged

    def get_ap_section(self):
        soup = BeautifulSoup(self.html, 'lxml')
        steps = [str_cleaner(BeautifulSoup(str(group.label), 'lxml').text)
                 for group in soup.find(
                'form', {"id": "task-proofs"}).find(
                'div', {"class": "job-info-list"}).find_all(
                "div", {'class': 'form-group'}) if group.label]
        if not steps:
            logger.warning("Actual Proofs could not be determined.")
        cleaned_steps = [self.get_clean_step(step) for step in steps]
        merged = list_to_str(cleaned_steps)
        return merged

    @staticmethod
    def get_clean_step(step: str) -> str:
        """
        Clean the step given by removing initial number, dot and other spaces that exists at the
        beginning and the end of the step. This method is used to provide much cleaner text for the
        Ai module and database storage.
        :return:
        """
        cleaned = re.sub(r'^\d\.\s', '', step)
        cleaned = re.sub(r'\|', ' ', cleaned)
        return cleaned.strip('\n :>')

    def store_submission_fields(self):
        """
        Save submission fields ids along with their type [file|text] to a json file.
        :return:
        """
        soup = BeautifulSoup(self.html, 'lxml')
        form_groups = soup.find('form', {"id": "task-proofs"}).find_all('div', {"class": "form-group"})
        form_groups.pop()

        all_proofs = []
        for group in form_groups:
            textarea = group.textarea
            input_tag = group.input

            file_submit = None
            if input_tag:
                # Check if the value of 'type' attribute is equal to 'file'
                bs4 = BeautifulSoup(str(input_tag), 'lxml')
                found = bs4.find('input', type='file')
                file_submit = True if found else None

            proof_type = elem_id = None
            if textarea and file_submit:
                # If both inputs available, then it is probably a file submission. <textarea> is optional.
                proof_type = 'file'
                elem_id = input_tag['id']
            if textarea and not file_submit:
                proof_type = 'text'
                elem_id = textarea['id']

            proof = {"type": proof_type, "textarea_id": elem_id}
            all_proofs.append(proof)

        # Save submission field type(text/file) and the ID of the submission field to use later.
        easyjson.into_json('proofs_submission_fields', all_proofs, 'json/proofs-fields.json')

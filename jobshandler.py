import re
import time
import logging
from datetime import datetime
from functions.fns import (
    str_cleaner,
    get_file_logger,
    get_syslogger,
    get_ascii)
from functions.driverfns import filter_mt, get_driver, modify_doing_job_page
from livecontrols import LiveControls
from constants import (
    DOING_JOB_PAGE_INITIALS,
    HIDE_JOB_CLSNAME,
    JOB_TITLE_CLASS,
    JOB_PAYMENT_CLASS)
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from regexes import RE_HTTP_LINK, RE_NO_HTTP_LINK, RE_CODE_SUBMIT
from tabshandler import TabsHandler
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException)
from widgetshandler import MainScreenWidgetsHandler
from pathlib import Path
from database import (
    get_session,
    InstructionItem,
    SubmissionItem,
    Job,
    Earnings)
from sqlalchemy.exc import IntegrityError, PendingRollbackError

base_dir = Path(__file__).parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/jobshandler.log", 'w+')
sys_logger = get_syslogger()

session = get_session()


class JobsHandler:
    """
    Handler for all the job related tasks.
    """

    """
    The IDs of the jobs to use for building the job page url.
    """
    job_ids = set()

    """
    The <Job> object of the currently ongoing job.
    This object is stored after saving the job page data.
    """
    current_job_obj = None

    def __init__(self):
        super(JobsHandler, self).__init__()
        self.driver = None
        self.actions = None
        self.current_job_id = None
        self.current_job_payment = None
        self.page_source = None  # Cleaned job page source

    @staticmethod
    def update_jobs():
        """
        Updates the active job list.
        :return:
        """
        sys_logger.info("Updating jobs")
        skipped = 0
        TabsHandler.switched_to_any_tab()
        filter_mt()
        JobsHandler.clear_job_ids()
        if TabsHandler.go_to_jobs_tab():
            soup = BeautifulSoup(
                str(TabsHandler.get_jobs_page_source()), 'lxml')
            job_bars = soup.find_all('a', {"class": "job-bar"})
            for bar in job_bars:
                danger = bar.find('div', {"class": "bg-danger"})
                if not danger:
                    JobsHandler.add_job_id(bar['data-job-id'])
                    continue
                skipped += 1
        else:
            logger.error("Failed to update jobs")
        sys_logger.debug(
            f"Stored: {len(JobsHandler.job_ids)}\t\tSkipped: {skipped} jobs.")

    @classmethod
    def add_job_id(cls, job_id):
        if job_id:
            cls.job_ids.add(job_id)

    @classmethod
    def clear_job_ids(cls):
        cls.job_ids.clear()

    @classmethod
    def get_first_job_id(cls):
        u = list(cls.job_ids)[0]
        return u

    @classmethod
    def get_all_job_ids(cls):
        return cls.job_ids

    @classmethod
    def remove_job_id(cls, job_id):
        try:
            cls.job_ids.remove(job_id)
        except KeyError:
            pass

    def select_a_job(self):
        """
        Selects the job from the <jobs_pool> list, referring to the given index.
        :return: HTML source of the job page.
        """
        from screens.mainscreen import MainScreen
        if not MainScreen.running:
            return

        self.skip_job()
        sys_logger.info("Selecting a new job")
        try:
            self.current_job_id = JobsHandler.get_first_job_id()
            self.remove_job_id(self.current_job_id)
            if not self.current_job_id:
                self.update_jobs()
            sys_logger.debug(f"Job ID: {self.current_job_id}")
        except (IndexError, StopIteration):
            self.update_jobs()
            return False
        except Exception as e:
            sys_logger.critical(f"Unexpected error while getting a Job ID: {e}")

        job_url = get_job_url(self.current_job_id)
        driver = get_driver()
        driver.open_url(job_url, target='_blank', force_chk_config=False)

        # If the current job has expired, select another job
        if not TabsHandler.go_to_doing_job_tab():
            self.select_a_job()
            return False

        logger.info(f"\n\nJob selected: {job_url}")

        # Setting up the current job page source after cleaning properly
        # This should be properly cleaned because, this will be accessed all over this class.
        self.page_source = get_job_page_source()

        if self.page_source:
            # Check for code submission and file submission settings
            from screens.mainscreen import MainScreen

            modify_doing_job_page()
            if self.store_job_page_data():
                # Check for code submission settings
                if MainScreen.skip_code_submit:
                    if self.code_submit_req:
                        self.select_a_job()
                        return False

                # Check for file submission settings
                if MainScreen.skip_file_submit:
                    if self.file_submit_req:
                        self.select_a_job()
                        return False

                self.open_req_urls(self.page_source)
                return True     # Job selected
            else:
                self.select_a_job()
                return False
        return False

    @staticmethod
    def open_req_urls(page_source):
        """
        Open the urls found in the job info section.
        :return:
        """
        sys_logger.debug("Opening urls in JI section")
        soup = BeautifulSoup(page_source, 'lxml')
        steps = [step.text for step in
                 soup.find('div', {"id": "job-instructions"}).find_all('li')]

        ji_str = ""
        for i in steps:
            ji_str += f"{i} "

        links_http = {link.group(0) for link in RE_HTTP_LINK.finditer(ji_str)}
        # sys_logger.debug(f"Found Http Links: {len(links_http)} from Ji_section")
        links_no_http = [f"https://{url.group(0).strip()}" for url in RE_NO_HTTP_LINK.finditer(ji_str)]
        # sys_logger.debug(f"Found Non-Http Links: {len(links_no_http)} from Ji_section")
        if (len(links_http) >= 8) or (len(links_no_http) >= 8):
            sys_logger.debug("Too many urls found. Not opening anything.")
            return True

        links_http.update(links_no_http)
        sys_logger.debug(f"Total links from ji_section: {len(links_http)}")
        for url in links_http:
            driver = get_driver()
            driver.open_url(url, target="_blank")

    def store_job_page_data(self):
        """
        Saving job page source and sections appropriately into a jason file.
        """
        ji_section = get_ji_section(self.page_source)
        ap_section = get_ap_section(self.page_source)

        job = Job(
            job_id=self.current_job_id,
            title=job_title(self.page_source))
        session.add(job)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

            # Delete the overlapping old job and add new one
            prev = session.query(Job).filter(
                Job.job_id.__eq__(self.current_job_id)).first()
            session.delete(prev)
            session.commit()
            session.add(job)
            session.commit()

        for i in ji_section:
            # <InstructionItem> text is unique and one item can be owned by
            # multiple jobs. So before adding these items, check if already
            # exists with same text, to avoid getting DuplicateEntry errors
            ins_item = session.query(InstructionItem).filter(
                InstructionItem.text == i).first()

            if not ins_item:
                ins_item = InstructionItem(job_id=job.id, text=i)
            job.instruction_items.append(ins_item)
        session.commit()

        # One submission item can only be owned by one Job.
        for i in ap_section:
            job.submission_items.append(
                SubmissionItem(job_id=job.id, text=ap_section[i], field_id=i))
        session.commit()

        self.set_current_job_obj(job)
        self.current_job_payment = get_payment(self.page_source)
        print("Successfully stored current job page data.")
        return True

    @classmethod
    def set_current_job_obj(cls, job):
        cls.current_job_obj = job
        print("New Job Set: ", job)

    def skip_job(self):
        """
        Apply protocols when user needs to skip the current task.
        :return:
        """
        if not LiveControls.driver:
            return

        # try to close the job update window, if opened
        try:
            from screens.mainscreen import MainScreen
            MainScreen.job_update_dialog.close()
        except:
            pass

        # If the current job is skipping without any choices
        # for the submission fields, that means the job is skipping
        # without submitting. Those jobs should be deleted because,
        # sometimes when running the programme again, the same job
        # will try to save the job into database. And that will generate
        # errors because job_id is unique. To prevent this, when skipping a job,
        # if it doesn't have any choices, delete it
        choices_ok = True
        if JobsHandler.current_job_obj:
            try:
                for sub in JobsHandler.current_job_obj.submission_items:
                    # Even if one submission field does not have choices, do not select
                    if not len(sub.choices) > 0:
                        choices_ok = False
                        break
            except PendingRollbackError:
                session.rollback()

            if not choices_ok:
                session.delete(self.current_job_obj)
                session.commit()

        self.page_source = None
        self.set_current_job_obj(None)
        self.current_job_id = None
        self.current_job_payment = None

        TabsHandler.close_junk()
        TabsHandler.close_doing_job_tab()
        LiveControls.set_default()

        wh = MainScreenWidgetsHandler()
        wh.clear_blog_url_field()  # Clear all url input field
        wh.but_go()
        logger.info("Job skipped.")
        sys_logger.info("Job skipped\n\n")

    def submit_job(self):
        """
        Clicks the submit button.
        WARNING: Should only use after filling all the proofs successfully.
        """
        if TabsHandler.go_to_doing_job_tab():
            driver = get_driver()
            try:
                driver.execute_script(open('js/click-submit-button.js').read())
                sys_logger.error(f"Job submitted")
            except Exception as e:
                sys_logger.error(f"Job submission failed: {e}")
            update_daily_earnings(get_payment(self.page_source))

    def hide_job(self):
        """
        Hide the current active job, clicking the "Hide this job"
        link in the job page.
        :return:
        """
        if not LiveControls.driver:
            return

        TabsHandler.go_to_doing_job_tab()
        try:
            driver = get_driver()
            hide_link = driver.find_element(By.CLASS_NAME, HIDE_JOB_CLSNAME)
            self.actions = ActionChains(driver)
            self.actions.move_to_element(hide_link).perform()
            hide_link.click()
            time.sleep(1)

            TabsHandler.close_active_tab()
            TabsHandler.close_junk()
            logger.info('Job Hiding Successful.')
            sys_logger.info('Job Hiding Successful.')
        except (NoSuchElementException,
                ElementClickInterceptedException,
                NoSuchWindowException):
            logger.warning("Job hiding failed.")
            pass

    @property
    def code_submit_req(self):
        """
        Check for code submission
        :return:
        """
        ap_section = get_ap_section(self.page_source)
        for label in get_ap_section(self.page_source):
            match = [match for match in RE_CODE_SUBMIT.finditer(ap_section[label])]
            if match:
                sys_logger.debug(f"Code submission detected")
                return True
            else:
                print(f"\n\n==== Code Submission not required for ===\n{ap_section[label]}")
        return False

    @property
    def file_submit_req(self):
        for sub_item in self.current_job_obj.submission_items:
            if str(sub_item.field_id).startswith('file'):
                return True


def update_daily_earnings(payment):
    # Try to update the database for calculating the daily earning.
    today = str(datetime.now()).split()[0]
    record = session.query(Earnings).filter(Earnings.date.__eq__(today)).first()
    if record:
        record.tasks = record.tasks + 1
        record.usd = record.usd + payment
        session.commit()
    else:
        # First job submission today
        session.add(
            Earnings(date=today, tasks=1, usd=payment))


"""
FUNCTIONS
"""


def get_ap_section(page_source) -> dict:
    soup = BeautifulSoup(page_source, 'lxml')
    steps = {group.label['for']: get_clean_step(str_cleaner(
        BeautifulSoup(str(group.label), 'lxml').text))
        for group in soup.find(
            'form', {"id": "task-proofs"}).find(
            'div', {"class": "job-info-list"}).find_all(
            "div", {'class': 'form-group'}) if group.label}

    if not steps:
        logger.warning("Actual Proofs could not be determined.")
    return steps


def get_ji_section(page_source) -> list:
    soup = BeautifulSoup(page_source, 'lxml')
    steps = [str_cleaner(step.text) for step in
             soup.find('div', {"id": "job-instructions"}).find_all('li')]
    if not steps:
        logger.warning("Job Info could not be determined.")
    return steps


def job_title(page_source) -> str:
    soup = BeautifulSoup(page_source, 'lxml')
    title = soup.select_one(f".{JOB_TITLE_CLASS}").text
    return str_cleaner(title)


def get_payment(page_source) -> float:
    soup = BeautifulSoup(page_source, 'lxml')
    price = soup.find('div', {'class': JOB_PAYMENT_CLASS}).find('span').text
    return float(price)


def get_job_page_source():
    try:
        TabsHandler.go_to_doing_job_tab()
        driver = get_driver()
        if driver.current_url.startswith(DOING_JOB_PAGE_INITIALS):
            source = driver.page_source

            try:
                """
                Replace all the <br> tags from the whole html page. This is done to prevent
                matching wrong urls form the Ji_section. If this method did not use before
                storing data into table[current_job_data], wrong and invalid urls will be opened
                by [JobsHandler.open_req_urls()]
                :param html:
                :return:
                """
                rm_br = re.sub(r"<br>|</br>|<br/>", " ", get_ascii(source))
                sys_logger.debug("Current job page source returned")
                return rm_br
            except Exception as e:
                sys_logger.error(f"Error when removing <br> from source: {e}")

    except Exception as e:
        logger.error(f"Error when getting current job page source: {e}")
        sys_logger.error(f"Error when getting current job page source: {e}")


def get_job_url(job_id) -> str:
    """
    Give me the job id and I will give you the url of the job
    """
    return f'{DOING_JOB_PAGE_INITIALS}{job_id}'


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

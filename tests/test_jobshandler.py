import unittest
from jobshandler import _JobDataSaver as Jds, JobsHandler
from selenium import webdriver
from functions.fns import db_handler

jobs_handler = JobsHandler()
driver = webdriver.Edge()
driver.get('http://localhost/picotest/test.html')


class TestJobsHandler(unittest.TestCase):

    def test_store_job_page_data(self):
        db_handler.clear_tb('current_job_data')
        self.page_source = driver.page_source
        self.assertTrue(jobs_handler.store_job_page_data(self.page_source))

    def test_get_clean_step(self):
        self.assertEqual(
            Jds.get_clean_step('3. Follow the step 4 to submit proof 3:'), 'Follow the step 4 to submit proof 3')
        self.assertEqual(
            Jds.get_clean_step('3. Submit Website Name'), 'Submit Website Name')
        self.assertEqual(
            Jds.get_clean_step('3. 1 Submit Website Name'), '1 Submit Website Name')
        self.assertEqual(
            Jds.get_clean_step('1 Submit Website Name'), '1 Submit Website Name')
        self.assertEqual(
            Jds.get_clean_step('.1 Submit Website Name'), '.1 Submit Website Name')
        self.assertEqual(
            Jds.get_clean_step('.1 Submit Website Name|something'), '.1 Submit Website Name something')
        self.assertEqual(
            Jds.get_clean_step('.1 Submit | Website Name|something'), '.1 Submit   Website Name something')

    def test_open_req_urls(self):
        jobs_handler.open_req_urls()


if __name__ == "__main__":
    unittest.main()

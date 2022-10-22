import unittest
from submitter import ProofsSubmitter
from selenium.webdriver import Edge
from picoconstants import db_handler
from jobshandler import JobsHandler

submitter = ProofsSubmitter(test_mode=True)
jobs_handler = JobsHandler()
jobs_handler.current_job_id = 'testing_id'

driver = Edge()
driver.get('http://localhost/test.html')

# Store job page data
page_source = driver.page_source
db_handler.clear_tb('current_job_data')
jobs_handler.store_job_page_data(page_source)


class TestSubmitter(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSubmitter, self).__init__(*args, **kwargs)
        self.current_job_id = '1'

    # @classmethod
    # def setUpClass(cls) -> None:
    #     db_handler.clear_tb('current_blog_and_ad_data')
    #     blog_links = 'blog_link_1|blog_link_2|blog_link_3|blog_link_3|blog_link_4|blog_link_5|blog_link_6|blog_link_7|'
    #     titles = 'title_1|title_2|title_3|title_4|'
    #     last_sentences = 'last_sentence_1|last_sentence_2|last_sentence_3|last_sentence_4|'
    #     last_words = 'last_word_1|last_word_2|last_word_3|last_word_4|'
    #     ad_first = 'First advertisement url'
    #     ad_contact = 'Ad contact url'
    #     ad_about = 'Ad about url'
    #     ad_links = 'ad_link1_1|ad_link_2|ad_link_3|ad_link_4|ad_link_5|ad_link_6|ad_link_7|'
    #     db_handler.add_record(
    #         'current_blog_and_ad_data',
    #         [blog_links, titles, last_sentences, last_words, ad_first, ad_contact, ad_about, ad_links])

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_submit_proofs(self):
        submitter.submit_proofs(driver)
        input()


if __name__ == "__main__":
    unittest.main()

import threadingimport loggingfrom ai import Ai, BooleanCheckfrom functions.driverfns import snap_history, get_driverfrom functions.fns import str_to_list, get_from_db, get_file_logger, get_sysloggerfrom selenium.webdriver.common.by import Byfrom functions import easyjsonfrom livecontrols import LiveControlsfrom picoconstants import db_handlerfrom tabshandler import TabsHandlerimport settingsfrom pathlib import Pathfrom widgetshandler import MainScreenWidgetsHandlerbase_dir = Path(__file__).parent.absolute()logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/submitter.log", 'w+')sys_logger = get_syslogger()class ProofsSubmitter(TabsHandler):    """    All the urls and other items submitted to the front end.    Can be used to avoid submitting same proof twice.    """    all_submitted_items = []    """    To stop opening blog and ad links for history page screenshot.    """    _stop_link_open = False    """    No. of blog post urls opened for history screenshot.    """    _blog_links_found = 0    """    No. of ad site urls opened for history screenshot.    """    _ad_links_found = 0    """    Cache the common submission data to submit efficiently.    """    _cache_blog_posts = []    _cache_titles = []    _cache_paragraphs = []    _cache_sentences = []    _cache_last_words = []    _cache_ad_first = None    _cache_ad_about = None    _cache_ad_contact = None    _cache_ad_inside = []    """    No. of submissions that has skipped    """    skipped_submissions = 0    def __init__(self, test_mode: bool = False, **kwargs):        """        :param test_mode: If True, the class will behave in a different way at some methods, for fulfilling        the requirements of the tests.        :param kwargs:        """        super(ProofsSubmitter, self).__init__(**kwargs)        self.test_mode = test_mode    @classmethod    def set_cls_default(cls):        """        Set all the class variables back to their default values.        These class variables may have changed from somewhere in another code.        :return:        """        cls.all_submitted_items = []        cls._stop_link_open = False        cls._blog_links_found = 0        cls._ad_links_found = 0        cls.clear_cache()        cls.skipped_submissions = 0    @classmethod    def clear_cache(cls):        cls._cache_blog_posts = []        cls._cache_titles = []        cls._cache_paragraphs = []        cls._cache_sentences = []        cls._cache_last_words = []        cls._cache_ad_first = None        cls._cache_ad_about = None        cls._cache_ad_contact = None        cls._cache_ad_inside = []    @classmethod    def clear_already_submitted(cls):        """        Use this when the submission data has reached the end.        This list is used to prevent the submission of same proof again and again.        :return:        """        cls.all_submitted_items.clear()    def submit_proofs(self, driver):        """        Take items from AP section one by one and run separate checks. If one check becomes <True>,        stops further checking for that submission and moves to next submission.        :type driver: Current active webdriver.        :return:        """        self.set_cls_default()        ap_section = db_handler.select_filtered('current_job_data', ['ap_section'])        try:            ap_section = str_to_list(ap_section[0][0])        except IndexError:            logger.error("Actual proofs section empty. Submission prohibited.")            return        proofs_fields = easyjson.from_json('proofs_submission_fields', 'json/proofs-fields.json')        # Start the submission.        for proof in ap_section:            # if the ap section contains same step more than one time, below lines will generate wrong outputs.            step_id = ap_section.index(proof) + 1            proof_type = proofs_fields[step_id - 1]['type']            proof_field_id = proofs_fields[step_id - 1]['textarea_id']            # If proof require a file submission, do not go ahead.            if proof_type != 'text':                proof_index = str(ap_section.index(proof)+1)                print("\n\nProof {}: {}".format(proof_index, proof))                print(f'File submission. Skipped.')                continue            LiveControls.submission_widgets[proof_field_id] = proof     # update the dict            MainScreenWidgetsHandler().update_submission_widgets()  # Emit the update signal            ai = Ai(proof).get_decision()            decision = ai.decision_code            print("\n\nProof {}: {}".format(ap_section.index(proof)+1, proof))            print("Decision: {}".format(decision))            value = ''            if decision == 0:                self.skipped_submissions += 1                print(f'PROOF: {step_id} -> I cannot submit.')            elif decision == 1:                print("No of posts req: ", ai.no_of_posts_req)                for _ in range(ai.no_of_posts_req):                    link = self.get_blog_post_link() if not self.test_mode else 'blog_link'                    value += f"{link}\n" if link else ''            elif decision == 2:                print("No of titles req: ", ai.no_of_titles_req)                for _ in range(ai.no_of_titles_req):                    title = self.get_post_title() if not self.test_mode else 'post_title'                    value += f"{title}\n" if title else ''            elif decision == 3:                print("No of words req: ", ai.no_of_words_req)                for _ in range(ai.no_of_words_req):                    word = self.get_last_word() if not self.test_mode else 'last_word'                    value += f"{word}\n" if word else ''            elif decision == 4:                print("No of sentences req: ", ai.no_of_sentences_req)                for _ in range(ai.no_of_sentences_req):                    sentence = self.get_last_sentence() if not self.test_mode else 'last_sentence'                    value += f"{sentence}\n" if sentence else ''            elif decision == 5:                para = self.get_last_para() if not self.test_mode else 'last_paragraph'                value = f"{para}\n" if para else ''            elif decision == 6:                value = self.get_ad_first_link() if not self.test_mode else 'ad_first_link'            elif decision == 7:                print("No of ad links req: ", ai.no_of_ad_links_req)                for _ in range(ai.no_of_ad_links_req):                    link = self.get_ad_inside_link() if not self.test_mode else 'ad_inside_link'                    value += f"{link}\n" if link else ''            elif decision == 8:                value = self.get_ad_about_link() if not self.test_mode else 'ad_about_url'            elif decision == 9:                value = self.get_ad_contact_link() if not self.test_mode else 'ad_contact_url'            else:                logger.warning('Invalid decision code generated by Ai: {}'.format(decision))            # Fill the proof into the correct submission field.            self.__fill_the_box(driver, step_id, value, proof_field_id)        if BooleanCheck.history_snapshot_req() and settings.AUTO_PICK_SNAPSHOT:            print("History page snapshot required.")            t = threading.Thread(target=snap_history)            t.start()    @classmethod    def get_blog_post_link(cls):        if not cls._cache_blog_posts:            cls._cache_blog_posts = get_from_db('blog_links', get_all=True)        if cls._cache_blog_posts:            for link in cls._cache_blog_posts:                if link not in cls.all_submitted_items:                    cls.all_submitted_items.append(link)                    return link        cls.nothing_to_submit()    @classmethod    def get_post_title(cls):        if not cls._cache_titles:            cls._cache_titles = get_from_db('titles', get_all=True)        if cls._cache_titles:            for title in cls._cache_titles:                if title not in cls.all_submitted_items:                    cls.all_submitted_items.append(title)                    return title        cls.nothing_to_submit()    @classmethod    def get_last_para(cls):        if not cls._cache_paragraphs:            cls._cache_paragraphs = get_from_db('last_paragraphs', get_all=True)        if cls._cache_paragraphs:            for paragraph in cls._cache_paragraphs:                if paragraph not in cls.all_submitted_items:                    cls.all_submitted_items.append(paragraph)                    return paragraph        cls.nothing_to_submit()    @classmethod    def get_last_word(cls):        if not cls._cache_last_words:            cls._cache_last_words = get_from_db('last_words', get_all=True)        if cls._cache_last_words:            for sentence in cls._cache_last_words:                if sentence not in cls.all_submitted_items:                    cls.all_submitted_items.append(sentence)                    return sentence        cls.nothing_to_submit()    @classmethod    def get_last_sentence(cls):        if not cls._cache_sentences:            cls._cache_sentences = get_from_db('last_sentences', get_all=True)        if cls._cache_sentences:            for sentence in cls._cache_sentences:                if sentence not in cls.all_submitted_items:                    cls.all_submitted_items.append(sentence)                    return sentence        cls.nothing_to_submit()    @classmethod    def get_ad_first_link(cls):        url = get_from_db('ad_first_opened')        if url:            return url        cls.nothing_to_submit()    @classmethod    def get_ad_about_link(cls):        url = get_from_db('ad_about_url')        if url:            return url        cls.nothing_to_submit()    @classmethod    def get_ad_contact_link(cls):        url = get_from_db('ad_contact_url')        if url:            return url        cls.nothing_to_submit()    @classmethod    def get_ad_inside_link(cls):        if not cls._cache_ad_inside:            cls._cache_ad_inside = get_from_db('ad_links', get_all=True)        if cls._cache_ad_inside:            for link in cls._cache_ad_inside:                if link not in cls.all_submitted_items:                    cls.all_submitted_items.append(link)                    return link        cls.nothing_to_submit()    def __fill_the_box(self, driver, step_id, value, proof_field_id):        if not value:            print(f"PROOF: {step_id} -> Nothing found from DB.")            return        if self.go_to_doing_job_tab():            proof_field = driver.find_element(By.ID, proof_field_id)            proof_field.send_keys(value)            val = value.replace('\n', '')            print(f"PROOF: {step_id} -> Submitted {val}")    @staticmethod    def nothing_to_submit():        """        Just used to give a hint to user, when they try to submit something and        that does not exist or already cached/submitted all items.        :return:        """        try:            get_driver().execute_script(open('js/nothing-to-submit.js').read(), "No more Blog post links")        except Exception as e:            logger.info(f"Failed to inform that nothing to submit: {e}")
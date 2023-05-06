"""
Analyze single step of the job page and provides a much better and accurate solutions or decisions.
"""
import logging
import re
from functions.fns import get_file_logger, get_syslogger
from regexes import (RE_HTTP_LINK, RE_NO_HTTP_LINK, RE_ABOUT_URL,
                     RE_CONTACT_URL, RE_AD_LINK, RE_AD_LINK_2, RE_BLOG_POST_LINK, RE_TITLE,
                     RE_LAST_SENTENCE, RE_LAST_WORD, RE_SNAPSHOT, RE_CODE_SUBMIT,
                     RE_LAST_PARAGRAPH, RE_AD_STEP_NO, RE_AD_SNAPSHOT_SITES, RE_NO_OF_POSTS, RE_NO_OF_AD_LINKS,
                     RE_NO_OF_TITLES, RE_SINGLE_NUMBER, RE_LAST__NO_OF_URL, RE_STEP_MATCH)
from pathlib import Path

base_dir = Path(__file__).parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/ai.log", 'w+')
sys_logger = get_syslogger()


RE_BLOG_POST_ILLEGALS = re.compile(r'\b(words?|senten[cs]es?|paragraphs?|codes?|titles?|step|'
                                   r'pastebin|yahoo|bing|google\s\d)\b', flags=re.I)
AD_INSIDE_ILLEGALS = re.compile(r'(sentences?|about us|contact us)', flags=re.I)


class BooleanCheck:

    @staticmethod
    def titles_req(ap_section):
        """
        Determine if the submission requires the post titles
        :return:
        """
        for label in ap_section:
            match = [match for match in RE_TITLE.finditer(label)]
            if match:
                return True
        return False

    @staticmethod
    def post_data_req(ap_section):
        """
        Determine if the submission requires some kind of post data such as
        last paragraphs, sentences or words.
        :return:
        """
        for label in ap_section:
            para_match = [match for match in RE_LAST_PARAGRAPH.finditer(label)]
            if para_match:
                return True
            sentence_match = [match for match in RE_LAST_SENTENCE.finditer(label)]
            if sentence_match:
                return True
            word_match = [match for match in RE_LAST_WORD.finditer(label)]
            if word_match:
                return True
        return False


class Ai:
    """
    Get the best decision.
    """

    class _Decision:
        """
        Decisions and important details found within the text.
        """

        def __init__(self, decision_code: int,
                     fault_decisions: list = None,
                     no_of_posts_req: int = 0,
                     no_of_titles_req: int = 0,
                     no_of_sentences_req: int = 0,
                     no_of_words_req: int = 0,
                     no_of_ad_links_req: int = 0):

            self.decision_code = decision_code
            self.fault_decisions = fault_decisions
            self.no_of_posts_req = no_of_posts_req
            self.no_of_titles_req = no_of_titles_req
            self.no_of_sentences_req = no_of_sentences_req
            self.no_of_words_req = no_of_words_req
            self.no_of_ad_links_req = no_of_ad_links_req

    def __init__(self, txt: str, test_mode: bool = False):
        """
        Decision codes with their meaning.
        0: None
        1: "BLOG_POST"
        2: "POST_TITLE"
        3: "LAST_WORD"
        4: "LAST_SENTENCE"
        5: "LAST_PARAGRAPH"
        6: "AD_FIRST"
        7: "AD_LINK"
        8: "AD_ABOUT"
        9: "AD_CONTACT
        """

        self.txt = txt.strip(' ')
        logger.info(f"AI procedure for: {' '*3}[ {self.txt} ]")

        self.words = self.txt.split()   # Words in the text given
        self.decisions = []             # All the decisions taken
        self.no_of_posts_req = 0
        self.no_of_titles_req = 0
        self.no_of_words_req = 0
        self.no_of_sentences_req = 0
        self.no_of_paragraphs_req = 0
        self.no_of_ad_links_req = 0
        self.test_mode = test_mode      # For unit testing
        if self.test_mode:
            logger.info("Running in test mode")

    def decision(self) -> _Decision:
        """
        Returns the decision as an object(_Decision).
        :return:
        """
        self.__solve()

        # If only one decision is available, it means probably the correct decision is taken.
        if len(self.decisions) == 1:
            decision_code = self.decisions[0]
            fault_decisions = []
            logger.debug(f"Decision taken: {decision_code}")
        else:
            decision_code = 0
            fault_decisions = self.decisions
            logger.debug(f"Faulty or Empty decision taken: {self.decisions[0::]}")
        logger.info("Ended\n\n")
        return self._Decision(decision_code=decision_code,
                              fault_decisions=fault_decisions,
                              no_of_posts_req=self.no_of_posts_req,
                              no_of_titles_req=self.no_of_titles_req,
                              no_of_words_req=self.no_of_words_req,
                              no_of_sentences_req=self.no_of_sentences_req,
                              no_of_ad_links_req=self.no_of_ad_links_req)

    def clear(self):
        """
        Clear some existing data.
        :return:
        """
        self.decisions.clear()
        self.words.clear()

    def __solve(self):
        """
        Analyze the text with regexes and returns the solution.
        :return:
        """
        self.clear()
        # First check the database for predefined solution.
        # if not self.test_mode:
        #     decision = db_handler.select_filtered('ai_success', ['decision'], f'text="{self.txt}"', limit=1)
        #     if decision:
        #         logger.info("Predefined decision found. not running Ai methods.")
        #         self.decisions.append(decision[0][0])
        #
        #         # Even if the decision is available, check some other requirements for submission
        #         self.__detect_multi_blog_links()
        #         self.__detect_multi_titles()
        #         self.__detect_multi_words()
        #         self.__detect_multi_sentences()
        #         self.__detect_multi_paragraphs()
        #         self.__detect_multi_ad_links()
        #         return

        # No database entry, matching the patterns.
        self.rq_blog_post()
        self.rq_post_title()
        self.rq_last_paragraph()
        self.rq_last_sentence()
        self.rq_last_word()
        self.rq_ad_about()
        self.rq_ad_contact()
        self.rq_ad_inside()

    #     self.__update_db_with_txt()
    #
    # def __update_db_with_txt(self):
    #     """
    #     Insert the given text into a suitable database table.
    #     :return:
    #     """
    #     # According to the decisions that has taken, store them properly in the database.
    #     if not self.test_mode:
    #         # Check if the current text is already exists in the tables.
    #         in_ai_success = db_handler.select_filtered('ai_success', ['text'], f'text="{self.txt}"')
    #         in_ai_failed = db_handler.select_filtered('ai_failed', ['text'], f'text="{self.txt}"')
    #
    #         try:
    #             if len(self.decisions) == 1:  # Good decision.
    #                 if not in_ai_success:
    #                     db_handler.add_record('ai_success', [self.txt, self.decisions[0]])
    #                     return
    #
    #             fault_decisions = list_to_str(self.decisions)
    #             if len(self.decisions) > 1:  # Bad output. Multiple decisions
    #                 if not in_ai_failed:
    #                     db_handler.add_record('ai_failed', [self.txt, fault_decisions])
    #                     return
    #
    #             if not self.decisions:  # Bad output. Completely failed
    #                 if not in_ai_failed:
    #                     db_handler.add_record('ai_failed', [self.txt, fault_decisions])
    #                     return
    #         except Exception as e:
    #             logger.info("Database update failed: {}".format(e))

    @staticmethod
    def get_http_links(text: str) -> list:
        """
        Opens the links that contain https(s).
        :return:
        """
        match = [item.group(0) for item in RE_HTTP_LINK.finditer(text)]
        return match

    @staticmethod
    def get_no_http_links(text: str) -> list:
        """
        Opens the links that contain http(s).
        :return:
        """
        match = [item.group(0) for item in RE_NO_HTTP_LINK.finditer(text)]
        return match

    def rq_blog_post(self):     # Decision Code: 1
        """
        Check for blog post link.
        :return:
        """
        match_1 = [item for item in RE_BLOG_POST_LINK.finditer(self.txt)]
        match_2 = [item for item in RE_LAST__NO_OF_URL.finditer(self.txt)]
        illegal_match = [item for item in RE_BLOG_POST_ILLEGALS.finditer(self.txt)]
        if (match_1 or match_2) and not illegal_match:
            self.decisions.append(1)
            self.no_of_posts_req = 1
            self.__detect_multi_blog_links()
            if match_2:
                self.no_of_posts_req = int(match_2[0].group(2))
            return True

    def __detect_multi_blog_links(self):
        """
        Determine if multiple blog links required
        :return:
        """
        if 1 in self.decisions:
            match = [match.group(1) for match in RE_NO_OF_POSTS.finditer(self.txt)]
            # Multiple posts will be available if the matched number <= 5.
            self.no_of_posts_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of blog links req: {self.no_of_posts_req}")

    def rq_post_title(self):     # Decision Code: 2
        """
        Check for blog post title.
        :return:
        """
        match = [item for item in RE_TITLE.finditer(self.txt)]
        if match:
            logger.debug("Post title required")
            self.decisions.append(2)
            self.no_of_titles_req = 1
            self.__detect_multi_titles()
            return True

    def __detect_multi_titles(self):
        if 2 in self.decisions:
            match = [match.group(1) for match in RE_SINGLE_NUMBER.finditer(self.txt)]
            self.no_of_titles_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of titles req: {self.no_of_titles_req}")

    def rq_last_word(self):     # Decision Code: 3
        """
        Check for blog post last word.
        :return:
        """
        match = [item for item in RE_LAST_WORD.finditer(self.txt)]
        if match:
            logger.debug("Last word required")
            self.decisions.append(3)
            self.no_of_words_req = 1
            self.__detect_multi_words()
            return True

    def __detect_multi_words(self):
        if 3 in self.decisions:
            match = [match.group(1) for match in RE_SINGLE_NUMBER.finditer(self.txt)]
            self.no_of_words_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of words req: {self.no_of_words_req}")

    def rq_last_sentence(self):     # Decision Code: 4
        """
        Check for blog post last sentence.
        :return:
        """
        match = [item for item in RE_LAST_SENTENCE.finditer(self.txt)]
        illegal_match = [item for item in RE_STEP_MATCH.finditer(self.txt)]
        if match and not illegal_match:
            logger.debug("Last sentence required")
            self.decisions.append(4)
            self.no_of_sentences_req = 1
            self.__detect_multi_sentences()
            return True

    def __detect_multi_sentences(self):
        if 4 in self.decisions:
            match = [match.group(1) for match in RE_SINGLE_NUMBER.finditer(self.txt)]
            self.no_of_sentences_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of sentences req: {self.no_of_sentences_req}")

    def rq_last_paragraph(self):     # Decision Code: 5
        """
        Check for blog post paragraph.
        :return:
        """
        match = [item for item in RE_LAST_PARAGRAPH.finditer(self.txt)]
        if match:
            logger.debug("Last paragraph required")
            self.decisions.append(5)
            self.no_of_paragraphs_req = 1
            self.__detect_multi_paragraphs()
            return True

    def __detect_multi_paragraphs(self):
        if 5 in self.decisions:
            match = [match.group(1) for match in RE_SINGLE_NUMBER.finditer(self.txt)]
            self.no_of_paragraphs_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of paragraphs req: {self.no_of_paragraphs_req}")

    def rq_ad_inside(self):     # Decision Code: 6 & 7
        """
        Check for ad site inside url.
        :return:
        """
        match_1 = [item for item in RE_AD_LINK.finditer(self.txt)]
        match_2 = [item for item in RE_AD_LINK_2.finditer(self.txt)]
        match_3 = [item for item in RE_AD_STEP_NO.finditer(self.txt)]
        match_4 = [item for item in RE_AD_SNAPSHOT_SITES.finditer(self.txt)]
        illegal_match = [item for item in AD_INSIDE_ILLEGALS.finditer(self.txt)]
        if (match_1 or match_2 or match_3 or match_4) and not illegal_match:
            self.no_of_ad_links_req = 1
            first_match = [item for item in re.compile(r'\b(1\s?st|first)\b').finditer(self.txt)]
            if first_match:
                logger.debug("First opened ad link required")
                self.decisions.append(6)
                return True
            logger.debug("Ad inside link required")
            self.decisions.append(7)
            self.__detect_multi_ad_links()
            return True

    def __detect_multi_ad_links(self):
        """
        Determine if multiple ad links required
        :return:
        """
        if 7 in self.decisions:
            match = [match.group(1) for match in RE_NO_OF_AD_LINKS.finditer(self.txt)]
            # Multiple posts will be available if the matched number <= 5.
            self.no_of_ad_links_req = int(match[0]) if match and int(match[0]) <= 5 else 1
            logger.debug(f"No of ad links req: {self.no_of_ad_links_req}")

    def rq_ad_about(self):     # Decision Code: 8
        """
        Check for ad site about url.
        :return:
        """
        match = [item for item in RE_ABOUT_URL.finditer(self.txt)]
        if match:
            logger.debug("Ad about url required")
            self.decisions.append(8)
            return True

    def rq_ad_contact(self):     # Decision Code: 9
        """
        Check for ad site contact url.
        :return:
        """
        match = [item for item in RE_CONTACT_URL.finditer(self.txt)]
        if match:
            logger.debug("Ad contact url required")
            self.decisions.append(9)
            return True

    def rq_snapshot(self):     # Decision Code: 10
        """
        Check for history page screenshot.
        :return:
        """
        match = [item for item in RE_SNAPSHOT.finditer(self.txt)]
        if match:
            logger.debug("Screenshot required")
            self.decisions.append(10)
            return True


if __name__ == "__main__":
    from constants import db_handler

    failed = [step[0] for step in db_handler.select_filtered('ai_failed', ['text']) if step]
    for step in failed:
        o = Ai(step, test_mode=True)
        print(o.decision().decision_code)

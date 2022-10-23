import pathlib
import re
import threading
import time
import requests
import logging
from requests.exceptions import ConnectionError
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException, WebDriverException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver import Edge
from typing import Union
from regexes import (RE_HTTP_LINK,
                     RE_SEARCH,
                     RE_DISCLAIMER,
                     RE_PRIVACY_POLICY,
                     RE_ABOUT_OR_CONTACT,
                     RE_CATEGORY,
                     RE_COOKIES,
                     RE_PAGE,
                     RE_TERMS_OF_USE,
                     RE_AUTHOR,
                     RE_TAG,
                     RE_LOGIN)
from webcrapy.urlmaster import UrlMaster
from functions.fns import get_file_logger, get_syslogger, get_ascii

base_dir = pathlib.Path(__file__).parent.absolute()

logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/miner.log", 'a')
sys_logger = get_syslogger()


def calc_network_time(func):
    def wrapper(self, url):
        s = time.perf_counter()
        response = func(self, url)
        e = time.perf_counter()
        logger.info(f"Network request finished in {round(e - s, 3)} second(s)\t-> {url}")
        return response

    return wrapper


class MineBase:
    """
    All common attributes and methods for blog and ad data mining.
    """

    """
    Header information for the requests made by 'requests' library.
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71",
    }

    def _request_site(self, url: str) -> requests:
        """
        Contact the site and returns the "requests" response object if success.
        :type url: Google ad url
        :return:
        """
        try:
            s = time.perf_counter()
            response = requests.get(url, headers=self.headers)
            e = time.perf_counter()
            logger.info(f"Network request finished in {round(e-s, 3)} second(s)")
            if response.ok:
                logger.info("Site live: {}".format(response.url))
                return response
            else:
                logger.warning("Bad response ( {} ) from: {}".format(response.status_code, url))
                return
        except ConnectionError:
            logger.debug(f"Connection error when requesting: {url}")
            return

    @staticmethod
    def _get_anchor(html: str):
        """
        Single anchor element generator
        :param html:
        :return:
        """
        for anchor in BeautifulSoup(html, 'lxml').find_all('a'):
            yield anchor

    @staticmethod
    def _get_href(anchor: Tag) -> Union[str, None]:
        """
        Only accepts BS4 Tag object.
        :param anchor:
        :return:
        """
        try:
            href = anchor['href']
            return href
        except KeyError:
            pass

    @staticmethod
    def get_home_url(url: str) -> str:
        """
        Gets any website link and returns the home url of the site
        :param url:
        :return:
        """
        if url:
            home = UrlMaster(url).home_url.strip('./\\')
            return home

    def get_orig_url(self, url: str, relative_url: str) -> str:
        """
        Rebuild the relative path url into a complete url
        :param url: Any complete url in the site.
        :param relative_url: Relative path url
        :return:
        """
        home = self.get_home_url(url)
        if home:
            orig_url = "{}/{}/".format(home, relative_url.strip('./\\'))
            logger.info("Url Rebuilt: {}  ->  {}".format(relative_url, orig_url))
            return orig_url


class Filters:
    """
    Contains the methods that need for url filtering.
    """

    @staticmethod
    def _is_same_domain(url_1: str, url_2: str):
        if UrlMaster.is_same_domain(url_1, url_2):
            return True

    @staticmethod
    def _is_search(url: str):
        if [match for match in RE_SEARCH.finditer(url)]:
            return True

    @staticmethod
    def _is_disclaimer(url: str):
        if [match for match in RE_DISCLAIMER.finditer(url)]:
            return True

    @staticmethod
    def _is_privacy(url: str):
        if [match for match in RE_PRIVACY_POLICY.finditer(url)]:
            return True

    @staticmethod
    def _is_about_or_contact(url: str):
        if [match for match in RE_ABOUT_OR_CONTACT.finditer(url)]:
            return True

    @staticmethod
    def _is_category(url: str):
        if [match for match in RE_CATEGORY.finditer(url)]:
            return True

    @staticmethod
    def _is_cookies(url: str):
        if [match for match in RE_COOKIES.finditer(url)]:
            return True

    @staticmethod
    def _is_author(url: str):
        if [match for match in RE_AUTHOR.finditer(url)]:
            return True

    @staticmethod
    def _is_terms_of_use(url: str):
        if [match for match in RE_TERMS_OF_USE.finditer(url)]:
            return True

    @staticmethod
    def _is_page(url: str):
        if [match for match in RE_PAGE.finditer(url)]:
            return True

    @staticmethod
    def _is_tag(url: str):
        if [match for match in RE_TAG.finditer(url)]:
            return True

    @staticmethod
    def _is_login(url: str):
        if [match for match in RE_LOGIN.finditer(url)]:
            return True

    @staticmethod
    def clean_link(url: str) -> str:
        """
        Remove if the url contains some unnecessary text at the end.
        :param url:
        :return:
        """
        filtered = re.sub('#(comments?|respond)/?$', '', url).strip()
        return filtered


class BlogData(MineBase, Filters):
    """
    Used to gather blog site information.
    """

    def __init__(self, url, mine_titles: bool = False, mine_post_content: bool = False):
        self.url = url  # Url of the blog site
        self.mine_titles = mine_titles
        self.mine_post_content = mine_post_content  # Includes [last words, last sentences, last paragraphs]

        self.response = None    # response from the blog site taken by requests.get
        self.home_url = None    # Blog site homa page url
        self.__dirty_posts = set()  # Non filtered blog post links

        """
        Following instance variables should not be class variables because,
        these lists only get appended and never gets cleared.
        
        So even with the new instance, they will still contain the data gathered from 
        previous instances. 
        
        CRITICAL OOP CONCEPT
        """

        """
        Ready to use blog posts links
        """
        self.posts = []

        """
        Post titles that gathered using above posts links
        """
        self._titles = []

        """
        Last paragraphs from the blog posts.
        """
        self._last_paragraphs = []

        """
        Last sentences from the blog posts
        """
        self._last_sentences = []

        """
        Last words from the blog posts
        """
        self._last_words = []

        logger.info(f"\n\n{'=' * 20} Starting with new Blog Data instance {'=' * 20}\n")
        self.start()

    @property
    def titles(self):
        no_dup = list(set(self._titles))
        no_dup.sort(key=len, reverse=True)
        return no_dup

    @property
    def last_paragraphs(self):
        no_dup = list(set(self._last_paragraphs))
        no_dup.sort(key=len, reverse=True)
        return no_dup

    @property
    def last_sentences(self):
        no_dup = list(set(self._last_sentences))
        no_dup.sort(key=len, reverse=True)
        return no_dup

    @property
    def last_words(self):
        no_dup = list(set(self._last_words))
        no_dup.sort(key=len, reverse=True)
        return no_dup

    def start(self):
        s = time.perf_counter()
        self.response = self._request_site(self.url)

        # Determine if the page redirection occurred or not
        if not self.response.url == self.url:
            logger.debug("Url redirection detected")
            logger.debug(f"Requested: {self.url} but response given by: {self.response.url}")

        if self.response:
            self.home_url = self.get_home_url(self.response.url)
            self.__dirty_posts = set(self._get_href(anchor) for anchor in self._get_anchor(str(self.response.text)))

            # Filter posts, to get the best results.
            with ThreadPoolExecutor() as executor:
                executor.map(self.__filter_blog_links, self.__dirty_posts)

            # Sort the filtered posts according to the length of the string because, there
            # is a higher chance that the longer link is probably a blog post.
            self.posts.sort(key=len, reverse=True)
            logger.debug(f"Found posts: {len(self.posts)}")

            # Find other info, only if told.
            if self.mine_titles:
                sys_logger.debug("Finding post titles")
                t = threading.Thread(target=self.store_titles)
                t.start()
                t.join()
            else:
                logger.debug("Not collecting post titles")
                sys_logger.debug("Not collecting post titles")

            if self.mine_post_content:
                sys_logger.debug("Finding post data: [paragraphs, sentences, words]")
                t1 = threading.Thread(target=self.store_post_data)
                t1.start()
                t1.join()
            else:
                logger.debug("Not collecting post data [paragraphs, sentences, words]")
                sys_logger.debug("Not collecting post data [paragraphs, sentences, words]")

        e = time.perf_counter()
        logger.debug("Blog data stuffs finished in {} seconds.".format(round(e-s, 3)))

    def store_titles(self):
        """
        Find and store posts titles. This is done by taking the text of html <a>, only if
        it's href attribute value is present in the self.posts.
        :return:
        """
        s = time.perf_counter()
        for anchor in self._get_anchor(str(self.response.text)):
            link = self._get_href(anchor)
            if link and self.clean_link(link) in self.posts:
                title = anchor.text.strip()
                if len(title.split(' ')) >= 2:  # Store only if title has at least 2 words
                    title_with_link = f"{title}\t\t->\t{self.clean_link(link)}"
                    if title_with_link not in self._titles:
                        self._titles.append(get_ascii(title_with_link))
                        logger.info(f"Title found: [{title}]\t\tfrom ->\t{link}")

        # When the title becomes longer, there is higher chance it being an actual title
        self._titles.sort(key=len, reverse=True)
        logger.debug(f"Total titles found: {len(self.titles)}")

        e = time.perf_counter()
        logger.debug(f"Storing titles finished in: {round(e - s, 5)} seconds")

    def store_post_data(self):
        """
        Finds the last paragraphs, sentences and words
        :return:
        """
        s = time.perf_counter()
        logger.debug("Starting post data gathering")

        def calc_no_of_p_tags_in_body(func):
            """
            @decorator
            Calculates the no of valid paragraphs exists in the given Beautifulsoup HTML DOM
            after running the given filter function
            :param func:
            :return:
            """
            def wrapper(body_soup: BeautifulSoup):
                body_soup = func(body_soup)
                paras = len(get_p_tags(body_soup))
                logger.debug(f"Exists {paras} paragraphs after filtering with func: <{func.__name__}>")
                return body_soup
            return wrapper

        @calc_no_of_p_tags_in_body
        def rm_by_elements(soup: BeautifulSoup) -> BeautifulSoup:
            rm_elements = ['header', 'ins', 'footer', 'script',
                           'style', 'svg', 'img', 'link', 'meta',
                           'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            for element in rm_elements:
                tags = soup.find_all(element)
                for tag in tags:
                    tag.decompose()
                logger.debug(f"Removed elements by Tag <{element}>: {len(tags)}")
            return soup

        @calc_no_of_p_tags_in_body
        def rm_by_class(soup: BeautifulSoup) -> BeautifulSoup:
            # Removing all the <div> elements that have special class names
            tags = soup.find_all(
                name=re.compile(r'div'),
                class_=re.compile(r'comment|footer|sidebar|cookie|notice|widget|preloader', flags=re.I),
            )
            for tag in tags:
                tag.decompose()
            logger.debug(f"Removed <div> elements by Class name: {len(tags)}")
            return soup

        def get_p_tags(soup: BeautifulSoup) -> list:
            """
            Returns the number of <p> tags in the given Beautifulsoup DOM object.
            :param soup:
            :return:
            """
            paras = [ptag for ptag in soup.find_all('p') if len(ptag.text.strip().split(' ')) >= 3]
            return paras

        def _thread(url):
            resp = self._request_site(url)
            if not resp:
                logger.warning(f"Blog post {url} could not be reached. skipped")
                return
            # If a redirection occurred, do not continue because, it is not the requested post
            elif resp.url != url:
                logger.debug(f"Redirected to: {resp.url} when requesting {url}. skipped")
                return
            logger.debug(f"Gathering posts data in: {url}")

            soup = BeautifulSoup(str(resp.text), 'lxml')
            body_soup = soup.find('body')   # This will be the final output after filtering
            logger.debug(f"{len(get_p_tags(body_soup))} paragraphs exists in the body as a total")

            # Removing unnecessary page elements by different aspects.
            body_soup = rm_by_elements(body_soup)
            body_soup = rm_by_class(body_soup)

            paras = [ptag.text.replace('\n', ' ').strip() for ptag in get_p_tags(body_soup)
                     if ptag.text.replace('\n', ' ').strip()]
            logger.debug(f"No. of valid paragraphs after applying all filters: {len(paras)}")

            last_p = last_s = last_w = None
            if paras:
                # If the paras[-1] has only one sentence, try with the paras[-2].
                # if it has more than 1 sentence, use it as the last paragraph
                sens_1 = len([s for s in paras[-1].split('. ') if s.strip()])  # No. of sentences in the paras[-1]
                if sens_1 == 1 and len(paras) >= 2:
                    sens_2 = len([s for s in paras[-2].split('. ') if s.strip()])  # No. of sentences in the paras[-2]
                    if sens_2 > 1:
                        last_p = paras[-2]
                        logger.debug("Choosing second last paragraph. "
                                     "Ignored last paragraph -> [ {} ]".format(paras[-1]))
                if not last_p:
                    last_p = paras[-1]
                self._last_paragraphs.append(get_ascii(last_p))    # Set last paragraph

                # Set last sentence
                sentences = [s.strip() for s in last_p.split('. ') if s.strip()]
                if sentences:
                    last_s = str(sentences[-1]).replace('\n', ' ')
                    self._last_sentences.append(get_ascii(last_s))

                    # Set last word
                    words = [w for w in last_s.split(' ') if w]
                    if words:
                        last_w = str(words[-1]).replace('\n', ' ')
                        self._last_words.append(get_ascii(last_w))
                logger.debug(f"\n{'{'}\n"
                             f"\tPOST: {get_ascii(url)}\n"
                             f"\tLAST_PARAGRAPH: {get_ascii(last_p)}\n"
                             f"\tLAST_SENTENCE: {get_ascii(last_s)}\n"
                             f"\tLAST_WORD: {get_ascii(last_w)}\n{'}'}\n")
            else:
                logger.warning(f"No paragraphs found in: {url}")

        with ThreadPoolExecutor() as executor:
            logger.info("Searching for posts data in first 10 posts.")
            executor.map(_thread, self.posts[0:10])

        e = time.perf_counter()
        logger.debug(f"Storing post data finished in: {round(e-s, 3)} seconds.")

    def __filter_blog_links(self, url: str):
        url_ok = True
        if not self._is_same_domain(self.url, url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_same_domain>")
        if self._is_search(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_search>")
        if self._is_disclaimer(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_disclaimer>")
        if self._is_privacy(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_privacy>")
        if self._is_about_or_contact(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_about_or_contact>")
        if self._is_category(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_category>")
        if self._is_cookies(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_cookies>")
        if self._is_author(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_author>")
        if self._is_terms_of_use(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_terms_of_use>")
        if self._is_page(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_page>")
        if self._is_login(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_login>")
        if self._is_tag(url):
            url_ok = False
            # print(f"Removed {url} because of: <_is_tag>")

        if url_ok:
            # Remove unnecessary parts at the end of the url
            url = self.clean_link(url)
            self.posts.append(url) if url not in self.posts else None


class AdData(MineBase):
    """
    Used to gather ad site information.
    """

    """
    Whether driver is currently switched into a frame or not
    """
    _inside_frame = False

    def __init__(self, url, driver: webdriver = None):
        """
        :param url: url of the website to scrape
        """

        self.url = url

        """
        First opened url, after requesting the url taken from iframe
        """
        self.first_url = None

        """
        Ad site home url
        """
        self.home_url = None

        """
        About-Us url of the site
        """
        self.about_url = None

        """
        Contact-Us url of the site
        """
        self.contact_url = None

        """
        Other ad links found that is not filtered.
        """
        self.__dirty_links = []

        """
        Clear ad links after filtering.
        """
        self.links = []

        """
        Webdriver
        """
        self.driver = driver

        """
        Regex: About us url pattern
        """
        self.__about_pat = re.compile(r"about+?")

        """
        Regex: Contact us url pattern
        """
        self.__contact_pat = re.compile(r"contact+?")

        """
        Whether driver should be closed or not after done.
        """
        self.__close_driver = False

        logger.info(f"\n\n{'='*20} Starting with new Ad Data instance {'='*20}\n")
        self.start()

    def __reset(self):
        """
        Set all the data into default values, when changing the ad frame.
        This is used to clear exists data, when switching to another frame.
        :return:
        """
        self.first_url = self.contact_url = self.about_url = None
        self.__dirty_links.clear()

    @staticmethod
    def __is_google_ad_url(url: str) -> bool:
        """
        Check if the given url is a Google ad site url or not.
        :param url:
        :return:
        """
        if url.startswith('https://adclick.g.doubleclick.net') or 'googleads' in url:
            logger.info("Google ad url found: {}".format(url))
            return True
        logger.info(f"Detected as non google ad url: {url}")

    def __get_live_site_response(self, frame_source: str):
        """
        Accepts the frame source and finds a live website from the links
        in the frame source
        :param frame_source:
        :return:
        """
        for anchor in self._get_anchor(str(frame_source)):
            url = self._get_href(anchor)
            logger.info(f"From frame: {url}")
            if url and self.__is_google_ad_url(url):
                # Google ad url found from the frame source
                response = self._request_site(url)
                if response:
                    return response
                # Already tried a Google ad url in this frame. But could not reach the website.
                # Even if another urls exists in the frame do not try with them because, a single
                # frame only contains the links for the same website. just Break the loop.
                break

    def start(self):
        start = time.perf_counter()
        self._open_site()

        print(f"Found: {len([f for f in self._get_iframes()])} ad frames.")

        for iframe in self._get_iframes():
            # Clear the stored data with previous frame, if exists.
            self.__reset()

            # Try to switch to the frame
            try:
                self.driver.switch_to.frame(iframe)
                self._inside_frame = True
            except Exception as e:
                logger.info(f'Frame skipped: {e}')
                self._inside_frame = False
                continue
            logger.info("Switched to a frame !")
            # Since you are here, you have successfully switched to an iframe.

            frame_source = self._get_frame_source()
            ad_site_response = self.__get_live_site_response(str(frame_source))
            if ad_site_response:
                self.first_url = ad_site_response.url
                self.home_url = UrlMaster(self.first_url).home_url
                logger.info("Home url set: {}".format(self.home_url))

                for anchor in self._get_anchor(ad_site_response.text):
                    if self._all_satisfied():
                        logger.info("All requirements satisfied!")
                        break

                    url = self._get_href(anchor)

                    # If url is a relative path url, rebuild it.
                    if url and (url.startswith('/') or url.startswith('./')):
                        url = self.get_orig_url(self.first_url, url)

                    if url and len(url) > 8:
                        # Start all the link checks.
                        if not self.about_url:
                            if self._is_about(url):
                                self.about_url = url
                                logger.info("About url set: {}".format(self.about_url))
                                continue
                        if not self.contact_url:
                            if self._is_contact(url):
                                self.contact_url = url
                                logger.info("Contact url set: {}".format(self.contact_url))
                                continue

                        self.__dirty_links.append(url) \
                            if url not in self.__dirty_links else None

            else:
                # No live ad sites found from the switched frame. Try another one.
                logger.info("Could not reach the ad site. Trying with another frame")
                self.driver.switch_to.default_content()
                continue

            # Break the loop if medium level requirements are satisfied.
            if self._satisfied():
                logger.info("Minimum requirements satisfied. Stopping..")
                break
            else:
                logger.info("Frame could not even fulfill minimum requirements. Trying with another frame")

        # Close the driver if it is not given by user.
        if self.__close_driver:
            self.driver.quit()

        # Filter stored links
        with ThreadPoolExecutor() as executor:
            executor.map(self.filter_ad_links, self.__dirty_links)

        # Sort the filtered posts according to the length of the string because, there
        # is a higher chance that the longer link is not going to be the home url.
        self.links.sort(key=len, reverse=True)

        end = time.perf_counter()
        logger.info("Ad site stuffs finished in {} second(s).".format(round(end - start, 3)))

    def _open_site(self) -> None:
        """
        Initializes the webdriver and opens the site.
        :return:
        """
        if not self.driver:
            self.driver = Edge(executable_path=f'{base_dir}/msedgedriver.exe')
            self.__close_driver = True
            self.driver.get(self.url)  # Should open in a new tab
            return

        # If ad site tab already opened, do not open a new tab. Use it.
        if self.__ad_tab_exists():
            return

        # Ad site has not opened, open it in a new tab.
        logger.info("Opening ad site url in a new tab.")
        from functions.driverfns import open_url
        open_url(self.url, '_blank', self.driver)
        time.sleep(25)
        self.switch_to_ad_tab()

    def __ad_tab_exists(self):
        """
        Check if the given ad site tab has already opened.
        Used to prevent ad site url opening twice.
        :return:
        """
        handles = None
        try:
            handles = self.driver.window_handles
        except Exception as e:
            logger.warning("Error when getting window handles: {}".format(e))

        if handles:
            for window in handles:
                self.driver.switch_to.window(window)
                try:
                    if self.driver.current_url == self.url:
                        print("Ad site tab has already opened. Switched.")
                        return True
                except (UnexpectedAlertPresentException,
                        WebDriverException):
                    pass

    def switch_to_ad_tab(self):
        """
        Switch to the ad site tab that was opened previously
        :return:
        """
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            try:
                if self.driver.current_url == self.url:
                    return True
            except (UnexpectedAlertPresentException,
                    WebDriverException):
                pass
        return False

    def _get_iframes(self):
        """
        Single frame generator.
        :return:
        """
        try:
            logger.info("Searching for ads in: {}".format(self.driver.current_url))
        except NoSuchWindowException:
            pass
        for frame in self.driver.find_elements(By.TAG_NAME, 'iframe'):
            yield frame

    def _get_frame_source(self) -> str:
        """
        Returns the frame source after switching to an iframe.
        Using this before switching to a frame, will return whole page source
        :return:
        """
        if self._inside_frame:
            return str(self.driver.page_source)

    def _satisfied(self):
        """
        Check if at least one of the about or contact urls found or not.
        Medium level satisfaction method.
        :return:
        """
        if len(self.__dirty_links) >= 5 and (self.about_url or self.contact_url):
            return True

    def _all_satisfied(self):
        """
        Check if all the required data is stored or not.
        :return:
        """
        if len(self.__dirty_links) >= 5 and self.about_url and self.contact_url:
            return True

    def _is_about(self, url: str) -> bool:
        """
        Check if a given url is an about us page url.
        :param url:
        :return:
        """
        match = [link for link in self.__about_pat.finditer(url) if link]
        return True if match else False

    def _is_contact(self, url: str) -> bool:
        """
        Check if a given url is an contact us page url.
        :param url:
        :return:
        """
        match = [link for link in self.__contact_pat.finditer(url) if link]
        return True if match else False

    def filter_ad_links(self, url: str) -> None:
        """
        Filter stored blog posts link based on required conditions.
        """
        if UrlMaster.is_same_domain(url, self.first_url):
            self.links.append(url)


if __name__ == "__main__":
    u_1 = "https://100springs.com/speak-freely-simon-should-always-say-yes-you-may/"
    # u_2 = 'https://www.sunja.id/2022/07/wisata-di-talaga-pineus-pangalengan.html'  # Failed to get post data
    u_3 = 'https://dryhair.searchjob24.com/2021/08/11/how-to-sublimate-dull-hair/'
    # u_4 = 'https://sahityamahal.blogspot.com/2022/08/dailymotion.html'  # Failed to get post data
    # u_5 = 'https://blog.ihis.info/id/aws-big-data/aws-big-data-analysis-with-hadoop'
    # u_7 = "https://tech.mobilebdinfo.com/2022/08/10/parents-can-monitor-their-childs-use-of-snapchat-account/"
    # u_9 = "https://www.belg12.com/business-ethics-6-basic-principles-of-business-etiquette/"
    # u_10 = "https://newsaya.com/bitcoin-and-ether-will-come-out-of-the-bear-market-ahead-of-stocks-mcglone-predicts/"
    # u_11 = "https://bitcoin.nccrea.com/bitcoin-and-ether-will-come-out-of-the-bear-market-ahead-of-stocks-mcglone-predicts/"
    # u_12 = "https://asianwalls.net/arcane-nexflix-jinx-vi-jayce-league-of-legends-wallpaper-full-hd-8901043604bc1d05a6564f3c083eee25/"
    u_13 = 'https://www.naijamula.com.ng/bst-loan-app-in-nigeria/'

    # Testing Ad data gathering
    blog = BlogData(u_13, mine_titles=True, mine_post_content=True)
    print(f"Posts: {len(blog.posts)}\t->", blog.posts)
    print(f"Titles: {len(blog.titles)}\t->", blog.titles)
    print(f"Paras: {len(blog.last_paragraphs)}\t->", blog.last_paragraphs)
    print(f"Sentences: {len(blog.last_sentences)}\t->", blog.last_sentences)
    print(f"Words: {len(blog.last_words)}\t->", blog.last_words)

    # Testing Ad data gathering
    ad = AdData(u_13)
    print("AD SITE STAT")
    print("First", ad.first_url)
    print("About", ad.about_url)
    print("Contact", ad.contact_url)
    print("All links found")
    for i in ad.links:
        print(i)

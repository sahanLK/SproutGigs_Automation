import pathlib
import re
from urllib import parse
import logging
from functions.fns import get_file_logger, get_syslogger

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/urlmaster.log", 'w+')
sys_logger = get_syslogger()


class InvalidUrlPassedError(Exception):
    def __init__(self, *args):
        super(InvalidUrlPassedError, self).__init__(args)
        self.msg = args

    def __repr__(self):
        print(self.msg)


class UrlMaster:
    """
    Validates a url
    """

    """
    RE pattern for matching a url.
    """
    URL_PATTERN = re.compile(r'\bhttps?://(\w+\d*)\.?(\w+)\.(\w+)([\w\d/.]*)\b')

    """
    Domain name of the url.
    """
    domain = None

    """
    Top Level Domain Name.
    """
    tld = None

    """
    Rest of the part in the url after TLD.
    """
    finals = None

    """
    Network Location of the url.
    """
    home_url = None

    def __init__(self, url):
        """
        IMPORTANT
        (/) is necessary at the end of any url, to process the url correctly.
        """
        self.dirty_url = f"{str(url)}/" if not str(url).endswith('/') else str(url)
        # print('Dirty url:', self.dirty_url)

        self.is_url_valid()

    def is_url_valid(self):
        """
        Checks url is valid or not.
        :return: bool
        """
        re_matched = self.__is_match_found(self.dirty_url)

        # If urllib module has a match, proceed only with netloc in urllib.
        if parse.urlparse(self.dirty_url).netloc:
            # logger.info('UrlMaster: proceeding with Urllib.')
            self.__set_url_partials_with_urllib(self.dirty_url)

        # If RE found a match, proceed only with RE.
        elif re_matched:
            # logger.info('UrlMaster: proceeding with RE.')
            self.__set_url_partials_with_re(re_matched)
            return True

        # Not a valid url.
        else:
            logger.info(f'Invalid url was passed -> {self.dirty_url}')
            pass

    def __is_match_found(self, exp_url_str):
        matches = self.URL_PATTERN.finditer(exp_url_str)
        try:
            match = matches.__next__()
            if match:
                return match
            return False
        except StopIteration:
            return False

    def __set_url_partials_with_re(self, match):
        self.tld = match.group(5)
        self.finals = match.group(7) + match.group(8)
        self.domain = match.group(4)

        # If "/" in domain name, needs some filtering for everything(domain, tld and finals).
        if '/' in self.domain:
            domain_name = ''
            domain_lst = self.domain.split('/')[0].split('.')
            finals_lst = self.domain.split('/')
            self.tld = f".{domain_lst[-1]}"
            domain_lst.pop()
            for domain in domain_lst:
                domain_name += f"{domain}."
            self.domain = domain_name.strip(domain_name[-1]) if \
                domain_name else domain_name

            # finals_lst.pop(0)
            finals = ''
            for final in finals_lst:
                final = f"{final}/" if not finals_lst[-1] == final else final
                finals += final
            self.finals = finals + match.group(5)
        self.finals = None if self.finals == '/' else self.finals

        # Home url
        self.home_url = f"{self.domain}{self.tld}/"

    def __set_url_partials_with_urllib(self, url):
        ullib_obj = parse.urlparse(url)
        self.home_url = f"{ullib_obj.scheme}://{ullib_obj.netloc}/"    # set Home-Url
        # logger.info(f'Home Url Set: {self.home_url}')

        split_home_url = ullib_obj.netloc.split('.')
        self.tld = f".{split_home_url[-1]}"   # set TLD

        domain_name = ''
        domain_parts = split_home_url[0:-1] if \
            split_home_url[0] != 'www' else split_home_url[1:-1]
        for part in domain_parts:
            domain_name += f"{part}."
        try:
            self.domain = domain_name.strip(domain_name[-1])   # set Domain
        except IndexError:
            # Maybe Domain name is empty
            pass

        before_finals = f"{ullib_obj.scheme}://{ullib_obj.netloc}"
        self.finals = url.split(before_finals)[-1]
        self.finals = None if self.finals == '/' else self.finals  # set Finals

    @staticmethod
    def is_same_domain(url1, url2):
        """
        Used to check if 2 urls are in the same domain.
        USE CASE: following 2 urls are in same domain.
            > www.site.com
            > www.data.site.com
        But Urlmaster doesn't match domain names of these 2 urls.
        To solve that problem, this method can be used.
        :param url1:
        :param url2:
        :return: bool
        """
        link1 = UrlMaster(url1)
        link2 = UrlMaster(url2)

        # print(f"Domains: {link1.domain} and {link2.domain}")
        # print(f"TLDs: {link1.tld} and {link2.tld}")
        # print(f"Home Urls: {link1.home_url} and {link2.home_url}")

        if link1.domain == link2.domain:
            logger.debug(f'Domains matched: {url1} = {url2}')
            return True
        return False

    @staticmethod
    def is_exact_same(url1, url2):
        """
        Compare 2 urls and check whether, they are exactly the same url.
        :param url1:
        :param url2:
        :return: Bool
        """
        u1 = UrlMaster(url1)
        u2 = UrlMaster(url2)

        if u1.domain == u2.domain:
            if u1.tld == u2.tld:
                if u1.finals == u2.finals:
                    logger.debug(f'Urls exactly matched: {url1} = {url2}')
                    return True
        return False

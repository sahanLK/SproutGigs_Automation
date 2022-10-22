import random
from picoconstants import db_handler


class BlogsDataSplitter:
    """
    Get a single record from blogs table and split items into separate items.
    """

    def __init__(self, domain, **kwargs):
        self.entry = db_handler.select_filtered('blogs', [], f'blog_domain="{domain}"')
        self.domain = domain
        self.posts = ''
        self.titles = ''
        self.last_sentences = ''
        self.last_paragraphs = ''
        self.last_words = ''

        if self.entry:
            self.__set_all()

    def __set_all(self, *args):
        self.posts = [link for link in self.entry[0][1].split('|') if link]
        self.titles = [title for title in self.entry[0][2].split('|') if title]
        self.last_words = [word for word in self.entry[0][3].split('|') if word]
        self.last_sentences = [sentence for sentence in self.entry[0][4].split('|') if sentence]
        self.last_paragraphs = [para for para in self.entry[0][5].split('|') if para]


class AdDataSplitter:
    def __init__(self):
        self.first_url = ''
        self.about_url = ''
        self.contact_url = ''
        self.links = ''
        self.set_all()

    def set_all(self):
        records = db_handler.select_all('ad_sites', limit=100)
        # Always maintain maximum of 100 ad sites or less
        if len(records) > 100:
            for record in records[0:70]:
                domain = record[0]
                db_handler.delete_records('ad_sites', f"domain='{domain}'")

        if records:
            random_ad = random.choice(records)
            self.first_url = random_ad[1]
            self.about_url = random_ad[2]
            self.contact_url = random_ad[3]
            self.links = [link for link in random_ad[4].split('|') if link]

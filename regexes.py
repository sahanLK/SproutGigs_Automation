import re

"""
Common expressions.
"""
RE_NO_HTTP_LINK = re.compile(r'\s(\w+[^/:*])\.(\w+\d*)(?=\s|\b)([\w\d/&%#=-_]*)', flags=re.I)
RE_HTTP_LINK = re.compile(r'\bhttps?://(\w+\d*)?\.?(\w+\d*)\.(\w+)([\w\d/.-]*)\b', flags=re.I)
RE_NTH_NUMBER = re.compile(r'\b(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th'
                           r'first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b', flags=re.I)
RE_SINGLE_NUMBER = re.compile(r'\b(\d)\s')
RE_TEL_NO = re.compile(r'\b(0?\d{2})-?(\d{7})\b', flags=re.I)
RE_STEP_MATCH = re.compile(r'(step)\s+(\d)\b')
RE_NUMBER = re.compile(r'\b\d+\s', flags=re.I)
RE_EMAIL = re.compile(r'\s(\w+)@\w+\.\w+\b', flags=re.I)
RE_ABOUT_OR_CONTACT = re.compile(r'\b(contact+?|about+?|contacto+?)(.*)(\bad)?', flags=re.I)
RE_PRIVACY_POLICY = re.compile(r'\bprivacy+|policy+', flags=re.I)
RE_TERMS_OF_USE = re.compile(r'(\bterms)(.*)(of?)?(.*)(use+|condition+|service)', flags=re.I)
RE_DISCLAIMER = re.compile(r'\bdisclaim', flags=re.I)
RE_CATEGORY = re.compile(r'category/', flags=re.I)
RE_COMMENT = re.compile(r'comment', flags=re.I)
RE_SITEMAP = re.compile(r'\bsitemap', flags=re.I)
RE_COOKIES = re.compile(r'cookies?', flags=re.I)
RE_SEARCH = re.compile(r'search/|/s\?', flags=re.I)
RE_AUTHOR = re.compile(r'(author|admin)(\b|\W)', flags=re.I)
RE_LOGIN = re.compile(r'login\.', flags=re.I)
RE_PAGE = re.compile(r'/page/', flags=re.I)
RE_TAG = re.compile(r'tag/', flags=re.I)


"""
Specific expressions.
"""

# Match about us url
RE_ABOUT_URL = re.compile(r'\b(about)(\sus)?\s.*(\burl|\blink)', flags=re.I)

# Match contact us url.
RE_CONTACT_URL = re.compile(r'\b(contact)(\sus)?\s.*(\burl|\blink)?', flags=re.I)

# Match advertisement site inside link.
RE_AD_LINK = re.compile(r'\b(ad|advertisement|ad\s?site)\s.*(\burl|\blink)', flags=re.I)
RE_AD_LINK_2 = re.compile(r'\b(\burls?|links?)\s.*(ad|advertisement|ad\s?site)', flags=re.I)
RE_AD_STEP_NO = re.compile(r'\b(urls?|links?|proofs?)\s.*(step)\s+(\d)', flags=re.I)

RE_AD_SNAPSHOT_SITES = re.compile(r'pastebin|snipboard|imgur', flags=re.I)
RE_NO_OF_AD_LINKS = re.compile(r'\b(\d)\s+(\w*\s)?(urls?|links?)', flags=re.I)

# Match blog site home url
RE_BLOG_HOME_LINK = re.compile(r'')

# Match blog post link.
RE_BLOG_POST_LINK = re.compile(r'\b(posts?|articles?|pages?)\b', flags=re.I)
RE_LAST__NO_OF_URL = re.compile(r'\b(last)\s+(\d)\s+(website|visited)\s+', flags=re.I)
RE_NO_OF_POSTS = re.compile(r'\b(\d)\s+(\w*\s)?(urls?|links?|posts?|articles?)', flags=re.I)

# Match blog post title.
# Use "(\b\d+\s+)?" group for checking how many titles are required.
RE_TITLE = re.compile(r'\b(titles?)\b[^\d]*(\b\d+\s+)?([\w\s]*)?(\bposts?|\barticles?|pages?|urls?)', flags=re.I)
RE_NO_OF_TITLES = re.compile(r'\b(titles?)(\w*\s)?\s+(\d)', flags=re.I)

# Match blog post last word.
# Use "(\b\d+\s+)?" group for checking how many last words are required.
RE_LAST_WORD = re.compile(r'\b(last words?)\b[^\d]*(\b\d+\s+)?(\w*)?(\bposts?|\barticles?)?', flags=re.I)

# Match blog post last sentence.
# Use "(\b\d+\s+)?" group for checking how many last sentences are required.
RE_LAST_SENTENCE = re.compile(r'\b(last senten(ce|se)s?)\b[^\d]*(\b\d+\s+)?(\w*)?(\bposts?|\barticles?)?', flags=re.I)

# Match blog post last paragraph.
RE_LAST_PARAGRAPH = re.compile(r'\b(last paragraphs?)\b[^\d]*(\b\d+\s+)?(\w*)?(\bposts?|\barticles?)?', flags=re.I)

# Match history page screenshot.
RE_SNAPSHOT = re.compile(r'(\bscreenshot+\b|\bhistory+\b)(.*?)(history+|\bscreenshot+\b)', flags=re.I)

# Match code submission.
RE_CODE_SUBMIT = re.compile(r'\bcode\b', flags=re.I)

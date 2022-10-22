import unittest
from ai import Ai


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


class TestAi(unittest.TestCase):

    def test_get_decision(self):
        self.assertEqual(
            Ai('Please give 1 Urls of the website you visited in step 3', test_mode=True).get_decision().decision_code, 7)
        self.assertEqual(
            Ai('Proof 1 step 5', test_mode=True).get_decision().decision_code, 7)
        self.assertEqual(
            Ai('Last sentence of 6th posts.', test_mode=True).get_decision().decision_code, 4)
        self.assertEqual(
            Ai('Please give 2 Urls inside website you visited from step 5', test_mode=True).get_decision().decision_code, 7)

        # Testing no of items required
        self.assertEqual(
            Ai('Please give 2 Urls inside website you visited from step 5').get_decision().no_of_ad_links_req, 2)
        self.assertEqual(
            Ai('Follow the step 4 to submit proof 3', test_mode=True).get_decision().no_of_ad_links_req, 0)

    def test_get_http_links(self):
        self.assertEqual(Ai.get_http_links('go to https://t.me/do-it and visit 4 pages'), ['https://t.me/do-it'])
        self.assertEqual(Ai.get_http_links(' blog.rinide**.com'), [])
        self.assertEqual(
            Ai.get_http_links('go to https://www.google.com/do-it and visit 4 pages'), ['https://www.google.com/do-it'])
        self.assertEqual(
            Ai.get_http_links('go to https://google.com/do-it and visit 4 pages'), ['https://google.com/do-it'])
        self.assertEqual(
            Ai.get_http_links(
                'go to You l https://snipboard.io/5JlDwB.jpg and visit 4 pages'), ['https://snipboard.io/5JlDwB.jpg'])
        self.assertEqual(
            Ai.get_http_links(
                'URL proof in step 6 from: https://pastebin.com/raw/aW5vRR6U'), ['https://pastebin.com/raw/aW5vRR6U'])
        self.assertEqual(
            Ai.get_http_links('inside: https://bit.ly/step3-until-6-uaiq-g'), ['https://bit.ly/step3-until-6-uaiq-g'])
        self.assertEqual(
            Ai.get_http_links('URL Proof 3 from: https://i.imgur.com/hCZLhsp.png'), ['https://i.imgur.com/hCZLhsp.png'])
        self.assertEqual(
            Ai.get_http_links('Submit Proof ( https://snipboard.io/YqCM8F.jpg )'), ['https://snipboard.io/YqCM8F.jpg'])
        self.assertEqual(Ai.get_http_links('step  2: https://bit.ly/3K5KA8e'), ['https://bit.ly/3K5KA8e'])
        self.assertEqual(Ai.get_http_links('step  2: https://bit.ly/3K5KA8e\n'), ['https://bit.ly/3K5KA8e'])
        self.assertEqual(Ai.get_http_links('step  2: https://bit.ly/3K5KA8e<br>'), ['https://bit.ly/3K5KA8e'])
        self.assertEqual(Ai.get_http_links(
            'step  2: https://salessoftwareofficer.blogspot.com/'), ['https://salessoftwareofficer.blogspot.com'])
        self.assertEqual(Ai.get_http_links(
            'open https://x99news.com/2022/02/05/the-best-latin-producer-of-hip-hop-and-reggaeton-called-mysterious/'),
            ['https://x99news.com/2022/02/05/the-best-latin-producer-of-hip-hop-and-reggaeton-called-mysterious'])
        self.assertEqual(Ai.get_http_links('step  2: https://prnt.sc/26q1bvh'), ['https://prnt.sc/26q1bvh'])


if __name__ == "__main__":
    unittest.main()

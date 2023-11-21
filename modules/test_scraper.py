import unittest
from scraper import Scraper
from video_maker import create_amazon_affiliate_description


class TestGetProductInfo(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()
        self.scraper.open_browser()

    def tearDown(self):
        self.scraper.browser.close()

    def test_get_product_info(self):
        product_url = 'https://www.amazon.com/dp/B00ZV9PXP2'
        title, description, images = self.scraper.get_product_info(product_url)
        self.assertNotEqual(title, '')
        self.assertNotEqual(description, '')
        self.assertGreater(len(images), 0)
        #print(title)
        print(description)
        video_script = create_amazon_affiliate_description(title, description)
        self.assertNotEqual(video_script, None)

        print(video_script)
    def test_get_product_links(self):
        url = "https://www.amazon.co.uk/cool-gadgets/s?k=cool+gadgets"
        urls = self.scraper.get_product_links(url)
        self.assertGreater(len(urls), 0)



if __name__ == '__main__':
    unittest.main()
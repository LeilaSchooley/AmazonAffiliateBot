import unittest

from scraper import get_product_info


class TestGetProductInfo(unittest.TestCase):
    def test_get_product_info(self):
        product_url = 'https://www.amazon.com/dp/B00ZV9PXP2'
        title, description, images = get_product_info(product_url)
        self.assertNotEqual(title, '')
        self.assertNotEqual(description, '')
        self.assertGreater(len(images), 0)

if __name__ == '__main__':
    unittest.main()
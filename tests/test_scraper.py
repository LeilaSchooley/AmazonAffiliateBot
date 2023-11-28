import unittest
import asyncio
from scraper import Scraper

class TestGetProductInfo(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.scraper = Scraper()
        await self.scraper.open_browser(use_state_file=False)

    async def asyncTearDown(self):
        await self.scraper.close_browser()

    async def test_get_product_info(self):
        product_url = 'https://www.amazon.com/dp/B00ZV9PXP2'
        title, description, images, link = await self.scraper.get_product_info(product_url)
        self.assertNotEqual(title, '')
        self.assertNotEqual(description, '')
        self.assertNotEqual(link, '')
        self.assertGreater(len(images), 0)

    @unittest.skip('Work in progress')
    async def test_get_product_links(self):
        url = "https://www.amazon.co.uk/cool-gadgets/s?k=cool+gadgets"
        urls = await self.scraper.get_product_links(url)
        self.assertGreater(len(urls), 0)

if __name__ == '__main__':
    unittest.main()

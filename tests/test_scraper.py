import os
import unittest
import asyncio

import pandas as pd

from modules.scraper import Scraper


class TestGetProductInfo(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.scraper = Scraper()
        await self.scraper.open_browser(use_state_file=False)

    async def asyncTearDown(self):
        await self.scraper.close_browser()

    async def test_get_product_info(self):
        try:
            product_url = 'https://www.amazon.com/Flask-Narrow-Mouth-Sports-Bottle/dp/B082H6BVFG?crid=FSABEHAGFGDU&keywords=water%2Bbottle&qid=1701314983&sprefix=w%2Caps%2C57&sr=8-15&linkCode=sl1&tag=iphonearmy-20&linkId=b61441eff3cc8c91ffeec225dea37ff3&language=en_US&ref_=as_li_ss_tl&th=1'
            title, description, images, link = await self.scraper.get_product_info(product_url)
            self.assertNotEqual(title, '')
            self.assertNotEqual(description, '')
            self.assertNotEqual(link, '')
            self.assertGreater(len(images), 0)
        finally:
            # Ensure the browser is closed even if the test fails
            await self.scraper.close_browser()

    async def test_get_product_links(self):
        try:
            keyword = "gadgets"
            url = "https://www.amazon.com/cool-gadgets/s?k=cool+gadgets"
            urls = await self.scraper.get_product_links_from_search(url, max_links=20,keyword=keyword )

            assert len(urls) >= 20, "The length of 'urls' should be 200 or more."

            for url in urls:
                print(url)
        finally:
            # Ensure the browser is closed even if the test fails
            await self.scraper.close_browser()

    async def test_extract_product_data_and_save_to_csv(self):
        # Initialize your Scraper
        keyword = "gadgets"
        max_links = 10

        # Define the search URL and maximum number of product links
        url = "https://www.amazon.com/cool-gadgets/s?k=cool+gadgets"

        # Get product links from the search URL
        product_links = await self.scraper.get_product_links_from_search(url, max_links=max_links, keyword=keyword)

        # Gather product details using the gathered links
        product_details = await self.scraper.gather_product_details(product_links)

        # Convert product details to a pandas DataFrame
        df = pd.DataFrame(product_details)

        # Assert that the DataFrame has data
        self.assertNotEqual(df.empty, True)

        # Define the CSV file path
        csv_file_path = "product_data.csv"

        # Write the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)

        # Assert that the CSV file has been created
        self.assertTrue(os.path.exists(csv_file_path))


if __name__ == '__main__':
    unittest.main()

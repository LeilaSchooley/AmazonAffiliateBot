import asyncio
from playwright.async_api import async_playwright

class Scraper:
    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None
        self.context = None

    async def open_browser(self):
        async with async_playwright() as p:
            self.p = p
            self.browser = await p.firefox.launch(headless=False)
            self.page = await self.browser.new_page()

    async def get_product_info(self, product_url):
        await self.page.goto(product_url)
        title = await self.page.locator('#productTitle').text_content()
        try:
            description = await self.page.locator('[data-feature-name="productDescription"]').text_content()
        except:
            description = await self.page.locator('#feature-bullets').text_content()

        images = await self.page.locator_all('img[src*="media-amazon.com"]')
        image_links = [await image.get_attribute('src') for image in images]
        return title.strip(), description.strip(), image_links

    async def get_product_links(self, url):
        await self.page.goto(url)
        product_links = await self.page.locator_all('a[href*="/dp/"]')
        unique_links = list(set([await link.get_attribute('href') for link in product_links]))
        return unique_links

    async def close_browser(self):
        await self.browser.close()

from playwright.sync_api import sync_playwright


class Scraper:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = None
        self.page = None
        self.context = None

    def open_browser(self):
        self.browser = self.p.firefox.launch(headless=True)
        self.page = self.browser.new_page()

    def get_product_info(self, product_url):
        self.page.goto(product_url)
        title = self.page.query_selector('#productTitle').text_content().strip()
        try:
            description = self.page.query_selector('[data-feature-name="productDescription"]').text_content().strip()
        except:
            description = self.page.query_selector('#feature-bullets').text_content()

        images = self.page.query_selector_all('img[src*="media-amazon.com"]')
        image_links = [image.get_attribute('src') for image in images]
        return title, description, image_links

    def get_product_links(self, url):
        self.page.goto(url)
        product_links = self.page.query_selector_all('a[href*="/dp/"]')
        unique_links = list(set([link.get_attribute('href') for link in product_links]))
        return unique_links

    def close_browser(self):
        self.browser.close()

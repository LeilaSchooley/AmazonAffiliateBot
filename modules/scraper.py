import requests
from playwright.sync_api import sync_playwright

import os
import requests


def check_if_file_exists(path):
    return os.path.isfile(path)


login_bot_file = "state.json"

def download_images(images, folder_path):
    if not os.path.exists(folder_path):

        os.makedirs(folder_path)
    print(os.path.exists(folder_path))
    filenames = []
    for idx, image_url in enumerate(images):
        filename = os.path.join(folder_path, f'image_{idx}.jpg')
        filenames.append(filename)

        print(f'Downloading {filename}...')
        response = requests.get(image_url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return filenames



class Scraper:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = None
        self.page = None
        self.context = None
        self.headless= False



    def save_login(self, context):
        print("Please login manually!")
        self.page.pause()
        context.storage_state(path=login_bot_file)
        print("Saved login!")

    def pause(self):
        self.page.pause()

    def open_browser(self):
        self.browser = self.p.firefox.launch(headless=self.headless)
        if check_if_file_exists(login_bot_file):

            self.context = self.browser.new_context(storage_state=login_bot_file)
        else:
            self.context = self.browser.new_context()

        self.context.set_default_timeout(15000)  # set timeout of 10 seconds
        self.page = self.context.new_page()
        self.page.goto("https://studio.youtube.com/")

        if "continue to" in self.page.content():
            self.save_login(self.context)
    def get_product_info(self, product_url):
        self.page.goto(product_url)
        title = self.page.query_selector('#productTitle').text_content().strip()
        try:
            description = self.page.query_selector('[data-feature-name="productDescription"]').text_content().strip()
        except:
            description = self.page.query_selector('#feature-bullets').text_content()

        element_selector = '.review-with-images-section'
        js_code = f'document.querySelector("{element_selector}").remove();'
        self.page.evaluate(js_code)

        images = self.page.query_selector_all('img.a-dynamic-image')
        image_links = [image.get_attribute('src') for image in images]


        return title, description, image_links

    def get_product_links(self, url):
        self.page.goto(url)
        product_links = self.page.query_selector_all('a[href*="/dp/"]')

        unique_links = [f'https://www.amazon.co.uk{link.get_attribute("href")}' for link in set(product_links)]
        return unique_links

    def create_affiliate_links(self, urls):
        for url in urls:
            self.page.goto(url)

            # Click the first selector
            self.page.click("#amzn-ss-text-link > span:nth-child(1) > strong:nth-child(1) > a:nth-child(1)")

            # Wait for the second selector to appear and get its text
            shortlink_textarea = self.page.wait_for_selector("#amzn-ss-text-shortlink-textarea")
            shortlink = shortlink_textarea.inner_text()
            print(shortlink)
    def close_browser(self):
        self.browser.close()

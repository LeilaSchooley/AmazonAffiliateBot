from playwright.sync_api import sync_playwright

    def get_product_info(product_url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(product_url)
            title = page.query_selector('#productTitle').text_content().strip()
            try:
            description = page.query_selector('[data-feature-name="productDescription"]').text_content().strip()
        except:
            description = page.query_selector('#feature-bullets').text_content()
        images = page.query_selector_all('img[src*="media-amazon.com"]')
        image_links = [image.get_attribute('src') for image in images]
        browser.close()
    return title, description, image_links
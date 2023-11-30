import asyncio
from playwright.async_api import async_playwright
import os
import re
import time
import traceback
import requests

from playwright.async_api import async_playwright, expect

import asyncio
import os
import time
import random

login_bot_file = os.path.join(os.path.dirname(__file__), 'state.json')


async def stop_browser(profile_id):
    for _ in range(15):
        try:
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop")
            return response.json()
        except Exception as e:
            print(f"Error stopping browser: {e}")
            await asyncio.sleep(1)


async def get_all_profiles(token):
    url = "https://anty-api.com/browser_profiles/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    for _ in range(15):
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error getting profiles: {e}")
            await asyncio.sleep(1)


async def launch_browser(token, id):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    for _ in range(15):
        try:
            response = requests.get(f"http://localhost:3001/v1.0/browser_profiles/{id}/start?automation=1",
                                    headers=headers)
            data = response.json()
            endpoint = data["automation"]["wsEndpoint"]
            port = data["automation"]["port"]
            return endpoint, port
        except Exception as e:
            print(f"Error launching browser: {e}")
            await asyncio.sleep(1)


async def login_dolphin():
    url = "https://anty-api.com/auth/login"
    payload = {'username': os.environ["DOLPHIN_LOGIN"], 'password': os.environ["DOLPHIN_PASSWORD"]}
    for _ in range(15):
        try:
            response = requests.post(url, data=payload)
            return response.json()["token"]
        except Exception as e:
            print(f"Error logging in: {e}")
            await asyncio.sleep(1)


class Scraper:
    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None
        self.context = None

        self.profile_id = "193419429"  # Retrieve the profile ID as needed

    async def launch_browser_playwright_dolphin(self, port, endpoint):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.connect_over_cdp(f"ws://127.0.0.1:{port}{endpoint}")
        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]
        return self.page

    async def open_browser(self, use_state_file):
        self.p = await async_playwright().start()
        self.browser = await self.p.firefox.launch(headless=False)

        # Dolphin code to launch the browser
        token = await login_dolphin()

        print(await get_all_profiles(token))
        endpoint, port = await launch_browser(token, self.profile_id)
        self.page = await self.launch_browser_playwright_dolphin(port, endpoint)


    async def get_current_page_number(self):
        # Get the current URL
        current_url = self.page.url
        # Extract the page number from the URL
        match = re.search(r'page=(\d+)', current_url)
        if match:
            # Return the page number as an integer
            return int(match.group(1))
        else:
            # If 'page=' is not in the URL, assume it's page 1
            return 1

    async def navigate_to_next_page(self):
        current_page_number = await self.get_current_page_number()
        next_page_number = current_page_number + 1

        # Fetch all links that contain 'page=' in their href attribute
        page_links_locator = self.page.locator('a[href*="page="]')
        page_links = await page_links_locator.evaluate_all('elements => elements.map(e => e.href)')

        # Filter the link that contains the desired next page number
        next_page_link = next(filter(lambda link: f"page={next_page_number}" in link, page_links), None)

        if next_page_link:
            try:
                await self.page.goto(next_page_link)  # Navigate using page.goto
                await self.page.wait_for_load_state("load")
                print(f"Successfully navigated to page {next_page_number}")
                return True
            except Exception as e:
                print(f"Error navigating to page {next_page_number}: {e}")
        else:
            print(f"No link found for page {next_page_number}")

        return False

    async def gather_product_details(self, links):
        products_data = []

        for link in links:
            title, description, image_links, affiliate_link = await self.get_product_info(link)
            products_data.append({
                "title": title,
                "description": description,
                "image_links": image_links,
                "affiliate_link": affiliate_link
            })

        return products_data
    async def get_product_links_from_search(self, search_url, max_links):
        product_links = set()  # Use a set to store unique links
        unique_ids = set()  # Keep track of unique product IDs
        keyword = "bottle"
        await self.page.goto(search_url)

        while len(product_links) < max_links:
            new_links = await self.page.locator('a[href*="/dp/"]').all()

            for link in new_links:
                href = await link.get_attribute('href')
                if "/dp/" in href and keyword in href and "customerReviews" not in href:
                    # Extract the unique product identifier
                    product_id = href.split('/dp/')[1].split('/')[0]
                    if product_id not in unique_ids:
                        unique_ids.add(product_id)
                        product_links.add(f"https://amazon.com{href}")

                # Break if reached max_links
                if len(product_links) >= max_links:
                    break

            await self.navigate_to_next_page()

        return list(product_links)[:max_links]  # Convert set back to list and limit to max_links

    async def get_product_info(self, product_url):
        try:
            await self.page.goto(product_url)
            # Instead of this:
            # title = await self.page.locator('#productTitle').first().text_content()

            # Use this for the title
            title_locator = self.page.locator('#productTitle')
            title = await title_locator.first.text_content()
            if title:
                title = title.strip()
                print("Title:", title)
            else:
                print("Title element not found")
            # Use this for the description
            description_locator = self.page.locator("#productDescription")
            description_count = await description_locator.count()

            if description_count > 0:
                description = await description_locator.first.text_content()
            else:
                description = await self.page.locator('#feature-bullets').text_content()

            if description:
                description = description.strip()
            print(description)

            await self.page.get_by_role("link", name="Text", exact=True).click()
            time.sleep(3)
            # Use querySelector to select the element by its class name

            element = await self.page.query_selector('.amzn-ss-text-shortlink-textarea')

            # Get the text content of the selected element
            if element:
                element_text = await element.text_content()
                print("Text content of the element:", element_text)
            else:
                print("Element not found")

            # Create a locator for all image elements
            image_elements_locator = self.page.locator('img[src*="media-amazon.com"]')

            # Get the number of elements
            image_count = await image_elements_locator.count()

            # Iterate through the elements and get their 'src' attributes
            image_links = []
            for i in range(image_count):
                image_element = image_elements_locator.nth(i)
                src = await image_element.get_attribute('src')
                image_links.append(src)

            # Now image_links contains the src attributes of all images

            return title, description, image_links, element_text
        except Exception:
            traceback.print_exc()

            await stop_browser(self.profile_id)

    async def pause(self):
        await self.page.pause()

    async def close_browser(self):
        # Save the state before closing the browser

        # Close the browser and cleanup
        await self.browser.close()
        await self.p.stop()

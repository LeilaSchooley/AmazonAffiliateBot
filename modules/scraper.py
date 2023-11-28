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

from modules.poster import check_if_file_exists

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


class Scraper:
    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None
        self.context = None

        self.profile_id = "193419429"  # Retrieve the profile ID as needed
    async def login_dolphin(self):
        url = "https://anty-api.com/auth/login"
        payload = {'username': os.environ["DOLPHIN_LOGIN"], 'password': os.environ["DOLPHIN_PASSWORD"]}
        for _ in range(15):
            try:
                response = requests.post(url, data=payload)
                return response.json()["token"]
            except Exception as e:
                print(f"Error logging in: {e}")
                await asyncio.sleep(1)

    async def launch_browser_playwright_dolphin(self, port, endpoint):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.connect_over_cdp(f"ws://127.0.0.1:{port}{endpoint}")
        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]
        return self.page

    async def open_browser(self, use_state_file):
        self.p = await async_playwright().start()
        self.browser = await self.p.firefox.launch(headless=False)

        if use_state_file and check_if_file_exists(login_bot_file):
            self.context = await self.browser.new_context(storage_state=login_bot_file)
            self.context.set_default_timeout(15000)  # set timeout of 10 seconds
            self.page = await self.context.new_page()
            await self.page.goto("https://instagram.com/")
        else:
            # Dolphin code to launch the browser
            token = await self.login_dolphin()


            print(await get_all_profiles(token))
            endpoint, port = await launch_browser(token, self.profile_id)
            self.page = await self.launch_browser_playwright_dolphin(port, endpoint)

    async def get_product_links_from_search(self, search_url, max_links):
        product_links = []
        await self.page.goto(search_url)
        while len(product_links) < max_links:
            new_links = await self.page.locator_all('a[href*="/dp/"]')
            unique_links = list(set([await link.get_attribute('href') for link in new_links]))
            product_links.extend(unique_links)
            # Break if reached max_links
            if len(product_links) >= max_links:
                break
            # Click next page or scroll
            # Add logic here to navigate to the next page

            await self.page.get_by_role("link", name="Go to next page, page 2").click()

        return product_links[:max_links]

    async def save_login(self, context):
        print("Please login manually!")
        await self.page.get_by_role("button", name="Allow all cookies").click()
        await self.page.get_by_label("Phone number, username, or email").type(INSTAGRAM_USERNAME)
        await self.page.get_by_label("Password").type(INSTAGRAM_PASSWORD)
        await self.page.locator("div").filter(has_text=re.compile(r"^Log in$")).first.click()

        await self.page.pause()
        await context.storage_state(path="state.json")
        print("Saved login!")

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
            description_locator = self.page.locator("[data-feature-name='productDescription']")
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


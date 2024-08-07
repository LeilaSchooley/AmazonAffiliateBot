import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def visit_url_with_stealth(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await stealth_async(page)  # Apply stealth settings
        await page.goto(url)
        # Perform other actions if needed
        await page.screenshot(path=f'screenshot-{url}.png')  # Take a screenshot
        await browser.close()

# List of URLs to visit
urls = [
    "https://example.com",
    "https://google.com",
    # Add more URLs here
]

# Create a list of coroutines for visiting URLs concurrently
coroutines = [visit_url_with_stealth(url) for url in urls]

# Run the coroutines concurrently using asyncio
asyncio.run(asyncio.gather(*coroutines))

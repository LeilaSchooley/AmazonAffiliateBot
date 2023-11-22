import asyncio
import os
from modules.scraper  import Scraper  # Import the Scraper class from your module


async def main():
    scraper = Scraper()  # Create an instance of the Scraper class
    try:
        await scraper.open_browser(use_state_file=False)  # Open the browser with state file
        # Perform login and save the login state (You need to implement this method)


        product_url = "https://www.amazon.com/Apple-MacBook-Chip-13-inch-512GB/dp/B08R2WTNQ6/ref=sr_1_1?keywords=Apple+MacBook+Air+13.3%22+%28512GB+SSD%2C+M1+Chip%2C+8GB%29+Laptop+-+Space+Grey+-+MGN73B%2FA&qid=1700658170&sr=8-1"  # Replace with the desired product URL


        title, description, image_links = await scraper.get_product_info(product_url)
        print("Product Title:", title)
        print("Product Description:", description)
        print("Image Links:", image_links)

        # search_url = "https://www.amazon.com/some-search-url"  # Replace with the desired search URL
        # product_links = await scraper.get_product_links(search_url)
        # print("Product Links:", product_links)

    except Exception as e:
        print("Error:", e)
    finally:
        await scraper.close_browser()  # Close the browser when done


if __name__ == "__main__":
    asyncio.run(main())

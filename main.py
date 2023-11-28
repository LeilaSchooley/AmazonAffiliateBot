import asyncio
import os
from modules.scraper  import Scraper  # Import the Scraper class from your module
import pandas as pd

from modules.upload_videos import upload_to_youtube


async def gather_product_details(links, scraper):
    products_data = []

    for link in links:
        title, description, image_links, affiliate_link = await scraper.get_product_info(link)
        products_data.append({
            "title": title,
            "description": description,
            "image_links": image_links,
            "affiliate_link": affiliate_link
        })

    return products_data
async def main():
    scraper = Scraper()  # Create an instance of the Scraper class
    try:
        await scraper.open_browser(use_state_file=False)  # Open the browser with state file
        # Perform login and save the login state (You need to implement this method)

        await scraper.pause()

        search_url = "https://www.amazon.com/Apple-MacBook-Chip-13-inch-512GB/dp/B08R2WTNQ6/ref=sr_1_1?keywords=Apple+MacBook+Air+13.3%22+%28512GB+SSD%2C+M1+Chip%2C+8GB%29+Laptop+-+Space+Grey+-+MGN73B%2FA&qid=1700658170&sr=8-1"  # Replace with the desired product URL
        product_links = await scraper.get_product_links_from_search(search_url, 10)  # Adjust the number as needed
        product_details = await gather_product_details(product_links, scraper)

        # Convert to a pandas DataFrame
        df = pd.DataFrame(product_details)
        print(df)
        # Write to a CSV file
        df.to_csv('product_data.csv', index=False)

    except Exception as e:
        print("Error:", e)

        await scraper.pause()
    finally:
        await scraper.close_browser()  # Close the browser when done

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        # Access columns by name
        column1 = row['column_name_1']  # Replace with your column name
        column2 = row['column_name_']

        await upload_to_youtube(scraper)



if __name__ == "__main__":
    asyncio.run(main())

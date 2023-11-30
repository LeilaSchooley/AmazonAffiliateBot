import asyncio
import os
from modules.scraper  import Scraper  # Import the Scraper class from your module
import pandas as pd

from modules.upload_videos import upload_to_youtube



async def main():
    scraper = Scraper()  # Create an instance of the Scraper class
    try:
        await scraper.open_browser(use_state_file=False)  # Open the browser with state file
        # Perform login and save the login state (You need to implement this method)



        search_url = "https://www.amazon.com/s?k=water+bottle&crid=FSABEHAGFGDU&sprefix=w%2Caps%2C57&ref=nb_sb_ss_ts-doa-p_1_1"  # Replace with the desired product URL
        product_links = await scraper.get_product_links_from_search(search_url, 10)  # Adjust the number as needed
        product_details = await scraper.gather_product_details(product_links)

        # Convert to a pandas DataFrame
        df = pd.DataFrame(product_details)
        print(df)
        # Write to a CSV file
        df.to_csv('product_data.csv', index=False)


        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            # Access columns by name
            column1 = row['column_name_1']  # Replace with your column name
            column2 = row['column_name_']

            await upload_to_youtube(scraper)


    except Exception as e:
        print("Error:", e)

        await scraper.pause()
    finally:
        await scraper.close_browser()  # Close the browser when done



if __name__ == "__main__":
    asyncio.run(main())

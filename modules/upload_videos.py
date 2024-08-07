import glob
import os
import time
from tinytag import TinyTag
from playwright.sync_api import sync_playwright


async def upload_to_youtube(page):
    page.goto("https://studio.youtube.com/")

    print("Starting upload")
    for video in glob.glob("../completed_videos/*.mp4"):
        try:
            page.click("#create-icon")
            page.click('text=Upload videos')
            page.set_input_files('input[type="file"]', video)
            time.sleep(5)  # Time for file processing

            if "Verify that it's you" in page.content():
                print("Please complete verification and restart script!")
                time.sleep(3000)
                continue

            if "Daily upload limit reached" in page.content():
                print("Upload limit reached!")
                break

            page.fill('textarea[aria-label="Title"]', TinyTag.get(video).title)
            page.click('text=No, it’s not "Made for Kids"')
            page.click('text=Next', timeout=5000)
            page.click('text=Next', timeout=5000)
            page.click('text=Public')
            page.click('text=Publish')

            print(f"Uploaded video: {TinyTag.get(video).title}")

        except Exception as e:
            print(f"Error during upload: {e}")
            page.pause()

        print("Waiting for 15 seconds before next upload.")
        time.sleep(15)

    print("Completed all uploads.")
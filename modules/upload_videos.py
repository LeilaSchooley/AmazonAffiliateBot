import glob
import os
import time
from tinytag import TinyTag
from playwright.sync_api import sync_playwright

class InstagramBot:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = None
        self.page = None
        self.context = None

    def open_browser(self):
        self.browser = self.p.firefox.launch(headless=False)
        self.context = self.browser.new_context(storage_state='state.json') if os.path.isfile('state.json') else self.browser.new_context()
        self.context.set_default_timeout(15000)
        self.page = self.context.new_page()
        self.page.goto("https://studio.youtube.com/")
        if "continue to" in self.page.content():
            self.save_login()

    def save_login(self):
        print("Please login manually!")
        self.page.pause()
        self.context.storage_state(path='state.json')
        print("Saved login!")

    def upload_to_youtube(self):
        print("Starting upload")
        for video in glob.glob("../completed_videos/*.mp4"):
            try:
                self.page.click("#create-icon")
                self.page.click('text=Upload videos')
                self.page.set_input_files('input[type="file"]', video)
                time.sleep(5)  # Time for file processing

                if "Verify that it's you" in self.page.content():
                    print("Please complete verification and restart script!")
                    time.sleep(3000)
                    continue

                if "Daily upload limit reached" in self.page.content():
                    print("Upload limit reached!")
                    break

                self.page.fill('textarea[aria-label="Title"]', TinyTag.get(video).title)
                self.page.click('text=No, it’s not "Made for Kids"')
                self.page.click('text=Next', timeout=5000)
                self.page.click('text=Next', timeout=5000)
                self.page.click('text=Public')
                self.page.click('text=Publish')

                print(f"Uploaded video: {TinyTag.get(video).title}")

            except Exception as e:
                print(f"Error during upload: {e}")
                self.page.pause()

            print("Waiting for 15 seconds before next upload.")
            time.sleep(15)

        print("Completed all uploads.")

    def close_browser(self):
        self.browser.close()


import glob
import os
import sys
import time
from tinytag import TinyTag
from playwright.sync_api import sync_playwright

video_folder_result = glob.glob(f"../completed_videos/*.mp4")


def check_if_file_exists(path):
    return os.path.isfile(path)


login_bot_file = "state.json"


class YoutubeUploader:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = None
        self.page = None
        self.context = None

    def check_for_copyright(self):
        html = self.page.content()

        if "Copyright claim found" in html:
            print("Copyright claim found! Skipping video!")

            try:
                self.page.click("ytcp-icon-button.ytcp-uploads-dialog:nth-child(3) > tp-yt-iron-icon:nth-child(1)")
            except:
                self.page.reload()
            return True
        return False




    def save_login(self, context):
        print("Please login manually!")
        self.page.pause()
        context.storage_state(path="state.json")
        print("Saved login!")

    def pause(self):
        self.page.pause()

    def open_browser(self):
        self.browser = self.p.firefox.launch(headless=False)
        if check_if_file_exists(login_bot_file):

            self.context = self.browser.new_context(storage_state=login_bot_file)
        else:
            self.context = self.browser.new_context()

        self.context.set_default_timeout(15000)  # set timeout of 10 seconds
        self.page = self.context.new_page()
        self.page.goto("https://studio.youtube.com/")

        if "continue to" in self.page.content():
            self.save_login(self.context)

    def check_for_limit(self):
        if "Daily upload limit reached" in self.page.content():
            print("Upload limit reached!")
            return True
        return False

    def upload_to_youtube(self):
        print("Starting upload")
        for video in video_folder_result:
            try:
                video_file_info = TinyTag.get(video)
                video_file_tags = video_file_info.title

                self.page.click("#create-icon")
                time.sleep(1)
                self.page.get_by_role("menuitem", name="Upload videos").click()
                elem = self.page.query_selector("//input[@type='file']")

                time.sleep(3)
                elem.set_input_files(video)

                if "Verify that it's you" in self.page.content():
                    print("Please complete verification and restart script!")
                    time.sleep(3000)

                time.sleep(3)

                limit = self.check_for_limit()

                if limit:
                    return

                time.sleep(3)

                try:
                    title = self.page.wait_for_selector("#textbox")
                    title.focus()
                    title.fill("test")
                    title.type("dddd")

                except:
                    pass
                self.page.get_by_role("radio", name="No, it's not 'Made for Kids'").click()

                self.page.click("#step-badge-3")
                time.sleep(2)

                try:
                    self.page.click(
                        "tp-yt-paper-radio-button.style-scope:nth-child(19) > div:nth-child(1) > div:nth-child(1)")
                except:
                    self.page.click(
                        "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[1]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]")
                time.sleep(2)

                html = self.page.content()
                while "Checks complete" not in html:
                    time.sleep(5)
                    html = self.page.content()

                copyright = self.check_for_copyright()
                if not copyright:
                    # Publish button
                    try:
                        self.page.click("#done-button > div:nth-child(2)")
                    except:
                        pass
                    try:
                        self.page.click("ytcp-button.ytcp-video-share-dialog")
                    except:
                        pass
                    print("Uploaded video!")
            except Exception as e:
                print(e)
                self.page.pause()

            print("Uploaded videos! Quitting in 15 seconds.")

            time.sleep(15)



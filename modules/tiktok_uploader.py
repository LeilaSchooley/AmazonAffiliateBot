import glob
import os
import sys
import time
from tinytag import TinyTag
from playwright.sync_api import sync_playwright

video_folder_result = glob.glob(f"../completed_videos/*.mp4")


def check_if_file_exists(path):
    return os.path.isfile(path)


login_bot_file = "tiktok.json"


class TiktokUploader:
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

    def login(self):

        self.page.get_by_role("button", name="Decline all").click()
        self.page.get_by_role("link", name="Use phone / email / username").get_by_role("link",
                                                                                       name="Use phone / email / username",
                                                                                       exact=True).filter(
            has_text="Use phone / email / username").click()
        self.page.get_by_role("link", name="Log in with email or username").click()
        self.page.get_by_placeholder("Email or username").click()
        self.page.get_by_placeholder("Email or username").click(modifiers=["Control"])
        self.page.get_by_placeholder("Email or username").fill("iphone_army")
        self.page.get_by_placeholder("Password").click()
        self.page.get_by_placeholder("Password").fill("Brjdo039@")

        self.page.get_by_role("dialog", name="Log in").get_by_role("button", name="Log in").click()

    def save_login(self, context):
        print("Please login manually!")
        self.page.pause()
        context.storage_state(path=login_bot_file)
        print("Saved login!")

    def pause(self):
        self.page.pause()

    def solve_captcha(self):
        self.page.locator("#secsdk-captcha-drag-wrapper div").nth(1).click()
        self.page.locator("#secsdk-captcha-drag-wrapper div").nth(1).click()
        self.page.locator(".sc-ckVGcZ").click()
        self.page.locator(".sc-ckVGcZ").click()

    def open_browser(self):
        self.browser = self.p.firefox.launch(headless=False)
        if check_if_file_exists(login_bot_file):

            self.context = self.browser.new_context(storage_state=login_bot_file)
        else:
            self.context = self.browser.new_context()

        self.context.set_default_timeout(15000)  # set timeout of 10 seconds
        self.page = self.context.new_page()
        self.page.goto("https://tiktok.com/")
        self.page.wait_for_load_state("networkidle")
        if "Log in to TikTok" in self.page.content():
            self.save_login(self.context)

    def check_for_limit(self):
        if "Daily upload limit reached" in self.page.content():
            print("Upload limit reached!")
            return True
        return False

    def upload_video(self):
        print("Starting upload")
        for video in video_folder_result:
            try:
                video_file_info = TinyTag.get(video)
                video_file_tags = video_file_info.title

                time.sleep(3)

                self.page.get_by_role("link", name="Upload a video").click()
                self.page.frame_locator("iframe").get_by_role("button", name="Select file").click()
                self.page.frame_locator("iframe").get_by_role("combobox").locator("div").nth(2).click()
                self.page.frame_locator("iframe").locator("div:nth-child(2) > .tiktok-switch__switch-wrapper").click()
                self.page.frame_locator("iframe").get_by_role("button", name="Select file")
                self.page.frame_locator("iframe").get_by_role("button", name="Select file").set_input_files(
                    "output_video.mp4")
                self.page.frame_locator("iframe").get_by_role("button", name="Post").click()

                print("Uploaded video!")
            except Exception as e:
                print(e)
                self.page.pause()

            print("Uploaded videos! Quitting in 15 seconds.")

            time.sleep(15)

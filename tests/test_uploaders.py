import unittest
from modules.youtube_uploader import YoutubeUploader
from modules.tiktok_uploader import TiktokUploader


class TestUploader(unittest.TestCase):

    def test_upload_to_youtube(self):
        # Test that the YouTube upload function completes without raising any exceptions
        self.youtube_uploader = YoutubeUploader()

        self.youtube_uploader.open_browser()
        self.youtube_uploader.upload_to_youtube()
        self.youtube_uploader.browser.close()

    def test_upload_to_tiktok(self):
        # Test that the TikTok upload function completes without raising any exceptions
        self.tiktok_uploader = TiktokUploader()
        self.tiktok_uploader.open_browser()

        self.tiktok_uploader.upload_video()


if __name__ == '__main__':
    unittest.main()

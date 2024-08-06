import unittest
from modules.scraper import Scraper, download_images
from modules.video_maker import create_amazon_affiliate_description, create_video_with_voiceover


class TestGetProductInfo(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()
        self.scraper.open_browser()

    def tearDown(self):
        self.scraper.browser.close()

    def test_get_product_info_and_create_video(self):
        product_url = 'https://www.amazon.com/dp/B00ZV9PXP2'
        title, description, images = self.scraper.get_product_info(product_url)
        self.assertNotEqual(title, '')
        self.assertNotEqual(description, '')
        self.assertGreater(len(images), 0)
        # print(title)
        print(description)
        print(images)
        folder_path = './images/'
        downloaded_filenames = download_images(images, folder_path)
        # self.assertNotEqual(video_script, None)

    def test_create_video(self):
        title = ' Acer Aspire Vero AV15-51-7617 Green PC | 15.6" FHD IPS 100% sRGB-Display | 11th Gen Intel Core i7-1195G7 | Intel Iris Xe Graphics | 16GB DDR4 | 512GB NVMe SSD | Wi-Fi 6 | PCR Materials | Vero-Sleeve '
        description = "All-new design is thinner and lighter, and now available in your choice of black or white.     With built-in Audible, access the world’s largest library of audiobooks. Easily switch between reading and listening on Bluetooth-enabled speakers or headphones.     Easy on your eyes—touchscreen display reads like real paper.     No screen glare, even in bright sunlight, unlike tablets.     Keep reading—a single charge lasts weeks, not hours.     Get lost in your story with no alerts or notifications.     Instant access to new releases and bestsellers, or from over a million titles at $2.99 or less. Prime members read free with unlimited access to over a thousand titles.     Looking for a light? Try Kindle Paperwhite."

        # video_script = create_amazon_affiliate_description(title, description)

        create_video_with_voiceover('../data/video_script.txt', "../images/image.jpg", '../data/music.mp3',
                                    "../videos/output_video.mp4")

    def test_create_affiliate_links(self):
        url = "https://www.amazon.co.uk/cool-gadgets/s?k=cool+gadgets"
        # urls = self.scraper.get_product_links(url)
        urls = ["https://www.amazon.com/dp/B00ZV9PXP2"]

        links = self.scraper.create_affiliate_links(urls)

        self.assertGreater(len(urls), 0)
        self.assertGreater(len(links), 0)


if __name__ == '__main__':
    unittest.main()

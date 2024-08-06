from modules.scraper import Scraper
from modules.tiktok_uploader import TiktokUploader
from modules.youtube_uploader import YoutubeUploader

scraper = Scraper()
scraper.open_browser()
url = "https://www.amazon.co.uk/cool-gadgets/s?k=cool+gadgets"
urls = scraper.get_product_links(url)
print(urls)



"""
video_script = create_amazon_affiliate_description(title, description)

create_video_with_voiceover('../data/video_script.txt', "../images/image.jpg", '../data/music.mp3',
                            "../videos/output_video.mp4")



"""
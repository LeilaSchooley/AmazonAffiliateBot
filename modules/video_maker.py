import configparser
import os

import openai
from TTS.api import TTS
from moviepy.editor import *

config_path = os.path.join(os.path.dirname(__file__), '../', 'data/' 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

COQUI_STUDIO_TOKEN = config["DEFAULT"]["COQUI_STUDIO_TOKEN"]
OPENAI_API_KEY = config["DEFAULT"]["OPENAI_API_KEY"]

os.environ['COQUI_STUDIO_TOKEN'] = COQUI_STUDIO_TOKEN
openai.api_key = OPENAI_API_KEY

# nltk.download('punkt')

MAX_TRIES = 3


def create_amazon_affiliate_description(title, keyword):
    generated_text = None
    prompt = f"Generate ONE tiktok advertising script to promote the product {title} using the source content {keyword}." \
             f"Make sure to mention how it will help apeople, make it no longer than 90 words"
    message = {
        "role": "user",
        "content": prompt
    }
    for _ in range(MAX_TRIES):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[message]
            )

            generated_text = response['choices'][0]['message']['content'].strip()

            # Save response to a text file
            with open('video_script.txt', 'w', encoding='utf-8') as f:
                f.write(generated_text)

            break
        except Exception as e:
            print(e)

            continue

    return generated_text

def create_video_with_voiceover(video_script_path, background_image_path, background_music_path, output_path):
    # Select the model for text-to-speech conversion
    model_name = TTS.list_models()[12]
    # Create an instance of the selected text-to-speech model
    tts = TTS(model_name)

    # Open the text file containing the video script, and read the contents
    with open(video_script_path, 'r', encoding='utf-8') as f:
        video_script = f.read()

    # Convert the video script to an audio file using the selected text-to-speech model
    tts.tts_to_file(text=video_script, file_path="../data/voiceover.wav")
    # Load the newly created audio file, and adjust the volume of the background music
    voiceover = AudioFileClip("../data/voiceover.wav")

    # Load the background music and set its duration to the voiceover's duration + 4 seconds
    background_music = AudioFileClip(background_music_path).volumex(0.2).set_duration(voiceover.duration + 4)

    new_audioclip = CompositeAudioClip([
        voiceover,
        background_music
    ])

    # Load the image file that will be used as the background of the final clip
    background_image = ImageClip(background_image_path)
    # Determine the dimensions of the image, and calculate the desired width based on the aspect ratio of 16:9
    width, height = background_image.size
    new_width = int(height * 16/9)
    # Crop the image to the desired width, centered horizontally
    clip = background_image.crop(x1=(width - new_width) / 2, x2=(width - new_width) / 2 + new_width)
    # Set the audio of the cropped image to the adjusted background music and voiceover audio
    clip.audio = new_audioclip
    # Set the duration of the video clip to be the same as the background music
    clip.duration = background_music.duration

    # Write the final video clip to disk
    clip.write_videofile(output_path, fps=24)

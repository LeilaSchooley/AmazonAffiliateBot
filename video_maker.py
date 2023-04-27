import math
import os
import random
from moviepy.editor import VideoFileClip
import openai
import requests
from gtts import gTTS
from moviepy.editor import *
import re

PEXELS_API_KEY = 'HrgherDGAVcPKSpQBdgqxii7Uy79NsLoos9FUcOGxKnerpU4jy2ih2gC'

VIDEO_DURATION = 60  # Desired duration of video in seconds
VIDEO_COUNT = 5  # Desired number of videos
MAX_TRIES = 3


class VideoCreator:
    openai.api_key = "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"

    @staticmethod
    def replace_numbers(string):
        # Define regular expression pattern to match all numbers
        pattern = r'\d+'
        # Replace all numbers in string with the word "NUMBER"
        new_string = re.sub(pattern, '', string)
        return new_string

    @staticmethod
    def download_pexels_videos(keyword, num_videos):
        url = f'https://api.pexels.com/videos/search?query={keyword}&per_page=40'
        headers = {'Authorization': PEXELS_API_KEY}
        total_videos_downloaded = 0
        # create a folder with the keyword name if it doesn't exist
        folder_name = keyword.replace(" ", "_")
        folder_path = os.path.join(folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        while total_videos_downloaded < num_videos:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                videos = data['videos']
                for video in videos:
                    if total_videos_downloaded >= num_videos:
                        break
                    video_url = video['video_files'][-1]['link']
                    video_id = video['id']
                    video_filename = f'{folder_path}/{keyword}_{video_id}.mp4'
                    response = requests.get(video_url)
                    if response.status_code == 200:
                        with open(f"{video_filename}", 'wb') as f:
                            f.write(response.content)
                            total_videos_downloaded += 1
                            print(f'Downloaded video {total_videos_downloaded}: {video_filename}')
            else:
                print(f'Error fetching data from Pexels API. Status code: {response.status_code}')
                break
            next_page = data['next_page']
            if not next_page:
                break
            url = next_page
        print(f"Downloaded {total_videos_downloaded} videos to {folder_path}")

    def get_random_videos(self, folder_path, total_duration):
        # Get all files in the folder
        all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        # Filter video files by extension (you may add more video extensions if needed)
        video_files = [f for f in all_files if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        # Shuffle the list of video files
        random.shuffle(video_files)

        selected_videos = []
        selected_duration = 0

        # Select random videos until the total duration reaches or exceeds the specified length
        for video_file in video_files:
            video_path = os.path.join(folder_path, video_file)
            video_clip = VideoFileClip(video_path)
            if selected_duration <= total_duration:
                selected_videos.append(video_path)
                selected_duration += video_clip.duration
            else:
                break

        if selected_duration < total_duration:
            print(
                f"The total duration of selected videos is {selected_duration} seconds, which is shorter than the specified length of {total_duration} seconds.")

        return selected_videos

    def create_questions(self, keyword):
        generated_text = None
        prompt = f"Generate 2 unordered youtube keywords related to '{keyword} '"
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
                print(generated_text)

                break
            except:
                continue
        if generated_text:
            generated_text = self.replace_numbers(generated_text)
            generated_text = generated_text.replace("- ", "")
            generated_text = generated_text.replace(". ", "")
            generated_text = [line for line in generated_text.split("\n")]
        return generated_text

    def create_answers(self, keyword, total_words):
        generated_text = None
        prompt = f"Generate a text with about {total_words} words on the topic: {keyword}."
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
                generated_text = response['choices'][0]['message']['content'].strip().split()
                break
            except:
                continue
        return generated_text

    def generate_text_and_images(self, prompt, video_length, words_per_second=2.5):
        total_words = int(video_length * words_per_second)
        message = {
            "role": "user",
            "content": f"Generate a text with about {total_words} words on the topic: {prompt}."
        }
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )
        generated_text = response['choices'][0]['message']['content'].strip()
        print(generated_text)
        # Split the generated text into smaller segments for each image
        num_images = math.ceil(total_words / 30)  # Assuming around 30 words per image
        words = generated_text.split()
        words_per_image = len(words) // num_images
        text_segments = [' '.join(words[i:i + words_per_image]) for i in range(0, len(words), words_per_image)]

        # Generate images for each text segment
        images = []
        for text in text_segments:
            response = openai.Image.create(
                prompt=f"Generate an image for the following description: {text}.",
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            images.append(image_url)

        return text_segments, images

    def generate_video(self, text_segments, media_files, output_file, resolution=(1280, 720)):
        fps = 24

        # Create voiceover
        if len(text_segments) > 1:
            voiceover_text = ' '.join(text_segments)
        else:
            voiceover_text = text_segments[0]

        tts = gTTS(voiceover_text, lang='en')
        tts.save('temp_voiceover.mp3')
        voiceover = AudioFileClip('temp_voiceover.mp3')

        # Calculate media durations based on voiceover length
        total_audio_duration = voiceover.duration
        media_duration = total_audio_duration / len(media_files)

        # Create media clips
        media_clips = []
        for media_file in media_files:
            if os.path.splitext(media_file)[1].lower() in ['.mp4', '.avi', '.mov', '.wmv']:
                video_clip = VideoFileClip(media_file).set_duration(media_duration).resize(resolution)
                video_clip = video_clip.resize(height=resolution[1])  # Maintain aspect ratio
                video_clip = video_clip.resize(width=resolution[0])  # Maintain aspect ratio
                video_clip = video_clip.set_audio(None)
                media_clips.append(video_clip)
            elif os.path.splitext(media_file)[1].lower() in ['.jpg', '.jpeg', '.png']:
                image_clip = ImageClip(media_file).set_duration(media_duration).resize(resolution)
                media_clips.append(image_clip)

        # Concatenate media clips
        final_media = concatenate_videoclips(media_clips).set_duration(total_audio_duration).set_fps(fps)
        final_media = final_media.set_audio(voiceover)

        # Save final video
        final_media.write_videofile(output_file, fps=fps, temp_audiofile='temp_audio.mp3', remove_temp=True,
                                    ffmpeg_params=['-preset', 'ultrafast', '-tune', 'fastdecode'])

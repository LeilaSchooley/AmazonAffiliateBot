import os
import moviepy.editor as mp
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import os
import datetime
import nltk
from TTS.api import TTS
from moviepy.editor import *
from nltk.tokenize import sent_tokenize
from moviepy.video.tools.subtitles import SubtitlesClip
import os
import openai


os.environ['COQUI_STUDIO_TOKEN'] = 'IyLxwjp58yobNeCbzYrk5I88G1myolV1Qy5xT37WCduDybw6DDilGwy1KlYBSrJS'
openai.api_key = "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"

nltk.download('punkt')

MAX_TRIES = 3

def create_amazon_affiliate_description(title, keyword):
    generated_text = None
    prompt = f"Generate ONE tiktok advertising script to promote the product {title} using the source content {keyword}." \
             f"Make sure to mention how it will help people"
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
            break
        except Exception as e:

            continue
    if not generated_text:
        print(response)
    return generated_text


def create_video_from_images(image_folder, output_file, fps=24, duration_between_images=1):
    image_list = sorted(os.listdir(image_folder))
    clip_list = []

    for image in image_list:
        if ".jpg" in image:
            full_path = os.path.join(image_folder, image)
            print(full_path)
            clip_list.append(mp.ImageClip(full_path).set_duration(duration_between_images))
    grid_clip = mp.clips_array([clip_list])
    final_clip = grid_clip.set_duration(duration_between_images * len(image_list)).set_fps(fps)
    final_clip.write_videofile(output_file)


def create_video_with_subtitles(video_script_path, background_video_path, background_music_path, output_path):
    # Download the 'punkt' module used for sentence tokenization if it has not already been downloaded
    nltk.download('punkt')

    # Select the model for text-to-speech conversion
    model_name = TTS.list_models()[12]
    # Create an instance of the selected text-to-speech model
    tts = TTS(model_name)
    # Open the text file containing the video script, and read the contents

    with open(video_script_path, 'r', encoding='utf-8') as f:
        video_script = f.read()

    # Convert the video script to an audio file using the selected text-to-speech model
    tts.tts_to_file(text=video_script, file_path="../data/voiceover.wav")
    # Load the newly created audio file
    new_audioclip = AudioFileClip("../data/voiceover.wav")
    if background_music_path:
        # Adjust the volume of the background music
        new_audioclip = CompositeAudioClip([
            AudioFileClip("../data/voiceover.wav"),
            AudioFileClip(background_music_path).volumex(0.2)
        ])
    # Load the video file that will be used as the background of the final clip
    video = VideoFileClip(background_video_path)
    # Determine the dimensions of the video, and calculate the desired width based on the aspect ratio of 16:9
    width, height = video.size
    new_width = int(height * 9 / 16)
    # Crop the video to the desired width, centered horizontally
    clip = video.crop(x1=(width - new_width) / 2, x2=(width - new_width) / 2 + new_width)
    # Set the audio of the cropped video to the adjusted background music and voiceover audio
    clip.audio = new_audioclip
    # Load the video file that will be used as the background of the final clip
    video = VideoFileClip(background_video_path)
    # Determine the dimensions of the video, and calculate the desired width based on the aspect ratio of 16:9
    width, height = video.size
    new_width = int(height * 9 / 16)
    # Crop the video to the desired width, centered horizontally
    clip = video.crop(x1=(width - new_width) / 2, x2=(width - new_width) / 2 + new_width)

    if new_audioclip:
        clip.audio = new_audioclip

    # Define a function to create subtitles for the video
    def subtitles(sentences):
        # Initialize an empty list to store the SRT file contents
        srt_lines = []
        # Initialize the start and end time to zero
        start = datetime.timedelta(seconds=0)
        end = datetime.timedelta(seconds=0)
        # Initialize a counter to keep track of subtitle numbers
        counter = 1
        # Loop over each sentence in the list of sentences passed to the function
        for sentence in sentences:
            # Split the sentence into words
            words = sentence.split()
            # Calculate the number of lines needed for this sentence (assuming each line has 4 words)
            num_lines = len(words) // 4 + 1
            # Loop over each line of the sentence
            for j in range(num_lines):
                # Get the words for this line
                line_words = words[j * 4: (j + 1) * 4]
                # Join the words into a single string to form the line
                line = ' '.join(line_words)
                # Calculate the end time for this line based on the length of the line
                end += datetime.timedelta(seconds=len(line_words) * 0.35)
                # Check if the line is not empty
                if line:
                    # Format the start and end times as  strings in the SRT format
                    start_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                        start.seconds // 3600,
                        (start.seconds // 60) % 60,
                        start.seconds % 60,
                        start.microseconds // 1000
                    )
                    end_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                        end.seconds // 3600,
                        (end.seconds // 60) % 60,
                        end.seconds % 60,
                        end.microseconds // 1000
                    )
                    # Add the subtitle number, start and end times, and line to the SRT list
                    srt_lines.append(str(counter))
                    srt_lines.append(start_str + ' --> ' + end_str)
                    srt_lines.append(line)
                    srt_lines.append('')
                    # Increment the subtitle counter
                    counter += 1
                    # Update the start time for the next line
                    start = end
                    # Join the lines of the SRT file into a single string
                    srt_file = '\n'.join(srt_lines)
                    # Write the SRT file to disk
                    with open("../data/subtitles.srt", "w") as f:
                        f.write(srt_file)

        # Call the 'subtitles' function with a list of sentences, which are obtained by tokenizing the video script

    subtitles(list(filter(None, (sent_tokenize(video_script)))))

    # Define a lambda function to generate the subtitle clips from the SRT file
    generator = lambda txt: TextClip(txt, font='Arial-Bold', fontsize=30, color='white', bg_color='rgba(0,0,0,0.4)')

    # Create the subtitle clip from the SRT file
    subtitle_source = SubtitlesClip("subtitles.srt", generator)

    # Get the height of the video and subtitle clip
    video_height = clip.size[1]

    # Calculate the position of the subtitle clip
    subtitle_y = video_height - 159  # adjust the value of 50 to move the subtitles up/down

    # Combine the video clip and the subtitle clip, and adjust the speed and length of the result

    clip = CompositeVideoClip([clip, subtitle_source.set_pos(('center', subtitle_y))]).speedx(factor=1.1).subclip(
        0, 60)
    # Write the final video clip to disk
    clip.write_videofile(output_path)


# create_video_from_images('./', 'output.mp4')

# Example usage with optional background music and voiceover

"""create_video_with_subtitles('video_script.txt', 'output.mp4',
                            'music.mp3', "output_video.mp4")
"""
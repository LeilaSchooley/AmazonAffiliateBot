import os
from moviepy.editor import TextClip, CompositeVideoClip, ImageClip, concatenate_videoclips, AudioFileClip
import pyttsx3

def create_video_with_tts(text, image_folder=None, filename="output.mp4", fontsize=24, color='white'):
    # Generate speech from text using pyttsx3
    tts = pyttsx3.init()
    tts_file = "temp_tts.mp3"
    tts.save_to_file(text, tts_file)
    tts.runAndWait()

    # Calculate the duration of the TTS file
    audio_clip = AudioFileClip(tts_file)
    tts_duration = audio_clip.duration

    clips = []
    if image_folder and os.path.isdir(image_folder):
        # Sort files in the folder and filter out non-image files
        image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])

        # Calculate duration per image based on total TTS duration
        duration_per_image = tts_duration / len(image_files)

        # Create a clip for each image
        for image in image_files:
            clip = ImageClip(image).set_duration(duration_per_image)
            clips.append(clip)

        # Concatenate all image clips
        video_clip = concatenate_videoclips(clips, method="compose")
    else:
        # Default to a text clip if no images are provided
        video_clip = TextClip(text, fontsize=fontsize, color=color, size=(640, 480)).set_duration(tts_duration)

    # Set the audio for the video clip
    final_video = CompositeVideoClip([video_clip.set_audio(audio_clip)])

    # Write the result to a file
    final_video.write_videofile(filename, fps=24)

    # Remove temporary audio file
    os.remove(tts_file)

# Example usage
text = """
m writing this post to let you know that we’re fully rolling back the changes made yesterday to the AUP and having them go through moderator review.

I also want to briefly talk about how it happened: much earlier this year - in May 2023, I received a preview copy of this from our legal team for community team review. I reviewed it personally, and thought it was okay to go out. To be explicit: I didn’t think there was anything in it that was a major change to how we operate the network and therefore did not flag it for any major risks or needs for broader community review (this was before we had agreements around it).

I was also out yesterday due to a holiday, but had already cleared the text to go out based on the above-mentioned review. After reading your comments around it, it’s clear to me that I missed a few key points on how the text reads rather than what it was intended to mean: to be clear, I think most of the issues flagged are not how we intended for this change set to be interpreted, but I understand that there is a difference between what we intended and how it reads. We’ll be re-working some of the text before presenting it to moderators.

Slate got handed this yesterday with little to no context of it because she was not a part of the review process; I was. She was further prompted with my notes that it had already received appropriate reviews and was going to be fairly trivial and non-controversial, which obviously was wrong. I want to personally apologize for the confusion this update caused and for it missing our agreement with the moderators: that’s on me. There are reasons for why it happened, but they do not excuse the fact that I dropped the ball to you all here and, for that, I apologize.

"""
image_folder = "./"  # Set to None if you don't want to use images
create_video_with_tts(text, image_folder)

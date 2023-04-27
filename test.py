import os
import moviepy.editor as mp
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

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

create_video_from_images('./', 'output.mp4')

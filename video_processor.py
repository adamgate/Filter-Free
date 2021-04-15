"""
File: video_processor.py
Author: Adam Applegate
Description: 

    Uses OpenCV to edit videos based on input from the UI
   
"""

import numpy as np
import cv2

class VideoProcessor():
    def __init__(self):
       super.__init__


    def filter_video(self, filter):
        video = cv2.VideoCapture(self.filename)

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video.get(cv2.CAP_PROP_FPS))

        video_writer = cv2.VideoWriter('temp/processed_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
        print('Processing video...')
         
        frame_num = 0
        while(video.isOpened()):
            ret, frame = video.read()

            if ret == True and frame_num <= frame_count:
                frame_num = frame_num + 1
                print(f'attempting to filter frame #{frame_num}')
                self.filter_image(filter, frame)

                image = np.array(self.current_media)
                cv_image = image.astype(np.uint8)


                cv2.imwrite('temp/frames/frame{}.png' .format(frame_num), cv_image)
                video_writer.write(cv_image)

            
            elif (frame_num == frame_count):
                print('Finished processing video.')
                break

            #If a frame isn't read properly, exit the loop
            else:
                print('Error reading file.')
                break

        print('Video processed!')
        video.release()
        video_writer.release()

        self.update_media('temp/processed_video.mp4')
"""
Course: CSS 353
File: filters.py
Author: Adam Applegate
Description: 

    Uses OpenCV to constuct photo and video filters
   
"""

import numpy as np
import cv2
from copy import deepcopy
import filters

class ImageProcessor():
    filename = None
    media_type = None
    original_media = None
    current_media = None

    undo_stack = None
    redo_Stack = None
    
    def __init__(self):
       super.__init__

       self.update_media('media/bird.jpg')

    def update_media(self, filename):
        """ A new file was loaded. Update the object accordingly """

        # Make sure a file was actually loaded
        if (filename is not None):
            # Update the filename
            self.filename = filename

            # Determine the filetype
            self.media_type = self.filename.split('.')[1]

            # It's an image
            if (self.media_type != 'mp4'):
                # Load the image
                self.original_media = cv2.imread(self.filename)

                # Set the correct color channels
                self.original_media = cv2.cvtColor(self.original_media, cv2.COLOR_BGR2RGB)

            # It's a video
            elif (self.media_type == 'mp4'):
                # Load the video
                self.original_media = cv2.VideoCapture(self.filename)

            # Load a second reference to edit without changing the original 
            self.current_media = self.original_media


    def filter_image(self, filter, image=[]):
        """ Applies a filter to an image """

        if len(image) == 0:
            image = self.original_media
        
        processed_image = None

        if (filter == 'Emboss'):
            processed_image = filters.emboss(image)
        
        elif (filter == 'Cartoon-Thick'):
            processed_image = filters.cartoon(image, 'thick')
        
        elif (filter == 'Cartoon-Thin'):
            processed_image = filters.cartoon(image, 'thin')

        elif (filter == 'Sketch'):
            processed_image = filters.sketch(image)

        elif (filter == 'Invert'):
            processed_image = filters.invert(image)

        elif (filter == 'Noisy'):
            processed_image = filters.noisy(image)

        # elif (filter == 'Surreal'):
        #     processed_image = filters.surreal(image)

        # elif (filter == 'Deep Fried'):
        #     processed_image = filters.deep_fried(image)

        elif (filter == 'Sharpen'):
            processed_image = filters.sharpen(image)

        else:
            processed_image = self.current_media
            return

        # self.current_media = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
        self.current_media = processed_image
    
    def filter_image_bc(self, brightness, contrast):
        """ Applies a brightness and contrast filter to an image """
    
        processed_image = filters.brightness_contrast(self.original_media, brightness, contrast)

        self.current_media = processed_image
        # self.current_media = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
    

    def filter_video(self, filter):
        video = cv2.VideoCapture(self.filename)

        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video.get(cv2.CAP_PROP_FPS))

        video_writer = cv2.VideoWriter('temp/processed_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
        print('Processing video...')
         
        percent_complete = 0
        frame_num = 0
        while(video.isOpened()):
            ret, frame = video.read()

            if ret == True:
                print(f'attempting to filter video with: {filter}')
                self.filter_image(filter, frame)
                video_writer.write(self.current_media)

                frame_num = frame_num + 1

                if frame_num % (frame_count / 100) == 0:
                    percent_complete += 1


            #If a frame isn't read properly, exit the loop
            else:
                print('Error reading frame')
                break

        print('Video processed!')
        video.release()
        video_writer.release()

        self.update_media('temp/processed_video.mp4')
        
    def undo():
        pass

    def redo():
        pass


   

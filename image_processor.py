"""
File: image_processor.py
Author: Adam Applegate
Description: 

    Uses OpenCV to edit photos based on input from the UI
   
"""

import numpy as np
import cv2
import filters

class ImageProcessor():
 
    def __init__(self):
       super.__init__



    def filter_image(self, filter, image=[]):
        """ Applies a filter to an image """

        # If there is no image passed in, return empty array
        if len(image) == 0:
            return image
        
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
            print('inverting image')
            processed_image = filters.invert(image)

        elif (filter == 'Noisy'):
            processed_image = filters.noisy(image)

        # elif (filter == 'Surreal'):
        #     processed_image = filters.surreal(image)

        # elif (filter == 'Deep Fried'):
        #     processed_image = filters.deep_fried(image)

        else:
            processed_image = self.current_media
            return

        # self.current_media = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
        return processed_image
    

    def filter_apply_scales(self, brightness, contrast, sharpness, image=[]):
        """ Applies a brightness and contrast filter to an image """
    
        processed_image = filters.brightness_contrast_sharpness(brightness, contrast, sharpness, image)

        # self.current_media = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
        return processed_image

   

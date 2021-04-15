"""
File: filters.py
Author: Adam Applegate
Description: 

    Contains the logic to filter images in different styles
   
"""

import numpy as np
import cv2

# Credit to Vardan Agarwal- https://medium.com/@vardanagarwal16
def brightness(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    hsv = np.array(hsv, dtype=np.float64)

    # First Channel
    hsv[:,:,1] = hsv[:,:,:1] * 1.25
    hsv[:,:,1][hsv[:,:,:1] > 255] = 255

    # Second Channel
    hsv[:,:,2] = hsv[:,:,:2] * 1.25
    hsv[:,:,2][hsv[:,:,:2] > 255] = 255

    hsv = np.array(hsv, dtype= np.uint8)

    processed_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return processed_image


# Credit to Geeks for Geeks: https://www.geeksforgeeks.org/changing-the-contrast-and-brightness-of-an-image-using-python-opencv/
# Credit to Vardan Agarwal- https://medium.com/@vardanagarwal16
def brightness_contrast_sharpness(brightness, contrast, sharpness, image):
    
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    else:
        buf = image
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    if sharpness != 0:
        buf = cv2.detailEnhance(buf, sigma_s=10, sigma_r=float(sharpness / 100))

        kernel_sharpening = np.array([[-1,-1,-1], 
                                [-1, 9,-1],
                                [-1,-1,-1]])

        buf = cv2.filter2D(buf, -1, kernel_sharpening)

    return buf

def splash(filename, color1, color2):
    pass


# Credit to Vardan Agarwal- https://medium.com/@vardanagarwal16
def noisy(image):

    height, width = image.shape[:2]

    processed_image = np.zeros((height, width), np.uint8)

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Determines how much noise to add to the image. Ranges from 0.0 to 1.0
    thresh = 0.8

    for i in range(height):
        for j in range(width):
            if (np.random.rand() <= thresh):
                if (np.random.randint(2) == 0):
                    # Add random values from 0-64. 255 is the upper bound
                    grayscale[i, j] = min(grayscale[i, j] + np.random.randint(0, 64), 255)
                else:
                    # Subtract random values from 0-64. 0 is the lower bound
                    grayscale[i, j] = max(grayscale[i, j] - np.random.randint(0, 64), 0)

    processed_image = grayscale

    return processed_image


# Credit to Vardan Agarwal- https://medium.com/@vardanagarwal16
def emboss(image):

    height, width = image.shape[:2]

    # Create an array the same size as the image, but it's gray
    y = np.ones((height, width), np.uint8) * 128

    # The final image will be stored here
    processed_image = np.zeros((height, width), np.uint8)

    # Top-left emboss kernel
    tl_kernel = np.array([[1,1,0],
                          [1,0,-1],
                          [0,-1,-1]])

    # Top-right emboss kernel
    tr_kernel = np.array([[0,1,1],
                          [-1,0,1],
                          [-1,-1,0]])

    # Bottom-left Emboss Kernel
    bl_kernel = np.array([[0,-1,-1],
                          [1,0,-1],
                          [1, 1, 0]])

    # Bottom-right Emboss Kernel
    br_kernel = np.array([[-1,-1,0],
                          [-1,0,1],
                          [0, 1, 1]])

    # PIL Emboss kernel - NOT BEING USED
    pil_kernel = np.array([[-1,0,0],
                      [0,1,0],
                      [0,0,0]])

    # Convert the image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Emboss each side of image with different kernels
    tl_emboss = cv2.add(cv2.filter2D(grayscale, -1, tl_kernel), y)
    tr_emboss = cv2.add(cv2.filter2D(grayscale, -1, tr_kernel), y)
    bl_emboss = cv2.add(cv2.filter2D(grayscale, -1, bl_kernel), y)
    br_emboss = cv2.add(cv2.filter2D(grayscale, -1, br_kernel), y)

    #Combine all 4 embossed images together
    for i in range(height):
        for j in range(width):
            processed_image[i, j] = max(tl_emboss[i, j], tr_emboss[i, j], bl_emboss[i, j], br_emboss[i, j])

    return processed_image


# Credit to Vardan Agarwal- https://medium.com/@vardanagarwal16
def cartoon(image, type):

    height, width = image.shape[:2]

    # Convert the image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    grayscale = cv2.medianBlur(grayscale, 5)

    # Thin edge style
    thin_edges = cv2.bitwise_not(cv2.Canny(image, 100, 200))

    # Thick edge style
    thick_edges = cv2.adaptiveThreshold(grayscale, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)

    processed_image = cv2.edgePreservingFilter(image, flags=2, sigma_s=64, sigma_r=0.25)

    thin_cartoon = cv2.bitwise_and(processed_image, processed_image, mask=thin_edges)
    thick_cartoon = cv2.bitwise_and(processed_image, processed_image, mask=thick_edges)

    if (type == 'thick'):
        return thick_cartoon

    if (type == 'thin'):
        return thin_cartoon


# Credit to Michael Beyeler- https://www.askaswiss.com
def sketch(image):

    height, width = image.shape[:2]
    processed_image = np.zeros((height, width), np.uint8)

    # Convert the image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    negative = cv2.bitwise_not(grayscale)

    # Blur the negative (this will be used as a mask)
    negative = cv2.GaussianBlur(negative, ksize=(21, 21), sigmaX=0, sigmaY=0)

    # Blend grayscale with blurred negative
    processed_image = cv2.divide(grayscale, 255 - negative, scale=256) # This is a "dodge" blending technique

    return processed_image


def invert(image):

    processed_image = cv2.bitwise_not(image)

    return processed_image


def surreal(image):

    kernel = np.array([[0,-1,-1],
                      [1,0,-1],
                      [1, 1, 0]])

    processed_image = cv2.filter2D(image, ddepth=cv2.CV_32F, kernel=kernel)

    processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

    processed_image = cv2.bitwise_not(processed_image)

    processed_image = np.random.random_sample(processed_image.shape) * 255
    processed_image = processed_image.astype(np.uint8)

    return processed_image


def deep_fried(image):
    pass





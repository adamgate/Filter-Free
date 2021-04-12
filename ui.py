"""
Course: CSS 353
File: main.py
Author: Adam Applegate
Description: 

    The main entry point that controls the logic for the program

"""

import tkinter as tk
import tkinter.filedialog
from tkinter.constants import ANCHOR
from PIL import ImageTk, Image
import cv2
from time import sleep
import os
from shutil import rmtree
from functools import partial

from image_processor import ImageProcessor

class Navbar(tk.Frame):
    """ The application's navbar """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):
        menubar = tk.Menu(self.master)

        self.master.config(menu=menubar)

        fileMenu = tk.Menu(self)
        
        fileMenu.add_command(label='Open File...', command=partial(MainApplication.openFile, self.parent))
        fileMenu.add_command(label='Save File...', command=partial(MainApplication.saveFile, self.parent))
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit', command=partial(MainApplication.onExit, self))

        menubar.add_cascade(label='File', menu=fileMenu)
        menubar.add_command(label='Undo', command=partial(MainApplication.refresh_canvas, MainApplication))
        menubar.add_command(label='Redo', command=partial(MainApplication.saveFile, self))


class Main(tk.Frame):
    """ The main window of the application """

    canvas = None

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):
        # Initialize frames to put items in

        # For the buttons
        frame_buttons = tk.Frame(root)
        frame_buttons.grid(row=0, column=0, sticky=tk.NE)

        # # For the image and image name
        frame_image = tk.Frame(root)
        frame_image.grid(row=0, column=1, sticky=tk.NE)

        label_drop = tk.Label(frame_buttons, text='Filters')
        label_drop.pack(side=('top'), pady=(15, 0))

        # Create filter dropdown menu
        # optionList = ['Emboss', 'Cartoon-Thick', 'Cartoon-Thin', 'Sketch', 'Invert', 'Noisy', 'Surreal', 'Deep Fried' 'Sharpen']
        optionList = ['Emboss', 'Cartoon-Thick', 'Cartoon-Thin', 'Sketch', 'Invert', 'Noisy', 'Sharpen']
        drop_var = tk.StringVar(self)
        drop_var.set('Filter')
        drop_menu1 = tk.OptionMenu(frame_buttons, drop_var, *optionList, command=self.parent.callFilter)
        drop_menu1.pack(side='top', fill=tk.X)

        label_brightness = tk.Label(frame_buttons, text='Brightness')
        label_brightness.pack(side=('top'), pady=(30, 0))

        # scale to adjust image brightness
        self.scale_brightness = tk.Scale(frame_buttons, from_=-255, to=255, orient=tk.HORIZONTAL)
        self.scale_brightness.pack(side=('top'))

        label_contrast = tk.Label(frame_buttons, text='Contrast')
        label_contrast.pack(side=('top'), pady=(15, 0))

        # scale to adjust image contrast
        self.scale_contrast = tk.Scale(frame_buttons, from_=-127, to=127, orient=tk.HORIZONTAL)
        self.scale_contrast.pack(side=('top'))

        btn_apply_scales = tk.Button(frame_buttons, text='Apply', command=self.parent.callFilter_Brightness_Contrast)
        btn_apply_scales.pack(side='top', pady=(15, 0))

        # btn_play_video = tk.Button(frame_buttons, text='Play Video', command=self.parent.playVideo)
        # btn_play_video.pack(side='bottom', pady=(200, 0))

        # Create a canvas to display images to the user
        self.canvas = tk.Canvas(frame_image, width=1080, height=720, background='gray')
        self.canvas.pack(side='top')

        self.label_canvas = tk.Label(frame_image, text=self.parent.image_processor.filename, font=('Helvetica', 15))
        self.label_canvas.pack(side='left')

        self.label_messages = tk.Label(frame_image, text='', font=('Helvetica', 15), border=5)
        self.label_messages.pack(side='right')


class MainApplication(tk.Frame):
    """ The main program. Contains the navbar and main classes, and most of the logic that ties everything together. """

    image_processor = ImageProcessor()
    main = None
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent

        # Add the other UI pieces
        self.navbar = Navbar(self)
        self.main = Main(self)

        # Determine the location of each UI piece
        self.navbar.grid(row=0, column=0, sticky=tk.NSEW)
        self.main.grid(row=1, column=1)

        self.refresh_canvas()

        self.messageUser('Welcome to Filter Free!', 'black')

        if not os.path.exists('temp'):
            os.makedirs('temp')


    def refresh_canvas(self):
        # Is the loaded object an image or a video?

        if (self.image_processor.media_type != None and self.image_processor.media_type != 'mp4'):
            image_canvas = self.image_processor.current_media

            shape = image_canvas.shape
            image_height = shape[0]
            image_width = shape[1]

            # If the image is larger than the screen, resize it to fit
            if (image_height > 720 or image_width > 1080):
                scale = image_height / 720
                image_canvas = cv2.resize(image_canvas, (int(image_width/scale), int(image_height/scale)), interpolation=cv2.INTER_CUBIC)

            # Convert the numpy array to a PIL image that can be displayed on Tkinter canvas
            image_canvas = ImageTk.PhotoImage(Image.fromarray(image_canvas))

             # Prevent garbage collection from deleting the image
            root.image_canvas = image_canvas

            # Display the image on the center of the canvas
            self.main.canvas.create_image(540, 360, image=image_canvas)

        elif (self.image_processor.media_type != None and self.image_processor.media_type == 'mp4'):
            # Load the first frame of the video
            ret, image_canvas = self.image_processor.current_media.read()

            # If the frame was successfully loaded
            if (ret == True):
                # Make sure the correct color channel is selected
                image_canvas = cv2.cvtColor(image_canvas, cv2.COLOR_BGR2RGBA)

                image_height, image_width, _ = image_canvas.shape

                # If the image is larger than the screen, resize it to fit
                if (image_height > 720 or image_width > 1080):
                    scale = image_height / 720
                    image_canvas = cv2.resize(image_canvas, (int(image_width/scale), int(image_height/scale)), interpolation=cv2.INTER_CUBIC)

                # Convert the numpy array to a PIL image that can be displayed on Tkinter canvas
                image_canvas = ImageTk.PhotoImage(Image.fromarray(image_canvas))

                 # Prevent garbage collection from deleting the image
                root.image_canvas = image_canvas

                # Display the image on the center of the canvas
                self.main.canvas.create_image(540, 360, image=image_canvas)
        
        else:
            self.messageUser('Error', 'red')

    def playVideo(self):
        
        while (self.image_processor.current_media.isOpened):
            # Load each frame of the video
            ret, image_canvas = self.image_processor.current_media.read()

            # If the frame was successfully loaded
            if (ret == True):
                # Make sure the correct color channel is selected
                image_canvas = cv2.cvtColor(image_canvas, cv2.COLOR_BGR2RGBA)

                image_height, image_width, _ = image_canvas.shape

                # If the image is larger than the screen, resize it to fit
                if (image_height > 720 or image_width > 1080):
                    scale = image_height / 720
                    image_canvas = cv2.resize(image_canvas, (int(image_width/scale), int(image_height/scale)), interpolation=cv2.INTER_CUBIC)

                # Convert the numpy array to a PIL image that can be displayed on Tkinter canvas
                image_canvas = ImageTk.PhotoImage(Image.fromarray(image_canvas))

                 # Prevent garbage collection from deleting the image
                root.image_canvas = image_canvas

                # Display the image on the center of the canvas
                self.main.canvas.create_image(540, 360, image=image_canvas)
    

    def callFilter(self, filter):
        """ Takes input from the dropdown menu,and calls the selected filter """
        if (self.image_processor.media_type != 'mp4'):
            self.image_processor.filter_image(filter)

        elif (self.image_processor.media_type == 'mp4'):
            self.image_processor.filter_video(filter)

        else:
            self.messageUser('Unknown filetype', 'red')
            return

        self.messageUser(f'{filter} filter Applied!', 'green')

        self.refresh_canvas()


    def callFilter_Brightness_Contrast(self):
        """ Takes input from the brightness and contrast sliders, and calls the filter """

        self.image_processor.filter_image_bc(self.main.scale_brightness.get(), self.main.scale_contrast.get())

        self.messageUser('B/C filter Applied!', 'green')

        self.refresh_canvas()


    def onExit(self):
        """ Exits the program """

        #TODO Cleanup the temp folder 

        self.parent.messageUser('Exiting program...', 'orange')

        self.quit()


    def openFile(self):
        """ Gets a filename from the user and passes it to the image processor """

        file = tkinter.filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(
            ('jpg files', '*.jpg'), 
            ('png files', '*.png'),
            ('mp4 files', '*.mp4'),
            ('all files', '*.*')
            ))

        # If there was an issue opening a file, let the user know
        if (file == None or file == ''):
            self.main.label_messages.config(text='Error opening file', fg='red')

        # File found. Load it into the program
        else:
            if(self.image_processor.media_type == 'mp4'):
                self.image_processor.original_media.release()
                
            self.image_processor.update_media(file)
            self.refresh_canvas()

            self.messageUser('File opened successfully', 'green')
            


    def saveFile(self):
        default_extension = self.image_processor.media_type
        filename = None

        if (default_extension == 'mp4'):
            filename = tkinter.filedialog.asksaveasfilename(defaultextension='mp4', initialdir='/', title='Save File', filetypes=(
                ('mp4 files', '*.mp4'),
                ('all files', '*.*')
                ))

            # If there was an issue saving a file, let the user know
            if filename == None or filename == '':
                self.messageUser('Error saving file', 'red')

            else:
                # Save a video
                video = cv2.VideoCapture(self.image_processor.filename)

                frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(video.get(cv2.CAP_PROP_FPS))

                video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))


                while(video.isOpened()):
                    ret, frame = video.read()

                    if ret == True:
                        video_writer.write(frame)

                    #If a frame isn't read properly, exit the loop
                    else:
                        break

                video.release()
                video_writer.release()

                self.messageUser('Video saved successfully', 'green')

        elif (default_extension == 'jpg' or default_extension == 'png'):
            filename = tkinter.filedialog.asksaveasfilename(defaultextension=default_extension, initialdir='/', title='Save File', filetypes=(
                ('jpeg files', '*.jpg'), 
                ('png files', '*.png')))

            # If there was an issue saving a file, let the user know
            if filename == None or filename == '':
                self.messageUser('Error saving file', 'red')

            # Save an image
            else:
                cv2.imwrite(filename, self.image_processor.current_media)
                self.messageUser('Image saved successfully', 'green')

    def messageUser(self, message, color):
        self.main.label_messages.config(text='')
        self.main.label_messages.config(text=message, fg=color)



if __name__ == '__main__':
    root = tk.Tk()
    app = MainApplication(root)
    root.title('Filter Free')
    root.configure(background='white')

    root.mainloop()
"""
File: ui.py
Author: Adam Applegate
Description: 

    Defines the program's UI

"""

import tkinter as tk
import tkinter.filedialog
from tkinter.constants import ANCHOR
from PIL import ImageTk, Image
import cv2
import os
from functools import partial

from image_processor import ImageProcessor
from video_processor import VideoProcessor
from undo_redo_manager import UndoRedoManager


class Navbar(tk.Frame):
    """ The application's navbar """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.menubar = ''

        self.initUI()

    def initUI(self):
        self.menubar = tk.Menu(self.master)

        self.master.config(menu=self.menubar)

        # create Submenu titled "File"
        fileMenu = tk.Menu(self)
        
        fileMenu.add_command(label='Open File...', command=partial(MainApplication.open_file, self.parent))

        fileMenu.add_separator()

        fileMenu.add_command(label='Save', command=partial(MainApplication.save_file, self.parent))
        fileMenu.add_command(label='Save As...', command=partial(MainApplication.save_file_as, self.parent))

        fileMenu.add_separator()

        fileMenu.add_command(label='Exit', command=partial(MainApplication.on_exit, self))

        self.menubar.add_cascade(label='File', menu=fileMenu)

        # self.menubar.add_command(label='Undo', command=partial(MainApplication.undo, MainApplication))
        # self.menubar.add_command(label='Redo', command=partial(MainApplication.redo, self))

        root.configure(menu=self.menubar)

    # # Enable Undo/ Redo buttons
    # def enable_undo(self):
    #     self.menubar.entryconfig('Undo', state='normal')
        
    # def enable_redo(self):
    #     self.menubar.entryconfig('Redo', state='normal')

    # # Disable Undo/ Redo buttons
    # def disable_undo(self):
    #     self.menubar.entryconfig('Undo', state='disabled')
    
    # def disable_redo(self):
    #     self.menubar.entryconfig('Redo', state='disabled')


class ImageToolbar(tk.Frame):
    """ The toolbar with image options """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):

        ###################################
        # Create the image toolbar
        ###################################
        self.frame = tk.Frame(root)
        self.frame.grid(row=1, column=0, sticky=tk.NE)

        label_drop = tk.Label(self.frame, text='Filters')
        label_drop.pack(side=('top'), pady=(15, 0))

        # Create filter dropdown menu
        optionList = ['Emboss', 'Cartoon-Thick', 'Cartoon-Thin', 'Sketch', 'Invert', 'Noisy']
        selected_var = tk.StringVar(self)
        selected_var.set('Filter')
        option_menu_filter = tk.OptionMenu(self.frame, selected_var, *optionList, command=self.parent.call_filter)
        option_menu_filter.pack(side='top', fill=tk.X)

        # Scale to adjust image brightness
        label_brightness = tk.Label(self.frame, text='Brightness')
        label_brightness.pack(side=('top'), pady=(30, 0))

        self.scale_brightness = tk.Scale(self.frame, from_=-255, to=255, orient=tk.HORIZONTAL)
        self.scale_brightness.pack(side=('top'))

        # Scale to adjust image contrast
        label_contrast = tk.Label(self.frame, text='Contrast')
        label_contrast.pack(side=('top'), pady=(15, 0))

        self.scale_contrast = tk.Scale(self.frame, from_=-127, to=127, orient=tk.HORIZONTAL)
        self.scale_contrast.pack(side=('top'))

        # Scale to adjust sharpness
        label_contrast = tk.Label(self.frame, text='Sharpness')
        label_contrast.pack(side=('top'), pady=(15, 0))

        self.scale_sharpness = tk.Scale(self.frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.scale_sharpness.pack(side=('top'))

        # Apply values in each scale
        btn_apply_scales = tk.Button(self.frame, text='Apply', command=self.parent.apply_scales)
        btn_apply_scales.pack(side='top', pady=(15, 0))

        # Reset values in each scale
        btn_reset_scales = tk.Button(self.frame, text='Reset', command=self.parent.reset_scales)
        btn_reset_scales.pack(side='top', pady=(15, 0))


class VideoToolbar(tk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):

        ###################################
        # Create the video toolbar
        ###################################
        self.frame = tk.Frame(root)
        self.frame.grid(row=1, column=0, sticky=tk.NE)

        label_video_length = tk.Label(self.frame, text='Video Length: ')
        label_video_length.pack(side=('top'), pady=(15, 0))

        label_video_size = tk.Label(self.frame, text='Video Size: ')
        label_video_size.pack(side=('top'), pady=(15, 0))

        btn_play_video = tk.Button(self.frame, text='Play Video', command=self.parent.play_video)
        btn_play_video.pack(side='bottom', pady=(200, 0))


class Display(tk.Frame):
    """ The area where the images are displayed """

    canvas = None

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initUI()

    def initUI(self):

        # Create the frame to store the pieces
        frame = tk.Frame(root)
        frame.grid(row=1, column=1, sticky=tk.NE)

        # Create a canvas to display images to the user
        self.canvas = tk.Canvas(frame, width=1080, height=720, background='gray')
        self.canvas.pack(side='top')

        # Label that displays the filename
        self.label_canvas = tk.Label(frame, text=self.parent.filename, font=('Helvetica', 15))
        self.label_canvas.pack(side='left')

        # Label that displays messages to the user
        self.label_messages = tk.Label(frame, text='', font=('Helvetica', 15), border=5)
        self.label_messages.pack(side='right')


class MainApplication(tk.Frame):
    """ The main program. Contains the navbar, toolbar, and display classes, and most of the logic that ties everything together. """

    image_processor = ImageProcessor()
    video_processor = VideoProcessor()
    # command_manager = UndoRedoManager()

    navbar = ''

    filepath = None
    filename = None
    filetype = None

    # The original image without edits
    original_file = None

    # The edited image
    processed_file = None
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent

        # Add the other UI pieces
        self.navbar = Navbar(self)
        self.image_toolbar = ImageToolbar(self)
        self.video_toolbar = VideoToolbar(self)
        self.display = Display(self)

        # Determine the location of each UI piece
        self.navbar.grid(row=0, column=0, sticky=tk.NSEW)
        self.image_toolbar.grid(row=1, column=0)
        self.video_toolbar.grid(row=1, column=0)
        self.display.grid(row=0, column=1)

        # Load default image when program starts
        self.update_file_type('media/old_fashioned.jpg')

        self.refresh_canvas()

        # self.manage_commands()

        self.message_user('Welcome to Filter Free!', 'green')

        # Create a temp folder if none exists
        if not os.path.exists('temp'):
            os.makedirs('temp')


    # def manage_commands(self):
    #     """ Enables or disables the undo/redo buttons depending on the size of the undo/redo stacks """

    #     if (self.command_manager.get_undo_size() > 0):
    #         self.navbar.enable_undo()
    #     elif (self.command_manager.get_undo_size() == 0):
    #         self.navbar.disable_undo()

    #     if (self.command_manager.get_redo_size() > 0):
    #         self.navbar.enable_redo()
    #     elif (self.command_manager.get_redo_size() == 0):
    #         self.navbar.disable_redo()


    # def undo(self):
    #     self.processed_file = self.command_manager.undo()
    #     self.manage_commands(self)
    #     self.refresh_canvas()


    # def redo(self):
    #     self.processed_file = self.command_manager.redo()
    #     self.manage_commands(self)
    #     self.refresh_canvas()


    def update_file_type(self, filepath):
        """ A new file was loaded. Update the object accordingly """

        # Make sure a file was actually loaded
        if (filepath is not None):
            # Update the filepath
            self.filepath = filepath

            # Determine the filetype
            self.filetype = self.filepath.split('.')[1]

            # Isolate the name of the file
            file_pieces = self.filepath.split('/')
            self.filename = file_pieces[len(file_pieces)-1]

            # It's an image
            if (self.filetype != 'mp4'):
                # Load the image
                self.original_file = cv2.imread(self.filepath)

                # Set the correct color channels
                self.original_file = cv2.cvtColor(self.original_file, cv2.COLOR_BGR2RGB)

                # Load the image toolbar & hide the video toolbar
                self.show_image_toolbar()

            # It's a video
            elif (self.filetype == 'mp4'):
                # Load the video
                self.original_file = cv2.VideoCapture(self.filepath)

                # Load the video toolbar & hide the image toolbar
                self.show_video_toolbar()

            # Load a second reference to edit without changing the original 
            self.processed_file = self.original_file

            self.display.label_canvas = self.filename

            
    def show_image_toolbar(self):
        """ Show the image toolbar and hide the video toolbar """

        self.video_toolbar.frame.grid_remove()
        self.image_toolbar.frame.grid()

    def show_video_toolbar(self):
        """ Show the video toolbar and hide the image toolbar """

        self.image_toolbar.frame.grid_remove()
        self.video_toolbar.frame.grid()


    def refresh_canvas(self):
        # Is the loaded object an image or a video?

        if (self.filetype != None and self.filetype != 'mp4'):
            image_canvas = self.processed_file

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
            self.display.canvas.create_image(540, 360, image=image_canvas)

        elif (self.filetype != None and self.filetype == 'mp4'):
            # Load the first frame of the video
            ret, image_canvas = self.processed_file.read()

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
                self.display.canvas.create_image(540, 360, image=image_canvas)
        
        else:
            self.message_user('Error', 'red')


    def play_video(self):
        """ Plays a video loaded into the display area """

        while (self.processed_file.isOpened):
            # Load each frame of the video
            ret, image_canvas = self.processed_file.read()

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
                self.display.canvas.create_image(540, 360, image=image_canvas)
    

    def call_filter(self, filter):
        """ Takes input from the dropdown menu,and calls the selected filter """

        if (self.filetype == 'png' or self.filetype == 'jpg' or self.filetype == 'jpeg'):
            # self.command_manager.push_undo_stack(self.processed_file)
            # self.manage_commands()

            self.processed_file = self.image_processor.filter_image(filter, self.original_file)

        else:
            self.message_user('Unknown filetype', 'red')
            return

        self.message_user(f'{filter} filter Applied!', 'green')

        self.refresh_canvas()


    def apply_scales(self):
        """ Takes input from the scales, and calls the appropriate filter """

        # self.command_manager.push_undo_stack(self.processed_file)
        # self.manage_commands()

        self.processed_file = self.image_processor.filter_apply_scales(
                        self.image_toolbar.scale_brightness.get(), 
                        self.image_toolbar.scale_contrast.get(), 
                        self.image_toolbar.scale_sharpness.get(),
                        self.original_file)

        self.message_user('Slider values applied!', 'green')

        self.refresh_canvas()


    def reset_scales(self):
        """ Resets the scales to 0 """

        self.image_toolbar.scale_brightness.set(0)
        self.image_toolbar.scale_contrast.set(0)
        self.image_toolbar.scale_sharpness.set(0)

        self.processed_file = self.image_processor.filter_apply_scales(
                        self.image_toolbar.scale_brightness.get(), 
                        self.image_toolbar.scale_contrast.get(), 
                        self.image_toolbar.scale_sharpness.get(),
                        self.original_file)

        self.message_user('Slider values reset', 'orange')

        self.refresh_canvas()


    def on_exit(self):
        """ Exits the program and performs necessary cleanup """

        #TODO Cleanup the temp folder

        #TODO Call this function when the X is pressed

        self.parent.message_user('Exiting program...', 'orange')

        self.quit()


    def open_file(self):
        """ Gets a filename from the user and passes it to the image processor """

        file = tkinter.filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(
            ('jpg files', '*.jpg'), 
            ('png files', '*.png'),
            ('mp4 files', '*.mp4'),
            ))

        # If there was an issue opening a file, let the user know
        if (file == None or file == ''):
            self.message_user('Error opening file', 'red')
   
        # File found. Load it into the program
        else:
            if(self.filetype == 'mp4'):
                self.original_file.release()
                
            self.update_file_type(file)
            self.refresh_canvas()

            self.message_user('File opened successfully', 'green')
            


    def save_file(self):
        """ Save the file to the saved filepath """

        # If there was an issue saving a file, let the user know
        if self.filepath == None or self.filepath == '':
                self.message_user('Error saving file. File not loaded', 'red')

        if (self.filetype == 'mp4'):
            video = cv2.VideoCapture(self.filepath)

            frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(video.get(cv2.CAP_PROP_FPS))

            video_writer = cv2.VideoWriter(self.filepath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))


            while(video.isOpened()):
                ret, frame = video.read()

                if ret == True:
                    video_writer.write(frame)

                #If a frame isn't read properly, exit the loop
                else:
                    break

            video.release()
            video_writer.release()

            self.message_user('Video saved successfully', 'green')

        elif (self.filetype == 'jpg' or self.filetype == 'png'):
            cv2.imwrite(self.filepath, self.processed_file)
            self.message_user('Image saved successfully', 'green')


    def save_file_as(self):
        """ Save the file to the location specified by the user """
       
        if (self.filetype == 'mp4'):
            filepath = tkinter.filedialog.asksaveasfilename(defaultextension='mp4', initialdir='/', title='Save File', filetypes=(
                ('mp4 files', '*.mp4'),
                ('all files', '*.*')
                ))

            # If there was an issue saving a file, let the user know
            if filepath == None or filepath == '':
                self.message_user('Error saving file', 'red')

            else:
                # Save a video
                video = cv2.VideoCapture(self.filepath)

                frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(video.get(cv2.CAP_PROP_FPS))

                video_writer = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))


                while(video.isOpened()):
                    ret, frame = video.read()

                    if ret == True:
                        video_writer.write(frame)

                    #If a frame isn't read properly, exit the loop
                    else:
                        break

                video.release()
                video_writer.release()

                self.message_user('Video saved successfully', 'green')

        elif (self.filetype == 'jpg' or self.filetype == 'jpeg' or self.filetype == 'png'):
            print('saving file...')
            filepath = tkinter.filedialog.asksaveasfilename(defaultextension=self.filetype, initialdir='/', title='Save File', filetypes=(
                ('jpeg files', '*.jpg'), 
                ('png files', '*.png')))

            # If there was an issue saving a file, let the user know
            if filepath == None or filepath == '':
                self.message_user('Error saving file', 'red')

            # Save an image
            else:
                cv2.imwrite(filepath, self.processed_file)
                self.message_user('Image saved successfully', 'green')



    def message_user(self, message, color):
        """ Prints a message to the message center in the specified color """
        self.display.label_messages.config(text='')
        self.display.label_messages.config(text=message, fg=color)


######################################
# Main loop that starts the program
######################################
if __name__ == '__main__':

    # Initialize the program
    root = tk.Tk()
    app = MainApplication(root)

    # Set the window title & some settings
    root.title('Filter Free')
    root.configure(background='white')
    root.option_add('*tearOff', False)

    # Run the main logic loop
    root.mainloop()
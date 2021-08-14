# Credit to Donz0r for help with this code. It has been adapted to the needs of the program
# https://derdon.github.io/blog/implementing-an-undo-redo-manager-in-python.html

class EmptyCommandStackError(Exception):
    pass

class UndoRedoManager(object):
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []


    def get_undo_size(self):
        """ Return the number of images in the undo stack"""

        return len(self.undo_stack)


    def get_redo_size(self):
        """ Return the number of images in the redo stack"""

        return len(self.redo_stack)


    def push_undo_stack(self, image):
        """ Push the image to the undo stack """

        self.undo_stack.append(image)


    def pop_undo_stack(self):
        """ Remove the last command from the undo stack and return it.
            Throws an error if the undo stack is empty """

        try:
            last_undo = self.undo_stack.pop()

        except IndexError:
            raise EmptyCommandStackError()

        return last_undo


    def push_redo_stack(self, image):
        """ Push the image to the redo stack """

        self.redo_stack.append(image)


    def pop_redo_stack(self):
        """ Remove the last command from the redo stack and return it.
            Throws an error if the redo stack is empty """

        try:
            last_redo = self.redo_stack.pop()

        except IndexError:
            raise EmptyCommandStackError()

        return last_redo


    def undo(self, n=1):
        """ Undo the last N commands (defaults to 1). 
            Removes the image from the undo stack and adds it to the redo stack """

        for _ in range(n):
            image = self.pop_undo_stack()
            self.push_redo_stack(image)

            return image


    def redo(self, n=1):
        """ Redo the last N commands (defaults to 1). 
            Removes the image from the redo stack and adds it to the undo stack """

        for _ in range(n):
            image = self.pop_redo_stack()
            self.push_undo_stack(image)

            return image
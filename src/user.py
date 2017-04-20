

class User:

    def __init__(self, username):
        self.username = username
        self.character = None
        self.location = None
        self.subloc = None
        self.pos = None

    def set_char(self, char):
        self.character = char

    def set_loc(self, loc):
        self.location = loc

    def set_subloc(self, subloc):
        self.subloc = subloc

    def set_pos(self, pos):
        self.pos = pos

    def get_char(self):
        return self.character

    def get_loc(self):
        return self.location

    def get_subloc(self):
        return self.subloc

    def get_pos(self):
        return self.pos

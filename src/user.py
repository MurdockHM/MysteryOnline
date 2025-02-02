from character import characters
from location import location_manager
from inventory import UserInventory

from kivy.app import App

from src.location import Location
from src.sprite import Sprite


class User:
    def __init__(self, username):
        self.username = username
        self.character = None
        self.location = None
        self.subloc = None
        self.pos = "center"
        self.current_sprite = None
        self.prev_subloc = None
        self.color = 'ffffff'  # Default color for text
        self.colored = None  # True for a color selected
        self.color_ids = ['ffffff', 'ff3333', '00adfc', 'ffd700', '00cd00', 'rainbow', '8b6fba']  # Color code for text
        self.sprite_option = -1
        self.inventory = UserInventory(self)
        self.has_choice_popup = False

    def set_from_msg(self, location, sublocation, position, sprite, character):
        self.set_loc(location, True)
        if self.location is not None:
            try:
                 self.set_subloc(self.location.get_sub(sublocation))
            except KeyError:
                self.set_subloc(self.location.placeholder_subloc)
            self.set_pos(position)
        self.set_current_sprite(sprite)
        self.character = characters.get(character)
        if self.character is None:
            self.character = characters['RedHerring']
            self.set_current_sprite('4')
        self.character.load_without_icons()

    def get_color(self):
        return self.color

    def on_col_select(self, col, color_button):
        color_button.text = col
        self.set_color(col)

    def set_color(self, col):
        if col == 'red':
            self.color = 'ff3333'
        elif col == 'blue':
            self.color = '00adfc'
        elif col == 'golden':
            self.color = 'ffd700'
        elif col == 'green':
            self.color = '00cd00'
        elif col == 'rainbow':
            self.color = 'rainbow'
        elif col == 'purple':
            self.color = '8b6fba'
        elif col == 'normal':
            self.color = 'ffffff'

        if self.color != 'ffffff':
            self.colored = True
        else:
            self.colored = False

    def set_current_sprite(self, num):
        self.current_sprite = num

    def get_current_sprite(self) -> Sprite:
        if self.character is not None:
            return self.character.get_sprite(self.current_sprite)
        else:
            red_herring = characters["RedHerring"]
            red_herring.load()
            return red_herring.get_sprite("3")

    def set_char(self, char):
        self.character = char

    def set_loc(self, loc, from_string=False):
        if from_string:
            locations = location_manager.get_locations()
            if loc in locations:
                self.location = locations[loc]
            else:
                self.location= None
        else:
            self.location = loc

        self.set_subloc(self.location.get_sub(self.location.get_first_sub()))

    def set_subloc(self, subloc):
        self.prev_subloc = self.subloc
        self.subloc = subloc

    def set_pos(self, pos):
        if self.pos is not None:
            if self.pos == 'right':
                if self.prev_subloc is not None and self in self.prev_subloc.r_users:
                    self.prev_subloc.remove_r_user(self)
                elif self in self.subloc.r_users:
                    self.subloc.remove_r_user(self)
            elif self.pos == 'left':
                if self.prev_subloc is not None and self in self.prev_subloc.l_users:
                    self.prev_subloc.remove_l_user(self)
                elif self in self.subloc.l_users:
                    self.subloc.remove_l_user(self)
            else:
                if self.prev_subloc is not None and self in self.prev_subloc.c_users:
                    self.prev_subloc.remove_c_user(self)
                elif self in self.subloc.c_users:
                    self.subloc.remove_c_user(self)
        self.pos = pos

    def set_sprite_option(self, option):
        self.sprite_option = option

    def get_char(self):
        return self.character

    def get_loc(self) -> Location:
        return self.location

    def get_subloc(self):
        return self.subloc

    def get_pos(self):
        return self.pos

    def get_sprite_option(self):
        return self.sprite_option

    def get_inventory(self):
        return self.inventory

    def remove(self):
        if self.pos is None or self.subloc is None:
            return
        if self.pos == 'right':
            self.subloc.remove_r_user(self)
        elif self.pos == 'left':
            self.subloc.remove_l_user(self)
        else:
            self.subloc.remove_c_user(self)

    def set_choice_popup_state(self, boolean):
        self.has_choice_popup = boolean

    def get_choice_popup_state(self):
        return self.has_choice_popup


class CurrentUserHandler:
    def __init__(self, user):
        self.user = user
        self.connection_manager = None
        self.current_loc = None
        self.current_sprite_name = ""
        self.current_subloc_name = ""
        self.current_pos_name = ""
        self.current_sprite_option = -1
        self.chosen_sprite_name = ""
        self.chosen_subloc_name = ""
        self.chosen_pos_name = ""
        self.chosen_sprite_option = -1

    def send_message(self, msg):
        col_id = 0
        if self.user.colored:
            col_id = self.user.color_ids.index(self.user.get_color())
        loc = self.user.get_loc().name
        char = self.user.get_char().name
        message_factory = App.get_running_app().get_message_factory()
        sfx_name = App.get_running_app().get_main_screen().get_toolbar().get_sfx_name()
        message = message_factory.build_chat_message(content=msg, location=loc, sublocation=self.chosen_subloc_name,
                                                     character=char, sprite=self.chosen_sprite_name,
                                                     position=self.chosen_pos_name, color_id=col_id,
                                                     sprite_option=self.get_chosen_sprite_option(), sfx_name=sfx_name)

        self.chosen_to_current()
        self.user.set_pos(self.current_pos_name)

        self.connection_manager.send_msg(message)
        self.connection_manager.send_local(message)

    def send_icon(self):
        loc = self.user.get_loc().name
        char = self.user.get_char().name
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_icon_message(location=loc, sublocation=self.chosen_subloc_name,
                                                     character=char, sprite=self.chosen_sprite_name,
                                                     position=self.chosen_pos_name,
                                                     sprite_option=self.chosen_sprite_option)

        self.chosen_to_current()
        self.user.set_pos(self.current_pos_name)

        self.connection_manager.send_msg(message)
        self.connection_manager.send_local(message)

    def chosen_to_current(self):
        self.set_current_pos_name(self.get_chosen_pos_name())
        self.set_current_sprite_name(self.get_chosen_sprite_name())
        self.set_current_sprite_option(self.get_chosen_sprite_option())
        self.set_current_subloc_name(self.get_chosen_subloc_name())

    def on_current_loc(self, *args):
        self.user.set_loc(self.current_loc)
        subloc_name = self.current_loc.get_first_sub()
        self.set_chosen_subloc_name(subloc_name)
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_location_message(self.current_loc.name)
        self.connection_manager.send_msg(message)

    def on_current_subloc_name(self, *args):
        subloc = self.current_loc.get_sub(self.current_subloc_name)
        self.user.set_subloc(subloc)

    def on_current_sprite_name(self, *args):
        self.user.set_current_sprite(self.current_sprite_name)

    def on_current_sprite_option(self, *args):
        self.user.set_sprite_option(self.current_sprite_option)

    def get_current_subloc(self):
        return self.user.get_subloc()

    def get_current_sprite(self) -> Sprite:
        return self.user.get_current_sprite()

    def get_chosen_sprite(self):
        character = self.user.get_char()
        if character is not None:
            return character.get_sprite(self.chosen_sprite_name)
        else:
            red_herring = characters["RedHerring"]
            red_herring.load()
            return red_herring.get_sprite("3")

    def set_connection_manager(self, connection_manager):
        self.connection_manager = connection_manager

    def get_connection_manager(self):
        return self.connection_manager

    def set_current_sprite_name(self, sprite_name):
        self.current_sprite_name = sprite_name
        self.on_current_sprite_name()

    def set_chosen_sprite_name(self, sprite_name):
        self.chosen_sprite_name = sprite_name

    def get_chosen_sprite_name(self):
        return self.chosen_sprite_name

    def set_chosen_subloc_name(self, subloc_name):
        self.chosen_subloc_name = subloc_name

    def get_chosen_subloc(self):
        return self.user.get_loc().get_sub(self.get_chosen_subloc_name())

    def get_chosen_subloc_name(self):
        return self.chosen_subloc_name

    def set_chosen_pos_name(self, pos_name):
        self.chosen_pos_name = pos_name

    def get_chosen_pos_name(self):
        return self.chosen_pos_name

    def set_chosen_sprite_option(self, sprite_option):
        self.chosen_sprite_option = sprite_option

    def get_chosen_sprite_option(self):
        return self.chosen_sprite_option

    def get_current_sprite_name(self):
        return self.current_sprite_name

    def set_current_loc(self, loc):
        self.current_loc = loc
        self.on_current_loc()

    def get_current_loc(self):
        return self.current_loc

    def set_current_subloc_name(self, subloc_name):
        self.current_subloc_name = subloc_name
        self.on_current_subloc_name()

    def get_current_subloc_name(self):
        return self.current_subloc_name

    def set_current_pos_name(self, pos_name):
        self.current_pos_name = pos_name

    def get_current_pos_name(self):
        return self.current_pos_name

    def set_current_sprite_option(self, sprite_option):
        self.current_sprite_option = sprite_option
        self.on_current_sprite_option()

    def get_current_sprite_option(self):
        return self.current_sprite_option

    def get_user(self):
        return self.user

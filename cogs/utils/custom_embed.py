from random import randint
from discord import Embed, User, Message


class CustomEmbed(Embed):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_author_to_user(self, user:User, *, use_user_colour:bool=True, image_to:str='author'):
        '''
        Runs the appropriate set_author method for a given user

        Parameters:
            user: User
                The user whose profile will be set into the embed
            image_to:str = "author" (optional)
                Where the user's profile image wil be set to
                Must be one of ["author", "image", "thumbnail", None]
            use_user_colour:bool = True (optional)
                Determines whether or not to use the passed user's role colour
        '''

        if image_to not in ['author', 'image', 'thumbnail', None]: 
            raise ValueError('image_to has not been set to an appropriate value')

        if image_to == 'author':
            self.set_author(name=str(user), icon_url=user.avatar_url)
        elif image_to == 'image':
            self.set_author(name=str(user))
            self.set_image(url=user.avatar_url)
        elif image_to == 'thumbnail':
            self.set_author(name=str(user))
            self.set_thumbnail(url=user.avatar_url)

        if use_user_colour:
            self.colour = user.colour.value

    def add_new_field(self, name:str, value:str, inline:bool=True):
        self.add_field(name=name, value=value, inline=inline)

    def add_blank_field(self):
        self.add_new_field('\u200B', '\u200B', False)

    def use_random_colour(self):
        self.colour = randint(0x1, 0xFFFFFF)

    def from_message(self, message:Message, *, use_user_colour:bool=False):
        '''
        Fills out the embed parameters and fields to be that of a given message
        '''

        self.set_author_to_user(message.author, use_user_colour=use_user_colour)
        timestamp = message.created_at.strftime('%A %B %d, %X')
        self.set_footer(text=timestamp)
        self.description = message.content 
        if len(message.attachments) > 0:
            att = message.attachments[0]
            if True in [att['filename'].lower().endswith(i) for i in ['.png', '.jpg', '.jpeg', '.gif']]:
                self.set_image(url=att['filename'])

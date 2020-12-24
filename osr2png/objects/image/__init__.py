from PIL import Image as ImagePil

from .classes.bg import Background
from .classes.avatar import Avatar
from .classes.text import Text
from .classes.overlay import Overlay, CustomBG

class Image:
    def __init__(self, settings):
        self.settings = settings
        self.image = ImagePil.new('RGBA', (int(self.settings.resolution[0]), int(self.settings.resolution[1])))

        starSize = int(64 * self.settings.sizeMultiplier)
        self.star = ImagePil.open('res/star.png').resize((starSize, starSize))


    def generate(self, style: str = 'default'):
        styles = {
                    'default': self.generate_default,
                    'ayreth': self.generate_ayreth
                }

        return styles.get(style, styles['default'])()


    def generate_default(self):
        img = self.image
        settings = self.settings

        Background(img, settings)
        # custom bg
        CustomBG(img, settings)
        # avatar
        Avatar(img, settings)




        text = Text(img, settings)

        # title - diff
        text.text(f"{self.settings.pp['data']['artist']} - {self.settings.pp['data']['title']}", align=1, offset=(0, -550))  
        text.text(f"{self.settings.pp['data']['diff']}", align=1, offset=(0, -400))

        # acc - mods
        text.text(f"{round(float(self.settings.pp['req']['acc']), 2)}%", align=2, offset=(-120, -100))
        text.text(f"{self.settings.pp['mods']['name']}", align=2, offset=(-120, 60))

        # star - pp
        accPos = text.text(f"{self.settings.pp['stats']['star']['pure']}", align=0, offset=(120, -100))
        img.paste(self.star, accPos, mask=self.star)

        text.text(f"{self.settings.pp['pp']['current']}pp", align=0, offset=(120, 60))


        # overlay
        Overlay(img, settings)

        return img


    def generate_ayreth(self):
        ''' credits to ayreth '''

        img = self.image
        settings = self.settings
        text = Text(img, settings)

        # stuff
        Background(img, settings)

        text.text(f"{self.settings.name}", align=1, shadow=False, size=100, offset=(0, -150))
        text.text(f"{self.settings.pp['data']['artist']} - {self.settings.pp['data']['title']}", align=1, shadow=False, size=100)


        return img






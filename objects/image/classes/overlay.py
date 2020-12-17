from PIL import Image

from .template import Template
from objects import glob

class Overlay(Template):
    def __init__(self, img, settings):
        super().__init__(img, settings)

        self.overlay = None

    def loadImage(self):
        self.overlay = Image.open('res/user/overlay.png').convert('RGBA')
        self.overlay = resize(self.settings.resolution, self.overlay)


    def addToImage(self):
        if not glob.config.customOverlay:
            return
        self.img.paste(self.overlay, mask=self.overlay)


class CustomBG(Template):
    ''' ez copy and paste '''
    def __init__(self, img, settings):
        super().__init__(img, settings)

        self.overlay = None

    def loadImage(self):
        self.overlay = Image.open('res/user/background.png').convert('RGBA')
        self.overlay = resize(self.settings.resolution, self.overlay)


    def addToImage(self):
        if not glob.config.customBG:
            return
        self.img.paste(self.overlay, mask=self.overlay)


def resize(resolution, img):
    width, height = img.size
    sizeMultiplier = resolution[0]/width

    width *= sizeMultiplier
    height *= sizeMultiplier

    img = img.resize(
        (
            int(width),
            int(height)
            )
        )

    return img
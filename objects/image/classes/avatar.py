from PIL import Image

from .template import Template

class Avatar(Template):
    def __init__(self, img, settings):
        super().__init__(img, settings)

        self.avatar = None




    def loadImage(self):
        borderColor = (220,220,220)
        #print(self.settings.sizeMultiplier)

        # resize image
        size, borderSize = int(200*self.settings.sizeMultiplier), int(205*self.settings.sizeMultiplier)
        avatar = Image.open(self.settings.avatar).convert('RGBA').resize((size, size))

        # "border"
        border = Image.new("RGBA", (borderSize, borderSize), borderColor)

        # paste Avatar to the centre of border
        posX, posY = (border.size[0]-avatar.size[0])/2, (border.size[1]-avatar.size[1])/2
        border.paste(avatar, (int(posX), int(posY)))

        self.avatar = border




    def addToImage(self):

        # paste to centre of the screen
        posX = (self.settings.resolution[0] - self.avatar.size[0])/2
        posY = (self.settings.resolution[1] - self.avatar.size[1])/2
        self.img.paste(self.avatar, (int(posX), int(posY)))



from PIL import Image


class Background:
    def __init__(self, img, settings):
        self.settings = settings
        self.img = img
        self.bg = None

        self.loadBG()
        self.addToImage()

    def loadBG(self):
        bg = Image.open(self.settings.mapBG).convert('RGBA')


        # resize to fit the canvas
        width, height = bg.size

        sizeMultiplier = self.settings.resolution[0]/width
        width *= sizeMultiplier
        height *= sizeMultiplier

        bg = bg.resize(
            (
                int(width),
                int(height)
                )
        )

        overlay = Image.new('RGBA', bg.size, (0, 0, 0, 128))
        bg.paste(overlay, mask=overlay)

        self.bg = bg



    def addToImage(self):
        # centre
        xPos = (self.settings.resolution[0] - self.bg.size[0])/2
        yPos = (self.settings.resolution[1] - self.bg.size[1])/2

        #print(self.settings.resolution[0], self.img.size[0])

        #xPos = 0
        #yPos = 0


        self.img.paste(self.bg, (int(xPos), int(yPos)))

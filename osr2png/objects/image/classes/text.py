from PIL import Image, ImageDraw, ImageFont

class Text:
    def __init__(self, img, settings):
        self.font = ImageFont.truetype('res/font.ttf', size=int(55*settings.sizeMultiplier))
        self.draw = ImageDraw.Draw(img)
        self.img = img
        self.settings = settings

    def text(self, text, color=(255, 255, 255), shadow=(0,0,0), align=0, offset=(0,0), size=55):
        # 0 - left
        # 1 - centre
        # 2 - right
        fontSize = size*self.settings.sizeMultiplier
        posX, posY = offset
        

        # word limit - 80
        if len(text) > 80:
            text = text[:80] + '...'

        # resize text to fix screen
        while self.font.getsize(text)[0] > self.settings.resolution[0] and fontSize > 20*self.settings.sizeMultiplier:
            fontSize -= 1*self.settings.sizeMultiplier
            self.font = ImageFont.truetype('res/font.ttf', size=int(fontSize*self.settings.sizeMultiplier))


        posX *= self.settings.sizeMultiplier
        posY *= self.settings.sizeMultiplier

        # font size
        textW, textH = self.draw.textsize(text, font=self.font)

        
        if align == 0:
            posX = (self.settings.resolution[0] - textW + textW)/2 + posX
            posY = (self.settings.resolution[1] + posY) / 2

        elif align == 1:
            posX = (self.settings.resolution[0] - textW) / 2 + posX
            posY = (self.settings.resolution[1] + posY) / 2 

        elif align == 2:
            posX = (self.settings.resolution[0] - textW - textW)/2 + posX
            posY = (self.settings.resolution[1] + posY) / 2


        shadowX = posX + (5 * self.settings.sizeMultiplier)
        shadowY = posY + (5 * self.settings.sizeMultiplier)

        if shadow: # user can set shadow as False
            self.draw.text((shadowX, shadowY), text, fill=shadow, font=self.font)
        self.draw.text((posX, posY), text, fill=color, font=self.font)

        # resets font size
        self.font = ImageFont.truetype('res/font.ttf', size=int(55*self.settings.sizeMultiplier))


        return (int(posX+textW+5*self.settings.sizeMultiplier), int(posY))



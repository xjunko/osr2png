

from objects import glob

from . import getSizeMultiplier

class Settings:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', -1)
        self.name = kwargs.get('name', 'No Name')

        self.replay = kwargs.get('replay')

        self.mapData = kwargs.get('mapData')
        self.mapID = kwargs.get('mapID', -1)
        self.mapSetID = kwargs.get('mapSetID', -1)
        self.mapBG = kwargs.get('mapBG', 'res/default_bg.png')

        self.avatar = kwargs.get('avatar', 'res/default_avatar.png')

        self.resolution = [int(x) for x in glob.config.resolution.split(',')]
        self.sizeMultiplier = getSizeMultiplier(self.resolution[1])



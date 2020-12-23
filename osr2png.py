import asyncio, re, os

from utils.replay import open_replay
from utils.settings import Settings
from utils import api

from objects.image import Image
from objects import glob


async def main(replay: str = 'test.osr'):
    r = open_replay(replay)
    userID = api._getUserID(r.player_name)
    _bsID, _bmID, _mapData = api._getMapID(r.map_md5)
    bg = api._getMapBackground(_bsID)
    avatar = api._getAvatar(userID)

    settings = Settings(
                        name=r.player_name, 
                        id=userID, 
                        mapData=_mapData,
                        mapSetID=_bsID, 
                        mapID=_bmID,
                        mapBG=bg,
                        avatar=avatar,
                        replay=r
                        )

    pp = api._getPP(settings)
    settings.pp = pp

    img = Image(settings)
    _img = img.generate()

    #_img.show()
    _img = _img.convert('RGB')
    _img.save(f'out/{_bmID}.png')


safeFilename = re.compile(r'[\\*?:"<>|]')

class osr2png:
    def __init__(self, replay: str, **kwargs):
        self.replay = open_replay(replay)
        self.userID = api._getUserID(self.replay.player_name)
        self.beatmapsetID, self.beatmapID, self.mapData = api._getMapID(self.replay.map_md5)
        self.background = api._getMapBackground(self.beatmapsetID)
        self.avatar = api._getAvatar(self.userID)

        self.settings = Settings(
                                    name = self.replay.player_name,
                                    id = self.userID,
                                    mapData = self.mapData,
                                    mapSetID = self.beatmapsetID,
                                    mapID = self.beatmapID,
                                    mapBG = self.background,
                                    avatar = self.avatar,
                                    replay = self.replay
                                )

        self.settings.pp = api._getPP(self.settings)

        self.outdir = kwargs.get('outdir', glob.config.outdir) # abit stupid i know

    def generate(self):
        img = Image(self.settings)
        res = img.generate()
        filename = f"[{self.settings.pp['mods']['name']}]{self.replay.player_name} on {self.mapData['title']} {self.mapData['version']}"
        # make filename safe
        filename = safeFilename.sub("", filename)

        res = res.convert('RGB') # convert to rgb else opacity fucked
        res.save(os.path.join(glob.config.outdir, filename + '.png'))



#m = osr2png('test2.osr')
#m.generate()




#asyncio.run(main())

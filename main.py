import asyncio

from utils.replay import open_replay
from utils.settings import Settings
from utils import api

from objects.image import Image


async def main():
    r = open_replay('test.osr')
    userID = await api.getUserID(r.player_name)
    _bsID, _bmID, _mapData = await api.getMapID(r.map_md5)
    bg = await api.getMapBackground(_bsID)
    avatar = await api.getAvatar(userID)

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

    pp = await api.getPP(settings)
    settings.pp = pp

    img = Image(settings)
    _img = img.generate()

    #_img.show()
    _img = _img.convert('RGB')
    _img.save(f'out/{_bmID}.png')





asyncio.run(main())

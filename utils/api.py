import aiohttp, requests

from PIL import Image
from io import BytesIO
from objects import glob


async def _request(url: str, params:dict = {}, _json: bool = False, _read: bool = False):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url, params=params) as res:
            if res.status == 200:

                if _json:
                    return await res.json()

                if _read:
                    return await res.read()

                return res

def __request(url: str, params:dict = {}, _json:bool = False, _read:bool = False):
    with requests.Session() as sess:
        with sess.get(url, params=params) as res:
            if res.status_code == 200:
                if _json:
                    return res.json()

                if _read:
                    return res.content

                return res



async def getUserID(username: str):
    url = 'https://osu.ppy.sh/api/get_user?k={key}&u={name}'.format(
                                                                        key = glob.config.apikey,
                                                                        name = username
                                                                    )
    if (res := await _request(url, _json=True)):
        _id = res[0]['user_id']
        return _id

    else:
        return -1

def _getUserID(username: str):
    url = 'https://osu.ppy.sh/api/get_user?k={key}&u={name}'.format(
                                                                        key = glob.config.apikey,
                                                                        name = username
                                                                    )
    if (res := __request(url, _json=True)):
        _id = res[0]['user_id']
        return _id

    else:
        return -1


async def getMapID(mapHash: str):
    url = 'https://osu.ppy.sh/api/get_beatmaps?k={key}&h={hash}'.format(
                                                                            key = glob.config.apikey,
                                                                            hash = mapHash
                                                                        )

    if (res := await _request(url, _json=True)):
        _mapID = res[0]

        return _mapID['beatmapset_id'], _mapID['beatmap_id'], _mapID

    return -1, -1

def _getMapID(mapHash: str):
    url = 'https://osu.ppy.sh/api/get_beatmaps?k={key}&h={hash}'.format(
                                                                            key = glob.config.apikey,
                                                                            hash = mapHash
                                                                        )

    if (res := __request(url, _json=True)):
        _mapID = res[0]

        return _mapID['beatmapset_id'], _mapID['beatmap_id'], _mapID

    return -1, -1


async def getMapBackground(mapID: int):
    url = 'https://assets.ppy.sh/beatmaps/{id}/covers/fullsize.jpg'.format(
                                                                            id = mapID
                                                                          )

    if (res := await _request(url, _read=True)):
        with open(f'cache/{mapID}.png', 'wb') as f:
            f.write(res)

        return f'cache/{mapID}.png'

    return 'res/default_bg.png'

def _getMapBackground(mapID: int):
    url = 'https://assets.ppy.sh/beatmaps/{id}/covers/fullsize.jpg'.format(
                                                                            id = mapID
                                                                          )

    if (res := __request(url, _read=True)):
        with open(f'cache/{mapID}.png', 'wb') as f:
            f.write(res)

        return f'cache/{mapID}.png'

    return 'res/default_bg.png'


async def getAvatar(userID: int):
    url = f'https://a.ppy.sh/{userID}'

    if (res := await _request(url, _read=True)):
        with open(f'cache/{userID}.png', 'wb') as f:
            f.write(res)

        return f'cache/{userID}.png'

    return 'res/default_avatar.png'

def _getAvatar(userID: int):
    url = f'https://a.ppy.sh/{userID}'

    if (res := __request(url, _read=True)):
        with open(f'cache/{userID}.png', 'wb') as f:
            f.write(res)
        return f'cache/{userID}.png'

    return 'res/default_avatar.png'


async def getPP(settings):
    params = {
    'id': settings.mapID,
    'mods': settings.replay.mods,
    'combo': settings.replay.max_combo,
    'miss': settings.replay.nmiss,
    'acc': str(calcAcc(settings.replay))
    }  

    if (res := await _request('https://pp.osuck.net/pp', params=params, _json=True)):
        return res

def _getPP(settings):
    params = {
    'id': settings.mapID,
    'mods': settings.replay.mods,
    'combo': settings.replay.max_combo,
    'miss': settings.replay.nmiss,
    'acc': str(calcAcc(settings.replay))
    }  

    if (res := __request('https://pp.osuck.net/pp', params=params, _json=True)):
        return res



def calcAcc(replay):
    res = (((replay.n300)*300+(replay.n100)*100+(replay.n50)*50+(replay.nmiss)*0)/((replay.n300+replay.n100+replay.n50+replay.nmiss)*300))*100
    return res
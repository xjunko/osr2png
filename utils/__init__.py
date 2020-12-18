import json
from types import SimpleNamespace

def getSizeMultiplier(height):
    return height/720

def getSizeMultiplier_(pixel: int):
    ''' this is retarded how tf am i supposed to calc resize shit '''
    defaultPixel = 921600 # 1280x720
    return (pixel/defaultPixel)*1



def loadConfig():
    with open('config.json') as file:
        res = json.loads(file.read(), object_hook=lambda d: SimpleNamespace(**d))

    return res


def saveConfig(settings):
    with open('config.json', 'w') as f:
        f.write(json.dumps(settings.__dict__, indent=4))

    print('Config Saved!')
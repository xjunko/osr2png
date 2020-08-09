from PIL import Image, ImageDraw
import requests, subprocess

class osr2png:
    def __init__(self, replaydata, apikey, mapbg=None,outdir='img/',redl=False):
        self.replay = replaydata
        self.apiKey = apikey
        self.reDL = redl
        self.outDir = outdir

        # image stuff
        self.width = 1280
        self.bg = {'pfpsize': 200}
        self.height = 720
        self.baseImage = None
        self.mapBG = 'data/bg.png' if mapbg is None else mapbg
        self.starImage = 'data/star.png'
        self.avatar = None

        # osu stuff
        self.mapData = None
        self.userData = None
        self.acc = 0
        self.pp = None
        self.wgetargs = '' if redl else '-nc'

        self.UrlBeatmapApi = f'https://osu.ppy.sh/api/get_beatmaps?k={self.apiKey}&h='
        self.UrlUserdataApi = f'https://osu.ppy.sh/api/get_user?k={self.apiKey}&u='


    def getBeatmap(self, mapHash):
        try:
            data = requests.get(f'{self.UrlBeatmapApi}{mapHash}').json()[0]
        except Exception as e:
            return e

        return data

    def getUserdata(self, id):
        try:
            data = requests.get(f'{self.UrlUserdataApi}{id}').json()[0]
        except Exception as e:
            return e
        return data

    def get_player_pfp(self, userID):
        subprocess.call(f'wget {self.wgetargs} -O ./img/{userID}.png https://a.ppy.sh/{userID}')



    def __init_replay_data__(self):
        self.mapData = self.getBeatmap(self.replay.beatmap_hash)
        self.userData = self.getUserdata(self.replay.player_name)
        self.get_player_pfp(self.userData['user_id'])
        self.avatar = f'img/{self.userData["user_id"]}.png'



    def __init_base_image__(self):
        self.bg['base'] = Image.new('RGBA', (self.width,self.height), (0, 0, 0)) # create blank/black image


        # load bg
        mapBG = Image.open(self.mapBG).convert('RGBA')
        width, height = mapBG.size
        # get size
        sizeMultiplier = self.width/width
        width *= sizeMultiplier
        height *= sizeMultiplier
        # resize to fit screen
        mapBG = mapBG.resize((round(width), round(height)))
        mapBG.putalpha(128)

        # yes
        self.bg['mapBG'] = mapBG

        # load avatar
        self.bg['avatar'] = Image.open(self.avatar).convert('RGBA').resize((self.bg['pfpsize'], self.bg['pfpsize']))
        self.bg['avatarX'], self.bg['avatarY'] = self.bg['avatar'].size

        # load star
        self.bg['star'] = Image.open(self.starImage).convert('RGBA').resize((64,64))

        # border test
        self.bg['border'] = Image.new("RGBA", (205,205), (220,220,220))
        self.bg['borderX'], self.bg['borderY'] = self.bg['border'].size

    def __join_image__(self):
        # bg
        self.bg['base'].paste(self.bg['mapBG'])
        # border
        self.bg['base'].paste(self.bg['border'], (round((self.width-self.bg['borderX'])/2), round((self.height-self.bg['borderY'])/2)))
        # avatar
        self.bg['base'].paste(self.bg['avatar'], (round((self.width-self.bg['avatarX'])/2), round((self.height-self.bg['avatarY'])/2)))


    def __save__(self):
        self.bg['base'].convert('RGB')
        self.bg['base'].save('lol.png')






    def run(self):
        self.__init_replay_data__()
        self.__init_base_image__()
        self.__join_image__()


        # ae
        self.__save__()
        






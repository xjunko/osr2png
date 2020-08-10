from PIL import Image, ImageDraw, ImageFont
import pyttanko as osu
import requests, subprocess

def getMods(modsNumber): # :) this is retarded but idc i cant think of something better
    mods = {
        0 : 'NM',
        1 : 'NF',
        2 : 'EZ',
        4 : 'TD',
        8 : 'HD',
        16 : 'HR',
        24 : 'HDHR',
        64 : 'DT',
        72 : 'HDDT',
        88 : 'HDHRDT',
        128 : 'RX',
        1024 : 'FL',
        256 : 'HT'
    }
    try:
        return '+' + mods[modsNumber]
    except:
        return 



class osr2png:
    def __init__(self, replay, apikey, mapdata, osufiledir, mapbg=None, outdir='data/', redl=False):
        self.replay = replay
        self.apiKey = apikey
        self.reDL = redl
        self.outDir = outdir
        self.mapDir = osufiledir

        # image stuff
        self.width = 1280
        self.bg = {'pfpsize': 200}
        self.height = 720
        self.baseImage = None
        self.mapBG = 'data/bg.png' if mapbg is None else mapbg
        self.starImage = 'data/star.png'
        self.avatar = None
        self.font = None
        self.imageDraw = None

        # osu stuff
        self.mapData = mapdata
        self.userData = None
        self.acc = 0
        self.pp = None
        self.mods = None
        self.starmodded = None
        self.wgetargs = '' if redl else '-nc'

        self.UrlBeatmapApi = f'https://osu.ppy.sh/api/get_beatmaps?k={self.apiKey}&h='
        self.UrlUserdataApi = f'https://osu.ppy.sh/api/get_user?k={self.apiKey}&u='
        self.ppApi = 'https://teal-second-spear.glitch.me/calc'



    def getUserdata(self, id):
        try:
            data = requests.get(f'{self.UrlUserdataApi}{id}').json()[0]
        except Exception as e:
            return e
        return data

    def get_player_pfp(self, userID):
        subprocess.call(f'wget {self.wgetargs} -O {self.outDir}{userID}.png https://a.ppy.sh/{userID}')

    def roundString(self, s: str, digits: int):
        n = round(float(s), digits)
        return str(n)

    def __init_replay_data__(self):
        self.userData = self.getUserdata(self.replay.player_name)
        self.get_player_pfp(self.userData['user_id'])
        self.avatar = f'{self.outDir}{self.userData["user_id"]}.png'

        mods = 0
        # mod fix for new osrparse - idk how to read enums so ill use this
        for x in self.replay.mod_combination:
            mods += x.value
        self.replay.mod_combination = mods

        self.mods = getMods(mods)


        # pee pee calculation
        self.acc = (((self.replay.number_300s)*300+(self.replay.number_100s)*100+(self.replay.number_50s)*50+(self.replay.misses)*0)/((self.replay.number_300s+self.replay.number_100s+self.replay.number_50s+self.replay.misses)*300))*100
        self.__get_pp__()



    def __get_pp__(self):
        try:
            self.pp = requests.get(f'{self.ppApi}', params={
                'id': self.mapData[1]['beatmap_id'],
                'acc' : self.acc,
                'combo' : self.replay.max_combo,
                'mods' : self.replay.mod_combination
            }).json()

        except: 
            return None
            raise RuntimeError('Failed to get pp')

        


    def __init_base_image__(self):
        self.bg['base'] = Image.new('RGBA', (self.width,self.height), (0, 0, 0)) # create blank/black image
        self.font = ImageFont.truetype('data/font.ttf', size=55) # font
        self.imageDraw = ImageDraw.Draw(self.bg['base']) # text thing

        # thx uyitroa again
        blackoverlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 128))


        # load bg
        mapBG = Image.open(self.mapBG).convert('RGBA')
        width, height = mapBG.size
        # get size
        sizeMultiplier = self.width/width
        width *= sizeMultiplier
        height *= sizeMultiplier
        # resize to fit screen
        mapBG = mapBG.resize((round(width), round(height)))

        # yes
        self.bg['mapBG'] = mapBG
        # shouldve done this
        self.bg['mapBG'].paste(blackoverlay, (0,0), mask=blackoverlay)

        # load avatar
        self.bg['avatar'] = Image.open(self.avatar).convert('RGBA').resize((self.bg['pfpsize'], self.bg['pfpsize']))
        self.bg['avatarX'], self.bg['avatarY'] = self.bg['avatar'].size

        # load star
        self.bg['star'] = Image.open(self.starImage).convert('RGBA').resize((64,64))
        self.bg['starX'], self.bg['starY'] = self.bg['star'].size

        # border test
        self.bg['border'] = Image.new("RGBA", (205,205), (220,220,220))
        self.bg['borderX'], self.bg['borderY'] = self.bg['border'].size



    def drawText(self, text, color=(255,255,255), shadowcolor=(0,0,0), xoffset=0, yoffset=0, shadowoffset=5):
        negative = '-' in str(xoffset)
        shadowoffset = shadowoffset
        textW, textH = self.imageDraw.textsize(text,font=self.font)
        args = []

        if xoffset and not negative:
            args.append([ (self.width-textW+textW)/2+xoffset+shadowoffset , (self.height-yoffset)/2+shadowoffset])
            args.append([ (self.width-textW+textW)/2+xoffset , (self.height-yoffset)/2])
        elif xoffset and negative:
            args.append([ (self.width-textW-textW)/2+xoffset+shadowoffset , (self.height-yoffset)/2+shadowoffset])
            args.append([ (self.width-textW-textW)/2+xoffset , (self.height-yoffset)/2])

        elif not xoffset:
            args.append([ (self.width-textW)/2+shadowoffset , (self.height-yoffset)/2+shadowoffset ])
            args.append([ (self.width-textW)/2 , (self.height-yoffset)/2 ])
            
        
        self.imageDraw.text(args[0], text, fill=shadowcolor, font=self.font)
        self.imageDraw.text(args[1], text, fill=color, font=self.font)

        return [textW,textH], args[1]


    def __join_image__(self):
        # bg
        self.bg['base'].paste(self.bg['mapBG'])
        
        # border
        self.bg['base'].paste(self.bg['border'], (round((self.width-self.bg['borderX'])/2), round((self.height-self.bg['borderY'])/2)))
        # avatar
        self.bg['base'].paste(self.bg['avatar'], (round((self.width-self.bg['avatarX'])/2), round((self.height-self.bg['avatarY'])/2)))

        # map title
        self.drawText(f"{self.mapData[1]['artist_name']} - {self.mapData[1]['song_title']}", yoffset=550)
        # diff name
        self.drawText(self.mapData[1]['version'], yoffset=400)
        # pee pee
        self.drawText(f'{self.pp["pp"]}pp', xoffset=120, yoffset=-60)
        # star rating
        star = self.drawText(f'{self.pp["stats"]["star"]}', xoffset=120, yoffset=100)
        # star logo thing
        self.bg['base'].paste(self.bg['star'], ( round(star[1][0]+star[0][0]+5), round(star[1][1])), mask=self.bg['star'])
        # acc
        self.drawText(f'{self.roundString(self.acc, 2)}%',xoffset=-120, yoffset=100)
        # mods
        self.drawText(f'{self.mods}', xoffset=-120, yoffset=-60)


    def __save__(self):
        mapTitle = self.mapData[0].info['Metadata'].split('\n')[0]
        self.bg['base'] = self.bg['base'].convert('RGB')
        self.bg['base'].save(f"[{self.mods}]{self.replay.player_name} on {self.mapData[1]['song_title']} [{self.mapData[1]['version']}].png")







    def run(self):
        self.__init_replay_data__()
        self.__init_base_image__()
        self.__join_image__()


        # ae
        self.__save__()
        






import pygame
from osrparse import parse_replay_file
import requests
import subprocess
import os, sys


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


class ReplayThumbnail:
    def __init__(self,replayfile, apikey, redl=0):
        #
        self.wgetargs = '-nc' if not redl else ''

        #
        self.replayfile = replayfile
        self.replaydata = None
        self.height = 1280
        self.width = 720
        self.font = None
        self.bg = {'pfpsize': 200}
        self.screen = None
        self.dir = './img/'
        self.apikey = apikey

        self.mapID = None
        self.mapData = None
        self.userID = None
        self.userData = None
        self.acc = 0
        self.pp = None


        self.UrlBeatmapApi = f'https://osu.ppy.sh/api/get_beatmaps?k={self.apikey}&h='
        self.UrlUserdataApi = f'https://osu.ppy.sh/api/get_user?k={self.apikey}&u='
        self.BloodcatImage = 'https://bloodcat.com/osu/i/'
        self.ppApi = 'https://teal-second-spear.glitch.me/calc'

    def __init_replay__(self):
        mods = 0
        try:
            self.replaydata = parse_replay_file(self.replayfile)

            # mod fix for new osrparse - idk how to convert it into numbers so ill use this
            for x in self.replaydata.mod_combination:
                mods += x.value
            self.replaydata.mod_combination = mods


            print(f'Player: {self.replaydata.player_name}\n'
                    f'Mods: {self.replaydata.mod_combination}')

            

        except Exception as err:
            print(f'Invalid Replay!')
            print(err)
            sys.exit()

        self.mapData = self.__getBeatmap__(self.replaydata.beatmap_hash)
        self.userData = self.__getUserdata__(self.replaydata.player_name)
        self.__get_map_bg__(self.mapData['beatmap_id'])
        self.__get_player_pfp__(self.userData['user_id'])

        # pp shit
        self.acc = (((self.replaydata.number_300s)*300+(self.replaydata.number_100s)*100+(self.replaydata.number_50s)*50+(self.replaydata.misses)*0)/((self.replaydata.number_300s+self.replaydata.number_100s+self.replaydata.number_50s+self.replaydata.misses)*300))*100
        self.__get_pp__()


    def __getBeatmap__(self, mapHash):
        try:
            data = requests.get(f'{self.UrlBeatmapApi}{mapHash}').json()[0]
        except:
            return

        return data

    def __getUserdata__(self, id):
        try:
            data = requests.get(f'{self.UrlUserdataApi}{id}').json()[0]
        except:
            return
        return data

    def __get_map_bg__(self, mapID):
        # u can just not call this function and just skip to pygame if u have the image
        subprocess.call(f'wget {self.wgetargs} -O ./img/{mapID}.png https://bloodcat.com/osu/i/{mapID}')

    def __get_player_pfp__(self, userID):
        # u can just not call this function and just skip to pygame if u have the image
        subprocess.call(f'wget {self.wgetargs} -O ./img/{userID}.png https://a.ppy.sh/{userID}')

    def __get_pp__(self):
        try:
            self.pp = requests.get(f'{self.ppApi}', params={
                'id': self.mapData['beatmap_id'],
                'acc' : self.acc,
                'combo' : self.replaydata.max_combo,
                'mods' : self.replaydata.mod_combination
            }).json()

        except: 
            return None
            raise RuntimeError('Failed to get pp')



    def retardedTextFunction(self, text, color=(255,255,255), shadowcolor=(0,0,0), xoffset=0, yoffset=0):
        negative = '-' in str(xoffset)
        textren = self.font.render(text, True, color)
        text_shadow_ren = self.font.render(text, True, shadowcolor)

        result = None
        args = []



        # oh god here we go
        # before i rewrite this it used to be an unreadable shit
        # somehow i managed to rewrite it
        # and it still unreadable
        if xoffset and not negative:
            args.append([self.height/2-textren.get_width()/2+textren.get_width()/2+xoffset+5, self.width/2-yoffset/2+5])
            args.append([self.height/2-textren.get_width()/2+textren.get_width()/2+xoffset, self.width/2-yoffset/2])

        elif xoffset and negative:
            args.append([self.height/2-textren.get_width()/2-textren.get_width()/2+xoffset+5, self.width/2-yoffset/2+5])
            args.append([self.height/2-textren.get_width()/2-textren.get_width()/2+xoffset, self.width/2-yoffset/2])

        elif not xoffset:
            args.append([self.height/2-textren.get_width()/2+5, self.width/2-yoffset/2+5])
            args.append([self.height/2-textren.get_width()/2, self.width/2-yoffset/2])

        # god i hate math


        self.screen.blit(text_shadow_ren, args[0])
        self.screen.blit(textren, args[1])
        return args[1]
        

    def __pygame__init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.height, self.width))
        self.font = pygame.font.Font('data/font.ttf', 55)

        self.__load_image__()
        self.__draw_image__()

    def __load_image__(self):
        # bg
        self.bg['image'] = pygame.image.load(f"{self.dir}{self.mapData['beatmap_id']}.png")
        self.bg['bgX'], self.bg['bgY'] = self.bg['image'].get_rect().size

        # bg resize - proud of this one
        newBGRes = self.height/self.bg['bgX']      

        self.bg['image'] = pygame.transform.rotozoom(self.bg['image'], 0, newBGRes) 
        self.bg['bgX'], self.bg['bgY'] = self.bg['image'].get_rect().size

        # pfp
        self.bg['pfp'] = pygame.image.load(f"{self.dir}{self.userData['user_id']}.png")
        self.bg['pfp'] = pygame.transform.scale(self.bg['pfp'], (self.bg['pfpsize'], self.bg['pfpsize']))
        self.bg['pfpX'], self.bg['pfpY'] = self.bg['pfp'].get_rect().size


        # star
        self.bg['star'] = pygame.image.load(f"./data/star.png")
        self.bg['star'] = pygame.transform.scale(self.bg['star'], (64,64))
        self.bg['starX'], self.bg['starY'] = self.bg['star'].get_rect().size
        

        # dark bg
        self.bg['dark'] = pygame.Surface((1280,720), pygame.SRCALPHA)
        self.bg['dark'].fill((0,0,0,150))

    def __draw_image__(self):
        # bg
        self.screen.blit(self.bg['image'], [self.height/2-self.bg['bgX']/2, self.width/2-self.bg['bgY']/2])
        # dark thing
        self.screen.blit(self.bg['dark'], [0,0])
        # pfp
        self.screen.blit(self.bg['pfp'], [self.height/2-self.bg['pfpX']/2, self.width/2-self.bg['pfpY']/2] )
        # square border thing on pfp
        pygame.draw.rect(self.screen, [220,220,220], [self.height/2-self.bg['pfpsize']/2, self.width/2-self.bg['pfpsize']/2, self.bg['pfpsize'], self.bg['pfpsize']], 3) # veri long its retarded
        # bad code moment. this took the longest to implement/rewrite
        
        # map title
        self.retardedTextFunction(f'{self.mapData["artist"]} - {self.mapData["title"]}', yoffset=550)
        # diff name
        self.retardedTextFunction(f'[{self.mapData["version"]}]', yoffset=400)
        # star rating 
        starTextPosX, starTextPosY = self.retardedTextFunction(f'{self.roundString(self.pp["stats"]["star"], 4)}', xoffset=175, yoffset=100)
        self.screen.blit(self.bg['star'], (self.height/2-self.bg['starX']/2+140, starTextPosY))
        # pee pee
        self.retardedTextFunction(f'{round(self.pp["pp"])}pp', xoffset=120, yoffset=-60)

        # mods
        self.retardedTextFunction(f'{getMods(self.replaydata.mod_combination)}', xoffset=-120, yoffset=-60)

        # acc
        self.retardedTextFunction(f'{str(self.acc)[:5]}%', xoffset=-120, yoffset=100)
        
    def roundString(self, s: str, digits: int):
        n = round(float(s), digits)
        return str(n)

    def render_and_save(self):
        pygame.display.flip()
        pygame.image.save(self.screen, f'[{self.userData["username"]}][{getMods(self.replaydata.mod_combination)}] {self.mapData["creator"]} - {self.mapData["title"]} [{self.mapData["version"]}].png')




    def run(self):
        self.__init_replay__()
        self.__pygame__init__()
        self.render_and_save()

        






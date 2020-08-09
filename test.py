from Utils.find_beatmap import find_beatmap_ as find_beatmap
from Utils.osuparser import Beatmap, read_file
from osrparse import parse_replay_file
from main import osr2png
import os

osupath = r'C:\Users\Alif\AppData\Local\osu!'
replayFile = 'replays/1.osr'

# read osu stuff
beatmap = find_beatmap(replayFile, osupath)
osufiledir = os.path.join(osupath, 'Songs', beatmap['folder_name'], beatmap['osu_file'])
mapdata = read_file(osufiledir)

bgdir = os.path.join(osupath, 'Songs', beatmap['folder_name'], mapdata.bg[2])

# read replay
replayData = parse_replay_file(replayFile)



# Run
osr2png(replayData, '78b9a37dca0884fee07ff3b7c3853e3e8615d422', bgdir).run()





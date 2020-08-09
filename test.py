from Utils.find_beatmap import find_beatmap_ as find_beatmap
from Utils.osuparser import Beatmap, read_file
from osrparse import parse_replay_file
from main import osr2png
import os, json

jsonStuff = json.loads(open('settings.json').read())

osupath = jsonStuff['osudir']
replayFile = 'replays/1.osr'

# read osu stuff
beatmap = find_beatmap(replayFile, osupath)
osufiledir = os.path.join(osupath, 'Songs', beatmap['folder_name'], beatmap['osu_file'])
mapdata = read_file(osufiledir)

bgdir = os.path.join(osupath, 'Songs', beatmap['folder_name'], mapdata.bg[2])

# read replay
replayData = parse_replay_file(replayFile)



# Run
osr2png(replayData, json['osukey'], bgdir).run()





import argparse
from osr2png import ReplayThumbnail
from osrparse import parse_replay_file
from osrparse.enums import Mod
import json,sys

import tkinter as tk
from tkinter import filedialog



parser = argparse.ArgumentParser(description='thing that convert osr files to thumbnail v0.69 by fireredz')
parser.add_argument('replay', help='replay file', default=None,  nargs='?')
args = parser.parse_args()

file_path = args.replay
# if no shit given
if args.replay is None:
    print('no file given bruh... opening filedialog')
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()


try:
    config = json.load(open('settings.json'))
    config['osuapikey']
except:
    print('Invalid api key!')
    sys.exit()

sys.exit() if len(str(config['osuapikey'])) < 10 else print('Loaded apikey!')

ReplayThumbnail(file_path, config['osuapikey'], config['forceDownload']).run()




# main stuff
from Utils.find_beatmap import find_beatmap_ as find_beatmap
from Utils.osuparser import Beatmap, read_file
from osrparse import parse_replay_file
from pathlib import Path
from osr2png import osr2png
import os, json, glob

# gui
import PySimpleGUI as sg

# init #####################

def setupSettings(osukey='osu api key here', osudir='your osu directory', outdir='thumbnail/', lastreplay=''):
    data = {
        'osukey' : osukey,
        'osudir' : osudir,
        'outdir' : outdir,
        'lastreplay': lastreplay
    }

    with open('settings.json', 'w') as file:
        file.write(json.dumps(data, indent=4))

# create data dir if it not exists 
if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isdir('thumbnail'):
    os.mkdir('thumbnail')


if os.path.isfile('settings.json'):
    try:
        temp = json.loads(open('settings.json').read())
    except:
        print('Failed to read settings.json... Can you check if something wrong in it?')
        exit()

if not os.path.isfile('settings.json'):
    print('No config found, creating...')
    setupSettings()
    print('Created!')


################

# gui starts here
settings = json.loads(open('settings.json').read())
sg.theme('DarkBlack')
layout = [
            [sg.Text('osu! api key:')],
            [sg.Input(settings['osukey'], key='osukey'), sg.Checkbox('Redownload Images?', key='redl')],

            [sg.Text('osu! path:')],
            [sg.Input(settings['osudir'], key='osudir'), sg.FolderBrowse(target=(3,-2))],

            [sg.Text('Output path: (must have / at the end, ex: C:/img/)')],
            [sg.Input(settings['outdir'], key='outdir'), sg.FolderBrowse(target=(5, -2))],

            [sg.Button('Save Setting')],

            [sg.Text('Replay File')],
            [sg.Input(settings['lastreplay'],key='replaydir'), sg.FilesBrowse(target=(8,-2))],

            [sg.Button('Render'), sg.Button('Close')],

            [sg.Output(size=(64,10))]
        ]



window = sg.Window('osr2png', layout)
while True:             
    event, values = window.read()
    # save to settings
    if event == 'Save Setting':
        setupSettings(osukey=values['osukey'], osudir=values['osudir'].replace('/', '\\'), outdir=values['outdir'], lastreplay=values['replaydir'])

    if event == 'Render':
        setupSettings(osukey=values['osukey'], osudir=values['osudir'].replace('/', '\\'), outdir=values['outdir'], lastreplay=values['replaydir'])
        #######################
        print('Starting...')
        # read replay and shit
        if values['replaydir'] == '':
            print('No replay given, stopping...')
            continue
        elif len(values['osukey']) < 40:
            print('Invalid osu! api key')
            continue


        # starts doing stuff
        replay = parse_replay_file(values['replaydir'])
        beatmap = find_beatmap(values['replaydir'], values['osudir'])
        osufiledir = os.path.join(settings['osudir'], 'Songs', beatmap['folder_name'], beatmap['osu_file'])
        mapdata = read_file(osufiledir)
        bgdir = os.path.join(settings['osudir'], 'Songs', beatmap['folder_name'], mapdata.bg[2])

        # when passed those fucked up shit above
        print('--------')
        print(f'Player: {replay.player_name}')
        print(f'Map: {beatmap["song_title"]}')
        print(f'Diff: {beatmap["version"]}')
        print('--------')
        print('Completed getting data for replay and renderer.')
        print('Rendering...')
        outdir = osr2png(replay, settings['osukey'], [mapdata,beatmap], osufiledir, mapbg=bgdir, outdir='data/', thumbnaildir=values['outdir'], redl=values['redl']).run()
        print(f'Completed!, your thumbnail is at {outdir}')



    if event in ('Close', None):
        break

window.close()

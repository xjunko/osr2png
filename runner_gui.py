# main stuff
from Utils.find_beatmap import find_beatmap_ as find_beatmap
from Utils.osuparser import Beatmap, read_file
from osrparse import parse_replay_file
from main import osr2png
import os, json, glob

# gui stuff
from gooey import Gooey, GooeyParser


@Gooey(program_name='osr2png', tabbed_groups=True)
def main():
    parser = GooeyParser(description='Convert osu! replay into a thumbnail.')
    settings = json.loads(open('settings.json').read())

    # main
    group1 = parser.add_argument_group('General')
    #group1.add_argument('replay', help='osu! replay file', widget='FileChooser') 
    replayfiles = getReplayFiles(os.path.join(settings['osudir'], 'replays/'))
    group1.add_argument(
        dest='replay',
        widget='Dropdown',
        choices=replayfiles['short']
        )
    
    

    # settings
    group2 = parser.add_argument_group('Settings')
    group2.add_argument('osudir', default=settings['osudir'], help='Your osu! directory',widget='DirChooser')
    group2.add_argument('osukey', default=settings['osukey'], help='Get it on https://old.ppy.sh/p/api')
    group2.add_argument("-r", "--redl", action='store_true',widget='CheckBox', help=" - Redownload Images such as Profile Picture")


    args = parser.parse_args()
    args.replay = replayfiles['normal'][replayfiles['short'].index(args.replay)]
    args.replay = os.path.join(args.osudir,'replays',args.replay)
    # save 
    setupSettings(osukey=args.osukey, osudir=args.osudir)


    # do stuff
    print('Initializing...')
    replay = parse_replay_file(args.replay)
    beatmap = find_beatmap(args.replay, settings['osudir'])
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
    outdir = osr2png(replay, settings['osukey'], [mapdata,beatmap],osufiledir, mapbg=bgdir, outdir='data/', thumbnaildir='thumbnail/', redl=args.redl).run()
    print(f'Completed!, your thumbnail is at {outdir}')

def setupSettings(osukey='osu api key here', osudir='your osu directory'):
    data = {
        'osukey' : osukey,
        'osudir' : osudir
    }

    with open('settings.json', 'w') as file:
        file.write(json.dumps(data, indent=4))

    #print('Saved settings.json') # only enable this when debugging

def getReplayFiles(dir):
    replays = glob.glob(f'{dir}*.osr')
    replays.sort(key=os.path.getmtime, reverse=True)
    replaysShort = map(getFileName, replays)
    replays = map(os.path.basename, replays)

    return {
        'short': list(replaysShort),
        'normal': list(replays)
    }

def getFileName(file):
    return os.path.basename(file) if len(os.path.basename(file)) < 100 else os.path.basename(file)[:100]+'...'


def init():
    # create data dir if it not exists 
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('thumbnail'):
        os.mkdir('thumbnail')


    try:
        json.loads(open('settings.json').read())
    except:
        print('No config found, creating...')
        setupSettings()
        print('Created!')


if __name__ == '__main__':
    init()

    main()

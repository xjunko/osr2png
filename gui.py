import PySimpleGUI as sg

from osr2png import osr2png, logger # what the fuck
from osr2png.utils import loadConfig, saveConfig, checkFolder
from osr2png.objects.enums import Event
from osr2png.objects import glob

# logging shit
import logging, sys
from autologging import logged, TRACE, traced

sg.theme('DarkBlack')
glob.config = loadConfig()
checkFolder(glob.config)

layout = [
            [sg.Text('osu! api key:')],
            [sg.Input(glob.config.apikey, key=Event.osukey)],

            [sg.Text('Output path:')],
            [sg.Input(glob.config.outdir, key=Event.outdir), sg.FolderBrowse(target=(3, -2))],

            [sg.Text('Resolution: (Width, Height)')],
            [sg.Input(glob.config.resolution, key=Event.resolution)],

            [sg.Checkbox("customBG", key=Event.custombg, default=glob.config.customBG), sg.Checkbox("customOverlay", key=Event.customoverlay, default=glob.config.customOverlay)],

            [sg.Button('Save Setting', key=Event.save)],

            [sg.Text('Replay File')],
            [sg.Input(glob.config.lastreplay, key=Event.replaydir), sg.FilesBrowse(target=(9, 0))],
            #[sg.Input(size=(100,250))],

            [sg.Button('Render', key=Event.render), sg.Button('Close', key=Event.close)],

            #[sg.Output(size=(64,10))],

         ]


window = sg.Window("fuck", layout)

#@logged(logger)
#@traced
# lol dont log this
def saveConfigGui(value):
    glob.config.outdir = value[Event.outdir]
    glob.config.lastreplay = value[Event.replaydir]
    glob.config.resolution = value[Event.resolution]
    glob.config.customBG = value[Event.custombg]
    glob.config.customOverlay = value[Event.customoverlay]
    saveConfig(glob.config)

@logged(logger)
@traced
def main():
    value = []
    event = None
    while True:
        event, value = window.read(timeout=300)
        if event == sg.WIN_CLOSED or event == Event.close:
            break

        if event == Event.save:
            saveConfigGui(value)
            

        if event == Event.render:
            if not value[Event.replaydir] or not value[Event.replaydir].endswith('.osr'):
                print('No replay given!')
                continue
            if len(value[Event.osukey]) < 40:
                print('Invalid osu!api key!')
                continue

            # save shit to settings
            saveConfigGui(value)

            app = osr2png(value[Event.replaydir])
            app.generate()
            print('done?')




if __name__ == '__main__':
    logging.basicConfig(level=TRACE,
                        filename='logs.log',
                        filemode="w",
                        format="%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s")
    main()
    window.close()
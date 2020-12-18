import PySimpleGUI as sg

from main import osr2png
from utils import loadConfig, saveConfig
from objects.enums import Event

sg.theme('DarkBlack')
settings = loadConfig()

layout = [
            [sg.Text('osu! api key:')],
            [sg.Input(settings.apikey, key=Event.osukey)],

            [sg.Text('Output path:')],
            [sg.Input(settings.outdir, key=Event.outdir), sg.FolderBrowse(target=(3, -2))],

            [sg.Text('Resolution: (Width, Height)')],
            [sg.Input(settings.resolution, key=Event.resolution)],

            [sg.Checkbox("customBG", key=Event.custombg, default=settings.customBG), sg.Checkbox("customOverlay", key=Event.customoverlay, default=settings.customOverlay)],

            [sg.Button('Save Setting', key=Event.save)],

            [sg.Text('Replay File')],
            [sg.Input(settings.lastreplay, key=Event.replaydir), sg.FilesBrowse(target=(8, 0))],
            #[sg.Input(size=(100,250))],

            [sg.Button('Render', key=Event.render), sg.Button('Close', key=Event.close)],

            [sg.Output(size=(64,10))],

         ]


window = sg.Window("fuck", layout)

while True:
    event, value = window.read(timeout=300)
    if event == sg.WIN_CLOSED or event == Event.close:
        break

    if event == Event.render:
        if not value[Event.replaydir] or not value[Event.replaydir].endswith('.osr'):
            print('No replay given!')
            continue
        if len(value[Event.osukey]) < 40:
            print('Invalid osu!api key!')
            continue

        app = osr2png(value[Event.replaydir])
        app.generate()
        print('done?')

        # save shit to settings
        settings.outdir = value[Event.outdir]
        settings.lastreplay = value[Event.replaydir]
        settings.resolution = value[Event.resolution]
        settings.customBG = value[Event.custombg]
        settings.customOverlay = value[Event.customoverlay]

        saveConfig(settings)


window.close()
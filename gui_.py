import PySimpleGUI as sg

from utils import loadConfig

sg.theme('DarkAmber')
settings = loadConfig()

layout = [
            [sg.Text('osu! api key:')],
            [sg.Input(settings['apikey'], key='osukey'), sg.Checkbox('Redownload Image?', key='redl')],

            [sg.Text('Output path:')],
            [sg.Input(settings['outdir'], key='outdir'), sg.FolderBrowse(target=(3, -2))],

            [sg.Button('Save Setting')],

            [sg.Text('Replay File')],
            [sg.Input('Choose a .osr file'), sg.FilesBrowse(target=(5, 0))],

            [sg.Button('Render'), sg.Button('Close')],

            [sg.Output(size=(64,10))],

         ]


window = sg.Window("fuck", layout)

while True:
    event, value = window.read(timeout=10)

    if event == sg.WIN_CLOSED:
        break


window.close()
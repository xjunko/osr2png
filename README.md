# osr2png - rewrite³

[![GitHub release](https://img.shields.io/github/release/xjunko/osr2png.svg?style=for-the-badge&logo=appveyor)](https://github.com/xjunko/osr2png/releases/latest)

osr2png is a CLI thumbnail generator for osu! maps.

as I am very lazy and only update this thing few times a year, lots of stuff gonna break. if that happens please file an issue.

## Examples
![](https://cdn.discordapp.com/attachments/703552229680087042/1051772453157871616/Vmdiqxj.png)
![](https://cdn.discordapp.com/attachments/703552229680087042/1051775122790416404/umTspt7.png)
![](https://cdn.discordapp.com/attachments/703552229680087042/1051775374725500968/UfHxc0O.png)


## Running

Latest binaries for Linux/Windows can be downloaded from [here](https://github.com/xjunko/osr2png/releases/latest).


Simply unpack the file somewhere and run it with your terminal.


##### Linux / Powershell
```bash
./osr2png <arguments>
```

## Run arguments
```txt
usage: osr2png [-h] [-r REPLAY] [-b BEATMAP] [-m MESSAGE] [-s STYLE] [-width WIDTH] [-height HEIGHT] [-dim BACKGROUND_DIM] [-blur BACKGROUND_BLUR] [-border BACKGROUND_BORDER]

An open-source osu! thumbnail generator for lazy circle clickers.

options:
  -h, --help            show this help message and exit
  -r REPLAY, --replay REPLAY
                        [Optional] The path of the .osr file
  -b BEATMAP, --beatmap BEATMAP
                        [Optional] The path of the .osu file, if using a custom beatmap.
  -m MESSAGE, --message MESSAGE
                        [Optional] The extra text at the bottom
  -s STYLE, --style STYLE
                        [Todo] Style of Image | Unimplemented!
  -width WIDTH, --width WIDTH
                        [Optional] The width of the image.
  -height HEIGHT, --height HEIGHT
                        [Optional] The width of the image.
  -dim BACKGROUND_DIM, --background-dim BACKGROUND_DIM
                        [Optional] The dim of beatmap background.
  -blur BACKGROUND_BLUR, --background-blur BACKGROUND_BLUR
                        [Optional] The blur of beatmap background.
  -border BACKGROUND_BORDER, --background-border BACKGROUND_BORDER
                        [Optional] The border of beatmap background's dim.
```

Examples:

```
./osr2png -r replay.osr 

./osr2png -r replay.osr -b beatmap_file.osu

./osr2png -r replay.osr -dim 0.5 -border 50 -blur 15

./osr2png -r replay.osr -m "FINALLY FCED"
```

## Credits

* [rosu-pp](https://github.com/MaxOhn/rosu-pp): The PP calculator used in this program.
* [kitsu.moe](https://kitsu.moe/): The mirror that is used for getting the beatmap
 data.

import json
from pathlib import Path
from dataclasses import dataclass, field


from objects.replay import Replay
from objects.api import osuAPI


@dataclass
class Settings:
    replay: Replay
    api: osuAPI
    player: dict = field(default_factory=dict)
    beatmap: dict = field(default_factory=dict)
    pp: dict = field(default_factory=dict)

    # Changeable
    token: str = field(default_factory=str)
    resolution: list = field(default_factory=list)
    font: str = field(default_factory=str)
    style: int = field(default_factory=int)
    background_blur: int = field(default_factory=int)
    background_border: int = field(default_factory=int)
    use_cache: bool = field(default_factory=bool)
    filename: str = field(default_factory=str)
    out_folder: str = field(default_factory=str)

    @property
    def scale(self) -> float:
        return self.resolution[1] / 720

    def load_from_file(self) -> None:
        filepath: Path = Path("settings.json")
        default_config: dict = {
            "token": "YOUR_OSU_TOKEN",
            "resolution": [1920, 1080],
            "font": "font.ttf",
            "background_blur": 5,
            "background_border": 32,
            "style": 1,
            "use_cache": True,
            "filename": "{artist} - {title} [{difficulty}] {player} [{mods}].png",
            "out_folder": "scores",
        }
        missing_keys: set = set(default_config.keys())

        if not filepath.exists():
            print("[Settings] No settings.json found, creating one!")
            # Create Default config
            filepath.write_text(json.dumps(default_config, indent=4))
            print("[Settings] Created settings.json!")
            print("[Settings] Please set token value in settings.json!")
        else:
            config = json.loads(filepath.read_text())

            for key, value in config.items():
                if key in default_config:
                    setattr(self, key, value)  # ez
                    missing_keys.remove(key)

            # Check for missing keys
            for missing_key in missing_keys:
                print(f"[Settings] `{missing_key}` is missing, using default value!")
                setattr(self, missing_key, default_config[missing_key])

                # Save em
                config[missing_key] = default_config[missing_key]

            filepath.write_text(json.dumps(config, indent=4))
            print("[Settings] settings.json loaded!")

    @classmethod
    def make_settings(cls: object, replay_path: Path) -> object:
        # Load settings from file first then get the shit
        settings = cls(replay=None, api=None)
        settings.load_from_file()

        print("[Settings] Getting stuff!")
        # Get the shit
        settings.replay = Replay.from_file(filepath=replay_path)
        settings.api = osuAPI(token=settings.token, settings=settings)
        settings.player = settings.api.get_user_from_name(
            name=settings.replay.player_name
        )
        settings.beatmap = settings.api.get_map_from_md5(
            md5=settings.replay.beatmap_md5
        )
        settings.pp = settings.api.get_pp(
            settings.beatmap["beatmap_id"],
            settings.replay.mods,
            settings.replay.max_combo,
            settings.replay.accuracy.hitmiss,
            settings.replay.accuracy.value,
        )

        return settings

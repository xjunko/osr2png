""" 

    deeznuts

"""
import re
from PIL import Image, ImageFilter
from pathlib import Path

from gen.text import TextComponent, TextAlignment
from objects.settings import Settings
from objects.api import ASSETS_FOLDER


class Canvas:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.image = Image.new(
            "RGBA", (int(settings.resolution[0]), int(settings.resolution[1]))
        )

        #
        self.load_assets()

    def load_assets(self) -> None:
        self.text = TextComponent(self.image, self.settings)
        #
        self.background = self.settings.api.get_beatmap_background(
            beatmap_id=self.settings.beatmap["beatmapset_id"]
        )
        self.avatar = self.settings.api.get_avatar_image(
            user_id=self.settings.player["user_id"]
        )
        self.star = Image.open(ASSETS_FOLDER / "star.png")
        self.star = self.resize_image_keep_ratio(self.star, [64 * self.settings.scale])

    def generate(self) -> None:
        print(f"[Canvas] Generating with style [{self.settings.style}]")
        return {
            1: self.generate_generic,
            2: self.generate_generic_2,
        }.get(self.settings.style, self.generate_generic)()

    def add_background_default(self) -> None:
        """

        kinda gay to just copy paste the same code so this exists

        """
        if self.settings.background_blur:
            self.background = self.background.filter(
                ImageFilter.GaussianBlur(radius=self.settings.background_blur)
            )

        # Background
        self.background = self.resize_image_keep_ratio(
            self.background, self.settings.resolution, extra=1.1
        )
        self.image.paste(
            self.background,
            (
                int((self.image.size[0] - self.background.size[0]) / 2),
                int((self.image.size[1] - self.background.size[1]) / 2),
            ),
        )
        #

    def check_for_overlays(self) -> None:
        if not (path := ASSETS_FOLDER / "user").exists():
            path.mkdir()

    def add_user_bg_overlay(self) -> None:
        background_overlay = (ASSETS_FOLDER / "user") / "background.png"

        if background_overlay.exists():
            background = Image.open(background_overlay).convert("RGBA")
            background = self.resize_image_keep_ratio(
                background, self.settings.resolution
            )
            self.image.paste(background, mask=background)

    def add_user_front_overlay(self) -> None:
        front_overlay = (ASSETS_FOLDER / "user") / "overlay.png"

        if front_overlay.exists():
            background = Image.open(front_overlay).convert("RGBA")
            background = self.resize_image_keep_ratio(
                background, self.settings.resolution
            )
            self.image.paste(background, mask=background)

    def add_dim(self, alpha: int = 128) -> None:
        # Dim Thing
        dim = Image.new(
            "RGBA",
            [x - self.settings.background_border for x in self.settings.resolution],
            (0, 0, 0, alpha),
        )
        self.image.paste(
            dim,
            (
                int((self.image.size[0] - dim.size[0]) / 2),
                int((self.image.size[1] - dim.size[1]) / 2),
            ),
            mask=dim,
        )
        #

    def generate_generic(self) -> None:
        # Background
        self.check_for_overlays()
        self.add_background_default()
        self.add_dim(alpha=128)
        self.add_user_bg_overlay()
        #

        # Avatar
        avatar = self.resize_image_keep_ratio(self.avatar, [200 * self.settings.scale])
        border_color = (220, 220, 220)
        border_width = int(205 * self.settings.scale)
        border = Image.new("RGBA", (border_width, border_width), border_color)
        # Create a bigger canvas for avatar
        self.avatar = Image.new("RGBA", (border_width, border_width))
        self.avatar.paste(border)
        self.avatar.paste(
            avatar,
            (
                int((self.avatar.size[0] - avatar.size[0]) / 2),
                int((self.avatar.size[1] - avatar.size[1]) / 2),
            ),
        )
        self.image.paste(
            self.avatar,
            (
                int((self.image.size[0] - self.avatar.size[0]) / 2),
                int((self.image.size[1] - self.avatar.size[1]) / 2),
            ),
        )
        #

        # THE MOTHERFUCKING TEXT OH MA GAWDDD I DONT LIKE THIS
        beatmap = self.settings.beatmap
        pp = self.settings.pp

        # Title and diff
        self.text.draw_text(
            f"{beatmap['artist']} - {beatmap['title']}",
            alignment=TextAlignment.centre,
            offset=(0, -550),
        )
        self.text.draw_text(
            f"[{beatmap['version']}]",
            alignment=TextAlignment.centre,
            offset=(0, -400),
        )

        # ACC and Mods
        self.text.draw_text(
            f"{self.settings.replay.accuracy.value: .2f}%",
            alignment=TextAlignment.right,
            offset=(-120, -100),
        )

        self.text.draw_text(
            pp["mods"]["name"],
            alignment=TextAlignment.right,
            offset=(-120, 60),
        )

        # Star and PP :flushed: :flushed:
        acc_text_position = self.text.draw_text(
            pp["stats"]["star"]["pure"],
            alignment=TextAlignment.left,
            offset=(120, -100),
        )
        self.image.paste(self.star, acc_text_position, mask=self.star)

        self.text.draw_text(
            f"{pp['pp']['current']}pp", alignment=TextAlignment.left, offset=(120, 60)
        )
        ## Done
        self.add_user_front_overlay()

    def generate_generic_2(self):
        # Background
        self.check_for_overlays()
        self.add_background_default()
        self.add_dim(alpha=128)
        self.add_user_bg_overlay()
        #

        # Texts
        beatmap = self.settings.beatmap

        # Beatmap artist and title
        self.text.draw_text(
            f"{beatmap['artist']} - {beatmap['title']}",
            alignment=TextAlignment.centre,
            shadow_color=None,
        )

        # PP
        self.text.draw_text(
            f"{self.settings.pp['pp']['current']}pp",
            alignment=TextAlignment.centre,
            color=(255, 211, 0),
            shadow_color=None,
            offset=(0, 150),
        )

        # Player name
        self.text.draw_text(
            self.settings.replay.player_name,
            alignment=TextAlignment.centre,
            shadow_color=None,
            offset=(0, -150),
        )

        #
        self.add_user_front_overlay()

    def resize_image_keep_ratio(
        self, image: Image.Image, target_resolution: list, extra: int = 1
    ) -> Image.Image:
        width, height = image.size
        ratio = (target_resolution[0] / width) * extra

        return image.resize((int(width * ratio), int(height * ratio)))

    def save(self) -> None:
        path = Path(self.settings.out_folder)

        if not path.exists():
            path.mkdir()

        self.image = self.image.convert("RGB")  # Remove the stupid ALPHA

        # Save
        print(f"[Canvas] Saving canvas to {str(path)}")
        self.image.save(
            path
            / re.sub(
                r'[\\*?:"<>|]',
                "_",
                str(
                    self.settings.filename.format(
                        artist=self.settings.beatmap["artist"],
                        title=self.settings.beatmap["title"],
                        difficulty=self.settings.beatmap["version"],
                        player=self.settings.replay.player_name,
                        mods=self.settings.pp["mods"]["name"],
                    )
                ),
            )
        )

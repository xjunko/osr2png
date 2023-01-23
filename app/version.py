""" version.py - chad scuffed version class"""


class Version:
    major: int
    minor: int
    patch: int
    message: str | None

    def __init__(self) -> None:
        self.major = self.minor = self.patch = 0
        self.message = None

    def __repr__(self) -> str:
        return (
            f"{self.major}.{self.minor}.{self.patch}"
            + ["", f" [{self.message}]"][len(self.message) > 0]  # type: ignore
        )

    def __gt__(self, other: "Version") -> bool:
        return [self.major, self.minor, self.patch] > [
            other.major,
            other.minor,
            other.patch,
        ]

    def __lt__(self, other: "Version") -> bool:
        return [self.major, self.minor, self.patch] < [
            other.major,
            other.minor,
            other.patch,
        ]

    @classmethod
    def from_str(cls, version_str: str) -> "Version":
        version_raw, *message = version_str.split("|")

        major, minor, patch = version_raw.split(".")

        ver: "Version" = cls()
        ver.major = int(major)
        ver.minor = int(minor)
        ver.patch = int(patch)
        ver.message = "".join(message)

        return ver

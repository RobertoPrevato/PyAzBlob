from json import loads
from pathlib import Path
from typing import Dict


class Settings:
    mimes: Dict[str, str]

    def __init__(self, mimes: Dict[str, str]):
        self.mimes = mimes

    @classmethod
    def from_settings_file(cls, file_name: str = "settings.json") -> "Settings":
        file_path = Path(Path.cwd() / file_name)

        with open(str(file_path), mode="rt", encoding="utf8") as file:
            data = loads(file.read())

        return Settings(data.get("mimes", {}))

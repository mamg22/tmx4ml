from collections.abc import Sequence
from dataclasses import dataclass, make_dataclass, asdict
from io import StringIO
from xml.etree import ElementTree as ET
import re


CAMEL_WORD_RE = re.compile(r"(?<!^)([A-Z][a-z]+)")


def camel_to_snake_case(text: str) -> str:
    return CAMEL_WORD_RE.sub(lambda s: "_" + s[0], text).lower()


@dataclass(frozen=True)
class ManiaCodeElement:
    def serialize(self) -> ET.Element:
        tag_name = camel_to_snake_case(self.__class__.__name__)
        elem = ET.Element(tag_name)

        for tag, value in asdict(self).items():
            if value is not None:
                sub_elem = ET.Element(tag)
                sub_elem.text = value
                elem.append(sub_elem)

        return elem


@dataclass(frozen=True)
class ShowMessage(ManiaCodeElement):
    message: str


def named_url_element(cls_name):
    return make_dataclass(
        cls_name, [("name", str), ("url", str)], bases=(ManiaCodeElement,), frozen=True
    )


InstallTrack = named_url_element("InstallTrack")
PlayTrack = named_url_element("PlayTrack")
InstallReplay = named_url_element("InstallReplay")
ViewReplay = named_url_element("ViewReplay")
PlayReplay = named_url_element("PlayReplay")


@dataclass(frozen=True)
class JoinServer(ManiaCodeElement):
    ip: str | None = None
    login: str | None = None

    def __post_init__(self) -> None:
        if self.ip is None and self.login is None:
            raise ValueError("Either `ip` or `login` must be set")
        elif self.ip is not None and self.login is not None:
            raise ValueError("Cannot set both `ip` and `login` in JoinServer")


@dataclass(frozen=True)
class InstallSkin(ManiaCodeElement):
    name: str
    file: str
    url: str


@dataclass(frozen=True)
class GetSkin(ManiaCodeElement):
    name: str
    file: str
    url: str


@dataclass(frozen=True)
class AddBuddy(ManiaCodeElement):
    login: str


@dataclass(frozen=True)
class AddFavourite(ManiaCodeElement):
    ip: str | None = None
    login: str | None = None

    def __post_init__(self) -> None:
        if self.ip is None and self.login is None:
            raise ValueError("Either `ip` or `login` must be set")
        elif self.ip is not None and self.login is not None:
            raise ValueError("Cannot set both `ip` and `login` in AddFavourite")


@dataclass(frozen=True)
class Goto(ManiaCodeElement):
    link: str


@dataclass(frozen=True)
class Track(ManiaCodeElement):
    name: str
    url: str


@dataclass(frozen=True)
class InstallTrackPack(ManiaCodeElement):
    name: str
    tracks: list[Track]

    def serialize(self):
        tag_name = camel_to_snake_case(self.__class__.__name__)
        elem = ET.Element(tag_name)

        name_elem = ET.Element("name")
        name_elem.text = self.name
        elem.append(name_elem)

        elem.extend(track.serialize() for track in self.tracks)

        return elem


def make_maniacode(
    items: Sequence[ManiaCodeElement], noconfirmation: bool = False
) -> ET.ElementTree:
    root = ET.Element("maniacode", noconfirmation=str(int(noconfirmation)))
    root.extend(item.serialize() for item in items)
    tree = ET.ElementTree(root)

    return tree


def render_maniacode(
    items: Sequence[ManiaCodeElement], noconfirmation: bool = False
) -> str:
    maniacode = make_maniacode(items, noconfirmation)
    string = StringIO()

    maniacode.write(string, encoding="unicode", xml_declaration=True)

    return string.getvalue()

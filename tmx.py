from datetime import datetime, timezone
from enum import Enum
from typing import Any


def format_time(millis: int) -> str:
    hours, rest = divmod(millis, 60 * 60 * 1000)
    minutes, rest = divmod(rest, 60 * 1000)
    seconds, millis = divmod(rest, 1000)

    time = f"{minutes:02d}:{seconds:02d}.{millis // 10:02d}"

    if hours > 0:
        time = f"{hours:02d}:{time}"

    return time


class StringableEnum(Enum):
    """Creates Enum types whose string representation is just their name"""

    def __str__(self) -> str:
        return self.name


class Difficulty(StringableEnum):
    Beginner = 0
    Intermediate = 1
    Expert = 2
    Lunatic = 3


class Environment(StringableEnum):
    Snow = 1
    Desert = 2
    Rally = 3
    Island = 4
    Coast = 5
    Bay = 6
    Stadium = 7


class Leaderboard(StringableEnum):
    Standard = 0
    Classic = 1
    Nadeo = 2
    Uncompetitive = 3
    Beta = 4
    Star = 5


class LeaderboardSearchOrder(Enum):
    ReplayCountAsc = 3
    ReplayCountDesc = 4
    WorldRecordCountAsc = 5
    WorldRecordCountDesc = 6
    Top10CountAsc = 7
    Top10CountDesc = 8


class Mood(StringableEnum):
    Sunrise = 0
    Day = 1
    Sunset = 2
    Night = 3


class Route(StringableEnum):
    Single = 0
    Multiple = 1
    Symmetrical = 2


class TrackpackSearchOrder(Enum):
    None_ = 0
    CreationDateAsc = 1
    CreationDateDesc = 2
    UpdateDateAsc = 3
    UpdateDateDesc = 4
    TrackCountAsc = 5
    TrackCountDesc = 6
    ActivityAsc = 7
    ActivityDesc = 8
    TrackpackNameAsc = 9
    TrackpackNameDesc = 10
    CreatorNameAsc = 11
    CreatorNameDesc = 12
    DownloadCountAsc = 13
    DownloadCountDesc = 14


class TrackSearchOrder(Enum):
    None_ = 0
    UploadDateAsc = 1
    UploadDateDesc = 2
    UpdateDateAsc = 3
    UpdateDateDesc = 4
    AwardCountAsc = 5
    AwardCountDesc = 6
    CommentCountAsc = 7
    CommentCountDesc = 8
    ActivityAsc = 9
    ActivityDesc = 10
    TrackNameAsc = 11
    TrackNameDesc = 12
    AuthorNameAsc = 13
    AuthorNameDesc = 14
    DifficultyAsc = 15
    DifficultyDesc = 16
    DownloadCountAsc = 17
    DownloadCountDesc = 18
    TrackValueAsc = 19
    TrackValueDesc = 20
    AwardsThisWeekAsc = 21
    AwardsThisWeekDesc = 22
    AwardsThisMonthAsc = 23
    AwardsThisMonthDesc = 24
    LastAwardDateAsc = 25
    LastAwardDateDesc = 26
    WorldRecordSetAsc = 27
    WorldRecordSetDesc = 28
    # Login required start
    PersonalRecordSetAsc = 29
    PersonalRecordSetDesc = 30
    PersonalAwardSetAsc = 31
    PersonalAwardSetDesc = 32
    PersonalDownloadAsc = 33
    PersonalDownloadDesc = 34
    PersonalCommentSetAsc = 35
    PersonalCommentSetDesc = 36
    # Login required end
    UserRecordPositionAsc = 37
    UserRecordPositionDesc = 38


class TrackTag(StringableEnum):
    Normal = 0
    Stunt = 1
    Maze = 2
    Offroad = 3
    Laps = 4
    Fullspeed = 5
    LOL = 6
    Tech = 7
    SpeedTech = 8
    RPG = 9
    PressForward = 10
    Trial = 11
    Grass = 12


class TrackType(StringableEnum):
    Race = 0
    Puzzle = 1
    Platform = 2
    Stunts = 3
    Shortcut = 4
    Laps = 5


class UnlimiterVersion(Enum):
    V0_4 = 1
    V0_6 = 2
    V0_7 = 3
    V1_1 = 4
    V1_2 = 5
    V1_3 = 6
    V2_0 = 7

    def __str__(self) -> str:
        return self.name.replace("_", ".").removeprefix("V")


class UserSearchOrder(Enum):
    None_ = 0
    NameAsc = 1
    NameDesc = 2
    TracksAsc = 3
    TracksDesc = 4
    TrackpacksAsc = 5
    TrackpacksDesc = 6
    AwardsReceivedAsc = 7
    AwardsReceivedDesc = 8
    AwardsGivenAsc = 9
    AwardsGivenDesc = 10
    CommentsReceivedAsc = 11
    CommentsReceivedDesc = 12
    CommentsGivenAsc = 13
    CommentsGivenDesc = 14
    ForumPostsAsc = 15
    ForumPostsDesc = 16
    ForumThreadsAsc = 17
    ForumThreadsDesc = 18
    RegisteredAsc = 19
    RegisteredDesc = 20
    VideosPostedAsc = 21
    VideosPostedDesc = 22
    VideosCreatedAsc = 23
    VideosCreatedDesc = 24


class Vehicle(Enum):
    SnowCar = 1
    DesertCar = 2
    RallyCar = 3
    IslandCar = 4
    CoastCar = 5
    BayCar = 6
    StadiumCar = 7

    def __str__(self) -> str:
        return self.name.removesuffix("Car")


SIMPLE_JSON_FIELDS = {
    "Difficulty": Difficulty,
    "Routes": Route,
    "Style": TrackTag,
    "Mood": Mood,
    "Environment": Environment,
    "Car": Vehicle,
    "ReplayType": Leaderboard,
    "PrimaryType": TrackType,
    "UnlimiterVersion": UnlimiterVersion,
}


def handle_tmx_json(obj: dict[str, Any]) -> dict[str, Any]:
    for key, value in filter(lambda pair: pair[1] is not None, obj.items()):
        match key:
            case (
                "UploadedAt"
                | "UpdatedAt"
                | "ActivityAt"
                | "CreatedAt"
                | "TrackAt"
                | "ReplayAt"
                | "RegisteredAt"
            ):
                obj[key] = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
            case "Tags":
                obj[key] = [TrackTag(tag) for tag in value]
            case simple if simple in SIMPLE_JSON_FIELDS:
                obj[key] = SIMPLE_JSON_FIELDS[simple](value)

    return obj

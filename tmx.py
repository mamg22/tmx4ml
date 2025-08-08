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


class ReplayType(StringableEnum):
    Standard = 0
    Classic = 1
    Nadeo = 2
    Uncompetitive = 3
    Beta = 4
    Star = 5


class LeaderboardsOrderBy(Enum):
    None_ = 0
    ScoreAsc = 1
    ScoreDesc = 2
    ReplaysAsc = 3
    ReplaysDesc = 4
    WorldRecordsAsc = 5
    WorldRecordsDesc = 6
    Top10sAsc = 7
    Top10sDesc = 8


class Mood(StringableEnum):
    Sunrise = 0
    Day = 1
    Sunset = 2
    Night = 3


class Routes(StringableEnum):
    Single = 0
    Multiple = 1
    Symmetric = 2


class TrackPackOrderBy(Enum):
    None_ = 0
    UploadedAsc = 1
    UploadedDesc = 2
    UpdatedAsc = 3
    UpdatedDesc = 4
    TracksAsc = 5
    TracksDesc = 6
    ActivityAsc = 7
    ActivityDesc = 8
    PackNameAsc = 9
    PackNameDesc = 10
    AuthorNameAsc = 11
    AuthorNameDesc = 12
    DownloadsAsc = 13
    DownloadsDesc = 14
    TrackPackValueAsc = 15
    TrackPackValueDesc = 16


class TrackOrderBy(Enum):
    None_ = 0
    UploadedAsc = 1
    UploadedDesc = 2
    UpdatedAsc = 3
    UpdatedDesc = 4
    AwardsAsc = 5
    AwardsDesc = 6
    CommentsAsc = 7
    CommentsDesc = 8
    ActivityAsc = 9
    ActivityDesc = 10
    TrackNameAsc = 11
    TrackNameDesc = 12
    AuthorNameAsc = 13
    AuthorNameDesc = 14
    DifficultyAsc = 15
    DifficultyDesc = 16
    DownloadsAsc = 17
    DownloadsDesc = 18
    ReplayScoreAsc = 19
    ReplayScoreDesc = 20
    AwardsWeekAsc = 21
    AwardsWeekDesc = 22
    AwardsMonthAsc = 23
    AwardsMonthDesc = 24
    AwardedAsc = 25
    AwardedDesc = 26
    WorldRecordSetAsc = 27
    WorldRecordSetDesc = 28
    UserRecordSetAsc = 29
    UserRecordSetDesc = 30
    UserAwardedAsc = 31
    UserAwardedDesc = 32
    UserDownloadedAsc = 33
    UserDownloadedDesc = 34
    UserCommentedAsc = 35
    UserCommentedDesc = 36
    UserRecordPositionAsc = 37
    UserRecordPositionDesc = 38
    TrackLengthAsc = 39
    TrackLengthDesc = 40
    WorldRecordTimeAsc = 41
    WorldRecordTimeDesc = 42
    UserRecordTimeAsc = 43
    UseeRecordTimeDesc = 44
    TrackpackPositionAsc = 45
    TrackpackPositionDesc = 46


class TrackTag(StringableEnum):
    Normal = 0
    Stunt = 1
    Maze = 2
    Offroad = 3
    Multilap = 4
    FullSpeed = 5
    LOL = 6
    Tech = 7
    SpeedTech = 8
    RPG = 9
    PressForward = 10
    Trial = 11
    Grass = 12
    Story = 13
    Nascar = 14
    Speedfun = 15
    Endurance = 16
    AlteredNadeo = 17
    Transitional = 18


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


class UserOrderBy(Enum):
    None_ = 0
    NameAsc = 1
    NameDesc = 2
    TracksAsc = 3
    TracksDesc = 4
    TrackPacksAsc = 5
    TrackPacksDesc = 6
    TrackAwardsAsc = 7
    TrackAwardsDesc = 8
    TrackAwardsOutAsc = 9
    TrackAwardsOutDesc = 10
    TrackCommentsAsc = 11
    TrackCommentsDesc = 12
    TrackCommentsOutAsc = 13
    TrackCommentsOutDesc = 14
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
    ReplayCountAsc = 25
    ReplayCountDesc = 26
    FavoritesAsc = 27
    FavoritesDesc = 28
    AchievementsAsc = 29
    AchievementsDesc = 30
    AuthorMedalsAsc = 31
    AuthorMedalsDesc = 32
    GoldMedalsAsc = 33
    GoldMedalsDesc = 34
    SilverMedalsAsc = 35
    SilverMedalsDesc = 36
    BronzeMedalsAsc = 37
    BronzeMedalsDesc = 38


class Car(StringableEnum):
    Snow = 1
    Desert = 2
    Rally = 3
    Island = 4
    Coast = 5
    Bay = 6
    Stadium = 7


SIMPLE_JSON_FIELDS = {
    "Difficulty": Difficulty,
    "Routes": Routes,
    "Style": TrackTag,
    "Mood": Mood,
    "Environment": Environment,
    "Car": Car,
    "ReplayType": ReplayType,
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

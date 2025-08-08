from collections.abc import Iterable
from enum import Enum
import shlex

import tmx


def find_member[T: Enum](enum_type: type[T], key: str) -> T:
    for member in enum_type.__members__:
        if key.lower() == member.lower():
            return enum_type[member]

    raise KeyError(key)


def parse_member_list[T: Enum](enum_type: type[T], members: str | Iterable[str]) -> str:
    if isinstance(members, str):
        members = members.split(",")
    values = (find_member(enum_type, mem) for mem in members)
    return ",".join(str(val.value) for val in values)


def try_parse_duration_section(duration_spec: str, symbol: str) -> tuple[int, str]:
    match duration_spec.split(symbol, 1):
        case [duration, rest]:
            return int(duration), rest
        case [spec]:
            return 0, spec
        case _:
            raise ValueError(duration_spec)


DURATION_MULTIPLIERS = {"h": 1000 * 60 * 60, "m": 1000 * 60, "s": 1000}


def parse_duration(spec: str) -> int:
    total = 0

    for symbol, multiplier in DURATION_MULTIPLIERS.items():
        duration, spec = try_parse_duration_section(spec, symbol)

        total += duration * multiplier

    return total


def parse_track_query(query: str) -> dict[str, str]:
    """Parses a track query into a dict of API parameters"""

    params = {}

    for item in shlex.split(query):
        match item.split(":", 1):
            case ["antispam", "newest" | "awarded" as anti_type]:
                params["antispam"] = "1" if anti_type == "newest" else "2"
            case ["length", timerange_spec]:
                min, max = timerange_spec.split("...", 1)

                if min:
                    params["authortimemin"] = str(parse_duration(min))
                if max:
                    # TMX makes the range end value inclusive of the given second
                    params["authortimemax"] = str(parse_duration(max) + 999)
            case ["author" | "awardedby" | "commentedby" as criteria, name]:
                params[criteria] = name
            case ["difficulty", diff_list]:
                params["difficulty"] = parse_member_list(tmx.Difficulty, diff_list)
            case ["environment", env_list]:
                params["environment"] = parse_member_list(tmx.Environment, env_list)
            case ["in", collection_list]:
                for collection in collection_list.split(","):
                    collection_name = collection.removeprefix("!")
                    negate = collection.startswith("!")
                    if collection_name not in (
                        "hasrecord",
                        "unlimiter",
                        "supporter",
                        "envmix",
                        "latestauthor",
                        "latestawardedauthor",
                        "screenshot",
                    ):
                        raise ValueError(collection)

                    params["in" + collection_name] = "0" if negate else "1"
            case ["lbtype", type_name]:
                leaderboard_type = find_member(tmx.ReplayType, type_name)
                params["lbtype"] = str(leaderboard_type.value)
            case ["mood", mood_list]:
                params["mood"] = parse_member_list(tmx.Mood, mood_list)
            case ["order1" | "order2" as order, order_name]:
                order_type = find_member(tmx.TrackOrderBy, order_name)
                params[order] = str(order_type.value)
            case ["packid", pack_id]:
                params["packid"] = pack_id
            case ["routes", route_list]:
                params["routes"] = parse_member_list(tmx.Routes, route_list)
            case ["tags", tags_str]:
                tags = []
                exclude = []

                for tag in tags_str.split(","):
                    if tag.startswith("!"):
                        exclude.append(tag[1:])
                    else:
                        tags.append(tag)

                if tags:
                    params["tag"] = parse_member_list(tmx.TrackTag, tags)
                if exclude:
                    params["etag"] = parse_member_list(tmx.TrackTag, exclude)
            case ["taginclusive", boolean]:
                boolean = boolean.lower()
                if boolean not in ("true", "false"):
                    raise ValueError(boolean)

                params["taginclusive"] = boolean
            case ["type", type_name]:
                track_type = find_member(tmx.TrackType, type_name)
                params["primarytype"] = str(track_type.value)
            case ["uploaded", daterange_spec]:
                begin, end = daterange_spec.split("...", 1)

                if begin:
                    params["uploadedafter"] = begin
                if end:
                    params["uploadedbefore"] = end
            case ["vehicle", car_list]:
                params["vehicle"] = parse_member_list(tmx.Car, car_list)
            case [text]:
                try:
                    params["name"] += f" {text}"
                except KeyError:
                    params["name"] = text

    return params


def parse_trackpack_query(query: str) -> dict[str, str]:
    params = {}

    for item in shlex.split(query):
        match item.split(":", 1):
            case ["creator", name]:
                params["creator"] = name
            case ["order1" | "order2" as order, order_name]:
                order_type = find_member(tmx.TrackPackOrderBy, order_name)
                params[order] = str(order_type.value)
            case ["trackid", trackid]:
                params["trackid"] = trackid
            case [text]:
                try:
                    params["name"] += f" {text}"
                except KeyError:
                    params["name"] = text

    return params


def parse_user_query(query: str) -> dict[str, str]:
    params = {}

    for item in shlex.split(query):
        match item.split(":", 1):
            case ["in", collection_list]:
                for collection in collection_list.split(","):
                    collection_name = collection.removeprefix("!")
                    negate = collection.startswith("!")
                    if collection_name not in ("supporters", "moderators"):
                        raise ValueError(collection)

                    params["in" + collection_name] = "0" if negate else "1"
            case ["order1" | "order2" as order, order_name]:
                order_type = find_member(tmx.UserOrderBy, order_name)
                params[order] = str(order_type.value)
            case ["tracks" | "awards" | "awardsgiven" as criteria, range_spec]:
                min, max = range_spec.split("...", 1)

                if min:
                    params[f"{criteria}min"] = min
                if max:
                    params[f"{criteria}max"] = max
            # Not a typo, for some weird reason TMX uses this keyword for registration date in searches
            case ["uploaded", daterange_spec]:
                begin, end = daterange_spec.split("...", 1)

                if begin:
                    params["registeredafter"] = begin
                if end:
                    params["registeredbefore"] = end
            case [text]:
                try:
                    params["name"] += f" {text}"
                except KeyError:
                    params["name"] = text

    return params


def parse_leaderboard_query(query: str) -> dict[str, str]:
    params = {}

    for item in shlex.split(query):
        match item.split(":", 1):
            case ["lbenv", "all"]:
                params["lbenv"] = "0"
            case ["lbenv", lb_env]:
                env = find_member(tmx.Environment, lb_env)
                params["lbenv"] = str(env.value)
            case ["lbid", lb_id]:
                try:
                    lb_type = find_member(tmx.ReplayType, lb_id)
                    params["lbid"] = str(lb_type.value)
                except KeyError:
                   params["lbid"] = lb_id
            case ["order1" as order, order_name]:
                order_type = find_member(tmx.LeaderboardsOrderBy, order_name)
                params[order] = str(order_type.value)
            case [name]:
                params["username"] = name

    return params

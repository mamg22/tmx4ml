import asyncio
from functools import partial
import json

from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_request import Request
import aiohttp_jinja2

import maniacode as mc
import query_parser
import tmx


def render_manialink(*args, **kwargs):
    response = aiohttp_jinja2.render_template(*args, **kwargs)
    response.content_type = "application/xml"
    return response


json_loader = partial(json.loads, object_hook=tmx.handle_tmx_json)


def handle_parser_error(err: query_parser.ParserError) -> web.Response:
    match err:
        case query_parser.InvalidValueError():
            invalid = err.fragment if err.fragment is not None else err.context.value
            text = f"Invalid value {invalid!r} at option {err.context.option!r}"
        case query_parser.InvalidOptionError():
            text = f"Invalid option {err.context.option!r}"
        case query_parser.MissingRangeSeparatorError():
            text = f'Missing "..." at option {err.context.option!r}'
        case _:
            text = f"Error parsing search query: {'\n'.join(err.args)!r} at {err.context.option!r}"

    msg = mc.render_maniacode([mc.ShowMessage(text)])
    return web.Response(text=msg, content_type="application/xml")


async def track_list(request: Request):
    session = request.app["client_session"]
    params = {
        "count": "10",
        "fields": "TrackId,TrackName,Authors[],Tags[],AuthorTime,Difficulty,PrimaryType,Environment,Car,WRReplay.ReplayId",
    }

    if query := request.query.get("query"):
        try:
            params |= query_parser.parse_track_query(query)
        except query_parser.ParserError as e:
            return handle_parser_error(e)

    if after := request.query.get("after"):
        params["after"] = after
    if before := request.query.get("before"):
        params["before"] = before

    url = (request.app["api_url"] / "tracks").with_query(params)

    async with session.get(url) as res:
        tracks = await res.json(loads=json_loader)

    return render_manialink("tracks.xml", request, {"tracks": tracks})


async def track_image(request: Request):
    trackid = request.match_info["trackid"]
    session = request.app["client_session"]

    async with session.get(
        request.app["base_url"].joinpath("trackshow", trackid, "image", "1")
    ) as res:
        response = web.Response(body=(await res.read()))
        response.content_type = "image/jpeg"
        return response


async def track_details(request: Request):
    trackid = request.match_info["trackid"]
    session = request.app["client_session"]

    async with asyncio.TaskGroup() as tg:
        track_query = {
            "id": trackid,
            "count": 1,
            "fields": "TrackId,TrackName,AuthorTime,GoldTarget,SilverTarget,BronzeTarget,Authors,Difficulty,Routes,Mood,Tags,"
            "Awards,Comments,ReplayType,TrackValue,PrimaryType,Car,Environment,UploadedAt,UpdatedAt,UnlimiterVersion,AuthorComments",
        }
        track_url = (request.app["api_url"] / "tracks").with_query(track_query)
        track_task = tg.create_task(session.get(track_url))

        replay_query = {
            "trackId": trackid,
            "best": 1,
            "fields": "ReplayId,User.Name,User.UserId,ReplayTime,Position",
        }
        replay_url = (request.app["api_url"] / "replays").with_query(replay_query)
        replay_task = tg.create_task(session.get(replay_url))

    track = await track_task.result().json(loads=json_loader)
    replays = await replay_task.result().json(loads=json_loader)

    return render_manialink(
        "track.xml",
        request,
        {"track": track["Results"][0], "replays": replays},
    )


async def play_track(request: Request):
    trackid = request.match_info["trackid"]
    session = request.app["client_session"]

    async with session.get(
        request.app["base_url"].joinpath("trackplay", trackid), allow_redirects=False
    ) as res:
        raise web.HTTPFound(res.headers["location"])


async def random_track(request: Request):
    session = request.app["client_session"]

    random_url = request.app["base_url"] / "trackrandom"

    if packid := request.query.get("packid"):
        random_url = random_url.with_query(packid=packid)
    if query := request.query.get("query"):
        random_url = random_url.with_query(query_parser.parse_track_query(query))

    async with session.get(random_url, allow_redirects=False) as res:
        if res.ok:
            location = res.headers["location"]
            trackid = location.split("/")[-1]
        else:
            text = mc.render_maniacode([mc.ShowMessage("No track found")])
            return web.Response(text=text, content_type="application/xml")

        return render_manialink(
            "redirect.xml",
            request,
            {
                "target": request.url.origin().join(
                    request.app.router["track-details"].url_for(trackid=trackid)
                )
            },
        )


async def view_replay(request: Request):
    replayid = request.match_info["replayid"]
    name = "Replay-" + replayid
    url = str(request.app["base_url"] / "recordgbx" / replayid)

    text = mc.render_maniacode([mc.ViewReplay(name, url)])
    return web.Response(text=text, content_type="application/xml")


async def trackpack_list(request: Request):
    session = request.app["client_session"]
    params = {"fields": "PackId,PackName,Creator.Name,Tracks", "count": 18}

    url = request.app["api_url"] / "trackpacks"

    if query := request.query.get("query"):
        try:
            params |= query_parser.parse_trackpack_query(query)
        except query_parser.ParserError as e:
            return handle_parser_error(e)

    if after := request.query.get("after"):
        params["after"] = after
    if before := request.query.get("before"):
        params["before"] = before

    async with session.get(url.with_query(params)) as res:
        results = await res.json(loads=json_loader)

    return render_manialink("trackpacks.xml", request, {"trackpacks": results})


async def trackpack_details(request: Request):
    packid = request.match_info["packid"]
    session = request.app["client_session"]

    params = {
        "id": packid,
        "fields": "PackId,PackName,Tracks,PackValue,IsLegacy,Downloads,CreatedAt,UpdatedAt,"
        "Creator.UserId,Creator.Name,AllowsTrackSubmissions",
        "count": 1,
    }

    url = request.app["api_url"] / "trackpacks"

    async with session.get(url.with_query(params)) as res:
        pack = await res.json(loads=json_loader)

    return render_manialink(
        "trackpack.xml",
        request,
        {"pack": pack["Results"][0]},
    )


async def random_trackpack(request: Request):
    session = request.app["client_session"]

    random_url = request.app["base_url"] / "trackpackrandom"

    if query := request.query.get("query"):
        random_url = random_url.with_query(query_parser.parse_trackpack_query(query))

    async with session.get(random_url, allow_redirects=False) as res:
        if res.ok:
            location = res.headers["location"]
            packid = location.split("/")[-1]
        else:
            text = mc.render_maniacode([mc.ShowMessage("No trackpack found")])
            return web.Response(text=text, content_type="application/xml")

        return render_manialink(
            "redirect.xml",
            request,
            {
                "target": request.url.origin().join(
                    request.app.router["trackpack-details"].url_for(packid=packid)
                )
            },
        )


async def user_list(request: Request):
    session = request.app["client_session"]
    params = {
        "fields": "UserId,Name,IsSupporter,IsModerator",
        "count": 18,
    }

    url = request.app["api_url"] / "users"

    if query := request.query.get("query"):
        try:
            params |= query_parser.parse_user_query(query)
        except query_parser.ParserError as e:
            return handle_parser_error(e)

    if after := request.query.get("after"):
        params["after"] = after
    if before := request.query.get("before"):
        params["before"] = before

    async with session.get(url.with_query(params)) as res:
        results = await res.json(loads=json_loader)

    return render_manialink("users.xml", request, {"users": results})


async def user_details(request: Request):
    session = request.app["client_session"]
    userid = request.match_info["userid"]

    params = {
        "id": userid,
        "fields": "UserId,Name,IsSupporter,IsModerator,RegisteredAt,Tracks,TrackPacks,UserComments,"
        "TrackCommentsReceived,TrackCommentsGiven,TrackAwardsReceived,TrackAwardsGiven,"
        "AuthorMedals,GoldMedals,SilverMedals,BronzeMedals,Replays,Favorites,Achievements",
        "count": 1,
    }

    url = request.app["api_url"] / "users"

    async with session.get(url.with_query(params)) as res:
        user = await res.json(loads=json_loader)

    return render_manialink("user.xml", request, {"user": user["Results"][0]})


async def random_user(request: Request):
    session = request.app["client_session"]

    async with session.get(
        request.app["base_url"] / "userrandom", allow_redirects=False
    ) as res:
        userid = res.headers["location"].split("/")[-1]

        return render_manialink(
            "redirect.xml",
            request,
            {
                "target": request.url.origin().join(
                    request.app.router["user-details"].url_for(userid=userid)
                )
            },
        )


async def leaderboards(request: Request):
    session = request.app["client_session"]
    params = {
        "fields": "User.Name,User.UserId,ReplayScore,ReplayWRs,Top10s,Replays,Position,Delta",
        "count": 17,
    }

    url = request.app["api_url"] / "leaderboards"

    if query := request.query.get("query"):
        try:
            params |= query_parser.parse_leaderboard_query(query)
        except query_parser.ParserError as e:
            return handle_parser_error(e)

    if after := request.query.get("after"):
        params["after"] = after
    if before := request.query.get("before"):
        params["before"] = before

    async with session.get(url.with_query(params)) as res:
        results = await res.json(loads=json_loader)

    return render_manialink("leaderboard.xml", request, {"leaderboard": results})


def make_simple_handler(template: str) -> Handler:
    async def handler(request: Request):
        return render_manialink(template, request, {})

    return handler

#!/usr/bin/env python3

import asyncio
from datetime import datetime, timezone
from functools import partial
import json
from typing import Any

import aiohttp
from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_request import Request
import aiohttp_jinja2
import jinja2
import yarl

import bbcode_tmx
import query_parser
import tmx


def render_manialink(*args, **kwargs):
    response = aiohttp_jinja2.render_template(*args, **kwargs)
    response.content_type = "application/xml"
    return response


SIMPLE_JSON_FIELDS = {
    "Difficulty": tmx.Difficulty,
    "Routes": tmx.Route,
    "Style": tmx.TrackTag,
    "Mood": tmx.Mood,
    "Environment": tmx.Environment,
    "Car": tmx.Vehicle,
    "ReplayType": tmx.Leaderboard,
    "PrimaryType": tmx.TrackType,
    "UnlimiterVersion": tmx.UnlimiterVersion,
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
                obj[key] = [tmx.TrackTag(tag) for tag in value]
            case simple if simple in SIMPLE_JSON_FIELDS:
                obj[key] = SIMPLE_JSON_FIELDS[simple](value)

    return obj


json_loader = partial(json.loads, object_hook=handle_tmx_json)


async def track_list(request: Request):
    session = request.app["client_session"]
    params = {
        "count": "10",
        "fields": "TrackId,TrackName,Authors[],Tags[],AuthorTime,Difficulty,PrimaryType,Environment,WRReplay.ReplayId",
    }

    if query := request.query.get("query"):
        params |= query_parser.parse_track_query(query)

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
            "fields": "ReplayId,User.Name,ReplayTime,Position",
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
        location = res.headers["location"]
        return render_manialink("redirect.xml", request, {"target": location})


async def random_track(request: Request):
    session = request.app["client_session"]

    async with session.get(
        request.app["base_url"] / "trackrandom", allow_redirects=False
    ) as res:
        location = res.headers["location"]
        trackid = location.split("/")[-1]

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

    return render_manialink("replay.xml", request, {"replayid": replayid})


async def trackpack_list(request: Request):
    session = request.app["client_session"]
    params = {"fields": "PackId,PackName,Creator.Name,Tracks", "count": 18}

    url = request.app["api_url"] / "trackpacks"

    if query := request.query.get("query"):
        params |= query_parser.parse_trackpack_query(query)

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

    async with session.get(
        request.app["base_url"] / "trackpackrandom", allow_redirects=False
    ) as res:
        location = res.headers["location"]
        packid = location.split("/")[-1]

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
        params |= query_parser.parse_user_query(query)

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
        "TrackCommentsReceived,TrackCommentsGiven,TrackAwardsReceived,TrackAwardsGiven",
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
        params |= query_parser.parse_leaderboard_query(query)

    if after := request.query.get("after"):
        params["after"] = after
    if before := request.query.get("before"):
        params["before"] = before

    async with session.get(url.with_query(params)) as res:
        results = await res.json(loads=json_loader)

    return render_manialink("leaderboard.xml", request, {"leaderboard": results})


async def home(request: Request):
    return render_manialink("home.xml", request, {})


async def index(request: Request):
    return render_manialink("index.xml", request, {})


async def client_session_ctx(app: web.Application):
    session = aiohttp.ClientSession()
    app["client_session"] = session
    for subapp in app._subapps:
        subapp["client_session"] = session

    yield

    await session.close()


@web.middleware
async def handle_redirects(request: Request, handler: Handler):
    try:
        response = await handler(request)
        return response
    except (
        web.HTTPMultipleChoices,
        web.HTTPMovedPermanently,
        web.HTTPFound,
        web.HTTPSeeOther,
        web.HTTPUseProxy,
        web.HTTPTemporaryRedirect,
    ) as redir:
        target = request.url.origin().join(yarl.URL(redir.location))

        return render_manialink("redirect.xml", request, {"target": target})


common_routes = [
    web.get("/", home, name="home"),
    web.get("/track/", track_list, name="track-list"),
    web.get("/track/random", random_track, name="track-random"),
    web.get("/track/{trackid}", track_details, name="track-details"),
    web.get("/image/{trackid}.jpg", track_image, name="track-image"),
    web.get("/play/{trackid}", play_track, name="track-play"),
    web.get("/replay/{replayid}", view_replay, name="replay-view"),
    web.get("/trackpack/", trackpack_list, name="trackpack-list"),
    web.get("/trackpack/{packid}", trackpack_details, name="trackpack-details"),
    web.get("/trackpack/random", random_trackpack, name="trackpack-random"),
    web.get("/user/", user_list, name="user-list"),
    web.get("/user/{userid}", user_details, name="user-details"),
    web.get("/user/random", random_user, name="user-random"),
    web.get("/leaderboards/", leaderboards, name="leaderboards"),
]

root_routes = [web.get("/", index, name="index")]


@jinja2.pass_context
def format_user(
    context: jinja2.runtime.Context, user: dict[str, Any], link: bool = False
) -> str:
    name = user["Name"]

    if link:
        origin = context["origin"]
        app = context["app"]
        uid = user["UserId"]

        target = origin.join(app.router["user-details"].url_for(userid=str(uid)))
        return f"$h[{target}]{name}$h"
    else:
        return name


def setup_jinja2(app: web.Application):
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader("templates"),
        context_processors=(aiohttp_jinja2.request_processor,),
    )

    jinja_env = aiohttp_jinja2.get_env(app)
    jinja_env.globals["tmx"] = tmx
    jinja_env.globals["format_bbcode"] = bbcode_tmx.format_bbcode

    jinja_env.filters["format_user"] = format_user


def init_app():
    app = web.Application(middlewares=[handle_redirects])

    app.add_routes(root_routes)

    app.cleanup_ctx.append(client_session_ctx)

    setup_jinja2(app)

    for site in ("tmnf", "tmuf"):
        subapp = web.Application()
        subapp.add_routes(common_routes)
        subapp["site"] = site

        base_url = yarl.URL(f"https://{site}.exchange")
        subapp["base_url"] = base_url
        subapp["api_url"] = base_url / "api"

        setup_jinja2(subapp)

        app.add_subapp("/" + site, subapp)
        app[site] = subapp

    return app


def main():
    app = init_app()
    web.run_app(app)


if __name__ == "__main__":
    main()

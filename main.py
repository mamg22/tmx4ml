#!/usr/bin/env python3

import asyncio
from collections.abc import Mapping
import json
import urllib.parse as uparse

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
import aiohttp_jinja2
import jinja2
import yarl

import tmx

app = web.Application()
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader("templates"),
    context_processors=(aiohttp_jinja2.request_processor,),
)

jinja_env = aiohttp_jinja2.get_env(app)
jinja_env.globals["tmx"] = tmx


BASE_URL = yarl.URL("https://tmnf.exchange")
API_URL = BASE_URL / "api"

TRACK_LIST_FIELDS = "TrackId,TrackName,Authors[],Tags[],AuthorTime,Difficulty"


async def fetch_track_list(params: Mapping[str, str]):
    url = (API_URL / "tracks").with_query(params)

    session = app["client_session"]
    async with session.get(url) as res:
        text = await res.text()

        query_res = json.loads(text)

    return query_res


def render_manialink(*args, **kwargs):
    response = aiohttp_jinja2.render_template(*args, **kwargs)
    response.content_type = "application/xml"
    return response


async def track_list(request: Request):
    query = {
        "count": "10",
        "fields": TRACK_LIST_FIELDS,
        "order1": str(tmx.TrackSearchOrder.UploadDateDesc.value),
    }

    if search := request.query.get("query"):
        query["name"] = search

    if after := request.query.get("after"):
        query["after"] = after
    if before := request.query.get("before"):
        query["before"] = before

    res = await fetch_track_list(query)

    return render_manialink("tracks.xml", request, {"latest": res})


async def track_image(request: Request):
    trackid = request.match_info["trackid"]
    session = app["client_session"]

    async with session.get(
        BASE_URL.joinpath("trackshow", trackid, "image", "1")
    ) as res:
        response = web.Response(body=(await res.read()))
        response.content_type = "image/jpeg"
        return response


async def track_details(request: Request):
    trackid = request.match_info["trackid"]
    session = app["client_session"]

    async with asyncio.TaskGroup() as tg:
        track_query = {
            "id": trackid,
            "count": 1,
            "fields": "TrackId,TrackName,AuthorTime,GoldTarget,SilverTarget,BronzeTarget,Uploader.Name,Difficulty,Routes,Mood,Tags,"
            "Awards,Comments,ReplayType,TrackValue,PrimaryType,Car,Environment,UploadedAt,UpdatedAt,UnlimiterVersion,AuthorComments",
        }
        track_url = (API_URL / "tracks").with_query(track_query)
        track_task = tg.create_task(session.get(track_url))

        replay_query = {
            "trackId": trackid,
            "best": 1,
            "fields": "User.Name,ReplayTime,Position",
        }
        replay_url = (API_URL / "replays").with_query(replay_query)
        replay_task = tg.create_task(session.get(replay_url))

    track = await track_task.result().json()
    replays = await replay_task.result().json()

    return render_manialink(
        "track.xml",
        request,
        {"track": track["Results"][0], "replays": replays},
    )


async def play_track(request: Request):
    trackid = request.match_info["trackid"]
    session = app["client_session"]

    async with session.get(
        BASE_URL.joinpath("trackplay", trackid), allow_redirects=False
    ) as res:
        location = res.headers["location"]
        return render_manialink("redirect.xml", request, {"target": location})


async def random_track(request: Request):
    session = app["client_session"]

    async with session.get(BASE_URL / "trackrandom", allow_redirects=False) as res:
        location = res.headers["location"]
        trackid = location.split("/")[-1]

        return render_manialink(
            "redirect.xml",
            request,
            {
                "target": request.url.origin().join(
                    app.router["track-details"].url_for(trackid=trackid)
                )
            },
        )


async def index(request: Request):
    return render_manialink("index.xml", request, {})


async def client_session_ctx(app: web.Application):
    session = aiohttp.ClientSession()
    app["client_session"] = session

    yield

    await session.close()


app.cleanup_ctx.append(client_session_ctx)

app.add_routes(
    [
        web.get("/", index, name="index"),
        web.get("/tracks/", track_list, name="track-list"),
        web.get("/tracks/random", random_track, name="track-random"),
        web.get("/tracks/{trackid}", track_details, name="track-details"),
        web.get("/image/{trackid}.jpg", track_image, name="track-image"),
        web.get("/play/{trackid}", play_track, name="track-play"),
    ]
)

if __name__ == "__main__":
    web.run_app(app)

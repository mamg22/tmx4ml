#!/usr/bin/env python3

from collections.abc import Mapping
import json
import urllib.parse as uparse

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
import aiohttp_jinja2
import jinja2

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))


API_URL = "https://tmnf.exchange/api"
TRACK_API_ENDPOINT = API_URL + "/tracks"

TRACK_LIST_FIELDS = "TrackId,TrackName,Authors[],Tags[],AuthorTime,Difficulty"


async def fetch_track_list(params: Mapping[str, str]):
    url = TRACK_API_ENDPOINT + "?" + uparse.urlencode(params)

    session = app["client_session"]
    async with session.get(url) as res:
        text = await res.text()

        query_res = json.loads(text)

    return query_res


def render_manialink(*args, **kwargs):
    response = aiohttp_jinja2.render_template(*args, **kwargs)
    response.content_type = "application/xml"
    return response


async def root(request: Request):
    query = {"inlatestauthor": "1", "count": "10", "fields": TRACK_LIST_FIELDS}

    if after := request.query.get("after"):
        query["after"] = after
    if before := request.query.get("before"):
        query["before"] = before

    res = await fetch_track_list(query)

    return render_manialink("index.xml", request, {"latest": res, "request": request})


async def track_image(request: Request):
    trackid = request.match_info["trackid"]
    session = app["client_session"]

    async with session.get(f"https://tmnf.exchange/trackshow/{trackid}/image/1") as res:
        response = web.Response(body=(await res.read()))
        response.content_type = "image/jpeg"
        return response


async def play_track(request: Request):
    trackid = request.match_info["trackid"]
    session = app["client_session"]

    async with session.get(
        f"https://tmnf.exchange/trackplay/{trackid}", allow_redirects=False
    ) as res:
        location = res.headers["location"]
        return render_manialink("redirect.xml", request, {"target": location})


async def client_session_ctx(app: web.Application):
    session = aiohttp.ClientSession()
    app["client_session"] = session

    yield

    await session.close()


app.cleanup_ctx.append(client_session_ctx)

app.add_routes(
    [
        web.get("/", root),
        web.get("/index.xml", root),
        web.get("/image/{trackid}.jpg", track_image),
        web.get("/play/{trackid}", play_track),
    ]
)

if __name__ == "__main__":
    web.run_app(app)

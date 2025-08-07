#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
from typing import Any

import aiohttp
from aiohttp import web
import aiohttp.log
from aiohttp.typedefs import Handler
from aiohttp.web_request import Request
import aiohttp_jinja2
import jinja2
import yarl

import bbcode_tmx
import routes as rt
import tmx


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
        location = yarl.URL(redir.location)

        if location.scheme != "tmtp":
            target = request.url.origin().join(yarl.URL(redir.location))
        else:
            target = redir.location

        return rt.render_manialink("redirect.xml", request, {"target": target})


common_routes = [
    web.get("/", rt.make_simple_handler("home.xml"), name="home"),
    web.get("/track/", rt.track_list, name="track-list"),
    web.get("/track/random", rt.random_track, name="track-random"),
    web.get("/track/{trackid}", rt.track_details, name="track-details"),
    web.get("/image/{trackid}.jpg", rt.track_image, name="track-image"),
    web.get("/play/{trackid}", rt.play_track, name="track-play"),
    web.get("/replay/{replayid}", rt.view_replay, name="replay-view"),
    web.get("/trackpack/", rt.trackpack_list, name="trackpack-list"),
    web.get("/trackpack/{packid}", rt.trackpack_details, name="trackpack-details"),
    web.get("/trackpack/random", rt.random_trackpack, name="trackpack-random"),
    web.get("/user/", rt.user_list, name="user-list"),
    web.get("/user/{userid}", rt.user_details, name="user-details"),
    web.get("/user/random", rt.random_user, name="user-random"),
    web.get("/leaderboards/", rt.leaderboards, name="leaderboards"),
]

root_routes = [
    web.get("/", rt.make_simple_handler("index.xml"), name="index"),
    web.get("/about", rt.make_simple_handler("about.xml"), name="about"),
]


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


@jinja2.pass_context
def format_bbcode(context: jinja2.runtime.Context, text: str) -> str:
    app = context["app"]
    request = context["request"]

    return bbcode_tmx.format_bbcode(text, request.url.origin(), app["site"])


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%F %H:%M:%S%:z")


def setup_jinja2(app: web.Application):
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader("templates"),
        context_processors=(aiohttp_jinja2.request_processor,),
    )

    jinja_env = aiohttp_jinja2.get_env(app)
    jinja_env.globals["tmx"] = tmx

    jinja_env.filters["format_user"] = format_user
    jinja_env.filters["format_bbcode"] = format_bbcode
    jinja_env.filters["format_datetime"] = format_datetime


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
    parser = argparse.ArgumentParser(
        description="ManiaLink frontend server for browsing TrackMania Exchange"
    )
    parser.add_argument("-p", "--port", type=int, help="Port to bind to. Default: 8080")
    parser.add_argument("-b", "--bind", help="Host to bind to. Default: 0.0.0.0")
    parser.add_argument("-s", "--socket", help="Path to a Unix socket to listen on")
    parser.add_argument("-L", "--no-request-logging", dest="request_logging", action="store_false", help="Disable request logging")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    access_log = aiohttp.log.access_logger if args.request_logging else None

    app = init_app()
    web.run_app(app, port=args.port, host=args.bind, path=args.socket, access_log=access_log)


if __name__ == "__main__":
    main()

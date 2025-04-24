# `tmx4ml`: TrackMania Exchange for ManiaLinks

Manialink frontend server for Trackmania Exchange Classic (TM1X). Allows browsing and playing tracks from TMX from the in-game manialink browser in TrackMania Nations/United Forever.

## Features

* Fetch track lists (only TMNF exchange for now) with pagination.
* Search and filter tracks with similar queries as the ones used in TMX.
* UI design very close to the style used in-game, for a native look and feel.
* View track details and top records.
* Browse trackpacks.
* Find and view users and their tracks.
* Display leaderboards.

## Running

Clone or download this project, install dependencies and run the `main.py` script. It will start a server listening on port `8000` for all interfaces `0.0.0.0`.

Using `uv` is recommended to allow easy installation of dependencies:

```console
$ uv sync
$ uv run main.py
```

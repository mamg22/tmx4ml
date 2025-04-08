# `tmx4ml`: TrackMania Exchange for ManiaLinks

Manialink frontend server for Trackmania Exchange Classic (TM1X). Allows browsing and playing tracks from TMX from the in-game manialink browser in TrackMania Nations/United Forever.

## Features

* Fetch track information (only TMNF exchange for now) and list it in multiple pages.
* Click to play tracks or open TMX page in browser.

## Running

Clone or download this project, install dependencies and run the `main.py` script. It will start a server listening on port `8000` for all interfaces `0.0.0.0`.

Using `uv` is recommended to allow easy installation of dependencies:

```console
$ uv sync
$ uv run main.py
```

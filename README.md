# `tmx4ml`: TrackMania Exchange for ManiaLinks

Manialink frontend server for Trackmania Exchange Classic (TM1X). Allows browsing and playing tracks from TMX from the in-game manialink browser in TrackMania Nations/United Forever.

## Features

* Support for both [Nations exchange](https://tmnf.exchange/) and [United exchange](https://tmuf.exchange/).
* UI design very close to the style used in-game, for a native look and feel.
* Search and filter tracks with similar queries as the ones used in TMX.
* View track details, top records and play them directly.
* Browse trackpacks.
* Find and view users and their content.
* Display leaderboards.

## Running

Clone or download this project, install dependencies and run the `main.py` script. It will start a server listening on port `8080` for all interfaces `0.0.0.0`. For a list of dependencies to manually install, check the `pyproject.toml` file.

Using `uv` is recommended to allow easy dependency management and for running the program:

```console
$ uv sync
$ uv run main.py
```

Once the server is running, open up `http://localhost:8080/` in the manialink browser.

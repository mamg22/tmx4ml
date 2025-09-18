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

For configurtion, pass the `-h`/`--help` flag to the program to check out the available options.

Using `uv` is recommended to allow easy dependency management and for running the program:

```console
$ uv sync
$ uv run main.py
```

Once the server is running, open up `http://localhost:8080/` in the manialink browser.

## Docker

You can build and run this project in Docker.

Build the image:

```bash
docker build -t tmx4ml .
```

Run the container (the app listens on 0.0.0.0:8080 inside the container):

```bash
docker run --rm -p 8080:8080 tmx4ml
```

Pass additional arguments to the program by appending them to the run command. For example, to see available options:

```bash
docker run --rm -p 8080:8080 tmx4ml --help
```

Then open http://localhost:8080/ in the manialink browser.

### Docker Compose

Alternatively, use Docker Compose:

```bash
# Build and start
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

To pass arguments to the app, you can run:

```bash
docker compose run --rm app --help
```

# Plex Playlist Interleaver and Cleaner

A command-line utility to interleave TV show episodes into a single playlist and clean watched episodes from existing playlists on a Plex server.

## Installation

This project is managed with uv. To install dependencies:

```bash
uv sync
```

Or using pip:

```bash
pip install -r pyproject.toml
```

## Configuration

Create a `.env` file in the root directory and configure your Plex credentials:

```env
PLEX_URL=http://your-plex-ip:32400
PLEX_TOKEN=your-plex-token
```

## CLI Reference

### Global Commands

* `list-shows`: List all available TV shows in the TV library on the server.
* `create`: Create or overwrite an interleaved playlist.
* `clean`: Remove watched episodes from a specific playlist.

### Arguments and Options

#### Command: list-shows

Lists all shows. No extra arguments.

#### Command: create

Creates or updates an interleaved playlist.

* `playlist` (required positional): The name of the playlist to create or overwrite.
* `--shows` (required option): List of show names to interleave. Usage: `--shows "Show A" "Show B"`.
* `--dry-run`: Preview the generated interleaved playlist in the terminal. No changes are written to Plex.
* `--skip-watched`: Filter out and exclude episodes that are marked as watched.

#### Command: clean

Cleans watched episodes from an existing playlist.

* `playlist` (required positional): The name of the playlist to clean.
* `--dry-run`: Preview the watched episodes that would be removed. No changes are written to Plex.

## Usage Examples

### List Available Shows

```bash
python plex_interleaver.py list-shows
```

### Create Interleaved Playlist

To preview creating an interleaved playlist of specific shows while skipping watched episodes:

```bash
python plex_interleaver.py create "My Interleaved Playlist" --shows "Regular Show" "Adventure Time" --skip-watched --dry-run
```

To create/overwrite the playlist in Plex:

```bash
python plex_interleaver.py create "My Interleaved Playlist" --shows "Regular Show" "Adventure Time" --skip-watched
```

### Clean Watched Episodes

To preview removing watched episodes from an existing playlist:

```bash
python plex_interleaver.py clean "My Interleaved Playlist" --dry-run
```

To permanently remove watched episodes from a playlist in Plex:

```bash
python plex_interleaver.py clean "My Interleaved Playlist"
```

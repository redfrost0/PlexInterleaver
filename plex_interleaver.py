import os
import argparse
from itertools import zip_longest
from dotenv import load_dotenv
from plexapi.server import PlexServer

load_dotenv()

PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')

if not PLEX_URL or not PLEX_TOKEN:
    raise ValueError("Missing PLEX_URL or PLEX_TOKEN in .env file or environment.")

plex = PlexServer(PLEX_URL, PLEX_TOKEN)

def get_tv_library():
    for name in ['TV Shows', 'TV']:
        try:
            return plex.library.section(name)
        except Exception:
            pass
    show_sections = [s for s in plex.library.sections() if s.type == 'show']
    if show_sections:
        return show_sections[0]
    raise Exception("No TV Show libraries found on this Plex server.")

def list_tv_shows():
    tv_library = get_tv_library()
    all_shows = tv_library.all()
    print(f"Available TV Shows (in section '{tv_library.title}'):")
    for show in all_shows:
        print(f"- {show.title}")

def create_master_playlist(playlist_name, shows, dry_run=False, skip_watched=False):
    tv_library = get_tv_library()
    
    missing_shows = []
    for title in shows:
        try:
            tv_library.get(title)
        except Exception:
            missing_shows.append(title)
            
    if missing_shows:
        print(f"Error: The following show(s) were not found in library '{tv_library.title}':")
        for s in missing_shows:
            print(f"  - {s}")
        print("Playlist creation aborted (no changes were made).")
        return

    show_lists = []

    for title in shows:
        try:
            show = tv_library.get(title)
            all_episodes = show.episodes()
            total_count = len(all_episodes)
            if skip_watched:
                all_episodes = [ep for ep in all_episodes if not ep.isWatched]
                print(f"Loaded {len(all_episodes)} unwatched episodes from {title} (skipped {total_count - len(all_episodes)} watched)")
            else:
                print(f"Loaded {len(all_episodes)} episodes from {title}")
            show_lists.append(all_episodes)
        except Exception as e:
            print(f"Error loading {title}: {e}")

    interleaved_items = []
    for episodes in zip_longest(*show_lists):
        for ep in episodes:
            if ep is not None:
                interleaved_items.append(ep)

    if interleaved_items:
        if dry_run:
            print(f"\n[DRY RUN] Would create playlist '{playlist_name}' with {len(interleaved_items)} episodes:")
            for idx, ep in enumerate(interleaved_items, start=1):
                print(f"  {idx:03d}. {ep.grandparentTitle} - {ep.seasonEpisode} - {ep.title}")
        else:
            try:
                existing = plex.playlist(playlist_name)
                existing.delete()
                print(f"Deleted existing playlist '{playlist_name}' to overwrite.")
            except Exception:
                pass
            plex.createPlaylist(title=playlist_name, items=interleaved_items)
            print(f"Created master playlist '{playlist_name}' with {len(interleaved_items)} episodes.")

def remove_watched_from_playlist(playlist_name, dry_run=False):
    try:
        playlist = plex.playlist(playlist_name)
    except Exception:
        print(f"Playlist '{playlist_name}' not found.")
        return

    items = playlist.items()
    watched_items = [item for item in items if item.isWatched]
    
    if not watched_items:
        print(f"No watched episodes found in playlist '{playlist_name}'.")
        return

    print(f"Found {len(watched_items)} watched episodes out of {len(items)} total episodes in playlist '{playlist_name}':")
    for idx, item in enumerate(watched_items, start=1):
        print(f"  {idx:02d}. {item.grandparentTitle} - {item.seasonEpisode} - {item.title}")

    if dry_run:
        print(f"\n[DRY RUN] Would remove {len(watched_items)} watched episodes from '{playlist_name}'.")
    else:
        playlist.removeItems(watched_items)
        print(f"\nSuccessfully removed {len(watched_items)} watched episodes from '{playlist_name}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plex Playlist Interleaver and Cleaner CLI Tool")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")
    
    create_parser = subparsers.add_parser("create", help="Create/update interleaved playlist")
    create_parser.add_argument("playlist", help="Name of the playlist to create/overwrite")
    create_parser.add_argument("--shows", nargs="+", required=True, help="List of show names to interleave")
    create_parser.add_argument("--dry-run", action="store_true", help="Preview the playlist without writing/modifying anything in Plex")
    create_parser.add_argument("--skip-watched", action="store_true", help="Skip episodes that are already marked as watched when creating the playlist")
    
    clean_parser = subparsers.add_parser("clean", help="Remove watched episodes from a specific playlist")
    clean_parser.add_argument("playlist", help="Name of the playlist to clean")
    clean_parser.add_argument("--dry-run", action="store_true", help="Preview the watched episodes that would be removed without modifying Plex")
    
    subparsers.add_parser("list-shows", help="List available TV shows on the server")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_master_playlist(playlist_name=args.playlist, shows=args.shows, dry_run=args.dry_run, skip_watched=args.skip_watched)
    elif args.command == "clean":
        remove_watched_from_playlist(playlist_name=args.playlist, dry_run=args.dry_run)
    elif args.command == "list-shows":
        list_tv_shows()

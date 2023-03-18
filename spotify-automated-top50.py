import spotipy
import pytz
from spotipy.oauth2 import SpotifyOAuth
import datetime
import json

scope = "user-top-read user-read-private user-read-email playlist-modify-public playlist-modify-private"

with open('config.json') as f:
    config = json.load(f)

client_id = config['client_id']
client_secret = config['client_secret']
redirect_uri = config['redirect_uri']
playlist_identifier = config['playlist_identifier']
song_limit = config['song_limit']

def get_blacklist():
    with open('blacklist.json') as f:
        return json.load(f)

def perform_login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".spotifycache"
    )

    # Get cached access token (if available)
    token_info = sp_oauth.get_cached_token()

    # If no cached token is available, prompt the user to log in
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        response = input(f"Go to the following URL to authorize the app: {auth_url}\nEnter the URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)


    # Create a spotipy client object using the cached token information
    global sp
    sp = spotipy.Spotify(auth=token_info['access_token'])

def get_user_top_tracks():
    #Fetches the top tracks for the current user.

    results = sp.current_user_top_tracks(time_range='short_term', limit=song_limit)

    tracks = []
    blocked = 0
    blacklist = get_blacklist()

    # if not blacklist["allow_explicit_content"]:
    #     results = [track for track in results if not track["explicit"]]

    for item in results['items']:
        if not blacklist["allow_explicit_content"] and item['explicit']:
            blocked += 1
            continue

        if item['id'] not in [song['id'] for song in blacklist['blocked_songs']]:
            track_name = item['name']
            artists = [artist['name'] for artist in item['artists']]
            track_id = item['id']
            tracks.append({'name': track_name, 'artists': artists, 'id': track_id})
        else:
            blocked += 1

    print(f"Blocked {blocked} songs.")
    return tracks


def delete_playlist_contents(playlist_id):
    #Deletes all the tracks in a given playlist.

    result = sp.playlist_replace_items(playlist_id, [])


def update_playlist(playlist_id, tracks):
    #Adds the top tracks to the given playlist and updates the description of the playlist.

    track_ids = [track['id'] for track in tracks]
    sp.playlist_add_items(playlist_id, track_ids)
    playlist = sp.playlist(playlist_id)

    utc_now = datetime.datetime.utcnow() # get the current datetime object
    now = utc_now.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone('Europe/Berlin'))

    day = now.strftime("%d") # get the day as a string without leading zeros
    month = now.strftime("%b") # get the month as a string formatted with 3 letters
    year = now.strftime("%Y") # get the year as a string formatted with 2 digits
    time = f'{now.strftime("%H:%M")}'

    blocked = song_limit - len(tracks)
    description = ""
    if blocked > 0:
        description = f'Update: {month} {day} {year} {time} (Europe/Berlin) // Built Using SpotiPy And Ubuntu OS // Blocked {blocked} Songs'
    elif blocked == 1:
        description = f'Update: {month} {day} {year} {time} (Europe/Berlin) // Built Using SpotiPy And Ubuntu OS // Blocked {blocked} Song'
    else:
        description = f'Update: {month} {day} {year} {time} (Europe/Berlin) // Built Using SpotiPy And Ubuntu OS'

    if not get_blacklist()["allow_explicit_content"]:
        description += " // Explicit Content Blocked"

    print(f'Description Update: {description}')
    sp.playlist_change_details(playlist_id, description=description)

def update_target_playlist():
    perform_login()
    print('Login Successful')

    delete_playlist_contents(playlist_identifier)
    print('Playlist Clearing Successful')

    update_playlist(playlist_identifier, get_user_top_tracks())
    print('Playlist Fill And Description Update Successful')

update_target_playlist()

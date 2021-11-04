import spotipy
import configparser
import copy
from itertools import count
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

MAX_LIMIT = 50

# get the default config from configuration file
app_config = configparser.ConfigParser()
app_config.read('app_credentials.conf')
default_config = app_config['default']

scope = 'user-library-read'  # I guess we might also need user-read-private or even user-read-email for visual identification on web

auth_manager = SpotifyOAuth(
    client_id=default_config['client_id'],
    client_secret=default_config['client_secret'],
    redirect_uri='http://localhost:8888/callback/',
    scope=scope,
    open_browser=True)

sp = spotipy.Spotify(auth_manager=auth_manager)


def get_all_current_user_saved_tracks():
    def add_track(track_info):
        artists = track_info['track']['artists']
        artists_names = {artist['name'] for artist in artists}
        track_name = track_info['track']['name']

        if track_name in current_user_tracks:
            if artists_names not in current_user_tracks[track_name]:  # to avoid duplicate lists of artists
                artists_new = current_user_tracks[track_name].copy()
                artists_new.append(artists_names)
                current_user_tracks[track_name] = artists_new
        else:
            artists_new = [artists_names]
            current_user_tracks[track_name] = artists_new

    def add_tracks(tracks_info):
        for item in tracks_info['items']:
            add_track(item)

    current_user_tracks = {}

    saved_tracks_info = sp.current_user_saved_tracks(limit=MAX_LIMIT)
    total_number_of_tracks = saved_tracks_info['total']
    remainder = total_number_of_tracks % MAX_LIMIT
    edge = total_number_of_tracks - remainder
    tracks_added = 0

    while tracks_added < total_number_of_tracks:
        if tracks_added != edge:
            saved_tracks_info = sp.next(saved_tracks_info)
            add_tracks(saved_tracks_info)
            tracks_added += MAX_LIMIT
        else:
            saved_tracks_info = sp.current_user_saved_tracks(limit=remainder, offset=tracks_added)
            add_tracks(saved_tracks_info)
            tracks_added += remainder

    return current_user_tracks


# get an API client
# sp_cred = spotipy.Spotify(
#     auth_manager=SpotifyClientCredentials(
#         client_id=default_config['client_id'],
#         client_secret=default_config['client_secret']))

def spotify_test():
    current_user_tracks = get_all_current_user_saved_tracks()
    print(current_user_tracks)

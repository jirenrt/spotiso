import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyClientCredentials
# Load environment variables
load_dotenv()
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")
spotify_redirect_url = os.getenv("SPOTIFY_REDIRECT_URL")

# Authenticate with Spotify
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
#                                                client_secret=spotify_secret,
#                                                redirect_uri=spotify_redirect_url,
#                                                scope="user-library-read"))

# # Function to get artist ID by name
# def get_artist_id(artist_name):
#     results = sp.search(q=artist_name, type='artist', limit=1)
#     if results['artists']['items']:
#         artist = results['artists']['items'][0]
#         return artist['id']
#     else:
#         return None

# # Example usage
# artist_name = 'Bob Marley'
# artist_id = get_artist_id(artist_name)
# if artist_id:
#     print(f"The artist ID for {artist_name} is {artist_id}")
# else:
#     print(f"Artist {artist_name} not found")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])

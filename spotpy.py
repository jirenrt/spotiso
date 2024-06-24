# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="204bcfe708d64cc7b61b1cdd929e19ac",
#                                                            client_secret="26b7e34d3dfe43bba3ea21192a5aa5b3"))

# results = sp.search(q='weezer', limit=20)
# for idx, track in enumerate(results['tracks']['items']):
#     print(idx, track['name'])


import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="204bcfe708d64cc7b61b1cdd929e19ac",
                                               client_secret="26b7e34d3dfe43bba3ea21192a5aa5b3",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
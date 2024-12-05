
def get_saved_tracks() : 
    name = "My Favorites"
    tracks = sp.current_user_saved_tracks()['items']
  
    return name, tracks

     

def get_album_tracks(sp,album_id) : 
    album_name = sp.album(album_id)["name"]
    album_tracks = sp.album_tracks(album_id)['items']
    return album_name, album_tracks


def get_playlist_info(sp,playlist_id):
    
    playlist = sp.playlist(playlist_id)
    name = playlist['name']
    tracks = playlist['tracks']['items']
    while playlist['tracks']['next']:
        playlist['tracks'] = sp.next(playlist['tracks'])
        tracks.extend(playlist['tracks']['items'])
    return name, tracks

def get_artist_tracks(sp,artist_id) : 
    artist_name = sp.artist(artist_id)["name"]
    artist_tracks = sp.artist_top_tracks(artist_id,"FR")["tracks"]
    return artist_name, artist_tracks


def format_track(track):
    artist = track['artists'][0]['name']
    track_name = track['name']
    return f'{artist} – {track_name}'








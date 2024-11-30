import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import yt_dlp
from youtubesearchpython import VideosSearch
import requests
from mutagen.id3 import ID3, APIC, USLT, TIT2, TPE1, error
from mutagen.mp3 import MP3
import lyricsgenius


load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")
spotify_redirect_url = os.getenv("SPOTIFY_REDIRECT_URL")
last_fm_api_key = os.getenv("LASTFM_API_KEY")
genius_api_token = os.getenv("GENIUS_API_TOKEN")




sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_secret,
                                               redirect_uri=spotify_redirect_url,
                                               scope="playlist-read-private"))


album_id = ""
playlist_id = ""
artist_id = ""

welcome_msg = "Welcome to SpotiSoa(Spotify Save On A...).\nHere are the choice : \nChoose 1 to download Playlist\nChoose 2 to download Album\nChoose 3 to download Artist Top Tracks"

print(welcome_msg)
choosen_collection = input("Your choice : ")

if choosen_collection == "1" :
    playlist_id = input("Playlist ID : ")
    print(playlist_id)
    print (choosen_collection)
elif choosen_collection == "2" :
    album_id = input("Album ID : ")
elif choosen_collection == "3" :
    artist_id = input("Artist ID")


def get_album_tracks(album_id) : 
    album_name = sp.album(album_id)["name"]
    album_tracks = sp.album_tracks(album_id)['items']
    return album_name, album_tracks


def get_playlist_info(playlist_id):
    
    playlist = sp.playlist(playlist_id)
    name = playlist['name']
    tracks = playlist['tracks']['items']
    while playlist['tracks']['next']:
        playlist['tracks'] = sp.next(playlist['tracks'])
        tracks.extend(playlist['tracks']['items'])
    return name, tracks

def get_artist_tracks(artist_id) : 
    artist_name = sp.artist(artist_id)["name"]
    print(artist_name)
    exit()
    artist_tracks = sp.artist_top_tracks(album_id,"FR")
    return artist_name, artist_tracks


def format_track(track):
    artist = track['artists'][0]['name']
    track_name = track['name']
    return f'{artist} – {track_name}'




def process_name_and_tracks(choosen_collection):
    name = ""
    formatted_tracks = []
    if choosen_collection == "1" :
        name, tracks = get_playlist_info(playlist_id)
        formatted_tracks = [format_track(item["track"]) for item in tracks]
    elif choosen_collection == "2" :
        name, tracks = get_album_tracks(album_id)
        formatted_tracks = [format_track(item) for item in tracks]
    elif choosen_collection == "3" :
        name, tracks = get_artist_tracks(artist_id)
        formatted_tracks = [format_track for item in tracks]
    
    return name, formatted_tracks


name, formatted_tracks = process_name_and_tracks(choosen_collection)


print(formatted_tracks)
os.makedirs(name, exist_ok=True)

with open(f'{name}/{name}.txt', 'w', encoding='utf-8') as file:
    for track in formatted_tracks:
        file.write(f"{track},\n")

print(f"Playlist tracks have been written to {name}/{name}.txt")


exit(1)




####################### DOWNLOAD PART ##########################

def load_songs_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        songs = [line.strip().strip(',') for line in file]
    return songs

songs = load_songs_from_file(f'{name}/{name}.txt')
genius = lyricsgenius.Genius(genius_api_token)

def get_youtube_url(query):
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()
    if results['result']:
        return results['result'][0]['link']
    else:
        return None

def download_song(url, title, directory):
    
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_')]).rstrip()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{directory}/{safe_title}.%(ext)s',
        'noplaylist': True,
        'continue': True,  # This enables resuming downloads
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f'{directory}/{safe_title}.mp3'
    except:
        return None

def fetch_cover_art(artist, track):
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={last_fm_api_key}&artist={artist}&track={track}&format=json'
    response = requests.get(url)
    data = response.json()
    if 'track' in data and 'album' in data['track'] and 'image' in data['track']['album']:
        images = data['track']['album']['image']
        if images:
            return images[-1]['#text']
    return None

def fetch_lyrics(artist, track):
    try:
        song = genius.search_song(track, artist)
        if song:
            return song.lyrics
        return None
    except:
        return None

def embed_metadata(mp3_file, cover_art_url, lyrics, title, artist):
    audio = MP3(mp3_file, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass
    if cover_art_url:
        response = requests.get(cover_art_url)
        if response.status_code == 200:
            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime='image/jpeg',
                    type=3,  # 3 is for the cover image
                    desc=u'Cover',
                    data=response.content
                )
            )
    if lyrics:
        audio.tags.add(
            USLT(
                encoding=3,  # 3 is for utf-8
                lang=u'eng',
                desc=u'Lyrics',
                text=lyrics
            )
        )
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.save()

for song in songs:
    print(f"Searching for: {song}")
    url = get_youtube_url(song)
    if url:
        print(f"Found URL: {url}")
        artist, title = [part.strip() for part in song.split("–")]
        mp3_file = download_song(url, title, name)

        cover_art_url = fetch_cover_art(artist, title)
        if cover_art_url:
            print(f"Fetching cover art from: {cover_art_url}")
        else:
            print(f"No cover art found for: {song}")

        lyrics = fetch_lyrics(artist, title)
        if lyrics:
            print(f"Lyrics found for: {song}")
        else:
            print(f"No lyrics found for: {song}")

        embed_metadata(mp3_file, cover_art_url, lyrics, title, artist)
        print(f"Downloaded and processed: {song}")
    else:
        print(f"No URL found for: {song}")

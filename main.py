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


# Load environment variables
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

playlist_id = input("Playlist ID: ")

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def format_track(track):
    artist = track['artists'][0]['name']
    track_name = track['name']
    return f'{artist} – {track_name}'

tracks = get_playlist_tracks(playlist_id)
formatted_tracks = [format_track(item['track']) for item in tracks]

with open(f'{playlist_id}.txt', 'w', encoding='utf-8') as file:
    for track in formatted_tracks:
        file.write(f"{track},\n")

print(f"Playlist tracks have been written to {playlist_id}.txt")

# playlist_id = "playlist_tracks"
####################### DOWNLOAD PART ##########################

def load_songs_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        songs = [line.strip().strip(',') for line in file]
    return songs

songs = load_songs_from_file(f'{playlist_id}.txt')
genius = lyricsgenius.Genius(genius_api_token)

def get_youtube_url(query):
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()
    if results['result']:
        return results['result'][0]['link']
    else:
        return None

def download_song(url, title):
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_')]).rstrip()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{safe_title}.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return f'{safe_title}.mp3'

def fetch_cover_art(artist, track):
    
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={last_fm_api_key}&artist={artist}&track={track}&format=json'
    print(url)
    response = requests.get(url)
    data = response.json()
    if 'track' in data and 'album' in data['track'] and 'image' in data['track']['album']:
        images = data['track']['album']['image']
        if images:
            return images[-1]['#text']
    return None

def fetch_lyrics(artist, track):
    song = genius.search_song(track, artist)
    if song:
        return song.lyrics
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
        mp3_file = download_song(url, title)

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

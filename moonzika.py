import os
import yt_dlp
from youtubesearchpython import VideosSearch
import requests
from mutagen.id3 import ID3, APIC, USLT, TIT2, TPE1, error
from mutagen.mp3 import MP3
import lyricsgenius

# Load songs from the text file
def load_songs_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        songs = [line.strip().strip(',') for line in file]
    return songs

songs = load_songs_from_file('playlist_tracks.txt')

LASTFM_API_KEY = '4eb1e72f89b41685a25cc9d5d5f7ef42'
GENIUS_API_TOKEN = 'rWy8r2sPGy1ze9R2QcHrrm02UoE9I7hUcYHrZliL7Jiexh3XzQbqzQSz3vwwLlga' 

genius = lyricsgenius.Genius(GENIUS_API_TOKEN)

def get_youtube_url(query):
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()
    if results['result']:
        return results['result'][0]['link']
    else:
        return None

def download_song(url, title):
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
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
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={LASTFM_API_KEY}&artist={artist}&track={track}&format=json'
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

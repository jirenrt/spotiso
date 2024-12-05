import os
from dotenv import load_dotenv
import requests
from mutagen.id3 import ID3, APIC, USLT, TIT2, TPE1, error
from mutagen.mp3 import MP3



load_dotenv()
last_fm_api_key = os.getenv("LASTFM_API_KEY")

def fetch_cover_art(artist, track):
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={last_fm_api_key}&artist={artist}&track={track}&format=json'
    response = requests.get(url)
    data = response.json()
    if 'track' in data and 'album' in data['track'] and 'image' in data['track']['album']:
        images = data['track']['album']['image']
        if images:
            return images[-1]['#text']
    return None

def fetch_lyrics(genius,artist, track):
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


from embeded_metadata import *
from youtubesearchpython import VideosSearch
import yt_dlp

def load_songs_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        songs = [line.strip().strip(',') for line in file]
    return songs


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
        "u":'tinatojo2@gmail.com',
        "p":"rabalitera6"

    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f'{directory}/{safe_title}.mp3'
    except:
        return None
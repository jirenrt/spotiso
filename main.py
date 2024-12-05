import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

import lyricsgenius
import pyfiglet
from colorama import Fore, Style
from process_spotify_data import *
from download_song import *


load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")
spotify_redirect_url = os.getenv("SPOTIFY_REDIRECT_URL")
genius_api_token = os.getenv("GENIUS_API_TOKEN")




sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_secret,
                                               redirect_uri=spotify_redirect_url,
                                               scope="playlist-read-private"))


album_id = ""
playlist_id = ""
artist_id = ""



def print_artwork():
    art = pyfiglet.figlet_format("SpotiSO")
    print(f"{Fore.GREEN}{art}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Spotify Save Offline.{Style.RESET_ALL}")

if __name__ == "__main__":
    print_artwork()


welcome_msg = "Welcome to SpotiSO.\nHere are the choice : \nChoose 1 to download Playlist\nChoose 2 to download Album\nChoose 3 to download Artist Top Tracks\nChoose 4 to download Your Saved Tracks"

print(welcome_msg)
choosen_collection = input("Your choice : ")

if choosen_collection == "1" :
    playlist_id = input("Playlist ID : ")
    print(playlist_id)
    print (choosen_collection)
elif choosen_collection == "2" :
    album_id = input("Album ID : ")
elif choosen_collection == "3" :
    artist_id = input("Artist ID : ")
elif choosen_collection == "4" :
     choosen_collection="4"

def process_name_and_tracks(choosen_collection):
    name = ""
    formatted_tracks = []
    if choosen_collection == "1" :
        name, tracks = get_playlist_info(sp,playlist_id)
        formatted_tracks = [format_track(item["track"]) for item in tracks]
    elif choosen_collection == "2" :
        name, tracks = get_album_tracks(sp,album_id)
        formatted_tracks = [format_track(item) for item in tracks]
    elif choosen_collection == "3" :
        name, tracks = get_artist_tracks(sp,artist_id)
        formatted_tracks = [format_track(item["album"]) for item in tracks]
    elif choosen_collection == "4" : 
        name, tracks = get_saved_tracks()
        formatted_tracks = [format_track(item["track"]) for item in tracks]
    return name, formatted_tracks
name, formatted_tracks = process_name_and_tracks(choosen_collection)



os.makedirs(name, exist_ok=True)

with open(f'{name}/{name}.txt', 'w', encoding='utf-8') as file:
    for track in formatted_tracks:
        file.write(f"{track},\n")

print(f"Playlist tracks have been written to {name}/{name}.txt")


songs = load_songs_from_file(f'{name}/{name}.txt')
genius = lyricsgenius.Genius(genius_api_token)

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

        lyrics = fetch_lyrics(genius,artist, title)
        if lyrics:
            print(f"Lyrics found for: {song}")
        else:
            print(f"No lyrics found for: {song}")

        embed_metadata(mp3_file, cover_art_url, lyrics, title, artist)
        print(f"Downloaded and processed: {song}")
    else:
        print(f"No URL found for: {song}")
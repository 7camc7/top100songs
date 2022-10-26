from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Scraping for top 100 songs:
date = input("What date do you want to travel to [yyyy-mm-dd]?")
response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
billboard = response.text
soup = BeautifulSoup(billboard, "html.parser")

song_titles = soup.find_all(name="h3", class_="a-no-trucate")
title_text = [title.getText().strip() for title in song_titles]

# Spotify authentication:
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

# Searching Spotify for song titles:
year = date.split("-")[0]
song_uris = []
for song in title_text:
    result = sp.search(q=f"track:{song} year:{year}",
                       type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} does not exist")


# Creating a new playlist:
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# Add songs into new playlist:
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

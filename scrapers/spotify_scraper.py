from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re
import requests
import spotipy
import spotipy.util as util
from unidecode import unidecode
import urllib.request

username="jdongmingo"
albums_seen = set()
track_names = set()

# Find all listed Drake songs on spotify using their API 

# Auth stuff
try:
    token = util.prompt_for_user_token(username)
except: 
    os.remove(".cache-{}".format(username))
    token = util.prompt_for_user_token(username)

sp = spotipy.Spotify(auth=token) 
search_result = sp.search(q="artist:Drake", type="artist")


# Fetch the artist (Drake) and retrieve his ID.
artist = search_result['artists']['items'][0]
artist_id = artist['id']

# Fetch all Drake albums using his ID.
album_results = sp.artist_albums(artist_id)['items']

# Retrieve all track names from each album.
for album in album_results:
    album_name = album['name']

    # Skip duplicate albums.
    if album_name in albums_seen:
        continue

    print ("Retrieving all song names from album: '{}'...".format(album_name))
    albums_seen.add(album_name)

    album_id = album['id']

    # Extract tracks from the album. 
    track_results = sp.album_tracks(album_id)['items']

    i = 0

    # Add each track to
    for track in track_results:
        track_name = track['name']

        # Metrolyrics filters '&' and '/'
        track_name = track_name.replace('&', '') \
                               .replace('/', '') \
                               .replace('\'', '') \
                               .replace(',', '') \
                               .replace('?', '') \
                               .replace('-', '') \
                               .replace('Album Version (Edited)', '')

        track_name = "-".join(track_name.lower().split())
        track_names.add(track_name)

        i += 1


print ("Total songs found: {}".format(len(track_names)))

# Fetch the lyrics for each track name.
unknown_songs = set()
quote_page = 'http://metrolyrics.com/{}-lyrics-drake.html'
filename = 'drake-songs.csv'
dictionary = {"song_name": list(track_names)}
songs = pd.DataFrame(data=dictionary)

for index, track in enumerate(track_names):
    page = urllib.request.urlopen(quote_page.format(track))
    r = requests.get(quote_page.format(track))

    if len(r.history) > 1:
        # Song doesn't exist on metrolyrics. Keep track of these songs.
        unknown_songs.add(track)

    soup = BeautifulSoup(page, 'html.parser')
    verses = soup.find_all('p', attrs={'class': 'verse'})
    lyrics = ''

    for verse in verses:
        text = verse.text.strip()
        text = re.sub(r"\[.*\]\n", "", unidecode(text))

        if lyrics == '':
            lyrics = lyrics + text.replace('\n', '|-|')
        else:
            lyrics = lyrics + '|-|' + text.replace('\n', '|-|')

    songs.at[index, 'lyrics'] = lyrics

    print("Saving the lyrics for '{}'...".format(track))


print("Writing results to {}...".format(filename))
songs.to_csv(filename, sep=',', encoding='utf-8')

print ("Songs not in metrolyrics DB: ".format(unknown_songs))

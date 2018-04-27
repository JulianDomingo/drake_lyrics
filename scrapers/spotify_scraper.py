from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re
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
    # You'll have to replace all the parameters passed to prompt_for_user_token() 
    # in order to correctly receive a token, except the redirect_uri which can be left alone.
    token = util.prompt_for_user_token(username, 
                                       client_id='001d00cea86f45918349dd8d039fbd5a',
                                       client_secret='fbd0dbe61cd7462e8f995288c3010090',
                                       redirect_uri='http://google.com')
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

# Retrieve all track names from each "regular" album.
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


print ("Total album songs found: {}".format(len(track_names)))


# Retrieve all track names from each "single" album.
singles_results = sp.artist_albums(artist_id, album_type='single')['items']
singles_found = 0
singles_seen = set()

for single in singles_results:
    single_name = single['name']

    if single_name in singles_seen:
        continue

    singles_seen.add(single_name)

    print ("Retrieving all song names from single: '{}'...".format(single_name))

    single_id = single['id']

    # Extract track(s) from the single. 
    track_results = sp.album_tracks(single_id)['items']

    i = 0

    # Add each track to
    for track in track_results:
        track_name = track['name']

        # Removing unused characters in metrolyrics URL 
        track_name = track_name.replace('&', '') \
                               .replace('/', '') \
                               .replace('\'', '') \
                               .replace(',', '') \
                               .replace('?', '') \
                               .replace('-', '') \
                               .replace('’', '') \
                               .replace('Album Version (Edited)', '')

        track_name = "-".join(track_name.lower().split())
        track_names.add(track_name)

        i += 1
        singles_found += 1


print ("Total singles found: {}".format(int(singles_found)))

# Fetch the lyrics for each track name.
quote_page_metro = 'http://metrolyrics.com/{}-lyrics-drake.html'
filename = '../data/drake-songs-spotify.csv'
# The songs listed below are either unavailable on metrolyrics or
# have a differing naming convention on metrolyrics, resulting in
# a failure to scrape the lyrics. We address them manually by either
# providing the correct naming convention or scraping on genius.com.

# Handle problematic songs which still exist in metrolyrics.
track_names.difference_update({"karaoke", "star67", "cameras-good-ones-go-interlude-medley", "buried-alive-interlude", "no-frauds", "look-alive-(feat.-drake)"})
track_names.update({"cameras-good-ones-go-interlude", 
                    "marvins-room-buried-alive-interlude"})
dictionary = {"song_name": list(track_names)}
metro_songs = pd.DataFrame(data=dictionary)

for index, track in enumerate(track_names):
    print("Saving the lyrics for '{}'...".format(track))
    page = urllib.request.urlopen(quote_page_metro.format(track))

    soup = BeautifulSoup(page, 'html.parser')
    verses = soup.find_all('p', attrs={'class': 'verse'})

    lyrics = ''

    for verse in verses:
        text = verse.text.strip()
        text = re.sub(r"\[.*\]\n", "", unidecode(text))

        if lyrics == '':
            lyrics = lyrics + text.replace('\n', ' ')
        else:
            lyrics = lyrics + ' ' + text.replace('\n', ' ')

    metro_songs.at[index, 'lyrics'] = lyrics


# Scrape songs from genius.com which don't exist in metrolyrics.
quote_page_genius = 'http://genius.com/Drake-{}-lyrics'
dictionary = {"song_name": ["star67", "karaoke"]}
genius_songs = pd.DataFrame(data=dictionary)

for index, track in enumerate(dictionary["song_name"]):
    req = urllib.request.Request(url=quote_page_genius.format(track), headers={"User-Agent": "Lyric Scraper"})
    page = urllib.request.urlopen(req)

    soup = BeautifulSoup(page, "html.parser") 
    verses = soup.find('div', class_='lyrics').text.strip()
    verses = verses.splitlines()

    lyrics = ''

    for verse in verses:
        if ("[" in verse) or ("]" in verse):
            continue

        text = verse.strip()
        text = re.sub(r"\[.*\]\n", "", unidecode(text))

        if lyrics == '':
            lyrics = lyrics + text.replace('\n', ' ')
        else:
            lyrics = lyrics + ' ' + text.replace('\n', ' ')
        
    genius_songs.at[index, 'lyrics'] = lyrics


songs = pd.concat([metro_songs, genius_songs], ignore_index=True)
print("Writing results to {}...".format(filename))
songs.to_csv(filename, sep=',', encoding='utf-8')

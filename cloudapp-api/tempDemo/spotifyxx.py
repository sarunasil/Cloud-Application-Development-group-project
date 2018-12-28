import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError


# def main():
# Get username from terminal
username = sys.argv[1]
# username = "11142500893"
scope = "user-read-private user-read-playback-state user-modify-playback-state"

# Erase cache and prompt for user permission
try:
    # token = util.prompt_for_user_token(username, scope)
    # hardcoded environment variables
    token = util.prompt_for_user_token(username, scope,
                                       client_id="964af63ba277465b8c43f83e035995a6",
                                       client_secret="f7ff54efb1d244e4897ffc4fdf9c6439",
                                       redirect_uri="https://google.com/")
except:
    os.remove(f".cache-{username}")
    # token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope,
                                       client_id="964af63ba277465b8c43f83e035995a6",
                                       client_secret="f7ff54efb1d244e4897ffc4fdf9c6439",
                                       redirect_uri="https://google.com/")

# Create spotify object
spotifyObject = spotipy.Spotify(auth=token)

# get current device
devices = spotifyObject.devices()
deviceID = devices["devices"][0]["id"]

# current track info
currTrack = spotifyObject.current_user_playing_track()
# causes error if no currently played song
artist = currTrack["item"]["artists"][0]["name"]
currTrack = currTrack["item"]["name"]

if artist != "":
    print(">>> CURRENTLY PLAYING " + artist + " - " + currTrack)

user = spotifyObject.current_user()

displayName = user['display_name']
followers = user['followers']['total']

while True:
    print()
    print(">>> Welcome to Spotipy " + displayName + " ! <<<")
    print(">>> You have " + str(followers) + " followers. <<<")
    print()
    print("0 - search for Artist")
    print("1 - exit")
    print()
    choice = input("Your choice: ")

    # Search for artist
    if choice == "0":
        print()
        artistName = input("Ok, what is the artist's name?: ")
        print()

        # Get search Results
        searchResults = spotifyObject.search(artistName, 1, 0, "artist")
        artist = searchResults["artists"]["items"][0]
        print(artist["name"])
        print(str(artist["followers"]["total"]) + " followers")
        print(artist["genres"][0])
        print()

        # cool artwork part
        webbrowser.open(artist["images"][0]["url"])
        artistID = artist["id"]

        # data
        count = 0
        trackURIs = []
        trackArt = []

        # album details query
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults["items"]
        for item in albumResults:
            print()
            albumID = item["id"]
            albumArt = item["images"][0]["url"]
            print("Album " + item["name"])
            # track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults["items"]

            for track in trackResults:
                print(str(count) + ": " + track["name"])
                # every song in Spotify has a unique identifier - uri
                trackURIs.append(track["uri"])
                trackArt.append(albumArt)
                count += 1
            print()
        while True:
            songSelection = input("Enter song number to show ART and PLAY (x to stop)")
            if songSelection == "x":
                break
            trackSelectionList = []
            trackSelectionList.append(trackURIs[int(songSelection)])
            # MOST IMPORTANT LINE - context is None since it is not needed
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
            webbrowser.open(trackArt[int(songSelection)])

    # End program
    if choice == "1":
        break

# if __name__ == "__main__": main()
# print(json.dumps(VARIABLE, sort_keys=True, indent=4))

import os
import spotipy
import spotipy.util as util


def main():

    # replace this with your own user ID
    username = "11142500893"
    scope = "user-read-private user-read-playback-state user-modify-playback-state"

    # Erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope,
                                           client_id="964af63ba277465b8c43f83e035995a6",
                                           client_secret="f7ff54efb1d244e4897ffc4fdf9c6439",
                                           redirect_uri="https://google.com/")
    except:
        os.remove(f".cache-{username}")
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

    print()
    print(">>> Welcome to Spotipy " + displayName + " ! <<<")
    print(">>> You have " + str(followers) + " followers. <<<")

    print()
    songName = input("Which song would you like to play?: ")
    print()

    # Get search Results
    searchResults = spotifyObject.search(songName, limit=10, type="track")
    searchResults = searchResults["tracks"]["items"]

    count = 0
    uriList = []

    for item in searchResults:
        print(str(count) + ": " + item["artists"][0]["name"] + " - " + item["name"])
        uriList.append(item["uri"])
        count += 1

    print()
    selection = input("Pick a number?: ")
    playlist = [uriList[int(selection)]]
    spotifyObject.start_playback(deviceID, None, playlist)

if __name__ == "__main__": main()
# print(json.dumps(VARIABLE, sort_keys=True, indent=4))

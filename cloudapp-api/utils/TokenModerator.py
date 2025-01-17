import config

'''
This set of functions deals with:
Spotify and Youtube specific tokens
'''

import requests
import json
import base64


# helper class for authenticating the application and giving it permissions by the user and spotify
class TokenModerator:
    # static variables
    # these CLIENT_ID an SECRET should be environment variables... not HARDCODED

    # TODO when frontend is deployed these two WILL be different - ask bobi what to set them to
    # TODO i set them it should work hopefully
    # if redirect_uri does not match one in frontend AUTH TOKEN WILL FAIL
    # redirect_uri = "http://localhost:3000/callback"
    # redirect_uri = "http://cad-nqme.s3-website.eu-west-2.amazonaws.com/callback"
    scopes = "user-read-private"

    concat = config.TOKEN_KEYS['CLIENT_ID'] + ":" + config.TOKEN_KEYS['CLIENT_SECRET']
    encoded_str = base64.b64encode(concat.encode("UTF-8"))
    decoded_bytes = encoded_str.decode("UTF-8")
    spotify_token_endpoint = "https://accounts.spotify.com/api/token"

    # It lets you search the Spotify library without tampering with user data
    # return: client_credentials_token
    @staticmethod
    def get_client_credentials_token():
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + TokenModerator.decoded_bytes
        }
        payload = {'grant_type': 'client_credentials'}

        spotify_res = requests.post(TokenModerator.spotify_token_endpoint, headers=headers, data=payload)
        spotify_res = json.loads(spotify_res.text)
        return spotify_res["access_token"]

    # get a link to a page where a user can accept terms and conditions
    # string with the terms and conditions url
    @staticmethod
    def get_authorization_link():
        spotify_authorize_url = "https://accounts.spotify.com/authorize"
        link = spotify_authorize_url + "?client_id=" + TokenModerator.CLIENT_ID\
               + "&response_type=code&redirect_uri=" + TokenModerator.redirect_uri + "&scope=" + TokenModerator.scopes
        return link

    # generate a token that lets the application operate with the user data
    # params: code - string that is generated when a user accepts spotify terms and conditions in the url
    # return user authentication token
    @staticmethod
    def get_auth_token(code, redirect_url):
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + TokenModerator.decoded_bytes
        }
        try:
            payload = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': redirect_url}
            spotify_res = requests.post(TokenModerator.spotify_token_endpoint, headers=headers, data=payload)
            print("SPOTIFY RESPONCE: ",spotify_res)
            spotify_res = json.loads(spotify_res.text)
            return True, spotify_res["access_token"]
        except:
            return False, ""

    # get api key for searching youtube content
    # return Youtube_Data_Api_v3 key
    @staticmethod
    def get_youtube_search_key():
        return config.TOKEN_KEYS['YOUTUBE_DATA_API']
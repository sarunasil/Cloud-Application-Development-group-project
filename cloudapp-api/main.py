from flask import Flask, request, jsonify
from routes.Router import Router
from utils.Response import Response
from utils.TokenModerator import TokenModerator

app = Flask(__name__)


'''
A not about documentation:
https://stackoverflow.com/questions/3898572/what-is-the-standard-python-docstring-format
- reST style seems like the most widely used
It may be smart to use it + it's PyCharm default option

Example:
"""
This is a reST style.

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
"""

'''

@app.route('/', methods=['GET'])
def home():
    """
    Home page message\n
    :returns: Welcome string
    """
    
    return Response.responseSuccess('Welcome to NQMe! Please enter your room number')

@app.route('/', methods=['POST'])
def create_room():
    """
    Create a room with a given room ID (if this ID is not used yet)\n
    Look at router.create_room for more detail\n
    :returns: response message, either success or failure which holds a room object
    """

    result, room, message = Router.create_room()
    if result:
        return Response.responseSuccess({'room': room})
    else:
        return Response.responseFailure({'room': room, 'message': message})

@app.route('/<room_number>/delete', methods=['POST'])
def delete_room(room_number):
    '''
    Completely deletes a party room and all associated information with it\n
    :param room_number: room id to be destroyed\n
    :bodyparam masterCookie: cookie to authenticate master\n
    :returns: JSON object holding a single key ("success" or "failure")
    '''
    cookie = "5c2d575c435a8d02bf3b9700:bb8a4c76c529880d0a9b88a3291df6ea5b9c51732d0524e2420df5714b3a3ac0:33e522edafb477dce7300b215f9860f5bb35da4d53dc0c67824cef0cc794dceb"

    status = Router.delete_room(room_number, cookie)
    if status==True:
        return Response.responseSuccess({
            'message': "Room "+room_number+" has been successfully destroyed."
        })
    else:
        return Response.responseFailure({
            'message': "Failed to destroy room "+room_number+". "+str(status)
        })

@app.route('/<room_number>', methods=['POST'])
def join_room(room_number):
    """
    Joins an existing party room\n
    Look at router.join_room for more detail\n
    :param room_number: party room identifier\n
    :returns: ?
    """

    return Router.join_room(room_number)

@app.route('/<room_number>/enqueue-song', methods=['POST'])
def enqueue_song(room_number):
    """
    Adds a song to the queue\n
    Look at router.enqueue_song for more detail\n
    :param room_number: party room identifier\n
    :bodyparam url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB\n
    bodyparam name: name of the song (together with author?)\n
    :returns: Response.responseSuccess if added successfully, Response.responseFailure if unable to add.
    """

    data = request.json
    if 'url' in data and 'name' in data:
        result, queue = Router.enqueue_song(room_number, data['url'], data['name'])

        if result:
            return Response.responseSuccess({
                'queue': queue,
                'msg': 'Song has been enqueued'
            })
        else: 
            return Response.responseFailure({
                'queue': queue,
                'msg': 'Song was already enqueued'
            })

    return Response.responseFailure('Song was not enqueued! Please enter url and name of the song!')

@app.route('/<room_number>/dequeue-song', methods=['POST'])
def dequeue_song(room_number):
    """
    Song is dequeued (removed from the queue) if it is in the queue list\n
    Look at router.dequeue_song for more detail\n
    :param room_number: party room identifier\n
    :bodyparam url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB\n
    bodyparam name: name of the song (together with author?)\n
    :returns: JSON object holding a single key ("success" or "failure"), holding queue, played songs, current song and a failure message (if any)
    """

    result, history, queue, song, message = Router.dequeue_song(room_number)
    if result:
        return Response.responseSuccess({
            'history': history,
            'queue': queue,
            'song': song,
            'message': 'Song has been dequeued successfully'
        })
    else:
        return Response.responseFailure({
            'history': history,
            'queue': queue,
            'song': song,
            'message': message
        })

# TODO - get a dictionary (json object) with pending songs (queue), where key is the URL and value is a nested dictionary (object)
@app.route('/pending-songs/<room_number>', methods=['POST'])
def get_pending_songs(room_number):
    """
        retrieves the queue of songs that have not been played yet, SORTED by upvotes
        :param room_number: party room identifier\n
        :bodyparam queue: list of songs
        :returns: Response.responseSuccess if retrieved successfully, Response.responseFailure if unable to get list
    """

    result, queue = Router.pending_songs(room_number)
    if result:
        return Response.responseSuccess({
            'queue': queue,
            'message': 'sorted queue of not yet played songs'
        })
    else:
        return Response.responseFailure({
            'message': 'failed to retrieve song queue'
        })

# TODO - get a dictionary (json object) with played songs, where key is the URL and value is a nested dictionary (object)
@app.route('/played-songs/<room_number>', methods=['POST'])
def get_played_songs(room_number):
    return room_number

@app.route('/upvote/<room_number>', methods=['POST'])
def upvote_song(room_number):
    """
    :param room_number: room id
    :authorization_headers: {
        "Authorization": "USER_ID FROM COOKIE"
    }
    :body: {
        "url": "SONG URL"
    }
    :return:
    """
    data = request.json
    if 'url' not in data:
        msg = 'URL has not been found!'
        return Response.responseFailure(msg)

    url = data['url']
    user_id = request.headers.get('Authorization')
    print(user_id)
    result, queue, msg = Router.upvote_song(room_number, url, user_id)

    if result:
        return Response.responseSuccess({
            'message': '',
            'queue': queue
        })
    else:
        return Response.responseFailure({
            'message': msg,
            'queue': queue
        })

# get the token that lets the frontend search through the spotify library
# return: a string token
@app.route('/', methods=['POST'])
def get_client_credentials_token():
    return TokenModerator.get_client_credentials_token()

# token generated when a user has alawed our application to use their spotify data
# return: a string token
@app.route('/spotify', methods=['POST'])
def get_auth_token(code):
    return TokenModerator.get_auth_token(code)

# start the application
if __name__ == '__main__':
    app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from routes.Router import Router
from utils.Response import Response
from utils.TokenModerator import TokenModerator
from utils.Middleware import MiddlewareUtils

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


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
@MiddlewareUtils.valid_master
def delete_room(room_number):
    '''
    Completely deletes a party room and all associated information with it\n
    :param room_number: room id to be destroyed\n
    :bodyparam masterCookie: cookie to authenticate master\n
    :returns: JSON object holding a single key ("success" or "failure")
    '''
    status = Router.delete_room(room_number)
    if status==True:
        return Response.responseSuccess({
            'message': "Room "+room_number+" has been successfully destroyed."
        })
    else:
        return Response.responseFailure({
            'message': "Failed to destroy room "+room_number+". "+str(status)
        })

@app.route('/<room_number>/nickname', methods=['GET'])
def generate_nickname(room_number):
    """
    Generates a random nickname using third-party API
    :param room_number:
    :return: json {Status, [msg, nickname]}
    """

    nickname = Router.generate_nickname(room_number)
    if nickname!="":
        return Response.responseSuccess({'nickname':nickname})
    return Response.responseFailure({'msg': 'Failed to generate unique nickname'})
    

@app.route('/<room_number>', methods=['POST'])
def join_room(room_number):
    """
    Joins an existing party room\n
    Look at router.join_room for more detail\n
    :param room_number: party room identifier\n
    :bodyParam nickname: \n
    :bodyParam IP: \n
    :returns: json{Status, [UserCookie]}
    """
    # print("in main.py")
    data = request.json
    print (str(data))
    if data is not None and 'nickname' in data and 'IP' in data:
        return Router.join_room(room_number, data['nickname'], data['IP'])

    return Response.responseFailure({'msg': 'Failed to join the room.'})

@app.route('/<room_number>/get-members', methods=['POST'])
@MiddlewareUtils.valid_master
def get_members(room_number):
    """
    Gets the list of party members\n
    :param room_number: party room identifier\n
    :returns: json{Status, users:{}}
    """

    return Router.get_members(room_number)

@app.route('/<room_number>/kick', methods=['POST'])
@MiddlewareUtils.valid_master
def kick(room_number):
    """
    Kicks a party member out of the room\n
    Look at router.kick for more detail\n
    :param room_number: party room identifier\n
    :bodyParam userId: member id to kick\n
    :returns: 'status' - success/failure
    """

    data = request.json

    # print("LOOK AT THIS", data)
    # print(data)
    if 'userId' in data:
        result = Router.kick(room_number, data['userId'])
        if result:
            return Response.responseSuccess({'msg': 'User kicked successfully'})
        else:
            return Response.responseFailure({'msg': 'Failed to kick user'})

    return Response.responseFailure({'msg': 'No userId field posted'})

@app.route('/<room_number>/block', methods=['POST'])
# @MiddlewareUtils.valid_master
def block(room_number):
    """
    Block a user from entering this party room\n
    Look at router.block for more detail\n
    :param room_number: party room identifier\n
    :bodyParam userId: member id to be blocked\n
    :returns: 'status' - success/failure
    """

    data = request.json
    if 'userId' in data:
        return Router.block(room_number, data['userId'])

    return Response.responseFailure({'msg': 'Failed to join the room.'})

@app.route('/<room_number>/enqueue-song', methods=['POST'])
# @MiddlewareUtils.valid_user
def enqueue_song(room_number):
    """
    Adds a song to the queue\n
    Look at router.enqueue_song for more detail\n
    :param room_number: party room identifier\n
    :bodyparam url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB\n
    bodyparam name: name of the song (together with author?)\n
    :bodyparam duration: duration of the song\n
    :bodyparam userId: user who added the song\n
    :returns: Response.responseSuccess if added successfully, Response.responseFailure if unable to add.
    """

    data = request.json

    param = {'url','name','duration','userId'}
    if  data is not None and param.issubset(set(data.keys())):
        #make sure userId is the same as in the cookie
        cookie = request.headers.get('Authorization')
        if MiddlewareUtils.get_userId(cookie) != data['userId']:
            return Response.responseFailure({
                'queue': '',
                'msg': 'User authentication unsuccessful',
            })

        result, queue = Router.enqueue_song(room_number, data['url'], data['name'], data['duration'], data['userId'])

        if result:
            return Response.responseSuccess({
                'queue': queue,
                'msg': 'Song has been enqueued',
            })
        else: 
            return Response.responseFailure({
                'queue': queue,
                'msg': 'Song was already enqueued',

            })

    return Response.responseFailure('Song was not enqueued! Please enter url and name of the song!')

@app.route('/<room_number>/dequeue-song', methods=['POST'])
@MiddlewareUtils.valid_master
def dequeue_song(room_number):
    """
    Song is dequeued (removed from the queue) if it is in the queue list and places in history\n
    Look at router.dequeue_song for more detail\n
    :param room_number: party room identifier\n
    :returns: json success/failure
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

#TODO implement properly
@app.route('/<room_number>/remove-song', methods=['POST'])
@MiddlewareUtils.valid_master
def remove_song(room_number):
    """
    Song is removed from the queue\n
    Look at router.remove_song for more detail\n
    :param room_number: party room identifier\n
    :param songId: song to be removed id\n
    :returns: json success/failure
    """

    data = request.json
    if 'url' not in data:
        msg = 'URL has not been found!'
        return Response.responseFailure(msg)

    url = data['url']

    result = True
    is_successful, updated_queue, msg = Router.remove_song(room_number, url)
    if is_successful:
        return Response.responseSuccess({
            'queue': updated_queue,
            'message': 'Song has been removed successfully'
        })
    else:
        return Response.responseFailure({
            'queue': updated_queue,
            'message': msg
        })   

# TODO - get a dictionary (json object) with pending songs (queue), where key is the URL and value is a nested dictionary (object)
@app.route('/<room_number>/pending-songs', methods=['GET'])
@MiddlewareUtils.valid_user
def get_pending_songs(room_number):
    """
        retrieves the queue of songs that have not been played yet, SORTED by upvotes\n
        :param room_number: party room identifier\n
        :returns: Response.responseSuccess if retrieved successfully, Response.responseFailure if unable to get list
    """
    # print("in Pending songs")
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
@app.route('/<room_number>/played-songs', methods=['GET'])
@MiddlewareUtils.valid_user
def get_played_songs(room_number):
    history = Router.played_songs(room_number)
    return Response.responseSuccess({
        'played_songs': history,
        'message': 'List with played songs'
    })

@app.route('/<room_number>/upvote', methods=['POST'])
@MiddlewareUtils.valid_user
def upvote_song(room_number):
    """
    :param room_number: room id
    :param url: url of the song to upvote
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
    cookie = request.headers.get('Authorization')
    result, queue, msg = Router.upvote_song(room_number, url, cookie)

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

@app.route('/<room_number>/unvote', methods=['POST'])
@MiddlewareUtils.valid_user
def unvote_song(room_number):
    """
    :param room_number: room id
    :param url: url of the song to unvote
    :authorization_headers: {
        "Authorization": "USER_ID FROM COOKIE"
    }
    :body: {
        "url": "SONG URL"
    }
    :return:
    """
    #make sure user is unvoting his own song. 

    data = request.json
    if 'url' not in data:
        msg = 'URL has not been found!'
        return Response.responseFailure(msg)

    url = data['url']
    cookie = request.headers.get('Authorization')
    result, queue, msg = Router.unvote_song(room_number, url, cookie)

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
@app.route('/credentials', methods=['GET'])
def get_client_credentials_token():
    return TokenModerator.get_client_credentials_token()

# token generated when a user has alawed our application to use their spotify data
# return: a string token
@app.route('/spotify', methods=['POST'])
@cross_origin()
def get_auth_token():
    data = request.json
    # print(data)
    # print(data['code'])
    if 'code' in data:
        result, token = TokenModerator.get_auth_token(data['code'])
        # print("TOKEN!!!!!:   ", token)
        if result:
            return Response.responseSuccess({
                'auth': token,
                'msg': 'Token successfully generated'
            })
        else:
            return Response.responseFailure({
                'msg': 'Problem with generating token'
            })

# start the application
if __name__ == '__main__':
    app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

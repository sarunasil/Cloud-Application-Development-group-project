from flask import Flask, request, jsonify
from routes.Router import Router
from models.RoomKeeper import RoomKeeper
from utils.Response import Response

app = Flask(__name__)

room_keeper = RoomKeeper()
router = Router(room_keeper)

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

# TODO - Home page @this line should be removed right? Saras
@app.route('/', methods=['GET'])
def home():
    """
    Home page message

    :returns: Welcome string
    """
    
    return Response.responseSuccess('Welcome to NQMe! Please enter your room number')

# TODO - user joins a room and is returned a party peasant identifier (which will be saved in a cookie as well)
@app.route('/<room_number>', methods=['GET'])
def join_room(room_number):
    """
    Joins an existing party room

    Look at router.join_room for more detail

    :param room_number: party room identifier

    :returns: ?
    """

    return router.join_room(room_number)

@app.route('/enqueue-song/<room_number>', methods=['POST'])
def enqueue_song(room_number):
    """
    Adds a song to the queue

    Look at router.enqueue_song for more detail

    :param room_number: party room identifier

    :bodyparam url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB

    bodyparam name: name of the song (together with author?)
    
    :returns: Response.responseSuccess if added successfully, Response.responseFailure if unable to add.
    """

    data = request.json
    if 'url' in data and 'name' in data:
        result, queue = router.enqueue_song(room_number, data['url'], data['name'])

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

@app.route('/dequeue-song/<room_number>', methods=['POST'])
def dequeue_song(room_number):
    """
    Song is dequeued (removed from the queue) if it is in the queue list

    Look at router.dequeue_song for more detail

    :param room_number: party room identifier

    :bodyparam url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB

    bodyparam name: name of the song (together with author?)
    
    #@Ivo, can you clarify this return explanation? Saras
    :returns: response message, either success or failure which holds queue and list with played songs, if a failure is returned, a message is also given both queue and history are dictionaries (json objects), where key is the url and value is a nested dictionary (object)
    """

    result, history, queue, song, message = router.dequeue_song(room_number)
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
    return room_number

# TODO - get a dictionary (json object) with played songs, where key is the URL and value is a nested dictionary (object)
@app.route('/played-songs/<room_number>', methods=['POST'])
def get_played_songs(room_number):
    return room_number

#@I don't think front end will know the room number before the call. Would make more sense for backend to generate a random room identifier and return it if the rest. Saras
@app.route('/create/<room_number>', methods=['POST'])
def create_room(room_number):
    """
    Create a room with a given room ID (if this ID is not used yet)

    Look at router.create_room for more detail

    :param room_number: party room identifier
    
    :returns: response message, either success or failure which holds a room object
    """

    #@will be moved to router.create_room
    # return: response message, either success or failure which holds a room object with the following fields:
    # queue - dictionary/json object with pending songs
    # history - dictionary/json object with played songs
    # searchToken - search token (TODO)
    # accessToken - access token (TODO)
    # master - id of creator of room (TODO)
    # users - list with user ids and their votes
    # return json response with room if it's created, otherwise empty object and a failure message

    result, room, message = router.create_room(room_number)
    if result:
        return Response.responseSuccess({'room': room})
    else:
        return Response.responseFailure({'room': room, 'message': message})

# TODO - delete a room given its number and a cookie (with master ID)
@app.route('/delete/<room_number>', methods=['POST'])
def delete_room(room_number):
    return room_number

# TODO - upvote for a given song by a given user
@app.route('/upvote/<room_number>', methods=['POST'])
def upvote_song(room_number):
    return room_number


# TODO - down for a given song by a given user (if such feature shall exist)
@app.route('/downvote/<room_number>', methods=['POST'])
def downvote_song(room_number):
    return room_number


#start the application
if __name__ == '__main__':
    app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

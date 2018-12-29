from flask import Flask, request, jsonify
from routes.Router import Router
from models.RoomKeeper import RoomKeeper
from utils.Response import Response

app = Flask(__name__)

room_keeper = RoomKeeper()
router = Router(room_keeper)

# TODO - Home page
@app.route('/', methods=['GET'])
def home():
    return Response.responseSuccess('Welcome to NQMe! Please enter your room number')

# TODO - user joins a room and is returned a cookie
@app.route('/<room_number>', methods=['GET'])
def join_room(room_number):
    return router.join_room(room_number)

# Song is enqueued if it has not been yet
# params: room_number - room id
# body params:
# url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB
# name: name of the song (together with author?)

# return: response message, either success or failure
@app.route('/enqueue-song/<room_number>', methods=['POST'])
def enqueue_song(room_number):
    data = request.json
    if 'url' in data and 'name' in data:
        result, queue = router.enqueue_song(room_number, data['url'], data['name'])
        return Response.responseSuccess('Song has been enqueued!') if result else Response.responseFailure('Song was already enqueued!')

    return Response.responseFailure('Song was not enqueued! Please enter url and name of the song!')

# Song is dequeued if it is in the queue list
# params: room_number - room id
# body params:
# url: url of the song (Spotify/Youtube), will act as a primary key in MongoDB
# (optional) name: name of the song (together with author?)

# return: response message, either success or failure which holds queue and list with played songs, if a failure is returned, a message is also given
# both queue and history are dictionaries (json objects), where key is the url and value is a nested dictionary (object)
@app.route('/dequeue-song/<room_number>', methods=['POST'])
def dequeue_song(room_number):
    data = request.json
    if 'url' in data:
        url = data['url']
        name = None if 'name' not in data else data['name']
        result, history, queue, message = router.dequeue_song(room_number, url, name)
        if result:
            return Response.responseSuccess({
                'history': history,
                'queue': queue,
                'message': 'Song has been dequeued successfully'
            })
        else:
            return Response.responseFailure({
                'history': history,
                'queue': queue,
                'message': message
            })

    return Response.responseFailure('Song was not dequeued! Please enter url and name of the song!')

# TODO - get a dictionary (json object) with pending songs (queue), where key is the URL and value is a nested dictionary (object)
@app.route('/pending-songs/<room_number>', methods=['POST'])
def get_pending_songs(room_number):
    return room_number

# TODO - get a dictionary (json object) with played songs, where key is the URL and value is a nested dictionary (object)
@app.route('/played-songs/<room_number>', methods=['POST'])
def get_played_songs(room_number):
    return room_number

# Create a room with a given room ID (if this ID is not used yet)
# params: room_number - room id
# body params:
# no body params

# return: response message, either success or failure which holds a room object with the following fields:
# queue - dictionary/json object with pending songs
# history - dictionary/json object with played songs
# searchToken - search token (TODO)
# accessToken - access token (TODO)
# master - id of creator of room (TODO)
# users - list with user ids and their votes
# return json response with room if it's created, otherwise empty object and a failure message
@app.route('/create/<room_number>', methods=['POST'])
def create_room(room_number):
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


if __name__ == '__main__':
    app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

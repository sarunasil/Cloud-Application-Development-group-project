from flask import Flask, request, jsonify
from routes.Router import Router
from models.RoomKeeper import RoomKeeper

app = Flask(__name__)

room_keeper = RoomKeeper()
router = Router(room_keeper)


@app.route('/', methods=['GET'])
def home():
    return 'Welcome to NQMe! Please enter your room number'

@app.route('/<room_number>', methods=['GET'])
def join_room(room_number):
    return router.join_room(room_number)

@app.route('/enqueue-song/<room_number>', methods=['POST'])
def enqueue_song(room_number):
    data = request.json
    if (data['url'] is not None and data['name'] is not None):
        result = router.enqueue_song(room_number, data['url'], data['name'])
    return room_number

@app.route('/dequeue-song/<room_number>', methods=['POST'])
def dequeue_song(room_number):
    return room_number

@app.route('/create/<room_number>', methods=['POST'])
def create_room(room_number):
    return router.create_room(room_number)

@app.route('/delete/<room_number>', methods=['POST'])
def delete_room(room_number):
    return room_number

@app.route('/upvote/<room_number>', methods=['POST'])
def upvote_song(room_number):
    return room_number

@app.route('/downvote/<room_number>', methods=['POST'])
def downvote_song(room_number):
    return room_number


if __name__ == '__main__':
    app.run()
    # app.run(host='127.0.0.1', port=8080, debug=True)

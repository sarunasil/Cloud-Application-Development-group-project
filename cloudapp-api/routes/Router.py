from utils.Response import Response
from utils.DatabaseUtilities import DBUtils

class Router:
    def __init__(self, room_keeper):
        self.room_keeper = room_keeper

    def create_room(self, room_number):
        room_obj = {
            'id': room_number,
            'searchToken': '', # TODO - add script to acquire token
            'accessToken': '', # TODO - add script to acquire token
            'queue': {},
            'history': {}, # played songs
            'users': [],
            'master': '' # TODO - add master's URL
        }

        result, room = DBUtils.create_room(room_obj)
        if result:
            return Response.responseSuccess({'room': room})
        else:
            return Response.responseFailure({'room': {}, 'msg': 'Room was not created, please try another ID'})

    def join_room(self, room_number):
        return Response.responseSuccess(room_number)

    def enqueue_song(self, room_number, url, name):
        room = DBUtils.get_room(room_number)
        if room.count() != 1:
            return

        queue = room[0]['queue']

        # Assume a song does not exist
        exists = False
        if url in queue:
            exists = True
            return

        queue['url'] = {
            'name': name,
            'score': 0 # initial score is always 0
        }

        result, queue = DBUtils.enqueue_song(room[0]['_id'], queue)
        return result


    def dequeue_song(self, room_number):
        return Response.responseSuccess(room_number)

    def upvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def downvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def delete_room(self, room_number, url):
        return Response.responseSuccess(room_number)

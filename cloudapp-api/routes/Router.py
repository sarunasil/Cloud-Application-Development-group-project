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
            return True, room, None
        else:
            msg = 'Room was not created, please try another ID'
            return False, {}, msg

    def join_room(self, room_number):
        return Response.responseSuccess(room_number)

    def enqueue_song(self, room_number, url, name):
        room = DBUtils.get_room(room_number)

        queue = room['queue']

        # Assume a song does not exist
        exists = False
        if url in queue:
            exists = True
            return False, queue

        queue[url] = {
            'name': name,
            'score': 0 # initial score is always 0
        }

        result, queue = DBUtils.enqueue_song(room['_id'], queue)
        return result, queue

    def dequeue_song(self, room_number, url, name=None, master_id=None):
        # TODO - change when master is known
        original_master = ''
        master_id='test'
        if master_id is not None:
            original_master = DBUtils.get_master(room_number)

        # TODO - uncomment once the master_id is on
        # if original_master != master_id:
        #     msg = 'Not a master to dequeue'
        #     return False, None, None, msg

        history, queue = DBUtils.get_all_songs(room_number)
        if url in queue:
            song = queue[url]
            del queue[url]
            history[url] = song
        else:
            msg = 'Song does not exist in queue'
            return False, history, queue, msg

        is_successful, history, queue = DBUtils.update_song_lists(room_number, history, queue)

        if is_successful:
            return True, history, queue, None
        else:
            msg = 'Something went wrong! please try again'
            return False, history, queue, msg

    def pending_songs(self, room_number):
        return

    def played_songs(self, room_number):
        return

    def upvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def downvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def delete_room(self, room_number, url):
        return Response.responseSuccess(room_number)

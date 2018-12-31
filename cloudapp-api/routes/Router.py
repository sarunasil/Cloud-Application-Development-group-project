from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.Security import SecurityUtils
from DataStructures.AbstractDataStructures import DuplicatePriorityQueue

class Router:
    """
    Hides all API actions complexity from main.py
    """
    
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
            'head': None,
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
        priority_queue = DuplicatePriorityQueue()
        queue_list = []
        if type(queue) is dict:
            for x in queue.keys():
                song = queue[x]
                song['url'] = x
                priority_queue.enqueue(queue[x], queue[x]['score'])

            while len(priority_queue) > 0:
                queue_list.append(priority_queue.dequeue())

        return result, queue_list

    def dequeue_song(self, room_number, master_id=None):
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
        head_url = DBUtils.get_head(room_number)
        song = {}
        if head_url is not None:
            if head_url in queue:
                song = queue[head_url]
                del queue[head_url]
                history[head_url] = song
                song['url'] = head_url
        else:
            msg = 'Song does not exist in queue'
            return False, history, queue, None, msg

        next_head = None
        if len(queue.keys()) > 0:
            for x in queue.keys():
                if next_head is None:
                    next_head = x
                    continue
                if queue[x]['score'] > queue[next_head]['score']:
                    next_head = x

        is_successful_lists, history, queue = DBUtils.update_song_lists(room_number, history, queue)
        is_successful_head, updated_head = DBUtils.update_head(room_number, next_head)

        if is_successful_lists:
            return True, history, queue, song, None
        else:
            msg = 'Something went wrong! please try again'
            return False, history, queue, song, msg

    def remove_song(self, room_number, url, name=None, master_id=None):
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
            del queue[url]
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

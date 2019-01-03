from DataStructures.AbstractDataStructures import DuplicatePriorityQueue
from utils.DatabaseUtilities import DBUtils
from utils.Security import SecurityUtils
from utils.ErrorUtils import ErrorMsg

'''
This set of functions deals with:
Enqueue song
Return queue
Remove head
Remove any song
Upvote a song
Unvote a song
'''

class QueueModerator:

    @staticmethod
    def enqueue_song(room_number, url, name):
        url = url.replace('.', '@')
        room = DBUtils.get_room(room_number)
        queue = room['queue']

        # Assume a song does not exist
        exists = False
        if url in queue:
            exists = True
            return False, queue
        song = {
            'name': name,
            'score': 0  # initial score is always 0
        }

        result = DBUtils.enqueue_song(room['_id'], url, song, len(queue.keys()) + 1)
        unsorted_queue = DBUtils.get_pending_songs(room_number)
        queue_list = QueueModerator.sort_pending_songs(unsorted_queue)

        return result, queue_list

    @staticmethod
    def sort_pending_songs(songs):
        priority_queue = DuplicatePriorityQueue()
        queue_list = []
        if type(songs) is dict:
            for x in songs.keys():
                song = songs[x]
                song['url'] = x
                priority_queue.enqueue(songs[x], songs[x]['score'])

            while len(priority_queue) > 0:
                queue_list.append(priority_queue.dequeue())

        return queue_list

    @staticmethod
    def dequeue_song(room_number, master_id=None):

        # TODO - change when master is known
        original_master = ''
        is_allowed = False # assume no access
        if master_id is not None:
            is_allowed = SecurityUtils.checkUser(room_number, master_id, True) # update access

        # TODO - uncomment once the master_id is on
        if not is_allowed:
            return False, None, None, None, ErrorMsg.NO_MASTER.value

        is_successful, dequeued_song, msg = DBUtils.dequeue_song(room_number)
        history, unsorted_queue = DBUtils.get_all_songs(room_number)
        queue = QueueModerator.sort_pending_songs(unsorted_queue)

        print(msg)
        if is_successful:
            return True, history, queue, dequeued_song, None
        else:
            return False, history, queue, dequeued_song, msg.value


    @staticmethod
    def remove_song(room_number, url, name=None, master_id=None):
        url = url.replace('.', '@')
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

    @staticmethod
    def upvote_song(room_number, url, user_id):
        url = url.replace('.', '@')
        pending_songs = DBUtils.get_pending_songs(room_number)

        # Check if a song is in the queue/pending songs
        if url not in pending_songs:
            msg = "Song does not belong to queue"
            return False, msg

        songs = DBUtils.get_votes_per_user(room_number, user_id)
        if url not in songs:
            result = DBUtils.upvote(room_number, url, user_id)
            msg = 'Something went wrong, please vote again!'
            pending_songs = DBUtils.get_pending_songs(room_number)
            sorted_queue = QueueModerator.sort_pending_songs(pending_songs)

            return (True, sorted_queue, None) if result else (False, sorted_queue, msg)
        elif songs[url]:
            sorted_queue = QueueModerator.sort_pending_songs(pending_songs)
            msg = 'User has already voted for this song'
            return False, sorted_queue, msg

        sorted_queue = QueueModerator.sort_pending_songs(pending_songs)
        return False, sorted_queue, None

    @staticmethod
    def pending_songs(room_number):
        return

    @staticmethod
    def played_songs(room_number):
        return
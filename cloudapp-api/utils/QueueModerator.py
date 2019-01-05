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
    def enqueue_song(room_number, url, name, duration, userId):
        url = SecurityUtils.encrypt_url(url)
        room = DBUtils.get_room(room_number)
        queue = room['queue']

        # Assume a song does not exist
        exists = False
        if url in queue:
            exists = True
            queue_list = QueueModerator.sort_pending_songs(queue)
            return False, queue_list

        song = {
            'name': name,
            'score': 0,  # initial score is always 0
            'duration': duration,
            'nickname': DBUtils.get_member(userId, room_number)[userId]['nickname'],
            'userId': userId
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
                song['url'] = SecurityUtils.decrypt_url(x)
                priority_queue.enqueue(songs[x], songs[x]['score'])

            while len(priority_queue) > 0:
                queue_list.append(priority_queue.dequeue())

        return queue_list

    @staticmethod
    def dequeue_song(room_number):
        is_successful, dequeued_song, msg = DBUtils.dequeue_song(room_number)
        history, unsorted_queue = DBUtils.get_all_songs(room_number)
        queue = QueueModerator.sort_pending_songs(unsorted_queue)
        history = QueueModerator.decrypt_urls(history)
        decrypted_song = None

        if dequeued_song is not None:
            for x in dequeued_song.keys():
                decrypted_song = dequeued_song[x]
                decrypted_song['url'] = SecurityUtils.decrypt_url(x)

                break

        if is_successful:
            return True, history, queue, decrypted_song, None
        else:
            return False, history, queue, decrypted_song, msg.value


    @staticmethod
    def remove_song(room_number, url):
        url = SecurityUtils.encrypt_url(url)
        is_successful, unsorted_queue = DBUtils.remove_song(room_number, url)
        sorted_queue = QueueModerator.sort_pending_songs(unsorted_queue)

        if is_successful:
            return True, sorted_queue, None
        else:
            return False, sorted_queue, ErrorMsg.NOT_REMOVED.value

    @staticmethod
    def upvote_song(room_number, url, cookie):
        user_id = SecurityUtils.get_userId(cookie)
        url = SecurityUtils.encrypt_url(url)
        pending_songs = DBUtils.get_pending_songs(room_number)

        # Check if a song is in the queue/pending songs
        if url not in pending_songs:
            return False, ErrorMsg.NO_SONG.value

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
    def unvote_song(room_number, url, cookie):
        user_id = SecurityUtils.get_userId(cookie)
        url = SecurityUtils.encrypt_url(url)
        pending_songs = DBUtils.get_pending_songs(room_number)

        # Check if a song is in the queue/pending songs
        if url not in pending_songs:
            sorted_queue = QueueModerator.sort_pending_songs(pending_songs)
            return False, sorted_queue, ErrorMsg.NO_SONG.value

        songs = DBUtils.get_votes_per_user(room_number, user_id)

        if url not in songs or songs[url] == 0:
            sorted_queue = QueueModerator.sort_pending_songs(pending_songs)
            return False, sorted_queue, ErrorMsg.NO_VOTE.value

        result, err = DBUtils.unvote(room_number, url, user_id)
        pending_songs = DBUtils.get_pending_songs(room_number)
        sorted_queue = QueueModerator.sort_pending_songs(pending_songs)

        if result:
            return True, sorted_queue, None
        else:
            return False, sorted_queue, err.value

    @staticmethod
    def decrypt_urls(songs_object):
        decrypted_url_songs = {}
        for x in songs_object.keys():
            decoded_url = SecurityUtils.decrypt_url(x)
            decrypted_url_songs[decoded_url] = songs_object[x]
        return decrypted_url_songs

    @staticmethod
    def pending_songs(room_number):
        # print("whats going on")
        try:
            unsorted_queue = DBUtils.get_pending_songs(room_number)
            # possible type error - idk if unsorted_queue is of type dict
            sorted_queue = QueueModerator.sort_pending_songs(unsorted_queue)
            return True, sorted_queue
        except:
            return False, []

    @staticmethod
    def played_songs(room_number):
        history = DBUtils.get_played_songs(room_number)
        history = QueueModerator.decrypt_urls(history)
        return history
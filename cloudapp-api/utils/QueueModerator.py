from DataStructures.AbstractDataStructures import DuplicatePriorityQueue
from utils.DatabaseUtilities import DBUtils

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
    def dequeue_song(room_number):
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

        is_successful_lists, history, unsorted_queue = DBUtils.update_song_lists(room_number, history, queue)
        queue = QueueModerator.sort_pending_songs(unsorted_queue)
        is_successful_head = DBUtils.update_head(room_number, next_head)
        return is_successful_lists, is_successful_head, song, queue, history,
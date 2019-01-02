from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils
from utils.QueueModerator import QueueModerator
from DataStructures.AbstractDataStructures import DuplicatePriorityQueue

class Router:
    """
    Hides all API actions complexity from main.py
    """
    
    #AS SOON AS we make Router static,
    #we will be able to separate this function cluster into xModerator.py files
    @staticmethod
    def create_room():
        '''

        :return: if successful - True, room object; else - False, {}, message

        # return: response message, either success or failure which holds a room object with the following fields:
        # queue - dictionary/json object with pending songs
        # history - dictionary/json object with played songs
        # searchToken - search token (TODO)
        # accessToken - access token (TODO)
        # master - id of creator of room (TODO)
        # users - list with user ids and their votes
        # return json response with room if it's created, otherwise empty object and a failure message
        '''


        userId = DBUtils.generateUniqueId(Purpose.USER)
        token = SecurityUtils.generateToken()
        cookie = SecurityUtils.generateCookie(userId, token)

        room_obj = {
            '_id': DBUtils.generateUniqueId(Purpose.ROOM),
            'master': {userId: token},
            'SpotifySearchToken': '', # TODO - add script to acquire token
            'SpotifyAccessToken': '', # TODO - add script to acquire token
            'head': None,
            'queue': {},
            'history': {}, # played songs
            'users': {},
        }

        #@think is it ok to return values as head, users, master, _id as those are not needed

        result = DBUtils.create_room(room_obj)

        # cookie to identify the master
        room_obj.update({'MasterCookie': cookie})
        if result:
            return True, room_obj, None
        else:
            msg = 'Room was not created'
            return False, {}, msg

    @staticmethod
    def join_room(room_number):
        """
        Register a new user

        Generates users id, computes it's secret token, saves it in database

        :param room_number:

        :return: json{Status, [UserCookie]}
        """

        userId = DBUtils.generateUniqueId(Purpose.USER, room_number)

        token = SecurityUtils.saveUser(userId);
        if token:
            #generate user identifiers
            cookie = SecurityUtils.generateCookie(userId, token)
            return Response.responseSuccess(room_number+" -> "+cookie)
        else:
            return Response.responseFailure("F");

    @staticmethod
    def enqueue_song(room_number, url, name):
        room = DBUtils.get_room(room_number)
        queue = room['queue']

        # Assume a song does not exist
        exists = False
        if url in queue:
            exists = True
            return False, queue
        song = {
            'name': name,
            'score': 0 # initial score is always 0
        }

        result = DBUtils.enqueue_song(room['_id'], url, song, len(queue.keys()) + 1)
        unsorted_queue = DBUtils.get_pending_songs(room_number)
        queue_list = QueueModerator.sort_pending_songs(unsorted_queue)

        return result, queue_list

    @staticmethod
    def dequeue_song(room_number, master_id=None):
        # TODO - change when master is known
        original_master = ''
        master_id='test'
        if master_id is not None:
            original_master = DBUtils.get_master(room_number)

        # TODO - uncomment once the master_id is on
        # if original_master != master_id:
        #     msg = 'Not a master to dequeue'
        #     return False, None, None, msg

        is_successful_lists, is_successful_head, song, queue, history = QueueModerator.dequeue_song(room_number)

        if is_successful_lists:
            return True, history, queue, song, None
        else:
            msg = 'Something went wrong! please try again'
            return False, history, queue, song, msg

    @staticmethod
    def remove_song(room_number, url, name=None, master_id=None):
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
    def pending_songs(room_number):
        return

    @staticmethod
    def played_songs(room_number):
        return

    @staticmethod
    def upvote_song(room_number, url, user_id):
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
    def delete_room(room_number, url):
        return Response.responseSuccess(room_number)

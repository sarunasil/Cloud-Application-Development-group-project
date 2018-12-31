from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils

class Router:
    """
    Hides all API actions complexity from main.py
    """
    
    #AS SOON AS we make Router static,
    #we will be able to separate this function cluster into xModerator.py files

    def __init__(self, room_keeper):
        self.room_keeper = room_keeper

    def create_room(self):
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
        token = SecurityUtils.generateToken();
        cookie = SecurityUtils.generateCookie(userId, token)

        room_obj = {
            '_id': DBUtils.generateUniqueId(Purpose.ROOM),
            'master': {userId:token},
            'SpotifySearchToken': '', # TODO - add script to acquire token
            'SpotifyAccessToken': '', # TODO - add script to acquire token
            'head': None,
            'queue': {},
            'history': {}, # played songs
            'users': {},
        }
        #cookie to identify the master
        room_obj.update({'MasterCookie': cookie})

        #@think is it ok to return values as head, users, master, _id as those are not needed

        result = DBUtils.create_room(room_obj)
        if result:
            return True, room_obj, None
        else:
            msg = 'Room was not created'
            return False, {}, msg

    def join_room(self, room_number):
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
        song = DBUtils.get_head(room_number)
        if song is not None:
            for url in song.keys():
                if url in queue:
                    del queue[url]
                    history[url] = song[url]
                break
            else:
                msg = 'Song does not exist in queue'
                return False, history, queue, song, msg

        next_head = {
            'name': '',
            'score': -1,
            'url': ''
        }
        if len(queue.keys()) > 0:
            for x in queue.keys():
                if queue[x]['score'] > next_head['score']:
                    next_head = {
                        'name': queue[x]['name'],
                        'url': x,
                        'score': queue[x]['score']
                    }
            next_head = {
                next_head['url']: {
                    'name': next_head['name'],
                    'score': next_head['score']
                }
            }
        else:
            next_head = None

        is_successful, history, queue = DBUtils.update_song_lists(room_number, history, queue)
        is_successful, updated_head = DBUtils.update_head(room_number, next_head)

        if is_successful:
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

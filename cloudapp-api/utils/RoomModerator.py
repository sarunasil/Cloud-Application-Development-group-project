from utils.TokenModerator import TokenModerator
from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils

'''
This set of functions deals with:
Room creation
Room deletion
Room editing?
'''

class RoomModerator:
    
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
        search = TokenModerator.get_client_credentials_token()

        room_obj = {
            '_id': DBUtils.generateUniqueId(Purpose.ROOM),
            'master': {userId: token},
            'SpotifySearchToken': search,
            'SpotifyAccessToken': '', # TODO - add script to acquire token
            'head': None,
            'queue': {},
            'history': {}, # played songs
            'users': {userId:{
                'token': token,
                'songs': {}
            }},
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
    def delete_room(roomId):
        '''
        DESTROY EXISTING ROOM AND ALL IT"S DATA\n
        Used as cleanup after the party happened and non of existing information is needed anymore\n
        :param roomId - id of the room to be destroyed\n
        :return Success/Failure json
        '''
        # no checks are required due to use of MiddlewareUtils in main.py
        return DBUtils.delete_room(roomId)

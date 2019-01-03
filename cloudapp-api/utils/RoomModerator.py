from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils

'''
This set of functions deals with:
Room creation
Room deletion
Room editing
General messages?
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

        room_obj = {
            '_id': DBUtils.generateUniqueId(Purpose.ROOM),
            'master': {userId: token},
            'SpotifySearchToken': '', # TODO - add script to acquire token
            'SpotifyAccessToken': '', # TODO - add script to acquire token
            'head': None,
            'queue': {},
            'history': {}, # played songs
            'users': {userId:token},
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

        result = "-> "
        #get unique ID
        try:
            userId = DBUtils.generateUniqueId(Purpose.USER, room_number)
            result = userId
        except ValueError as error:
            return Response.responseFailure("Room does not exist");
        token = SecurityUtils.generateToken()

        user = {
            userId: {}
        }
        #save in database
        result = DBUtils.add_member(room_number, user)

        if result:
            #generate user identifiers
            cookie = SecurityUtils.generateCookie(userId, token)
            return Response.responseSuccess( {"UserCookie":cookie, "UserId":userId} )
        else:
            return Response.responseFailure("Failed to add new party member");

    @staticmethod
    def delete_room(roomId, masterCookie=None):
        '''
        DESTROY EXISTING ROOM AND ALL IT"S DATA
        
        Used as cleanup after the party happened and non of existing information is needed anymore

        :param roomId - id of the room to be destroyed
        :parma masterCookie - only party master can do this, thus verification is required
        
        :return Success/Failure json
        '''
        if masterCookie==None:
            return False

        # check is masterCookie legit this room master identifier
        if SecurityUtils.checkUser(roomId, masterCookie, True):
            return DBUtils.delete_room(roomId)

        return False

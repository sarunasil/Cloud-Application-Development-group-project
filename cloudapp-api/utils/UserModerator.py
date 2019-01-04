from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils

'''
This class deals with:
User joining
Get user list
User removing
User blocking
'''

class UserModerator:
    @staticmethod
    def join_room(room_number):
        """
        Register a new user\n
        Generates users id, computes it's secret token, saves it in database\n
        :param room_number:\n
        :return: json{Status, [UserCookie]}
        """

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
    def get_members(room_number):
        """
        Get the list of all party members\n
        
        :param room_number:\n
        :return: json{Status, {party_members_data}}
        """

        #save in database
        result = True

        if result:
            return Response.responseSuccess( {''} )
        else:
            return Response.responseFailure("Failed");

    @staticmethod
    def kick(room_number, userId):
        """
        Kick a user from party\n
        User can still reenter the party using the link
        :param room_number:\n
        :param userId:\n
        :return: json{Status}
        """

        #save in database
        result = True

        if result:
            return Response.responseSuccess( {''} )
        else:
            return Response.responseFailure("Failed");

    @staticmethod
    def block(room_number, userId):
        """
        Block an existing user from entering a party\n
        User is blocked according to IP?
        :param room_number:\n
        :param userId:\n
        :return: json{Status}
        """

        #save in database
        result = True

        if result:
            return Response.responseSuccess( {''} )
        else:
            return Response.responseFailure("Failed");

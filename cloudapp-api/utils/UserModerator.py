from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils
from utils.TokenModerator import TokenModerator
import requests
import config

'''
This class deals with:
Nickname generator
User joining
Get user list
User removing
User blocking
'''

class UserModerator:
    @staticmethod
    def generate_nickname(room_number):
        '''
        Generates a unique nickname for a specific room\n
        :param room_number: \n
        :return: string nickname
        '''

        nickname = ''
        while True:
            response = requests.post("https://api.codetunnel.net/random-nick", json={'sizelimit':'20'}).json()

            if response['success']: #make sure this doesn't enter infinite loop
                nickname = response['nickname']
            else:
                return ""

            if DBUtils.nicknameUnique(room_number, nickname):
                break

        return nickname

    @staticmethod
    def join_room(room_number, nickname, ip):
        """
        Register a new user\n
        Generates users id, computes it's secret token, saves it in database\n
        :param room_number:\n
        :param nickname: \n
        :param ip: \n
        :return: json{Status, [UserCookie]}
        """
        
        #do not allow blocked IP users join
        blocked_members = DBUtils.get_fields(room_number, ['blocked_members'])
        if blocked_members is not None:
            blocked_members = blocked_members[0]['blocked_members']
            ips = []
            for userId in blocked_members:
                ips.append(blocked_members[userId]['IP'])

            if ip in ips:
                return Response.responseFailure("Blocked from entering this party room")

        #get unique ID
        try:
            # print("pre user ID")
            userId = DBUtils.generateUniqueId(Purpose.USER, room_number)
            # print("after UserID has been assigned")
            result = userId
        except ValueError as error:
            return Response.responseFailure("Room does not exist")
        token = SecurityUtils.generateToken()

        user = {
            userId:{
                'nickname': nickname,
                'token': token,
                'IP': ip,
                'songs': {}
            },
        }

        #save in database
        result = DBUtils.add_member(room_number, user)

        if result:
            #generate user identifiers
            cookie = SecurityUtils.generateCookie(userId, token)
            return Response.responseSuccess( {"UserCookie":cookie, "UserId":userId, "SpotifySearchToken": TokenModerator.get_client_credentials_token(),
            "YoutubeSearchToken": config.TOKEN_KEYS['YOUTUBE_DATA_API']} )
        else:
            return Response.responseFailure("Failed to add new party member");

    @staticmethod
    def get_members(room_number):
        """
        Get the list of all party members\n
        :param room_number:\n
        :return: json{Status, users:{party_members_data}}
        """

        fields = [
            'users'
        ]

        users = DBUtils.get_fields(room_number, fields)
        result = False
        for u in users:
            result = u['users']
        
        if result is not False:
            return Response.responseSuccess( result )
        else:
            return Response.responseFailure("Failed to retrieve users list.")

    @staticmethod
    def kick(room_number, userId):
        """
        Kick a user from party\n
        User can still reenter the party using the link
        :param room_number:\n
        :param userId:\n
        :return: json{Status}
        """

        result = DBUtils.delete_member(userId, room_number)
        return result

    @staticmethod
    def block(room_number, userId):
        """
        Block an existing user from entering a party\n
        User is blocked according to IP
        :param room_number:\n
        :param userId:\n
        :return: json{Status}
        """

        #get user
        member = DBUtils.get_member(userId, room_number)
        
        if member is None:
            return Response.responseFailure("User is not a member of this party room.");    
        else:
            member = member[userId]
            #block user IP to block
            result = DBUtils.block_member(userId, member['IP'], member['nickname'], room_number)

            if result:
                #kick user out
                result = DBUtils.delete_member(userId, room_number)

            if result:
                return Response.responseSuccess( "Kicked user successfully. Blocked user "+member['nickname']+"." )

        return Response.responseFailure("Failed to block user.");

    @staticmethod
    def unblock(room_number, userId):
        """
        Unblock a user\n
        Look at router.unblock for more detail\n
        :param room_number:\n
        :param userId:\n
        :return: json{Status}
        """
        
        #unblock user
        result = DBUtils.unblock_member(userId, room_number)

        if result:
            return Response.responseSuccess( "Unblocked user IP successfully." )

        return Response.responseFailure("Failed to block user.");

    @staticmethod
    def get_blocked_members(room_number):
        """
        Get the list of blocked party members\n
        :param room_number:\n
        :return: json{Status, 'blocked_members':{}}
        """
        
        fields = [
            'blocked_members'
        ]

        users = DBUtils.get_fields(room_number, fields)
        result = False
        for u in users:
            result = u['blocked_members']
            break

        if result is not False:
            return Response.responseSuccess( result )
        else:
            return Response.responseFailure("Failed to retrieve block members list.")
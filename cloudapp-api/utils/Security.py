import hashlib
import secrets

PEPPER = "XqM7PSC7iPSJVGYBESgiduinDBNmFOKqRbLSvYUYl38nyWX2Npy1cY275KIe5pbIcoj2U0NuBQwMzaIxsC1rkF8NVVfzU2b6EO6n40uFltehxFAzPUmsrqvCFf28Viae"

#define pepper as constant value here
class SecurityUtils:
    """
    Contains method for user authentication and authorization

    """

    @staticmethod
    def generateToken(length=32):
        '''
        Generates a unique string
        '''
        return secrets.token_hex(length);

    @staticmethod
    def generateCookie(userId, token):
        """
        Generate a cookie to uniquely identify a user

        computes the user cookie using 'id+':'+token+':'+hash(pepper+id+':'+token)

        :param userId: user id used to refer to the user

        :returns: user cookie 
        """

        global PEPPER
        hash = hashlib.sha256()
        hash.update((PEPPER+":"+str(userId)+":"+token).encode('utf-8'))

        return str(userId)+":"+token+":"+hash.hexdigest()

    @staticmethod
    def saveUser(userId):
        """
        Registers the user in the database as a unique party member
        Saves as key-value pair: userId - token

        :param userId: 

        :returns: token
        """

        token = generateToken()

        #save userId-token in nosql

        return token

    @staticmethod
    def checkUser(roomId, cookie):
        """
        Checks if a given userToken represents an legitimate party room member

        :param roomId: room of which the user supposedly belongs to
        :param cookie: value saved on the user device in a cookie

        :returns: if verified - success, else - failure
        """

        return ""
import hashlib
import secrets
from utils.DatabaseUtilities import DBUtils
import base64

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
        Generate a cookie to uniquely identify a user\n
        computes the user cookie using 'id+':'+token+':'+hash(pepper+id+':'+token)\n
        :param userId: user id used to refer to the user\n
        :returns: user cookie 
        """

        global PEPPER
        hash = hashlib.sha256()
        hash.update((PEPPER+":"+str(userId)+":"+token).encode('utf-8'))

        return str(userId)+":"+token+":"+hash.hexdigest()

    @staticmethod
    def checkUser(roomId, cookie, master=False):
        """
        Checks if a given userToken represents an legitimate party room member\n
        It could also check if the userToken belongs to master if "master" flag is present

        :param roomId: room of which the user supposedly belongs to\n
        :param cookie: value saved on the user device in a cookie\n
        :optionalParam master: True - check against master instead of regular user\n
        :returns: if verified - success, else - failure
        """

        #parse the cookie
        userId = token = mac = ''
        parts = cookie.split(':')
        if len(parts) == 3:
            userId = parts[0]
            token = parts[1]
            mac = parts[2]
        else:
            return False

        #check cookie integrity
        if SecurityUtils.generateCookie(userId, token) == cookie:

            #check is cookie not fake
            if master:
                user = DBUtils.get_master(roomId)
            else:
                user = DBUtils.get_member(userId, roomId);
            
            if user is not None:
                
                #check do tokens match
                if token == user[userId]:
                    return True

        return False

    @staticmethod
    def encrypt_url(url):
        byte_url = url.encode('UTF-8')
        encoded = base64.b64encode(byte_url)
        decoded = encoded.decode('UTF-8')
        return decoded

    @staticmethod
    def decrypt_url(encrypted_url):
        try:
            byte_url_encoded = encrypted_url.encode('UTF-8')
            byte_url_decoded = base64.b64decode(byte_url_encoded)
            decoded = byte_url_decoded.decode('UTF-8')
            return decoded
        except:
            return None
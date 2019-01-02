import config
import pymongo
import bson
from enum import Enum

class Purpose(Enum):
    ROOM = 1
    USER = 2

# Helper class for managing with Database interactions
# IMPORTANT: Every query to the database shall occur from here as an exit point of the app (exit in terms that MongoDB database is in Mongo Atlas Cloud)
class DBUtils:
    @staticmethod
    def generateUniqueId(purpose, room_id=None, client=None):
        '''
        Generates a unique identifier using ObjectId - same as MongoDb auto-assigned _id

        :param purpose: one of Purpose Enum value

        :return unique ObjectId string

        :Exception ValueError: if room with roomId does not exist. 
        '''

        id = "";
        while True:
            #generate unique id
            id = bson.ObjectId();

            existing_id = ""
            #check if id is already used
            if purpose == Purpose.ROOM:
                existing_id = DBUtils.get_room(id, client)
            elif purpose == Purpose.USER and room_id is not None:
                existing_id = DBUtils.get_member(id, room_id, client)
            else:#this is expected to fire if generating id for party master
                break;

            # repeat while Id is unique
            if existing_id is None:
                break
        return str(id)

    @staticmethod
    def create_room(room):
        client = pymongo.MongoClient(config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        try:
            db.rooms.insert_one(room)
        except pymongo.errors.DuplicateKeyError:
            return False, None
        return True

    @staticmethod
    def get_room(room_number, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        room = db.rooms.find({'_id': room_number})
        
        if room is not None and  room.count() != 1:
            return None

        return room[0]

    @staticmethod
    def add_member(roomId, user, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        with client.start_session() as s:
            s.start_transaction()

            #break after first result. As it's unique, there should only be one
            users = '';
            for r in db.rooms.find( {'_id': roomId}, {"users": 1} ):
                users = r['users'];
                break

            if users != '' and  list(user.keys())[0] not in users:
                users = {**users, **user}
            else:
                s.commit_transaction()
                return False

            result = db.rooms.update(
                { '_id': roomId },
                { '$set': {'users': users} }
            )
            s.commit_transaction()

        return True

    @staticmethod
    def get_member(userId, roomId, client=None):
        '''
        :param userId: user id to search for
        :param roomId: room id to search in

        :return: user object of a specific room if exists, else - None

        :Exception ValueError: if room with roomId does not exist. 
        '''

        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        #return first result. As it's unique, there should only be one
        for r in db.rooms.find({'_id': roomId, 'users': userId}):
            return r;

        return None; # no results found

    @staticmethod
    def enqueue_song(room_number, queue, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_fields = {
            'queue': queue
        }

        # if head is empty
        if len(queue.keys()) == 1:
            for x in queue.keys():
                updated_fields['head'] = x

        db.rooms.update({'_id': room_number}, {'$set': updated_fields})
        return True, queue

    @staticmethod
    def get_head(room_number):
        fields = [
            'head',
        ]

        result = DBUtils.get_fields(room_number, fields)

        if result.count() == 0:
            return None

        song = None if 'head' not in result[0] else result[0]['head']
        print(result[0])
        return song

    @staticmethod
    def get_master(room_number):
        fields = [
            'master',
        ]

        result = DBUtils.get_fields(room_number, fields)

        if result.count() == 0:
            return None

        master = None if 'master' not in result[0] else result[0]['master']
        return master

    @staticmethod
    def get_pending_songs(room_number):
        fields = [
            'queue',
        ]

        pending_songs = DBUtils.get_fields(room_number, fields)

        queue = None if 'queue' not in pending_songs[0] else pending_songs[0]['queue']
        return queue

    @staticmethod
    def get_played_songs(room_number):
        fields = [
            'history',
        ]

        played_songs = DBUtils.get_fields(room_number, fields)

        history = None if 'history' not in played_songs[0] else played_songs[0]['history']
        return history

    @staticmethod
    def get_all_songs(room_number):
        fields = [
            'queue',
            'history'
        ]

        all_songs = DBUtils.get_fields(room_number, fields)

        history = None if 'history' not in all_songs[0] else all_songs[0]['history']
        queue = None if 'queue' not in all_songs[0] else all_songs[0]['queue']
        return history, queue

    @staticmethod
    def get_fields(room_number, fields):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        fields_obj = {}

        for x in fields:
            fields_obj[x] = 1

        result = db.rooms.find({'_id': room_number}, fields_obj)

        return result

    @staticmethod
    def update_song_lists(room_number, history, queue):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_fields = {
            'queue': queue,
            'history': history
        }
        write_result = db.rooms.update({'_id': room_number}, {'$set': updated_fields})
        is_successful = write_result['nModified'] == 1
        return is_successful, history, queue

    @staticmethod
    def update_head(room_number, url):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_fields = {
            'head': url
        }

        write_result = db.rooms.update({'_id': room_number}, {'$set': updated_fields})
        is_successful = write_result['nModified'] == 1
        return is_successful, url


import config
import pymongo
import bson
from enum import Enum
from utils.ErrorUtils import ErrorMsg

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
    def delete_room(roomId):
        '''
        Delete room by roomId\n
        :param roomId: room id to be destroyed\n
        :return: True - if sucessfull, False - overwhise
        '''
        client = pymongo.MongoClient(config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        result = db.rooms.remove(roomId)
        
        print(result)
        if 'ok' in result and result['ok']==1.0:
            return True

        return False

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

        fields = [
            'users.' + userId,
        ]

        result = DBUtils.get_fields(roomId, fields)

        if result.count() == 0:
            return None

        user = None if 'users' not in result[0] else result[0]['users']
        return user

    @staticmethod
    def enqueue_song(room_number, url, song, num_elements, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_fields = {
            ('queue.' + url): song
        }

        # if head is empty
        if num_elements == 1:
            updated_fields['head'] = url

        db.rooms.update({'_id': room_number}, {'$set': updated_fields})
        return True

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
        return is_successful

    @staticmethod
    def get_votes_per_user(room_number, user_id):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        fields = [
            'users.' + user_id
        ]
        print(room_number)
        print(fields)
        result = DBUtils.get_fields(room_number, fields)

        users = None if 'users' not in result[0] else result[0]['users']
        songs = {}
        if users is not None and user_id in users:
            songs = users[user_id]

        return songs

    @staticmethod
    def upvote(room_number, url, user_id):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_fields = {
            'users.' + user_id + '.songs.' + url: 1
        }

        with client.start_session() as s:
            s.start_transaction()
            write_result = db.rooms.update({'_id': room_number}, {'$set': updated_fields})
            is_successful = write_result['nModified'] == 1
            if is_successful:
                score_field = {
                    '$inc': {
                        'queue.' + url + '.score': 1
                    }
                }
                write_result_score_update = db.rooms.update({'_id': room_number}, score_field)
                is_successful = write_result_score_update['nModified'] == 1 and is_successful

                result = db.rooms.find({'_id': room_number}, {'queue': 1, 'head': 1})
                queue = None if 'queue' not in result[0] else result[0]['queue']
                current_head = None if 'head' not in result[0] else result[0]['head']
                upvoted_song_score = -1
                current_head_score = -1
                if url in queue and 'score' in queue[url]:
                    upvoted_song_score = queue[url]['score']
                if current_head in queue and 'score' in queue[current_head]:
                    current_head_score = queue[current_head]['score']
                if current_head_score == -1 or upvoted_song_score == -1:
                    s.abort_transaction()
                    return False

                if upvoted_song_score > current_head_score:
                    write_result_head_update = db.rooms.update({'_id': room_number}, {'$set': {'head': url}})
                    is_successful = write_result_head_update['nModified'] == 1 and is_successful
                s.commit_transaction()
            else:
                s.abort_transaction()
                return False

        return is_successful

    @staticmethod
    def dequeue_song(room_number):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        retrieved_fields = {
            'head': 1,
            'queue': 1
        }

        with client.start_session() as s:
            s.start_transaction()
            # Get head and queue
            result = db.rooms.find({'_id': room_number}, retrieved_fields)
            head = None if 'head' not in result[0] else result[0]['head']
            queue = None if 'queue' not in result[0] else result[0]['queue']
            if head is None:
                s.commit_transaction()
                return False, None, ErrorMsg.NO_HEAD # TODO change with appropriate return values
            elif queue is None:
                s.commit_transaction()
                return False, None, ErrorMsg.NO_QUEUE # TODO change with appropriate return values

            # Pop from queue object
            song = {}
            if head in queue:
                song[head] = queue[head]
                del queue[head]

            if len(song[head].keys()) == 0:
                s.commit_transaction()
                return False, None, ErrorMsg.NO_SONG # TODO change with appropriate return values

            # Get next highest scored song
            next_head = None
            if len(queue.keys()) > 0:
                for x in queue.keys():
                    if next_head is None:
                        next_head = x
                        continue
                    if queue[x]['score'] > queue[next_head]['score']:
                        next_head = x

            updated_fields = {
                '$set': {
                    'history.' + head: song[head],
                    'head': next_head
                },
                '$unset': {
                    'queue.' + head: "" # emptry string according to MongoDB's doc
                }
            }

            write_result = db.rooms.update({'_id': room_number}, updated_fields)
            is_successful = write_result['nModified'] > 0
            s.commit_transaction()
        if not is_successful:
            return is_successful, {}, ErrorMsg.DEQ_FAIL

        return is_successful, song, ''


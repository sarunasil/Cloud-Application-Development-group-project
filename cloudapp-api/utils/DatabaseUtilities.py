import config
import pymongo

# Helper class for managing with Database interactions
# IMPORTANT: Every query to the database shall occur from here as an exit point of the app (exit in terms that MongoDB database is in Mongo Atlas Cloud)
class DBUtils:
    @staticmethod
    def create_room(room):
        client = pymongo.MongoClient(config.MONGODB_CONFIG['URL'])
        existing_room = DBUtils.get_room(room['id'], client)

        # room with this ID already exists
        if existing_room is not None:
            return False, None

        db = client.pymongo_test
        room['_id'] = room['id']
        try:
            db.rooms.insert_one(room)
        except pymongo.errors.DuplicateKeyError:
            return False, None
        return True, room

    @staticmethod
    def get_room(room_number, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        room = db.rooms.find({'_id': room_number})
        if room.count() != 1:
            return None

        return room[0]

    @staticmethod
    def enqueue_song(room_number, queue, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        updated_queue = {
            'queue': queue
        }

        db.rooms.update({'_id': room_number}, {'$set': updated_queue})
        return True, queue

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

import config
import pymongo

class DBUtils:
    @staticmethod
    def create_room(room):
        client = pymongo.MongoClient(config.MONGODB_CONFIG['URL'])
        existing_room = DBUtils.get_room(room['id'], client)

        # room with this ID already exists
        if existing_room.count() != 0:
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
        return room

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
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
        Generates a unique identifier using ObjectId - same as MongoDb auto-assigned _id\n
        :param purpose: one of Purpose Enum value\n
        :return unique ObjectId string\n
        :Exception ValueError: if room with roomId does not exist. 
        '''

        id = "";
        while True:
            #generate unique id
            id = bson.ObjectId();

            existing_id = ""
            #check if id is already used
            if purpose == Purpose.ROOM:
                existing_id = DBUtils.get_room(str(id), client)
            elif purpose == Purpose.USER and room_id is not None:
                existing_id = DBUtils.get_member(str(id), room_id, client)
            else:#this is expected to fire if generating id for party master
                break;
            print(id)

            # repeat while Id is unique
            if existing_id is None:
                break
        return str(id)

    @staticmethod
    def nicknameUnique(roomId, nickname):
        '''
        Test if a nickname is already used in the room
        :param roomId:
        :param nickname: nickname to check
        :return: True - nickname is unique; False - nickname is not unique
        '''

        fields = [
            'users'
        ]
        users = DBUtils.get_fields(roomId, fields)

        nicknames=[]
        if users is not None:
            users = users[0]['users']
            for id in users.keys():#go through every user entry and extract nickname
                nick = users[id]['nickname']
                nicknames.append(nick)

            #self-explanatory
            if nickname not in nicknames:
                return True

        return False

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

            #check user nickname for uniqueness
            nicknames=[]
            if users is not None:
                for id in users.keys():#go through every user entry and extract nickname
                    nick = users[id]['nickname']
                    nicknames.append(nick)

                #self-explanatory
                if list(user.values())[0]['nickname'] in nicknames:
                    s.abort_transaction()
                    return False

            if users != '' and  list(user.keys())[0] not in users:
                users = {**users, **user}
            else:
                s.abort_transaction()
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
        :param userId: user id to search for\n
        :param roomId: room id to search in\n
        :return: user object of a specific room if exists, else - None\n
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

        user = None if 'users' not in result[0] or len(result[0]['users'])==0 else result[0]['users']
        return user

    @staticmethod
    def delete_member(userId, roomId, client=None):
        '''
        :param userId: user id to remove for\n
        :param roomId: room id to remove from in\n
        :return: is_successful - boolean
        '''
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        #don't kick master!
        master = DBUtils.get_master(roomId)
        if userId in master:
            return False

        #kick
        with client.start_session() as s:
            s.start_transaction()
            fields = {
                '$unset': {
                    'users.' + userId: ""
                }
            }

            #remove according to fields
            remove_user_result = db.rooms.update({'_id': roomId}, fields)
            is_successful = remove_user_result['nModified'] > 0

            if is_successful:
                s.commit_transaction()
            else:
                s.abort_transaction()

            return is_successful

    @staticmethod
    def block_member(userId, ip, nickname, roomId, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        #don't block master!
        master = DBUtils.get_master(roomId)
        if userId in master:
            return False

        with client.start_session() as s:
            s.start_transaction()

            #get the list of blocked 
            blocked_members = None
            for r in db.rooms.find( {'_id': roomId}, {"blocked_members": 1} ):
                blocked_members = r['blocked_members']
                break
            
            if blocked_members is not None and userId not in blocked_members:
                blocked_members[userId] = {
                    'IP': ip,
                    'nickname':nickname
                }
            else:
                s.abort_transaction()
                return False

            result = db.rooms.update(
                { '_id': roomId },
                { '$set': {'blocked_members': blocked_members} }
            )
            s.commit_transaction()
            return True
        return False

    @staticmethod
    def unblock_member(userId, roomId, client=None):
        if client is None:
            client = pymongo.MongoClient(
                config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        with client.start_session() as s:
            s.start_transaction()
            fields = {
                '$unset': {
                    'blocked_members.' + userId: ""
                }
            }

            #remove according to fields
            remove_user_result = db.rooms.update({'_id': roomId}, fields)
            is_successful = remove_user_result['nModified'] > 0

            if is_successful:
                s.commit_transaction()
            else:
                s.abort_transaction()
            s.commit_transaction()
            return True

        return False

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
        if users is not None and user_id in users and 'songs' in users[user_id]:
            songs = users[user_id]['songs']

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
    def unvote(room_number, url, user_id):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test
        unset_fields = {
           '$unset': {
               'users.' + user_id + '.songs.' + url: ""
           }
        }

        with client.start_session() as s:
            s.start_transaction()
            # Update user votes
            write_result = db.rooms.update({'_id': room_number}, unset_fields)
            is_successful = write_result['nModified'] == 1
            # Update queue with song's new score
            if is_successful:
                score_field = {
                    '$inc': {
                        'queue.' + url + '.score': -1
                    }
                }
                write_result_score_update = db.rooms.update({'_id': room_number}, score_field)
                is_successful = write_result_score_update['nModified'] == 1 and is_successful

                # Update head if necessary
                result = db.rooms.find({'_id': room_number}, {'queue': 1, 'head': 1})
                queue = None if 'queue' not in result[0] else result[0]['queue']
                current_head = None if 'head' not in result[0] else result[0]['head']
                if current_head is None:
                    if queue is not None:
                        # If queue is not empty, it must have a head
                        if len(queue.keys()) > 0:
                            s.abort_transaction()
                            return False, ErrorMsg.HEAD_MISMATCH
                    else:
                        # No queue returned
                        s.abort_transaction()
                        return False, ErrorMsg.NO_QUEUE
                elif current_head in queue and url in queue:
                    # Check if the head (downvoted song) is actually leading again
                    if current_head == url:
                        for x in queue.keys():
                            if queue[x]['score'] > queue[current_head]['score'] - 1:
                                current_head = x
                                # Update head if it is not head anymore
                                updated_fields = {
                                    '$set': {
                                        'head': current_head
                                    }
                                }
                                write_result_score_update = db.rooms.update({'_id': room_number},
                                                                            updated_fields)
                                break
                else:
                    # head or unvoted song are not in the queue, abort
                    s.abort_transaction()
                    return False, ErrorMsg.ERROR
                s.commit_transaction()
            else:
                s.abort_transaction()
                return False, ErrorMsg.VOTE_NOT_REMOVED

        return is_successful, None

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

    @staticmethod
    def remove_song(room_number, url):
        client = pymongo.MongoClient(
            config.MONGODB_CONFIG['URL'])

        db = client.pymongo_test

        fields = {
            '$unset': {
                'queue.' + url: ""
            }
        }

        with client.start_session() as s:
            s.start_transaction()
            head_result = db.rooms.find({'_id': room_number}, {'head': 1})
            head = None

            for x in head_result:
                head = x['head']
                break

            queue = None
            # Check if the deleted song is at the head of the queue
            if head is not None and url == head:
                result = db.rooms.find({'_id': room_number}, {'queue': 1})

                # get actual queue if the deleted song is at the head, because we need to change the head
                for x in result:
                    queue = x['queue']
                    if head in queue:
                        del queue[head]
                    break

            # check the next highest-voted song
            if queue is not None:
                max_head = None
                for x in queue.keys():
                    if max_head is None:
                        max_head = x
                        continue

                    if queue[x]['score'] > queue[max_head]['score']:
                        max_head = x

                if max_head is not None:
                    fields['$set'] = {
                        'head': max_head
                    }

            remove_song_result = db.rooms.update({'_id': room_number}, fields)
            is_successful = remove_song_result['nModified'] > 0

            # get up-to-date queue
            updated_queue_result = db.rooms.find({'_id': room_number}, {'queue': 1})
            for x in updated_queue_result:
                queue = x['queue']
                break

            if is_successful:
                s.commit_transaction()
            else:
                s.abort_transaction()

            return is_successful, queue


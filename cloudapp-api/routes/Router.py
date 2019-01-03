from utils.Response import Response
from utils.DatabaseUtilities import DBUtils
from utils.DatabaseUtilities import Purpose
from utils.Security import SecurityUtils
from utils.QueueModerator import QueueModerator
from DataStructures.AbstractDataStructures import DuplicatePriorityQueue

from utils.RoomModerator import RoomModerator
from utils.QueueModerator import QueueModerator
from utils.TokenModerator import TokenModerator
from utils.UserModerator import UserModerator

class Router(RoomModerator, QueueModerator, TokenModerator, UserModerator):
    """
    Hides all API actions complexity from main.py

    Functions are split between files:
    
    RoomModerator.py
    - create_room
    - join_room
    - delete_room

    QueueModerator.py
    - enqueue_song
    - dequeue_song
    - remove_song
    - upvote_song

    TokenModerator.py
    -

    UserModerator.py
    -
    """

    @staticmethod
    def pending_songs(room_number):
        try:
            unsorted_queue = DBUtils.get_pending_songs(room_number)
            # possible type error - idk if unsorted_queue is of type dict
            sorted_queue = QueueModerator.sort_pending_songs(unsorted_queue)
            return True, sorted_queue
        except:
            return False, []

    @staticmethod
    def played_songs(room_number):
        return
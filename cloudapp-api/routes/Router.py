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
from enum import Enum

class ErrorMsg(Enum):
    NO_HEAD = 'No head is provided'
    NO_QUEUE = 'Queue does not exist'
    NO_SONG = 'Song does not exist'
    DEQ_FAIL = 'Song was not dequeued'
    NO_MASTER = 'Access denied! User is not a master'
    NO_USER = 'Access denied! User does not belong to this room'
    NOT_REMOVED = 'Song was not removed! It either does not exist or an error has occurred!'
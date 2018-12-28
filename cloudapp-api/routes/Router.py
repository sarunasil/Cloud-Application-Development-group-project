from utils.Response import Response

class Router:
    def __init__(self, room_keeper):
        self.room_keeper = room_keeper

    def create_room(self, room_number):
        result, queue = self.room_keeper.create_room(room_number)
        msg = ''
        if result:
            msg = 'Room has been created'
            return Response.responseSuccess(msg)
        else:
            msg = 'Room with this number already exists'
            return Response.responseFailure(msg)

    def join_room(self, room_number):
        return Response.responseSuccess(room_number)

    def enqueue_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def dequeue_song(self, room_number):
        return Response.responseSuccess(room_number)

    def upvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def downvote_song(self, room_number, url):
        return Response.responseSuccess(room_number)

    def delete_room(self, room_number, url):
        return Response.responseSuccess(room_number)

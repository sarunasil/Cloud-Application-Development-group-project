# Class for mapping all rooms
class RoomKeeper:
    def __init__(self):
        self.__map = {}

    def create_room(self, room_number):
        room_num = self.get_room_number_int(room_number)
        if self.has_room(room_number):
            return False, self.get_queue(room_number)

        # TODO - change empty string to queue
        self.__map[room_num] = ''
        return True, ''

    def delete_room(self, room_number):
        room_num = self.get_room_number_int(room_number)
        room = self.__map[room_num]
        if self.has_room(room_number):
            del self.__map[room_num]

        return room

    def get_queue(self, room_number):
        room_num = self.get_room_number_int(room_number)

        return self.__map.get(room_num, 'Empty')

    def has_room(self, room_number):
        return self.get_queue(room_number) != 'Empty'

    def get_room_number_int(self, room_number):
        return int(room_number) if not isinstance(room_number, int) else room_number


from redis import Redis
from json import dumps
## custom stubs / types ##
from custom_types.socket_io_stubs import MessageData

class RedisController: 
    redis_instance = Redis(host="localhost", port=6379, db=0)
    connected_clients: str = "connected_clients"
    live_private_rooms: str = "live_private_rooms"
    live_general_rooms: str = "live_general_rooms"
   
    def setup(self) -> None: 
        print(self.redis_instance.delete(self.connected_clients))

    def add_connected_client_info(self, socket_id: str) -> int:
        return self.redis_instance.lpush(self.connected_clients, socket_id)
    def remove_connected_client_info(self, socket_id: str) -> int:
        return self.redis_instance.lrem(self.connected_clients, 0, socket_id)
    ## ROOM HANDLERS ##
    def join_private_room(self, room_name: str, client_socket_id: str) -> bool:
        ## check if room exists ##
        room_exists: int = self.redis_instance.exists(room_name)
        if room_exists:
            self.redis_instance.sadd(room_name, client_socket_id)
            return True
        else:
            ## add a new room to the <live_private_rooms> set first ##
            self.redis_instance.sadd(self.live_private_rooms, room_name)
            self.redis_instance.sadd(room_name, client_socket_id)
            return True

    def leave_private_room(self, room_name: str, client_socket_id: str) -> bool:
        ## check if room exists ##
        room_exists: int = self.redis_instance.exists(room_name)
        if (room_exists):
            ## remove client_socket_id from the room ##
            ## remove the room_name from <self.live_private_rooms> if last <client_socket_id> ##
            self.redis_instance.srem(room_name, client_socket_id)
            if self.redis_instance.scard(room_name) == 0: self.redis_instance.srem(self.live_private_rooms, room_name) 
            return True
        else:
            ## room does not exist ##
            print("Room doesnt exist")
            return False

    def join_general_room(self, room_name: str) -> int:
        room_exists: int = self.redis_instance.exists(room_name)
        return self.redis_instance.lpush(self.live_general_rooms) if room_exists else 0

    def leave_general_room(self, room_name: str) -> int:
        return self.redis_instance.lrem(self.live_general_rooms, 0, room_name)

    ## MESSAGE HANDLERS ## 
    def handle_new_message(self, room_name: str, message_data: MessageData) -> int:
        string_message_data: str = dumps(message_data)
        message_position: int = self.redis_instance.hlen(room_name)
        return self.redis_instance.hset(room_name, str(message_position), string_message_data)
    def remove_specific_message(self, room_name: str, message_position: int) -> int:
        if self.redis_instance.hexists(room_name, str(message_position)):
            ## room must exists ##
            return self.redis_instance.hdel(room_name, str(message_position))
        else:
            ## better error reporting? ##
            return 0
    def remove_all_messages(self, room_name: str) -> int:
        if room_name:
            return self.redis_instance.delete(room_name)
        else:
            ## better error reporting? ##
            return 0

    def get_number_of_connected_clients(self) -> int:

        return self.redis_instance.llen(self.connected_clients)



RedisControllerInstance = RedisController()
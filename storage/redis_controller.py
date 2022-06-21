from redis import Redis
from json import dumps
## custom stubs / types ##
from custom_types.socket_io_stubs import MessageData

class RedisController: 
    redis_instance = Redis(host="localhost", port=6379, db=0)
    connected_clients: str = "connected_clients"
    live_rooms: str = "live_rooms"
   
    def setup(self) -> None: 
        print(self.redis_instance.delete(self.connected_clients))

    def add_connected_client_info(self, socket_id: str) -> int:
        return self.redis_instance.lpush(self.connected_clients, socket_id)
    def remove_connected_client_info(self, socket_id: str) -> int:
        return self.redis_instance.lrem(self.connected_clients, 0, socket_id)
    ## ROOM HANDLERS ##
    def add_a_live_room(self, room_name: str) -> int:
        return self.redis_instance.lpush(self.live_rooms, room_name)
    def remove_a_live_room(self, room_name: str) -> int:
        return self.redis_instance.lrem(self.live_rooms, 0, room_name)

    ## MESSAGE HANDLERS ## 
    def handle_new_message(self, room_name: str, message_data: MessageData,) -> int:
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
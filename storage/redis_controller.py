from redis import Redis
from json import dumps
from typing import Dict, List, Literal, Set, Tuple
## custom stubs / types ##
from custom_types.socket_io_stubs import GenPrivateRoomInfo, MessageData, QueriedRoomData, SpecificPrivateRoomInfo

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
    ## PRIVATE ROOM HANDLERS ##
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
        if room_exists:
            ## remove client_socket_id from the room ##
            ## remove the room_name from <self.live_private_rooms> if last <client_socket_id> ##
            self.redis_instance.srem(room_name, client_socket_id)
            if self.redis_instance.scard(room_name) == 0: self.redis_instance.srem(self.live_private_rooms, room_name) 
            return True
        else:
            ## room does not exist ##
            print("Room doesnt exist")
            return False
    ## GENERAL ROOM HANDLERS ##
    def join_general_room(self, room_name: str, client_socket_id: str) -> bool:
        ## check if room exists ##
        ## if does add <client_socket_id> to the room else add room to the set ##
        room_exists: int = self.redis_instance.exists(room_name)
        if room_exists: 
            self.redis_instance.sadd(room_name, client_socket_id)
            return True
        else:
            self.redis_instance.sadd(self.live_general_rooms, room_name)
            self.redis_instance.sadd(room_name, client_socket_id)
            return True
    
    def leave_general_room(self, room_name: str, client_socket_id: str) -> bool:
         ## check if room exists ##
        room_exists: int = self.redis_instance.exists(room_name)
        if room_exists:
            ## remove client_socket_id from the room ##
            ## remove the room_name from <self.live_live_general_rooms> if last <client_socket_id> ##
            self.redis_instance.srem(room_name, client_socket_id)
            if self.redis_instance.scard(room_name) == 0: self.redis_instance.srem(self.live_general_rooms, room_name) 
            return True
        else:
            ## room does not exist ##
            print("General room doesnt exist")
            return False

    ## MESSAGE HANDLERS ## 
    ## NEW MESSAGE HANDLER ##
    def handle_new_message(self, message_data: MessageData) -> int:
        ## <message_position> is needed for exact deletion of messages from hash ##
        ## room must already exist for a new message to be processed ##
        room_name: str = message_data["room_name"]
        room_exists: bool = self.redis_instance.sismember(self.live_general_rooms, room_name) or self.redis_instance.sismember(self.live_private_rooms, room_name)
        if room_exists:
            string_message_data: str = dumps(message_data)
            message_position: int = self.redis_instance.hlen(room_name)
            return self.redis_instance.hset(room_name, str(message_position), string_message_data)
        else:
            ## TODO Insert custom errors ##
            return 0
    ## MESSAGE DELETION ##
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

    ## INFORMATION GETTERS ##
    ## ROOMS AND CLIENTS ##
    def get_number_of_connected_clients(self) -> int:
        return self.redis_instance.llen(self.connected_clients)
    
    def get_general_private_room_data(self) -> GenPrivateRoomInfo:
        byte_set: Set[bytes] = self.redis_instance.smembers(self.live_private_rooms)
        room_names: List[str] = []
        for value in byte_set:
            room_names.append(value.decode("utf-8"))
        return { "total_rooms": len(room_names), "room_names": room_names }

    def get_specific_private_room_data(self, room_name: str) -> SpecificPrivateRoomInfo:
        room_active: bool = self.redis_instance.sismember(self.live_private_rooms, room_name)
        connected_clients: List[str] = []
        num_of_connected_clients: int = 0
        if (room_active):
            users_byte_set: Set[bytes] = self.redis_instance.smembers(room_name)
            for value in users_byte_set:
                connected_clients.append(value.decode("utf-8"))
            num_of_connected_clients = len(connected_clients)
        return { 
            "active": room_active, 
            "room_name": room_name, 
            "connected_clients": connected_clients, 
            "num_of_connected_clients": num_of_connected_clients
        }
    ## MESSAGES ##
    def get_complete_room_data(self, room_name: str, room_type: Literal["general", "private"]) -> QueriedRoomData | Literal[False]:
        messages: List[str] = []; num_of_messages: int = 0; num_of_connected_clients: int = 0; 
        if room_type == "general" and self.redis_instance.sismember(self.live_general_rooms, room_name):
            messages, num_of_messages, num_of_connected_clients = self.__retrieve_room_msgs_and_clients(room_name)
        elif room_type == "private" and self.redis_instance.sismember(self.live_private_rooms, room_name):
            messages, num_of_messages, num_of_connected_clients = self.__retrieve_room_msgs_and_clients(room_name)
        else:
            print("Could not resolve room data")
            return False
        ##
        return {
            "room_type": room_type,
            "room_name": room_name,
            "num_of_connected_clients": num_of_connected_clients,
            "num_of_messages": num_of_messages,
            "messages": messages
        }
    
    def __retrieve_room_msgs_and_clients(self, room_name: str) -> Tuple[List[str], int, int]:
        messages: List[str] = []; num_of_messages: int = 0
        ## query and convert info on room from redis ##
        num_of_connected_clients: int = self.redis_instance.scard(room_name)  
        messages_dict: Dict[bytes, bytes] = self.redis_instance.hgetall(room_name)

        for value in messages_dict.values():
            messages.append(value.decode("UTF-8"))
        
        num_of_messages = len(messages)
        
        return messages, num_of_messages, num_of_connected_clients


RedisControllerInstance = RedisController()
from redis import Redis
from json import dumps
from typing import Dict, List, Literal, Set, Tuple
## custom stubs / types ##
from custom_types.socket_io_stubs import GenAllRoomInfo, MessageData, QueriedRoomData, SpecificRoomInfo
from custom_types.constants import RedisDBConstants

class RedisController: 
    redis_instance = Redis(host="localhost", port=6379, db=0, decode_responses=True, charset="utf-8")
   
    def setup(self) -> None: 
        ## TODO - We will need to clear everying on launc? ##
        ## print(self.redis_instance.delete(self.connected_clients)) ##
        pass

    def add_connected_client_info(self, socket_id: str) -> int:
        return self.redis_instance.sadd(RedisDBConstants.ConnectedClientsSet, socket_id)
    def remove_connected_client_info(self, socket_id: str) -> bool:
        num_of_gen_rooms: int = 0; num_of_private_rooms: int = 0
        ## client socket id needs to be removed from all rooms in which may be ##
        live_gen_rooms: set[str] = self.redis_instance.smembers(RedisDBConstants.LiveGeneralRoomsSet)
        live_private_rooms: set[str] = self.redis_instance.smembers(RedisDBConstants.LivePrivateRoomsSet)
        ## check all live rooms the client may be in and remove ##
        for gen_room_name in live_gen_rooms:
            if self.redis_instance.sismember(gen_room_name, socket_id): 
                self.leave_general_room(room_name=gen_room_name, client_socket_id=socket_id)
                num_of_gen_rooms += 1
        for private_room_name in live_private_rooms:
            if self.redis_instance.sismember(private_room_name, socket_id): 
                self.leave_private_room(room_name=private_room_name, client_socket_id=socket_id)
                num_of_private_rooms +=1
        ## finally disconnect client from <RedisDBConstants.ConnectedClientsSet> ##
        self.redis_instance.srem(RedisDBConstants.ConnectedClientsSet, socket_id)
        print("disconnected client")
        print({ "num_of_gen_rooms": num_of_gen_rooms, "num_of_private_rooms": num_of_private_rooms, "client_socket_id": socket_id  })
        return True    


    ## ROOM HANDLERS ##
    ## PRIVATE ROOM HANDLERS ##
    def join_private_room(self, room_name: str, client_socket_id: str) -> bool:
        ## check if room exists ##
        redis_named_room_key: str = self.__redis_named_room_key(room_name)
        room_exists: int | bool  = self.redis_instance.exists(redis_named_room_key) and self.redis_instance.sismember(RedisDBConstants.LivePrivateRoomsSet, room_name)
        if room_exists:
            ## add <client_socket_id> to <RedisDBConstants.LivePrivateRoomsSet> only ##
            self.redis_instance.sadd(redis_named_room_key, client_socket_id)
            return True
        else:
            ## add a new room to the <live_private_rooms> SET first ##
            ## add <client_socket_id> to the <redis_named_room_key> SET ##
            self.redis_instance.sadd(RedisDBConstants.LivePrivateRoomsSet, room_name)
            self.redis_instance.sadd(redis_named_room_key, client_socket_id)
            return True

    def leave_private_room(self, room_name: str, client_socket_id: str) -> bool:
        ## check if room exists ##
        redis_named_room_key: str = self.__redis_named_room_key(room_name)
        room_exists: int | bool  = self.redis_instance.exists(redis_named_room_key) and self.redis_instance.sismember(RedisDBConstants.LivePrivateRoomsSet, room_name)
        if room_exists:
            ## remove client_socket_id from the <redis_named_room_key> SET ##
            ## remove the room_name from <RedisDBConstants.LivePrivateRoomsSet> if last <client_socket_id> ##
            self.redis_instance.srem(redis_named_room_key, client_socket_id)
            if self.redis_instance.scard(redis_named_room_key) == 0: self.redis_instance.srem(RedisDBConstants.LivePrivateRoomsSet, room_name) 
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
    ## client info getters ##
    def get_number_of_connected_clients(self) -> int:
        return self.redis_instance.scard(self.connected_clients)

    ## general room info getters ##
    def get_all_general_room_data(self) -> GenAllRoomInfo:
        room_names: List[str] = list(self.redis_instance.smembers(self.live_general_rooms))
        return { "room_type": "general", "total_rooms": len(room_names), "room_names": room_names }

    def get_all_private_room_data(self) -> GenAllRoomInfo:
        room_names: List[str] = list(self.redis_instance.smembers(self.live_private_rooms))
        return { "room_type": "private", "total_rooms": len(room_names), "room_names": room_names }
    
    ## specific room info getters ##
    def get_specific_general_room_data(self, room_name: str) -> SpecificRoomInfo:
        room_active: bool = self.redis_instance.sismember(self.live_general_rooms, room_name)
        connected_clients: List[str] = list()
        num_of_connected_clients: int = 0
        if (room_active):
            connected_clients = list(self.redis_instance.smembers(room_name))
            num_of_connected_clients = len(connected_clients)
        return {
            "room_type": "general",
            "active": room_active,
            "room_name": room_name,
            "connected_clients": connected_clients,
            "num_of_connected_clients": num_of_connected_clients
        }
    
    def get_specific_private_room_data(self, room_name: str) -> SpecificRoomInfo:
        room_active: bool = self.redis_instance.sismember(self.live_private_rooms, room_name)
        connected_clients: List[str] = list()
        num_of_connected_clients: int = 0
        if (room_active):
            connected_clients = list(self.redis_instance.smembers(room_name))
            num_of_connected_clients = len(connected_clients)
        return { 
            "room_type": "private",
            "active": room_active, 
            "room_name": room_name, 
            "connected_clients": connected_clients, 
            "num_of_connected_clients": num_of_connected_clients
        }
    
    ## room info getter with clients and messages ##
    def get_complete_room_data(self, room_name: str, room_type: Literal["general", "private"]) -> QueriedRoomData | Literal[False]:
        messages: List[str] = []; num_of_messages: int = 0; num_of_connected_clients: int = 0; 
        if room_type == "general" and self.redis_instance.sismember(self.live_general_rooms, room_name):
            connected_clients, messages, num_of_messages, num_of_connected_clients = self.__retrieve_room_msgs_and_clients(room_name)
        elif room_type == "private" and self.redis_instance.sismember(self.live_private_rooms, room_name):
            connected_clients, messages, num_of_messages, num_of_connected_clients = self.__retrieve_room_msgs_and_clients(room_name)
        else:
            print("Could not resolve room data")
            return False
        ##
        return {
            "room_type": room_type,
            "room_name": room_name,
            "num_of_connected_clients": num_of_connected_clients,
            "connected_clients": connected_clients,
            "num_of_messages": num_of_messages,
            "messages": messages
        }
    
    ## HELPERS ##
    def __redis_named_room_key(self, room_name: str) -> str:
        return room_name.upper() + "_" + RedisDBConstants.NamedRoomSet

    def __retrieve_room_msgs_and_clients(self, room_name: str) -> Tuple[List[str], List[str], int, int]:
        messages: List[str] = []; num_of_connected_clients: int = 0; num_of_messages: int = 0
        ## query and convert info on room from redis ##
        connected_clients: List[str] = list(self.redis_instance.smembers(room_name))
        messages_dict: Dict[str, str] = self.redis_instance.hgetall(room_name)

        for value in messages_dict.values():
            messages.append(value)
        
        num_of_messages = len(messages)
        num_of_connected_clients = len(connected_clients)
        
        return connected_clients, messages, num_of_messages, num_of_connected_clients


RedisControllerInstance = RedisController()
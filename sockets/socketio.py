from json import dumps
from flask import request
from flask_socketio import SocketIO, join_room, leave_room, Namespace
from typing import Dict, List
##
from storage.redis_controller import RedisControllerInstance
from custom_types.socket_io_stubs import ClientData, GenPrivateRoomInfo, MessageData, PrivateRoomData

class SocketIOChatNamespace(Namespace):
    def on_connect(self, data: ClientData) -> None:
        print("Connected to Room")
        print(data)

class SocketIODefaultNamespace(Namespace):

    def on_connect(self, data: str) -> None:
        client_info = { 'socket_id': request.sid, 'namespace': request.namespace, 'message': "You are now connected live" } # type: ignore
        RedisControllerInstance.add_connected_client_info(request.sid) # type: ignore
        self.emit("client connected", client_info)
        print("Client has connected")
        print("Number of connected clients is: " + str(RedisControllerInstance.get_number_of_connected_clients()))

    def on_disconnect(self) -> None:
        print("Client has disconnected")
        RedisControllerInstance.remove_connected_client_info(request.sid) # type: ignore
        print("Number of connected clients is: " + str(RedisControllerInstance.get_number_of_connected_clients()))
    
    def on_join_private_room(self, data: PrivateRoomData) -> None:
        print("Joining room")
        try: 
            room_name: str = data["room_name"]; socket_id: str = request.sid # type: ignore
            print(join_room(room_name, socket_id, "/"))
            ## add room name to redis #
            print(RedisControllerInstance.join_private_room(room_name, socket_id))
        except Exception as e: 
            print("Room join exception")
            print(e)
    
    def on_leave_private_room(self, data: PrivateRoomData) -> None:
        print("Leaving Room")
        try: 
            room_name: str = data["room_name"]; socket_id: str = request.sid # type: ignore
            leave_room(room_name, socket_id, "/")
            print(RedisControllerInstance.leave_private_room(room_name, socket_id))
        except Exception as e:
            print("Leave room exception")
            print(e)
    
    ## MESSAGING ##
    def on_new_message(self, message_data: MessageData) -> None:
        sender_socket_id: str = request.sid # type: ignore 
        try:
            ## ensure that client sent all correct info ##
            input_errors: List[str] = self.__validate_message_data(message_data)
            if input_errors: self.__send_error_response(sender_socket_id, input_errors)
            ## save the message to the specfic room message hash ##
            ## emit the message to all in room BUT the sender ##
            room_name: str = message_data["room_name"]
            if RedisControllerInstance.handle_new_message(message_data): self.emit("receive_new_message", data=message_data, room=room_name, include_self=False)
            ## TODO: include an error emit ##
        except Exception as e:
            print("ON_NEW_MESSAGE ERROR")
            print(e)


    ## information getters ##
    def on_get_gen_private_room_data(self, data: Dict[str, str]) -> None: 
        ## should have authorization ##
        print("General private room info")
        print(data)
        try:
            client_socket_id: str = request.sid # type: ignore
            RedisControllerInstance.get_general_private_room_data()
        except Exception as e:
            print(e)

    ## 'PRIVATE' METHODS AND HELPERS ##
    def __validate_message_data(self, message_data: MessageData) -> List[str]:
        input_errors: List[str] = []
        
        if not message_data["room_name"]: input_errors.append("No room name sent")
        if not message_data["message_str"]: input_errors.append("No message string sent")

        return input_errors

    def __send_error_response(self, sender_socket_id: str, input_errors: List[str]) -> None:
        message_JSON: str = dumps({ "erros": input_errors })
        return self.emit("wrong_data_error", data=message_JSON, to=sender_socket_id)

class SocketIOInstance: 
    def __init__(self, app) -> None:
        self.socketio = SocketIO(app, cors_allowed_origins='*', logger=True, engineio_logger=True)
        self.app = app
    
    def run(self) -> "SocketIOInstance":
        self.socketio.on_namespace(SocketIODefaultNamespace("/"))
        self.socketio.on_namespace(SocketIOChatNamespace("/chats"))
        self.socketio.run(self.app)
        return self



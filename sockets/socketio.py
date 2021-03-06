import json, traceback
##
from flask import request
from flask_socketio import SocketIO, join_room, leave_room, Namespace
from typing import Dict, List, Literal
##
from storage.redis_controller import RedisControllerInstance
from custom_types.socket_io_stubs import ClientData, ErrorEmitLiteral, GetConvoMessagesData, GenErrorResponse, MessageData, ClientRoomData
from custom_types.constants import ConnectionConst, ErrorEmitConst, MessageEmitConst, RoomEmitConst

class SocketIOChatNamespace(Namespace):
    def on_connect(self, data: ClientData) -> None:
        print("Connected to CHAT Namespace")
        print(data)

class SocketIODefaultNamespace(Namespace):

    def on_connect(self) -> None:
        client_socket_id: str = request.sid # type: ignore
        try:
            client_data: ClientData = {
                "user_id": "none_for_now",      ## TODO: later assign unique <user_id> to each user ##
                "socket_id": client_socket_id,
                "user_name": "anonymous"        ## TODO: implementaion of <user_name> later ##
            }
            if RedisControllerInstance.add_connected_client_info(client_socket_id):
                self.emit(ConnectionConst.NewClientConnected, data=client_data, room=client_socket_id)
            else:
                error_response: GenErrorResponse = { "socket_id": client_socket_id, "error_messages": [ "Error saving live connection. Try again" ]}
                self.emit(ConnectionConst.NewClientConnected, data=error_response, room=client_socket_id)
                self.disconnect(client_socket_id)
        except Exception as e:
            print(traceback.format_exc())
            ## disconnect and send the exception ##
            self.__send_caught_exception_response(client_socket_id, e)
            self.disconnect(sid=client_socket_id)
    
    def on_disconnect(self) -> None:
        client_socket_id: str = request.sid # type: ignore
        try:
            RedisControllerInstance.remove_connected_client_info(client_socket_id)
            print("Number of connected clients is: " + str(RedisControllerInstance.get_number_of_connected_clients()))
            self.emit(ConnectionConst.ClientDisconnected)
        except Exception as e:
            print(traceback.format_exc())
            self.__send_caught_exception_response(sender_socket_id=client_socket_id, exception=e)
    
    ## JOIN AND LEAVE ROOMS #
    ## general rooms ##
    def on_join_general_room(self, room_data: ClientRoomData) -> None:
        client_socket_id: str = request.sid # type: ignore 
        try:
            ## ensure that client sent all correct info ##
            input_errors: List[str] = self.__validate_join_room_data(room_data)
            if input_errors: return self.__send_client_data_error_response(client_socket_id, input_errors)
            ##
            room_name: str = room_data["room_name"]
            if RedisControllerInstance.join_general_room(room_name, client_socket_id): 
               return self.__join_room_and_emit(RoomEmitConst.JoinGenRoomSuccess, client_socket_id, room_name)
            ## TODO: include an error emit ##
            else:
                self.__send_client_data_error_response()
        except Exception as e:
            print(traceback.format_exc())
            self.__send_caught_exception_response(sender_socket_id=client_socket_id, exception=e)

    def on_leave_general_room(self, room_data: ClientRoomData) -> None:
        client_socket_id: str = request.sid # type: ignore 
        try:
            ## ensure that the client sent all correct info ##
            input_errors: List[str] = self.__validate_join_room_data(room_data)
            if input_errors: return self.__send_client_data_error_response(client_socket_id, input_errors)
            ##
            room_name: str = room_data["room_name"]
            if RedisControllerInstance.leave_general_room(room_name, client_socket_id):
               return self.__leave_room_and_emit(RoomEmitConst.LeaveGenRoomSuccess, client_socket_id, room_name)
            ## TODO: include an error emit ##
        except Exception as e:
            print(traceback.format_exc())
            self.__send_caught_exception_response(sender_socket_id=client_socket_id, exception=e)
        
    ## private rooms ##
    def on_join_private_room(self, data: ClientRoomData) -> None:
        socket_id: str = request.sid # type: ignore
        try: 
            room_name: str = data["room_name"]
            join_room(room_name, socket_id, "/")
            ## add room name to redis and emit a <JoinPrivateRoomSuccess> event to specific client #
            RedisControllerInstance.join_private_room(room_name, socket_id)
        except Exception as e: 
            print(traceback.format_exc())
            self.__send_caught_exception_response(sender_socket_id=socket_id, exception=e)
    
    def on_leave_private_room(self, data: ClientRoomData) -> None:
        room_name: str = data["room_name"]; socket_id: str = request.sid # type: ignore
        try: 
            leave_room(room_name, socket_id, "/")
            print(RedisControllerInstance.leave_private_room(room_name, socket_id))
        except Exception as e:
            print(traceback.format_exc())
            self.__send_caught_exception_response(sender_socket_id=socket_id, exception=e)
   
    ## MESSAGING ##
    def on_new_message(self, message_data: MessageData) -> None:
        sender_socket_id: str = request.sid # type: ignore 
        try:
            ## user has to be part of a room to send a message ##
            ## ensure that client sent all correct info ##
            input_errors: List[str] = self.__validate_message_data(message_data)
            if input_errors: return self.__send_client_data_error_response(sender_socket_id, input_errors)
            room_name: str = message_data["room_name"]
            ## ensure that the <message_data.room_name> exists ##
            if not RedisControllerInstance.check_if_room_exists(room_name): 
                self.__send_client_data_error_response(sender_socket_id, [ "Seems like room doesn't exist" ])
            ## save the message to the specfic room message hash ##
            ## emit the message to all in room BUT the sender ##
            no = 10 / 0
            if RedisControllerInstance.handle_new_message(message_data): 
                self.emit("receive_new_message", data=message_data, room=room_name, include_self=False)
            ## TODO: include an error emit ##
        except Exception as e:
            print(traceback.print_exc())
            self.__send_caught_exception_response(sender_socket_id, exception=e)

    ## INFORMATION GETTERS ##
    def on_get_convo_messages(self, get_convo_messages_data: GetConvoMessagesData) -> None:
        sender_socket_id: str = request.sid # type: ignore 
        try:
            room_name: str = get_convo_messages_data["room_name"]; start: int = get_convo_messages_data["start"] or 0; end: int = get_convo_messages_data["end"] or -1
            if not room_name: self.__send_client_data_error_response(sender_socket_id, input_errors=[ "Could not resolve room name to fetch" ])
            conversation_messages = RedisControllerInstance.get_conversation_messages(room_name, start=start, end=end)
            self.emit(MessageEmitConst.RecConvoMessages, json.dumps(conversation_messages), room=sender_socket_id)
        except Exception as e:
            print(traceback.print_exc())
            self.__send_caught_exception_response(sender_socket_id, exception=e)

    def on_get_all_general_room_data(self, data: Dict[str, str] | None = None) -> None:
        ## TODO should have authorization ##
        client_socket_id: str = request.sid # type: ignore
        try: 
            all_general_room_data: str = json.dumps(RedisControllerInstance.get_all_general_room_data())
            self.emit(RoomEmitConst.RecAllGeneralRoomData, data=all_general_room_data, room=client_socket_id)
        except Exception as e:
            print(traceback.print_exc())
            self.__send_caught_exception_response(client_socket_id, exception=e)

    def on_get_all_private_room_data(self, data: Dict[str, str] | None = None) -> None: 
        ## TODO should have authorization ##
        client_socket_id: str = request.sid # type: ignore
        try:
            all_private_room_data: str = json.dumps(RedisControllerInstance.get_all_private_room_data())
            self.emit(RoomEmitConst.RecAllPrivateRoomData, data=all_private_room_data, room=client_socket_id)
        except Exception as e:
            print(traceback.print_exc())
            self.__send_caught_exception_response(client_socket_id, exception=e)

    ## 'PRIVATE' METHODS AND HELPERS ##
    ## action helpers ##
    def __join_room_and_emit(self, emit_event: Literal[RoomEmitConst.JoinGenRoomSuccess, RoomEmitConst.JoinPrivateRoomSuccess], client_socket_id: str, room_name: str, name_space: str = "/") -> None:
        join_room(room=room_name, sid=client_socket_id, namespace=name_space)
        updated_room_data: ClientRoomData = {
            "room_name": room_name,
            "client_socket_id": client_socket_id,
            "user_name": "anonymous"  ## TODO user_name(s) will be implemented later ##
        }
        self.emit(emit_event, data=updated_room_data, room=client_socket_id)
    
    def __leave_room_and_emit (self, emit_event: Literal[RoomEmitConst.LeaveGenRoomSuccess, RoomEmitConst.LeavePrivateRoomSuccess], client_socket_id: str, room_name: str, name_space: str = "/") -> None:
        leave_room(room=room_name, sid=client_socket_id, namespace=name_space)
        updated_room_data: ClientRoomData = {
            "room_name": room_name,
            "client_socket_id": client_socket_id,
            "user_name": "anonymous"  ## TODO user_name(s) will be implemented later ##
        }
        self.emit(emit_event, data=updated_room_data, room=client_socket_id)

    ## validators for sent data ## 
    def __validate_message_data(self, message_data: MessageData) -> List[str]:
        input_errors: List[str] = []
        
        if not message_data["room_name"]: input_errors.append("No room name sent")
        if not message_data["message_str"]: input_errors.append("No message string sent")

        return input_errors

    def __validate_join_room_data(self, room_data: ClientRoomData) -> List[str]:
        input_errors: List[str] = []

        if not room_data["room_name"]: input_errors.append("No room name sent")
        ## will add as expands ##
        return input_errors
    ## error responses ##
    
    def _send_error_response(self, emit_message: ErrorEmitLiteral, to: str,  error_messages: List[str], exception: Exception | None) -> None:
        if exception:
            string_exception: str = str(exception)
            error_data: Dict[str, List[str]] = { "error_messages": [ string_exception ]}
            self.emit(emit_message, data=error_data, room=to)
        else:
            error_data: Dict[str, List[str]] = { "error_messages": error_messages }
            self.emit(emit_message, data=error_data, room=to)

class SocketIOInstance: 
    def __init__(self, app) -> None:
        self.socketio = SocketIO(app, cors_allowed_origins='*')
        self.app = app
    
    def run(self) -> "SocketIOInstance":
        self.socketio.on_namespace(SocketIODefaultNamespace("/"))
        self.socketio.on_namespace(SocketIOChatNamespace("/chats"))
        self.socketio.run(self.app)
        return self



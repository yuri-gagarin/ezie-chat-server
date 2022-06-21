from flask_socketio import SocketIO, join_room, leave_room, Namespace
from flask import request
from storage.redis_controller import RedisControllerInstance
from custom_types.socket_io_stubs import ClientData

"""
class SocketIOServer:
  redisInstance = RedisController()

  def __init__(self, app):
    self.socketio = SocketIO(app, cors_allowed_origins='*')
    self.app = app
  
  def connection(self) -> None:
    @self.socketio.on("connect")
    def handle_connection(data: str) -> None:
      client_info = { 'socket_id': request.sid, 'namespace': request.namespace, 'message': "You are now connected live" } # type: ignore
      self.redisInstance.add_connected_client_info(request.sid) # type: ignore
      self.socketio.emit("client connected", client_info)
      print("Client has connected")
      print("Number of connected clients is: " + str(self.redisInstance.get_number_of_connected_clients()))
    
    @self.socketio.on("disconnect")
    def handle_disconnection():
      print("Client has disconnected")
      self.redisInstance.remove_connected_client_info(request.sid) # type: ignore
      print("Number of connected clients is: " + str(self.redisInstance.get_number_of_connected_clients()))
  
  def room_handlers(self) -> None:
    @self.socketio.on("join-room")
    def join_room(client_user_data: ClientData) -> None:
      print("Joining a room")
      f = client_user_data["socket_id"]

  def message_listeners(self) -> None:
    @self.socketio.on("message")
    def handle_message(message_data: str) -> None:
      print('received message: ' + message_data)

  def run(self) -> 'SocketIOServer':
    self.connection()
    self.message_listeners()
    self.room_handlers()
    self.socketio.run(self.app)
    self.redisInstance.setup()
    return self
"""
class SocketIOChatNamespace(Namespace):
    def on_connect(self, data: ClientData) -> None:
        print("Connected to Room")
        print(data)

class SocketIODefaultNamespace(Namespace):

    def on_connect(self, data: str) -> None:
        client_info = { 'socket_id': request.sid, 'namespace': request.namespace, 'message': "You are now connected live" } # type: ignore
        RedisControllerInstance.add_connected_client_info(request.sid) # type: ignore
        self.socketio.emit("client connected", client_info)
        print("Client has connected")
        print("Number of connected clients is: " + str(RedisControllerInstance.get_number_of_connected_clients()))

    def on_disconnect(self) -> None:
        print("Client has disconnected")
        RedisControllerInstance.remove_connected_client_info(request.sid) # type: ignore
        print("Number of connected clients is: " + str(RedisControllerInstance.get_number_of_connected_clients()))
    
    def on_join_room(self, data: ClientData) -> None:
        print("Joining room")
        print(data)
        user_name = data["user_name"]
        sid = request.sid # type: ignore
        room_name: str = "room" + "_" + user_name + "_" + sid
        print(join_room(room_name, sid, "/"))
    

class SocketIOInstance: 
    def __init__(self, app) -> None:
        self.socketio = SocketIO(app, cors_allowed_origins='*', logger=True, engineio_logger=True)
        self.app = app
    
    def run(self) -> "SocketIOInstance":
        self.socketio.on_namespace(SocketIODefaultNamespace("/"))
        self.socketio.on_namespace(SocketIOChatNamespace("/chats"))
        self.socketio.run(self.app)
        return self



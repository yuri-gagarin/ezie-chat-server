from flask_socketio import SocketIO, join_room, leave_room
from flask import request
from storage.redis_controller import RedisController
from typing import Dict

class SocketIOServer:
  """
  SocketIOServer class
  """
  redisInstance = RedisController()

  def __init__(self, app):
    self.socketio = SocketIO(app, cors_allowed_origins='*')
    self.app = app
  
  def connection(self) -> None:
    """Connection handling"""
    @self.socketio.on("connect")
    def handle_connection(data: str) -> None:
      """send a welcome message"""
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
    def join_room(data: Dict[str, str]) -> None:
      print("Joining a room")
      print(data)
      self.socketio.

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
from flask_socketio import SocketIO

"""
Provides some arithmetic functions
"""
class SocketIOServer:
  def __init__(self, app):
    self.socketio = SocketIO(app, cors_allowed_origins='*', logger=True,  engineio_logger=True)
    self.app = app
  
  def connection(self) -> None:
    """Connection handling"""
    @self.socketio.on("connection")
    def handle_connection():
      """send a welcome message"""
      print("Client connected")

  def message_listeners(self) -> None:
    @self.socketio.on("message")
    def handle_message(message_data: str) -> None:
      print('received message: ' + message_data)

  def run(self) -> 'SocketIOServer':
    self.socketio.run(self.app)
    self.connection()
    self.message_listeners()
    print("ran all")
    return self
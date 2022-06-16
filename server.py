from flask import Flask
from sockets.socketio import SocketIOServer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tochangelater'

socket_io_instance = None

print("running here")
if __name__ == "__main__":
  print("running")
  socket_io_instance = SocketIOServer(app)
  socket_io_instance.run()
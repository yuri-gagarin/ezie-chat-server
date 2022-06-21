from flask import Flask
from sockets.socketio import SocketIOInstance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tochangelater'

socket_io_instance = None

if __name__ == "__main__":
  print("running main server")
  socket_io_instance = SocketIOInstance(app)
  socket_io_instance.run()
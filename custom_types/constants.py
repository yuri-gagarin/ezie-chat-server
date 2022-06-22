import enum

class RoomEmitConst(str, enum.Enum):
    JoinGenRoomSuccess = "join_general_room_success"
    JoinPrivateRoomSuccess = "join_private_room_success"
    LeaveGenRoomSuccess = "leave_general_room_success"
    LeavePrivateRoomSuccess ="leave_private_room_success"

class ConnectionConst(str, enum.Enum):
    NewClientConnected = "new_client_connected"
    ClientDisconnected = "client_disconnected"
    ClientConnectionError = "client_connection_error"

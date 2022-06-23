import enum

class MessageEmitConst(str, enum.Enum):
    RecConvoMessages = "rec_convo_messages"

class RoomEmitConst(str, enum.Enum):
    JoinGenRoomSuccess = "join_general_room_success"
    JoinPrivateRoomSuccess = "join_private_room_success"
    LeaveGenRoomSuccess = "leave_general_room_success"
    LeavePrivateRoomSuccess ="leave_private_room_success"
    ##
    RecAllGeneralRoomData = "rec_all_general_room_data"
    RecAllPrivateRoomData = "rec_all_private_room_data"
    RecSpecificGeneralRoomData = "rec_specific_general_room_data"
    RecSpecificPrivateRoomData = "rec_specific_private_rooom_data"
    RecCompleteRoomData = "rec_complete_room_data"

class ErrorEmitConst(str, enum.Enum):
    CaughtExceptionError = "caught_exception_error"
    WrongDataError = "wrong_data_error"

class ConnectionConst(str, enum.Enum):
    NewClientConnected = "new_client_connected"
    ClientDisconnected = "client_disconnected"
    ClientConnectionError = "client_connection_error"


class RedisDBConstants(str, enum.Enum):
    ConnectedClientsSet = "CONNECTED_CLIENTS_SET"
    LiveGeneralRoomsSet = "LIVE_GENERAL_ROOMS_SET"
    LivePrivateRoomsSet = "LIVE_PRIVATE_ROOMS_SET"
    NamedRoomSet = "NAMED_ROOM_SET"
    MessagesList = "MESSAGES_LIST"


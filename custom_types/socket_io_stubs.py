from typing import List, Literal, Set, TypedDict
from .constants import ErrorEmitConst

ClientRoomData = TypedDict("GeneralRoomData", { "room_name": str, "client_socket_id": str, "user_name": str })

GenAllRoomInfo = TypedDict("GenPrivateRoomInfo", {
  "room_type": Literal["general", "private"],
  "total_rooms": int,
  "room_names": List[str]
})
SpecificRoomInfo = TypedDict("SpecificPrivateRoomInfo", {
  "active": bool,
  "room_type": Literal["general", "private"],
  "room_name": str,
  "connected_clients": List[str],
  "num_of_connected_clients": int
})

QueriedRoomData = TypedDict("QueriedRoomData", {
  "room_type": Literal["general", "private"],
  "room_name": str,
  "num_of_connected_clients": int,
  "connected_clients": List[str],
  "num_of_messages": int,
  "messages": List[str]
})



ClientData = TypedDict("ClientData", { "user_id": str, "socket_id": str, "user_name": str })
MessageData = TypedDict("MessageData", { "room_name": str, "sender_name": str, "client_socket_id": str, "message_str": str })
GetConvoMessagesData = TypedDict("GetConvoMessagesData", { "room_name": str, "start": int, "end": int })

## error responses ##
ErrorEmitLiteral = Literal[
  ErrorEmitConst.CaughtExceptionError, ErrorEmitConst.GeneralClientError, ErrorEmitConst.NewMessageError,
  ErrorEmitConst.RoomJoinError, ErrorEmitConst.RoomLeaveError, ErrorEmitConst.WrongDataError
]
GenErrorResponse = TypedDict("GenErrorResponse", { "socket_id": str, "error_messages": List[str] })


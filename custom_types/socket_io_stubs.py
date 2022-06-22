from typing import List, Literal, TypedDict

ClientRoomData = TypedDict("GeneralRoomData", { "room_name": str, "client_socket_id": str, "user_name": str })

GenPrivateRoomInfo = TypedDict("GenPrivateRoomInfo", {
  "total_rooms": int,
  "room_names": List[str]
})
SpecificPrivateRoomInfo = TypedDict("SpecificPrivateRoomInfo", {
  "active": bool,
  "room_name": str,
  "connected_clients": List[str],
  "num_of_connected_clients": int
})

QueriedRoomData = TypedDict("QueriedRoomData", {
  "room_type": Literal["general", "private"],
  "room_name": str,
  "num_of_connected_clients": int,
  "num_of_messages": int,
  "messages": List[str]
})



ClientData = TypedDict("ClientData", { "user_id": str, "socket_id": str, "user_name": str })
MessageData = TypedDict("MessageData", { "room_name": str, "sender_name": str, "socket_id": str, "message_str": str })

## error responses ##
GenErrorResponse = TypedDict("GenErrorResponse", { "socket_id": str, "error_messages": List[str] })


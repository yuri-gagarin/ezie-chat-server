from typing import List, Literal, TypedDict

PrivateRoomData = TypedDict("PrivateRoomData", { "room_name": str, "socket_id": str, "user_name": str })

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
MessageData = TypedDict("MessageData", { "room_name": str, "sender_name": str, "message_data": str })

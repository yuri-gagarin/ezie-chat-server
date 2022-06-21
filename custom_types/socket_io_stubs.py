from typing import TypedDict

ClientData = TypedDict("ClientData", { "user_id": str, "socket_id": str, "user_name": str })
MessageData = TypedDict("MessageData", { "room_name": str, "sender_name": str, "message_data": str })

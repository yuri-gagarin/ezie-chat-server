import redis

class RedisController: 
    redis_instance = redis.Redis(host="localhost", port=6379, db=0)
    connected_clients = "connected_clients"
   
    def setup(self) -> None: 
        print(self.redis_instance.delete(self.connected_clients))

    def add_connected_client_info(self, socket_id: str) -> None:
        self.redis_instance.lpush(self.connected_clients, socket_id)

    def remove_connected_client_info(self, socket_id: str) -> None:
        self.redis_instance.lrem(self.connected_clients, 0, socket_id)

    def get_number_of_connected_clients(self) -> int:
        return self.redis_instance.llen(self.connected_clients)



RedisControllerInstance = RedisController()
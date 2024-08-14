import gzip
from jwt_multi_workers.redis_server_conf import custom_redis
import redis
def compress(data:str)->bytes:
    print("commpress this >", data)
    return gzip.compress(data.encode("utf-8"))

def decompress(data:bytes)->str:
    return gzip.decompress(data).decode("utf-8")


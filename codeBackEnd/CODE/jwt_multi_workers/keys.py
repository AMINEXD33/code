import redis
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidKey
import json
from jwcrypto import jwk
from jwcrypto.common import json_encode, json_decode
import time


class NotAredisObject(ValueError):
    """
    raised when the passed object is not a redis connection
    """

    def __init__(self):
        super().__init__("the passed object is not a redis connection object")


class Keys:
    # the value that will be set in redis
    __PUB_KEY_REFERENCE = "public_key"
    __PRI_KEY_REFERENCE = "private_key"

    def __init__(self, redis_instance: redis.StrictRedis):
        self.private_key = None
        self.public_key = None
        self.redis_instance = redis_instance
        self.lock_key = "xhso24lf//afgs"

    def to_jsondef(self):
        """
        serialize the key pair into json
        return : dict {json, json}
        """
        if self.private_key is not None and self.public_key is not None:
            return json.dumps(
                {
                    "private_key": self.private_key.export(),
                    "public_key": self.private_key.export_public(),
                }
            )

    def generate_new_pairs(self, rsa_key_size=2048):
        """
        a function that generates a key pair using
        RSA
        @Return: dict {JWK_object, JWK_object}
        """
        private_key = jwk.JWK.generate(kty="RSA", size=2048)
        public_key = jwk.JWK()
        public_key.import_key(**json_decode(private_key.export_public()))
        return {"private_key": private_key, "public_key": public_key}

    def acquire_lock(self, timeout=100, retry=0.05):
        """
        this function acquires a lock for a transaction in redis
        """
        while not self.redis_instance.set(self.lock_key, "locked", nx=True, ex=timeout):
            time.sleep(retry)  # Retry every 50ms

    def release_lock(self):
        """
        this function releases the lock in redis
        """
        self.redis_instance.delete(self.lock_key)

    def set_pair_into_redis(self, public_key: jwk.JWK, private_key: jwk.JWK):
        """
        transforms the keys into json ,and update the redis db, ofc
        using a simple loc to prevent any Race condition
        @public_key: the public key JWK obj
        @private_key: the private key JWK obj
        """
        public_key_exported = public_key.export_public()
        private_key_exported = private_key.export()
        # try and update the two keys in one transaction
        with self.redis_instance.pipeline() as pip:
            try:
                self.acquire_lock()
                # start transaction
                pip.multi()
                # update keys
                self.redis_instance.set(Keys.__PRI_KEY_REFERENCE, private_key_exported)
                self.redis_instance.set(Keys.__PUB_KEY_REFERENCE, public_key_exported)
                # execute the transaction
                pip.execute()
                # print("redis are updated !")
            except redis.exceptions.RedisError as e:
                print(f"error while updating keys: {e}")
            finally:
                self.release_lock()

    def remove_pair(self):
        """
        removes the key pair from redis db using a transaction
        """
        with self.redis_instance.pipeline() as pip:
            try:
                # start transaction
                pip.multi()
                # update keys
                self.redis_instance.delete(Keys.__PRI_KEY_REFERENCE)
                self.redis_instance.delete(Keys.__PUB_KEY_REFERENCE)
                # execute the transaction
                pip.execute()
            except redis.exceptions.RedisError as e:
                print(f"error while deleting keys: {e}")

    def get_pair(self):
        """
        get the key pair from redis
        return: dict {dict, dict}
        """
        pri_fromdb = self.redis_instance.get(Keys.__PRI_KEY_REFERENCE)
        pub_fromdb = self.redis_instance.get(Keys.__PUB_KEY_REFERENCE)
        # only if the two keys exist in redis
        if pri_fromdb is not None and pri_fromdb is not None:
            # load both keys
            pri_fromdb = json.loads(pri_fromdb)
            pub_fromdb = json.loads(pub_fromdb)
            return {"private_key": pri_fromdb, "public_key": pub_fromdb}
        print("didn't expect None! line 101, keys.py")
        return None

    def from_json(self, private_key, public_key):
        """
        from a json load the key pair into the instance
        @Return: JWK <object>
        """
        # load both keys
        self.private_key = jwk.JWK(**private_key)
        self.public_key = jwk.JWK(**public_key)
        # print("pair loaded from json !")

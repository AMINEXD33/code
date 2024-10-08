import datetime
from datetime import timedelta
import json
import hashlib
from logs_util.log_core import LogCore
import time

log = LogCore("token_manager.py", False)


class Token_manager:

    __CALLS_TO_CHANGE_KEYS = 10000  #

    __CALLS = 0
    __EXPIRED_AFTER = 15  # min
    __USE_CACHING = True  # cache the tokens
    __BLACK_LIST_NAME = "bllist"  # the name of the black hash set in redis
    __CACHING_LIST_NAME = "tkcach"  # the name of the caching hash set in redis

    # class attr
    __PROVIDER = "code"

    def __init__(self, jwt_impl_reference):
        self.jwt_impl = jwt_impl_reference
        self.lock_key = "blacklist_lock/zd14sfd"
        self.lock_key2 = "caching_lock/afafgaf"
        self.lock_count = "countafagagaga"

    def to_sha_256(self, jwt_token: str):
        """
        hash jwt_token to an sha256
        """
        try:
            hashed = hashlib.sha256(jwt_token.encode("utf-8")).hexdigest()
            return hashed
        except Exception as e:
            log.log_exception("hashing error " + e)
            return None

    """token configuration methods"""

    def configure_token(self, token: dict):
        """
        this function get's a token , and configures it based on the
        attributes of the class
        """
        # calculate expiration data
        current_date = datetime.datetime.now()
        expiration_date = current_date + timedelta(
            minutes=Token_manager.__EXPIRED_AFTER
        )  ### REFACTOR TO DAYS !!!!
        expiration_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")

        # TO DO , add if the user is admin

        # attach the new values
        token["provider"] = Token_manager.__PROVIDER
        token["expiration_date"] = expiration_date
        # we return the token and it's expiration date
        return token, expiration_date

    def make_configured_token(self, claims: dict):
        """
        this function takes the claims configures them then encrypt them
        using the jwt_impl.make_token function
        Return: encrypted_token(str), expiration_date(str)
        """
        # check count calls
        if Token_manager.__CALLS >= Token_manager.__CALLS_TO_CHANGE_KEYS:
            self.safe_reload()  # reset the encryption keys , cach set , balack list
            Token_manager.__CALLS = 0  # reset calls

        configured_claims, expiration_date = self.configure_token(claims)
        encrypted_token = self.jwt_impl.make_token(**configured_claims)
        Token_manager.__CALLS += 1
        # after making the token , we can cach it
        return encrypted_token, expiration_date

    """locks methods"""

    def acquire_lock(self, lock_number, timeout=100, retry=0.05):
        """
        this function acquires a lock for a transaction in redis
        the lock_number specifies if the function should acquire
        the lock for the blacklist(1) or caching(2)
        """
        lock = None
        if lock_number == 1:
            lock = self.lock_key
        elif lock_number == 2:
            lock = self.lock_key2
        else:
            lock = self.lock_count
        while not self.jwt_impl.Redis.set(lock, "locked", nx=True, ex=timeout):
            time.sleep(retry)  # Retry every 50ms

    def release_lock(self, lock_number):
        """
        this function releases the lock in redis
        the lock_number specifies if the function should release
        the lock for the blacklist(1) or caching(2)
        """
        lock = None
        if lock_number == 1:
            lock = self.lock_key
        else:
            lock = self.lock_key2
        self.jwt_impl.Redis.delete(lock)

    """blacklist methods"""

    def add_to_blacklist(self, token: str):
        """
        this function hashes the token and adds it to the blacklist
        """

        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.hset(
                    Token_manager.__BLACK_LIST_NAME, self.to_sha_256(token), ""
                )
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(1)

    def remove_from_blacklist(self, token: str):
        """
        this function removes a token from the black list  in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.hdel(
                    Token_manager.__BLACK_LIST_NAME, self.to_sha_256(token)
                )
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(1)

    def is_black_listed(self, token: str):
        """
        this function checks if a token is black listed
        return : true or false
        """
        token = self.jwt_impl.Redis.hget(
            Token_manager.__BLACK_LIST_NAME, self.to_sha_256(token)
        )
        # sinse we've used "" for the value of the key, we can't compair using == since it will always
        # return False
        if token != None:
            return True
        return False

    def reset_black_list(self):
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.delete(Token_manager.__BLACK_LIST_NAME)
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(1)

    """caching methods"""

    def cash_token(self, username: str, data: dict):
        """
        this function cahches some dict in a locked transaction
        """
        jsonify_dict = json.dumps(data)
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.hset(
                    Token_manager.__CACHING_LIST_NAME, username, jsonify_dict
                )
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(2)

    def uncash_token(self, username: str):
        """
        this function removes a cached token in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.hdel(Token_manager.__CACHING_LIST_NAME, username)
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(2)

    def is_cached(self, username: str):
        """
        this function checks if a token is cached or not
        Return: a dict or false
        """
        cached = self.jwt_impl.Redis.hget(Token_manager.__CACHING_LIST_NAME, username)
        try:
            if cached:
                return json.loads(cached)
            else:
                return False
        except:
            return False

    def reset_cach(self):
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.delete(Token_manager.__CACHING_LIST_NAME)
                pip.execute()
            except Exception as e:
                log.log_exception(e)
            finally:
                self.release_lock(2)

    """token expiration methods"""

    def figure_token(self, username: str, password: str, token: str):
        key = username + password
        decrypted_tok = self.jwt_impl.decr_token(token)
        current_date = datetime.datetime.now()
        if current_date >= decrypted_tok["expiration_date"]:
            # this token is not valid anymore , we can black list it
            self.add_to_blacklist(token)
            return False
        # still a valid token
        return True

    """on calls limit reached"""

    def safe_reload(self):
        try:
            self.reset_black_list()
            self.reset_cach()
            self.jwt_impl.keys.remove_pair()
            self.jwt_impl.sync_keys()
        except Exception as e:
            log.log_exception("safe reload error " + e)

    """abstraction to validate the token"""

    def abstract_token_validation(self, token: str):
        """
        this function will validate the giving token , by checking the blacklist
        and then try and decrypt it, and finally checking the expiration date
        Return: if the token is good (decrepted token), unvalid token (False)
        """
        # check if token is black listed
        if self.is_black_listed(token):
            return False
        # decrypt token
        dec_tok = None
        try:
            dec_tok = json.loads(self.jwt_impl.decr_token(token).claims)
        except:
            log.log_exception("can't decrept")
            return False
        # check if token is expired
        expiration_date_str = dec_tok["expiration_date"]
        current_date = datetime.datetime.now()
        expiration_date_obj = None
        try:
            expiration_date_obj = datetime.datetime.strptime(
                expiration_date_str, "%Y/%m/%d %H:%M:%S"
            )
        except:
            try:
                expiration_date_obj = datetime.datetime.strptime(
                    expiration_date_str, "%Y-%m-%d %H:%M:%S"
                )
            except:
                log.log_exception("WTF IS THAT DATE")
                return False

        if current_date >= expiration_date_obj:
            self.add_to_blacklist(token)
            log.log_exception("expired tok")
            return False

        return dec_tok

    def abstract_token_validation_get_reqs(self, username: str):
        """
        this function is meant to be used in the context of an authentication request , when the user send
        a username/email and a password, it checks if a token is cached , if so it will check the validity of
        it , if it's valid it will return the token
        return: if valid (token, expired_date)  , if not valid (False, None)
        """
        # check if the token is cached
        data = self.is_cached(username)
        if data == False:
            return (False, None)
        cached = data.get("JWT")
        if not cached:
            # not cached
            return (False, None)
        # if it's cached it need not to be blacklisted
        if self.is_black_listed(cached):
            self.uncash_token(username)
            return (False, None)
        dec_tok = None
        try:
            dec_tok = json.loads(self.jwt_impl.decr_token(cached).claims)
        except:
            return (False, None)
        expiration_date = dec_tok["expiration_date"]
        # is the token valid
        current_datetime = datetime.datetime.now()
        expiration_date_parsed = datetime.datetime.strptime(
            expiration_date, "%Y-%m-%d %H:%M:%S"
        )
        if current_datetime >= expiration_date_parsed:
            self.uncash_token(username)
            self.remove_from_blacklist(cached)
            return (False, None)
        # the token then must be valid
        return (data, expiration_date)

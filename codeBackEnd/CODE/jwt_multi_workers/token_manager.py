import datetime
from datetime import timedelta


class Token_manager:

    __CALLS_TO_CHANGE_KEYS = 5  #

    __CALLS = 0
    __EXPIRED_AFTER = 1  # days
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

    """token configuration methods"""

    def configure_token(self, token: dict):
        """
        this function get's a token , and configures it based on the
        attributes of the class
        """
        # calculate expiration data
        current_date = datetime.datetime.now()
        expiration_date = current_date + timedelta(days=Token_manager.__EXPIRED_AFTER)
        expiration_date = expiration_date.strftime("%Y/%m/%d %H:%M:%S")

        # TO DO , add if the user is admin

        # attach the new values
        token["provider"] = Token_manager.__PROVIDER
        token["expitation_date"] = expiration_date

        # we return the token and it's expiration date
        return token, expiration_date

    def make_configured_token(self, username: str, password: str, claims: dict):
        """
        this function takes the claims configures them then encrypt them
        using the jwt_impl.make_token function
        Return: encrypted_token(str), expiration_date(str)
        """
        # check count calls
        print(Token_manager.__CALLS)

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

    def add_to_blacklist(self, token):
        """
        this function black lists a token in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.hset(Token_manager.__BLACK_LIST_NAME, token, "")
                pip.execute()
                print("added tp black list")
            except:
                pass
            finally:
                self.release_lock(1)

    def remove_from_blacklist(self, token):
        """
        this function removes a token from the black list  in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.hdel(Token_manager.__BLACK_LIST_NAME, token)
                pip.execute()
                print("removed black list")
            except:
                pass
            finally:
                self.release_lock(1)

    def is_black_listed(self, token):
        """
        this function checks if a token is black listed
        return : true or false
        """
        token = self.jwt_impl.Redis.hget(Token_manager.__BLACK_LIST_NAME, token)
        if token:
            return True
        return False

    def reset_black_list(self):
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(1)
                pip.multi()
                self.jwt_impl.Redis.delete(Token_manager.__BLACK_LIST_NAME)
                pip.execute()
                print("black list reseted")
            except:
                pass
            finally:
                self.release_lock(1)

    """caching methods"""

    def cash_token(self, username: str, password: str, token: str):
        """
        this function cahches a token in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.hset(
                    Token_manager.__CACHING_LIST_NAME, username + password, token
                )
                pip.execute()
                print("cached successfully")
            except:
                pass
            finally:
                self.release_lock(2)

    def uncash_token(self, username: str, password: str, token: str):
        """
        this function removes a cached token in a locked transaction
        """
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.hdel(
                    Token_manager.__CACHING_LIST_NAME, username + password, token
                )
                pip.execute()
                print("unchached successfully")
            except:
                pass
            finally:
                self.release_lock(2)

    def is_cached(self, username: str, password: str):
        """
        this function checks if a token is cached or not
        Return: the token  or false
        """
        cached = self.jwt_impl.Redis.hget(
            Token_manager.__CACHING_LIST_NAME, username + password
        )
        if cached:
            return cached
        else:
            return False

    def reset_cach(self):
        with self.jwt_impl.Redis.pipeline() as pip:
            try:
                self.acquire_lock(2)
                pip.multi()
                self.jwt_impl.Redis.delete(Token_manager.__CACHING_LIST_NAME)
                pip.execute()
                print("reseted cach")
            except:
                pass
            finally:
                self.release_lock(2)

    """token expiration methods"""

    def figure_token(self, username: str, password: str, token: str):
        key = username + password
        decrypted_tok = self.jwt_impl.decr_token(token)
        current_date = datetime.datetime.now()
        if current_date >= decrypted_tok["expitation_date"]:
            # this token is not valid anymore , we can black list it
            self.add_to_blacklist(token)
            print("figure_token")
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
            print("safe reload done")
        except Exception as e:
            print("safe reload error", e)

    """abstraction to validate the token"""
    def abstract_token_validation(self, username:str, password:str, token:str, expiration_date:str):
        """
        this function validate if a token is a valid one or not, it will check if it's black listed,
        if not it will check the expiration date, and cach the token if the __USE_CACHING is true
        Return: if the token is valid (True), if not (False)
        """
        # check if token is black listed
        if self.is_black_listed(token):
            print("token found in black list")
            return (False)
        # check if the token is valid
        current_datetime = datetime.datetime.now()
        expiration_date_parsed = datetime.datetime.strptime(expiration_date, "%Y/%m/%d %H:%M:%S")
        if current_datetime >= expiration_date_parsed:
            # add to black list
            self.add_to_blacklist(token)
            print("black listing token")
            # token expired
            return (False)
        # if no caching allowed then return true, sinse the token is valid
        if not Token_manager.__USE_CACHING:
            return (True)
        # cach token
        self.cash_token(username, password, token)
        print("cached token")
        return (True)


        
        
        

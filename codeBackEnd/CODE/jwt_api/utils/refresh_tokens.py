
from hashlib import sha384
import random, os
import datetime, json
from datetime import timedelta
from django.utils import timezone
class Refresh_tokens_manager:
    __EXPERATION_RANGE = 3 # days
    __CACHE_TOKENS = True
    __LOCK_NAME = "RFT_LOCK"
    @staticmethod
    def rand_word():
        """
        this is a helper function that randomly generates a word
        of some random size from 150, 300 , adn each char is picked
        randomaly
        Return: the generated word
        """
        word_length = random.choice(range(150, 300))
        word = ""
        for x in range(word_length):
            word += chr(random.choice(range(48, 122)))
        return word
    @staticmethod
    def gen_refresh_tok():
        """
        using a randomy generated word this function will also
        generate some random bytes, and hash the randomly generated word
        and combined them both and rehash them to get a token
        Return: token
        """
        random_word = Refresh_tokens_manager.rand_word()
        token = ""
        random_bytes = os.urandom(32)
        mask = sha384(random_word.encode("utf-8")).hexdigest()
        combined = mask.encode("utf-8") + random_bytes
        final_token = sha384(combined).hexdigest()
        return(final_token)

    @staticmethod
    def create_new_refresh_token():
        """
        this function get's a new token, and set an expiration date for it
        based on the configured value in the class
        Return: token, expiration_date_isonformat
        """
        token = Refresh_tokens_manager.gen_refresh_tok()
        exp_date = datetime.datetime.now() + timedelta(minutes=Refresh_tokens_manager.__EXPERATION_RANGE)
        aware_object = timezone.make_aware(exp_date)
        return token, exp_date.isoformat(), aware_object
    
    @staticmethod
    def cache_refresh_token(redis_conn_instance, token, exp_date, first_requester_ip):
        """
        this function caches a refresh token, with it's values as json
        """
        try:
            value = {"exp_date":exp_date, "first_requester_ip":first_requester_ip}
            redis_conn_instance.set(token, json.dumps(value))
            return True
        except:
            return False

    def acquire_lock(redis_conn_instance, timeout=100, retry=0.05):
        """
        acquire a lock for a transaction
        """
        lock = Refresh_tokens_manager.__LOCK_NAME
        while not redis_conn_instance.set(lock, "locked", nx=True, ex=timeout):
            time.sleep(retry)  # Retry every 50ms

    def release_lock(redis_conn_instance):
        """
        release the lock after a transaction
        """
        lock = Refresh_tokens_manager.__LOCK_NAME
        redis_conn_instance.delete(lock)

    @staticmethod
    def remove_refresh_token_from_cach(redis_conn_instance,token):
        """
        this function removes a cached refresh_token
        """
        with redis_conn_instance.pipeline() as pip:
            try:
                Refresh_tokens_manager.acquire_lock(redis_conn_instance)
                pip.multi()
                redis_conn_instance.delete(token)
                pip.execute()
                print("refresh token removed")
            except:
                pass
            finally:
                Refresh_tokens_manager.release_lock(redis_conn_instance)

    @staticmethod
    def check_cached_refresh_token(Redis_conn,token:str, token_isonformate_expdate):
        """
        this function checks if the a refresh token is cached, if so it checks
        that it's not expired , then the requester ip, if the requester ip is not 
        the same as the one cached
        """
        
        current_date = timezone.make_aware(datetime.datetime.now())
        print("TAHAT TYPE = ", type(token_isonformate_expdate))
        loaded_ison_format = token_isonformate_expdate
        if type(loaded_ison_format) == type(""):
            loaded_ison_format = datetime.datetime.fromisoformat(token_isonformate_expdate)

        if current_date > loaded_ison_format:
            Refresh_tokens_manager.remove_refresh_token_from_cach(Redis_conn, token)
            print("expired refrech token")
            return False
        return True



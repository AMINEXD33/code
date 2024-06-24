import datetime
from datetime import timedelta
import logging
import threading
from jwt_impl import JWT_IMP
import json
import datetime
from datetime import timedelta
import time

class some:
    def current_time(self):
        curr = datetime.datetime.now()
        day_ = curr.strftime("%d")
        min_ = curr.strftime("%M")
        sec_ = curr.strftime("%S")
        return(int(day_), int(min_), int(sec_))
    def await_time(self, time_at: datetime.timedelta, callBack):
            
            while True:
                day_, min_, sec_ = self.current_time()
                current_ = timedelta(days=day_, minutes=min_, seconds=sec_)
                time.sleep(0.3)  # import time
                print(current_,    time_at)
                if current_ >= time_at:
                    # time reached
                    print("IT'S TIME")
                    with open("trash.txt", "a") as file:

                        file.write(callBack())
                    break
    def return_public_pricate_json(self):
        """
        just return the private and public keys json
        """
        
        return ("test")

    def driver_function_(self):
        """
        this function is meant to execute the await_time function
        """
        day_, min_, sec_ = self.current_time()
        print("passed:", day_, min_, sec_)
        target_time = timedelta(days=day_, minutes=min_, seconds=sec_)+timedelta(seconds=4)
        self.await_time(target_time, self.return_public_pricate_json)

    def in_other_thread(self):
        """
        to not interfear with any running code, we can just run this
        process in an other thread
        """        
        thread__ = threading.Thread(target=self.driver_function_)
        thread__.start()
        thread__.join()
ss = some()
ss.in_other_thread()
#current_time()
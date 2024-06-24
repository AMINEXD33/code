

import logging
import threading
from jwt_impl import JWT_IMP
import json
import datetime
from datetime import timedelta
import time



# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

class ThreadRoutine:
    def __init__(self, id):
        self.jwt_reference = JWT_IMP()
        self.id = id

    def check_if_two_pairs_are_equal_same_instance(self):
        pair = self.jwt_reference.keys.get_pair()
        private_dump = json.dumps(pair["private_key"])
        public_dump = json.dumps(pair["public_key"])
        logging.debug(f"Thread {self.id}: Checking if keys are equal")
        if self.jwt_reference.keys.public_key.export_public().replace(" ", "") == public_dump.replace(" ", "") and \
           self.jwt_reference.keys.private_key.export().replace(" ", "") == private_dump.replace(" ", ""):
            logging.debug(f"Thread {self.id}: Keys are equal")
        else:
            logging.debug(f"Thread {self.id}: Keys are not equal")
    """
    got an idea to log the keys when a specific time is met, to see 
    if all workers synced the keys correctly 
    """
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
                    with open("at_time.txt", "a") as file:
                        content = f"Thread-{self.id}---\n{callBack()}\n---------"
                        file.write(content)
                    break
    def return_public_pricate_json(self):
        """
        just return the private and public keys json
        """
        json_private = "private::>"+self.jwt_reference.keys.private_key.export()
        json_public  = "public ::>"+self.jwt_reference.keys.public_key.export_public()
        return (str(json_private)+"\n"+str(json_public))

    def driver_function_(self):
        """
        this function is meant to execute the await_time function
        """
        day_, min_, sec_ = self.current_time()
        print("passed:", day_, min_, sec_)
        target_time = timedelta(days=day_, minutes=min_, seconds=sec_)+timedelta(seconds=15)
        self.await_time(target_time, self.return_public_pricate_json)

    def in_other_thread(self):
        """
        to not interfear with any running code, we can just run this
        process in an other thread
        """        
        thread__ = threading.Thread(target=self.driver_function_)
        thread__.start()
        thread__.join()
    """"""
    
    def refresh_keys_same_instance(self):
        pairs = self.jwt_reference.keys.generate_new_pairs()
        self.jwt_reference.SubPubManager.update_and_publish(
            pairs["private_key"],
            pairs["public_key"]
        )
        logging.debug(f"Thread {self.id}: Refreshed keys and published updates")

    def routine1(self):
        logging.debug(f"Thread {self.id}: Starting routine 1")
        self.refresh_keys_same_instance()
        self.check_if_two_pairs_are_equal_same_instance()
        logging.debug(f"Thread {self.id}: Completed routine 1")

    def routine3(self):
        self.refresh_keys_same_instance()
        self.in_other_thread()

    def routine2(self):
        logging.debug(f"Thread {self.id}: Starting routine 2")
        self.refresh_keys_same_instance()
        logging.debug(f"Thread {self.id}: Completed routine 2")
if __name__ == "__main__":
    test_threads_target = 48
    thread_routines = []
    
    # Create instances of ThreadRoutine
    for x in range(test_threads_target):
        thread_routines.append(ThreadRoutine(x))
    
    threads = []
    
    # Create threads with corresponding ThreadRoutine targets
    for x in range(test_threads_target):
        threads.append(
            threading.Thread(target=thread_routines[x].routine3(), name=f"thread-{x}")
        )
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
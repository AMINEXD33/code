bind = "192.168.1.9:4000"
workers = 5
threads = 3
timeout = 30
worker_class = (
    "gevent"  #'eventlet'  # Choose the worker type that suits your application
)
# accesslog = 'access.log'
# errorlog = 'error.log'
loglevel = "info"

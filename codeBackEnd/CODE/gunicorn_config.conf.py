bind = '0.0.0.0:8000'
workers = 5
threads = 3
timeout = 30
worker_class = 'gevent'#'eventlet'  # Choose the worker type that suits your application
# accesslog = 'access.log'
# errorlog = 'error.log'
loglevel = 'info'
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet'
bind = '127.0.0.1:8000'
proc_name = "faro_api"

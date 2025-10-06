import multiprocessing
bind = "0.0.0.0:8000"

# Vertical scaling knobs
workers = max(2, multiprocessing.cpu_count() * 2 + 1)   # start point
threads = 8                                             # adds concurrency without extra processes
worker_class = "gthread"                                # good general default for Django I/O mix
timeout = 60
graceful_timeout = 30
keepalive = 5

# Memory / restart hygiene
max_requests = 1000
max_requests_jitter = 200
preload_app = True                                      # faster forks, lower RSS once warmed

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Temp to avoid Docker overlayfs issues
worker_tmp_dir = "/dev/shm"

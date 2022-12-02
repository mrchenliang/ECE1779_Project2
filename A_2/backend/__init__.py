from flask import Flask
import threading
webapp = Flask(__name__)
memcache_pool = {
    "i-0ca59c2326be01a9b": None,
    "i-034ee52984dc9bd2e": None,
    "i-0972b8c8d8d577ec0": None,
    "i-07a760bbdad228a87": None,
    "i-067ee0ffdf31ca474": None,
    "i-033d4ce97a7e3f234": None,
    "i-0a7a70f7ed4da4cbc": None,
    "i-062be943d0df0ee8a": None
}
from backend import main
from backend.AWS_Log_operator import thread_stats

th = threading.Thread(target=thread_stats)
th.start()
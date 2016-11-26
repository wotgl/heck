import time
from threading import Thread
import requests

def get_data(vk_id, token):
    pass

for i in range(10):
    t = Thread(target=myfunc, args=(i,))
    t.start()
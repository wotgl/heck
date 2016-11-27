import requests
import json
import time
import re

access_token = 'bd0d455eaea280b948c6444b117a4bb7a5a5f348f7055897b4698b85b5241c1dc5c9ea18e92a28a8e2ed4'
owner_id = '37974828'
url = 'https://api.vk.com/method/wall.get?owner_id=-%s&filter=all&count=2&access_token=%s' % (owner_id, access_token)

r = requests.get(url)

data = json.loads(r.text)['response'][1:]
dataset = []
# print len(data)
for i in data:
    print(i['comments'])
    if i['comments']['count'] > 0:
        url = 'https://api.vk.com/method/wall.getComments?owner_id=-%s&post_id=%s&filter=all&count=100&access_token=%s' % (owner_id, i['id'], access_token)
        r = requests.get(url)
        _data = json.loads(r.text)['response'][1:]
        for j in _data:
            if j['text'] not in dataset:
                dataset.append(j['text'])
        time.sleep(1)
print(dataset)

f = open('spam.txt', 'w')
for i in dataset:
    # ptr = re.compile('\[id.*?\|.*?\]')
    i = re.sub('\[id.*?\|.*?\]', '', i)
    f.write(i + '\n')
f.close()
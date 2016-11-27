from django.shortcuts import render
from django.http import HttpResponse

import json
from models import *
import time
from threading import Thread
import requests
import random
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt




def _get_comments(vk_id, token, post_id):
    url = 'https://api.vk.com/method/wall.getComments?access_token=%s&owner_id=-%s&post_id=%s&count=100' % (token, vk_id, post_id)
    r = requests.get(url)
    time.sleep(0.5)
    return json.loads(r.text)

def get_data(community, vk_id, token):
    while True:
        url = 'https://api.vk.com/method/wall.get?access_token=%s&owner_id=-%s&count=100' % (token, vk_id)
        r = requests.get(url)
        data = json.loads(r.text)
        try:
            data = data['response'][1:]
        except Exception as e:
            print e
            print data
            return
        for i in data:
            post = ''
            try:
                post = Post.objects.get(pid=i['id'])
            except Post.DoesNotExist as e:
                post = Post.objects.create(
                    community=community, pid=i['id'], text=i['text'], comments=i['comments']['count'])
            if i['comments']['count'] == '0':
                continue
            # get_comments
            comments = _get_comments(vk_id, token, i['id'])
            for j in comments['response'][1:]:
                try:
                    Comment.objects.get(cid=j['cid'])
                except Comment.DoesNotExist as e:
                    uid = j['uid']
                    user = ''
                    try:
                        user = VkUser.objects.get(uid=uid)
                    except VkUser.DoesNotExist as e:
                        user = VkUser.objects.create(uid=uid)
                    comment = Comment.objects.create(cid=j['cid'], post=post, text=j['text'], user=user)
        time.sleep(5)





# Create your views here.

def json_resp(data):
    return HttpResponse(json.dumps(data), content_type="application/json")


def error():
    data = {'result': 'error'}
    return json_resp(data)


def set_access_token(request):
    token = request.GET.get('token', None)
    vk_id = request.GET.get('owner_id', None)

    if token == None or vk_id == None:
        token = "02dd253a350b2b6aff570f118db4a44d9a788486980329f286781e06a803d5acda2f80506571efbb808dc"
        vk_id = '133948748'

    community = Community.objects.get_or_create(vk_id=vk_id, token=token)[0]
    t = Thread(target=get_data, args=(community, vk_id, token,))
    t.start()
    # get_data(vk_id, token)
    response_data = {}
    response_data['result'] = 'Ok'
    return json_resp(response_data)


def get_comments(request):
    group_id = request.GET.get('group_id', None)

    if group_id == None:
        return error()

    try:
        c = Community.objects.get(vk_id=group_id)
    except Community.DoesNotExist as e:
        return error()

    p = Post.objects.filter(community=c)
    result = []
    if len(p) == 0:
        return json_resp({'result': result})

    for i in p:
        cm = Comment.objects.filter(post=i)
        if len(cm) == 0:
            return json_resp({'result': result})
        for k in cm:
            result.append({'text': k.text, 'cid': k.cid})
    return json_resp(result)


def redirect(request):
    try:
        code = request.GET.get('code', None)
        group_id = request.GET.get('group_id', None)
    except Exception as e:
        return error()

    community = ''
    try:
        community = Community.objects.get(vk_id=group_id)
        return error()
    except Exception as e:
        pass

    url = 'https://oauth.vk.com/access_token?client_id=5748766&client_secret=TKCRZDIecDW5F3TKy6yY&redirect_uri=https://reunited.tk/api/redirect/?group_id=%s&code=%s' % (group_id, code)
    r = requests.get(url)
    print r.text
    token = ''
    try:
        token = json.loads(r.text)['access_token_' + group_id]
    except Exception as e:
        token = json.loads(r.text)['access_token']
    print token
    community = Community.objects.create(vk_id=group_id, token=token)
    t = Thread(target=get_data, args=(community, group_id, token,))
    t.start()

    response_data = {}
    response_data['result'] = 'OK'
    return json_resp(response_data)


def get_comments_admin(request):
    group_id = request.GET.get('group_id', None)

    if group_id == None:
        return error()

    try:
        c = Community.objects.get(vk_id=group_id)
    except Community.DoesNotExist as e:
        return error()

    p = Post.objects.filter(community=c)
    result = []
    if len(p) == 0:
        return json_resp({'result': result})

    print 'posts length = ', len(p)
    for i in p:
        # print i
        cm = Comment.objects.filter(post=i)
        print 'comments length = ', len(cm)
        if len(cm) == 0:
            continue
            # return json_resp({'result': result})
        avatars = {}
        avatars_ids = ''
        for k in cm:
            avatars_ids += k.user.uid + ","
        url = 'https://api.vk.com/method/users.get?user_ids=%s&fields=photo_100' % (avatars_ids)
        print url
        r = requests.get(url)
        for k in json.loads(r.text)['response']:
            avatars[k['uid']] = k['photo_100']
        
        for k in cm:
            d = requests.get('http://127.0.0.1:5000/?data=' + k.text)
            result.append({'id': k.cid, 'text': k.text, 'score': d.text, 'uid': k.user.uid, 'pid': k.post.pid, 'photo': avatars[int(k.user.uid)]})

    newlist = sorted(result, key=lambda k: k['score'])
    return json_resp(result)


def check_group(request):
    group_id = request.GET.get('group_id', None)

    if group_id == None:
        return error()

    try:
        c = Community.objects.get(vk_id=group_id)
        response_data = {}
        response_data['result'] = 'OK'
        return json_resp(response_data)
    except Community.DoesNotExist as e:
        response_data = {}
        response_data['result'] = 'NOT OK'
        return json_resp(response_data)

def ban_user(request):
    group_id = request.GET.get('group_id', None)
    uid = request.GET.get('uid', None)

    c = ''
    user = ''
    try:
        c = Community.objects.get(vk_id=group_id)
    except Community.DoesNotExist as e:
        return error()

    try:
        user = VkUser.objects.get(uid=uid)
    except VkUser.DoesNotExist as e:
        return error()

    c.banned.add(user)

    url = 'https://api.vk.com/method/groups.banUser?reason=1&access_token=%s&group_id=-%s&user_id=%s' % (c.token, group_id, uid)
    r = requests.get(url)
    print r.text

    response_data = {}
    response_data['result'] = 'Ok'
    return json_resp(response_data)


@csrf_exempt
def fetch_result(request):
    print request.POST

    response_data = {}
    response_data['result'] = 'Ok'
    return json_resp(response_data)

from django.shortcuts import render
from django.http import HttpResponse

import json
from models import *
import time
from threading import Thread
import requests
import random
from django.http import HttpResponseRedirect



def _get_comments(vk_id, token, post_id):
    url = 'https://api.vk.com/method/wall.getComments?access_token=%s&owner_id=-%s&post_id=%s&count=10' % (token, vk_id, post_id)
    r = requests.get(url)
    return json.loads(r.text)

def get_data(community, vk_id, token):
    while True:
        url = 'https://api.vk.com/method/wall.get?access_token=%s&owner_id=-%s&count=10' % (token, vk_id)
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
                    comment = Comment.objects.create(cid=j['cid'], post=post, text=j['text'])
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
    owner_id = request.GET.get('owner_id', None)

    if owner_id == None:
        return error()

    try:
        c = Community.objects.get(vk_id=owner_id)
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
            result.append(k.text)
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

    for i in p:
        cm = Comment.objects.filter(post=i)
        if len(cm) == 0:
            return json_resp({'result': result})
        for k in cm:
            result.append({'id': k.cid, 'text': k.text, 'score': random.random()})
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
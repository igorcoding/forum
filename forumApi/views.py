import json
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import time

from forumApi.api import forum
from forumApi.api import user
from forumApi.api import thread
from forumApi.api import post
from forumApi.util.DataService import DataService
from forumApi.util.helpers import response_good, parse_get


@csrf_exempt
def index(request, entity, action):
    entity = {
        "forum": forum,
        "user": user,
        "thread": thread,
        "post": post
    }[entity]

    data_dict = json.loads(request.body, encoding='utf-8') if request.method == 'POST' else parse_get(request.GET)
    print data_dict

    func = getattr(entity, action)

    ds = DataService()
    result = func(ds, **data_dict)
    response = response_good(result)
    ds.close_all()

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')
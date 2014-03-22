import json
from django.http.response import HttpResponse
from django.shortcuts import render

from forumApi.api import forum
from forumApi.util.DataService import DataService


def index(request):
    data_service = DataService()
    db = data_service.db
    result = forum.details(db, forum='test_forum', related=['user'])
    return HttpResponse(json.dumps(result), content_type='application/json')
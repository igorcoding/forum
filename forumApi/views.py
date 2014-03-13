from django.http.response import HttpResponse
from django.shortcuts import render

import api
from forumApi.util.ForumDataService import ForumDataService

data_service = ForumDataService()


def index(request):
    query = """SELECT * FROM forum
                   INNER JOIN user ON forum.user_id = user.id
                   WHERE forum.short_name = '{0}'
                """\
                .format('test')

    res = data_service.query(query)
    row = res.fetch_row(how=1, maxrows=10)
    return HttpResponse("Hello!")
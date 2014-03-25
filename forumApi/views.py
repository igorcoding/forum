import json

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from api import user
from api import thread
from api import post
from api import forum
from api.util.DataService import DataService
from api.util.response_helpers import response_good, response_error


@csrf_exempt
def index(request, entity, action):
    entity = {
        "forum": forum,
        "user": user,
        "thread": thread,
        "post": post
    }[entity]

    data_dict = json.loads(request.body, encoding='utf-8') if request.method == 'POST' else request.GET.dict()
    print data_dict

    func = getattr(entity, action)

    ds = DataService()
    try:
        result = func(ds, **data_dict)
        response = response_good(result)
    except Exception as e:
        response = response_error(str(e))
    ds.close_all()

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')
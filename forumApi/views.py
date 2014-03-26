import json

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from api import api_executor


@csrf_exempt
def index(request, entity, action):
    data = json.loads(request.body, encoding='utf-8') if request.method == 'POST' else request.GET.dict()
    response = api_executor.execute(entity, action, data)

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')
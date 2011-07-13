from django.http import HttpResponse
import json

class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs['content_type'] = "application/json"
        super(JsonResponse, self).__init__(json.dumps(data), **kwargs)



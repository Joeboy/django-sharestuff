import json
import httplib
import base64

from django.http import HttpResponse
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings

from piston.emitters import Emitter


class RestError(Exception):
    """
    An exception for known, handled errors raised by RestHandler methods
    """
    def __init__(self, message, status_code=httplib.INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code

class HackyEmitter(Emitter):
    """
    A hack to use piston's base Emitter class - we only want construct(),
    which needs a couple of attrs set
    """
    anonymous = True

    def __init__(self, data, fields=None):
        self.data = data
        self.fields = fields
        self.typemapper = {}


def JsonResponse(data, status=httplib.OK, content_type='application/json'):
    """
    An HttpResponse that sends json
    """
    e = HackyEmitter(data)
    indent = settings.DEBUG and 4 or None
    return HttpResponse(json.dumps(e.construct(),
                                   cls=DateTimeAwareJSONEncoder,
                                   ensure_ascii=False, indent=indent),
                        status=status,
                        content_type=content_type)


class RestHandler(object):
    """
    Base Handler for api requests. Routes requests to the appropriate method
    according to the request method. Decodes data for POST/PUT requests.
    Json encodes data returned from methods

    """
    http_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @staticmethod
    def decode_base64_body(body):
        """
        This is kind of hacked together. Seems to work well enough but might
        need doing more properly at some point. Or hopefully will go away
        altogether if we manage to get browsers to send binary blobs.
        """
        bits = body.split(',')
        if len(bits) != 2:
            raise RestError("Couldn't decode body data", 400)
        try:
            return base64.decodestring(bits[1])
        except:
            raise RestError("Couldn't decode body data", 400)


    def decode_body(self, func):
        """
        Decorator that adds decoded body data  (ie POST data)to the handler
        function's signature
        """
        def _inner(request, *args, **kwargs):
            content_type = request.META['CONTENT_TYPE'].split(';')[0]
            print 'Content_type=%s' % content_type
            if content_type == 'application/json':
                try:
                    post_data = json.loads(request.raw_post_data)
                except ValueError:
                    raise RestError("Couldn't decode json data", httplib.BAD_REQUEST)
            elif content_type == "application/x-www-form-urlencoded":
                post_data = request.POST
            elif content_type == "multipart/form-data":
                post_data = request.POST
            elif request.is_ajax() and content_type == 'text/plain':
                post_data = self.decode_base64_body(request.raw_post_data)
            elif request.is_ajax() and content_type == 'application/xml':
                # Chrome seems really keen to send data as application/xml. I
                # think XHR.overrideMimeType isn't working. Hopefully this can
                # go away at some point
                post_data = self.decode_base64_body(request.raw_post_data)
            else:
                raise RestError("Unhandled content type: %s, post: %s" % (content_type, request.POST), httplib.BAD_REQUEST)

            result = func(request, post_data, *args, **kwargs)

            if not request.is_ajax() and content_type == "multipart/form-data":
                return (result, httplib.OK, 'text/html')
            else:
                return result
        return _inner


    def auth_required(self, func):
        """
        Decorator that refuses unauthorised requests
        """
        def _inner(request, *args, **kwargs):
            if request.user.is_anonymous():
                raise RestError("You must be logged in to use this resource", httplib.FORBIDDEN)
            return func(request, *args, **kwargs)
        return _inner


    def __init__(self, *args, **kwargs):
        """
        Build a map of handlers for request methods.
        """
        self.method_map = {}

        for m in self.http_methods:
            meth = getattr(self, m, None)
            if meth:
                if not getattr(meth, 'no_auth_required', False):
                    meth = self.auth_required(meth)
                if m in ('POST', 'PUT'):
                    self.method_map[m] = self.decode_body(meth)
                else:
                    self.method_map[m] = meth


    def __call__(self, request, *args, **kwargs):
        """
        Route the request to the appropriate method. Return the resulting
        data as a JsonResponse
        """
        meth = self.method_map.get(request.method)

        if meth is None:
            return JsonResponse({'success':False, 'error':'Not allowed (405)'},
                                status=httplib.METHOD_NOT_ALLOWED)

        try:
            raw = meth(request, *args, **kwargs)
        except RestError, e:
            return JsonResponse({'success':False, 'error':e.message},
                                 status=e.status_code)
        except Exception, e:
            if settings.DEBUG:
                raise
            else:
                return JsonResponse({'success':False,
                                     'error':"Sorry, there was an error " \
                                             "processing the request."},
                                    status=httplib.INTERNAL_SERVER_ERROR)

        # This is probably silly
        if isinstance(raw, tuple):
            if len(raw) == 2:
                (data, status, content_type) = raw[0], raw[1], 'application/json'
            elif len(raw) == 3:
                (data, status, content_type) = raw
        else:
            (data, status, content_type) = raw, httplib.OK, 'application/json'

        if type(data) == dict:
            data['success'] = True

#        if settings.DEBUG and not request.is_ajax() and not request.method == 'POST': content_type = 'text/plain' # Handy for debugging

        return JsonResponse(data, status, content_type)


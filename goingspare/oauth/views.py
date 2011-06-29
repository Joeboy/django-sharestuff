import oauth2
import httplib
from django.core.urlresolvers import reverse
from django.http import HttpResponse

oauth_server = oauth2.Server()

consumer = oauth2.Consumer('CONSUMER_KEY', 'CONSUMER_SECRET')

def request_token(request):
    print request.environ
    # create a request token
    url = request.build_absolute_uri()
    oauth_request = oauth2.Request.from_request('GET', url, headers=request.environ)
    print url, oauth_request

    token_field = oauth_request.get_parameter('oauth_token')
    token = self.data_store.lookup_token(token_type, token_field)
    if not token:
        raise OAuthError('Invalid %s token: %s' % (token_type, token_field))

    print token, token.to_string()

    return HttpResponse('ho')



def playpen(request):
#    print dir(request)
#    print type(request.META)
    parameters = {'oauth_callback': reverse('request-token-ready'),}
    oauth_request = oauth2.Request.from_consumer_and_token(consumer,
                                                           parameters=parameters,
                                                           http_url='http://localhost:8080'+reverse('request-token'))
    oauth_request.sign_request(oauth2.SignatureMethod_PLAINTEXT(), consumer, None)
    connection = httplib.HTTPConnection("localhost:8001")
    connection.request(oauth_request.method, reverse('request-token'), headers=oauth_request.to_header())
    print oauth_request.to_header()
    response = connection.getresponse()
#    print response.read()
    return HttpResponse('hi')
#    print oauth2.Token.from_string(response.read())




def request_token_ready(request):
    pass

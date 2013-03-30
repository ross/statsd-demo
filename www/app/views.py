# Create your views here.

from app.models import Employee
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django_statsd.clients import statsd
from urlparse import urlparse
import requests
import requests_futures.sessions


def index(request):

    q = int(request.GET.get('q', 0))
    statsd.incr('query', q)

    data = {'employees': Employee.objects.all()}
    return render_to_response('app/index.html', data,
                              RequestContext(request))


@cache_page(60 * 1)
def cached(request):
    # we'll only see the post-cache (page building) stats on the first call
    return index(request)


def request(request):
    with statsd.timer('requests.httpbin'):
        response = requests.get('http://httpbin.org/get')
    data = {'response': response.content}
    return render_to_response('app/request.html', data,
                              RequestContext(request))


class StatsSession(requests.Session):

    def request(self, method, url, *args, **kwargs):
        host = urlparse(url).netloc.replace('.', '_')
        key = 'requests.%s.%s' % (host, method)
        statsd.incr(key)
        with statsd.timer(key):
            return super(StatsSession, self).request(method, url, *args,
                                                     **kwargs)


stats_session = StatsSession()


def session(request):
    # we'll use the post
    response = stats_session.post('http://httpbin.org/post',
                                  {'key': 'value'})
    # call this twice just to have more interesting data
    stats_session.get('http://httpbin.org/get')
    stats_session.get('http://httpbin.org/get')
    data = {'response': response.content}
    return render_to_response('app/request.html', data,
                              RequestContext(request))


class StatsFuturesSession(requests_futures.sessions.FuturesSession):

    def request(self, method, url, *args, **kwargs):
        host = urlparse(url).netloc.replace('.', '_')
        key = 'requests.%s.%s' % (host, method)
        statsd.incr(key)
        with statsd.timer(key):
            return super(StatsFuturesSession, self).request(method, url,
                                                            *args, **kwargs)


stats_futures_session = StatsFuturesSession()


def async(request):
    # same as session, but async!
    future = stats_futures_session.post('http://httpbin.org/post',
                                        {'key': 'value'})
    future_1 = stats_futures_session.get('http://httpbin.org/get')
    future_2 = stats_futures_session.get('http://httpbin.org/get')
    # block on the result, if it's not already back
    with statsd.timer('requests_futures.wait'):
        # the junk
        future_1.result()
        future_2.result()
        # the one we care about
        response = future.result()
    data = {'response': response.content}
    return render_to_response('app/request.html', data,
                              RequestContext(request))

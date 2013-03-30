from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.views',
    url(r'^cached/$', 'cached', name='cached'),
    url(r'^request/$', 'request', name='request'),
    url(r'^session/$', 'session', name='session'),
    url(r'^async/$', 'async', name='async'),
    url(r'^$', 'index', name='index'),
)

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'publisher.views.index', name='publisher_index'),
    url(r'^post/$', 'publisher.views.post', name='publisher_post'),
    url(r'^authorize/(?P<code>\w+)/$', 'publisher.views.authorize', name='publisher_authorize'),
)
from django.conf.urls.defaults import patterns, include, url
from views import gallery, photo, api_photo


urlpatterns = patterns('',
    url(r'^api/photo/(?P<photo_id>[0-9]+)/download/$', api_photo, name='api_photo'),
    url(r'^photo/(?P<photo_id>[0-9]+)/$', photo, name='photo'),
    url(r'^$', gallery, name='gallery'),
   # url(r'^project/', include('project.foo.urls')),
)

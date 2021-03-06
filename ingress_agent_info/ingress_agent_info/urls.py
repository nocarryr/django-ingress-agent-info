from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'user_profile.views.index'), 
    url(r'^accounts/', include('user_profile.urls')), 
    url(r'^agent/', include('agent.urls')), 
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

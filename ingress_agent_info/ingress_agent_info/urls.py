from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ingress_agent_info.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/$', 'user_profile.views.home'), 
    url(r'^logout/$', 'user_profile.views.logout'), 
    url(r'^done/$', 'user_profile.views.done'), 
    url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'user_profile.views.ajax_auth',
        name='ajax-auth'),
    url('', include('social.apps.django_app.urls', namespace='social')), 
    url(r'^admin/', include(admin.site.urls)),
)

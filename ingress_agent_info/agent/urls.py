from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^info_form/$', 'agent.views.agent_info_form'), 
    url(r'^info_form/(?P<user_id>\d+)/$', 'agent.views.agent_info_form'), 
    url(r'^list/$', 'agent.views.agent_list'), 
)

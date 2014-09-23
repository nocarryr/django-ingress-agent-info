from django.conf.urls import patterns, url

urlpatterns = patterns('', 
    url(r'^login/$', 'user_profile.views.login_page'), 
    url(r'^login/post/$', 'user_profile.views.login_post'), 
    url(r'^logout/$', 'user_profile.views.logout'), 
    url(r'^logout/post/$', 'user_profile.views.logout_post'), 
    url(r'^logout/success/$', 'user_profile.views.logout_success'), 
    url(r'^oauth2callback', 'user_profile.views.auth_return'), 
)

import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import logout as auth_logout, login
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import strategy

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')
    
def build_context(extra):
    d = {
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
    }
    d.update(extra)
    return d
    
def render_template(template_name, req, cdict=None):
    if cdict is None:
        cdict = {}
    cdict = build_context(cdict)
    return render_to_response(template_name, 
                              cdict, 
                              context_instance=RequestContext(req))
    
def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('done')
    return render_template('user_profile/home.html', request)
    
@login_required
def done(request):
    """Login complete view, displays user data"""
    return render_template('user_profile/done.html', request, {'user': request.user})
    
    
@strategy('social:complete')
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            'oauth_token': request.REQUEST.get('access_token'),
            'oauth_token_secret': request.REQUEST.get('access_token_secret'),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get('access_token')
    else:
        raise HttpResponseBadRequest('Wrong backend type')
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {'id': user.id, 'username': user.username}
    return HttpResponse(json.dumps(data), mimetype='application/json')

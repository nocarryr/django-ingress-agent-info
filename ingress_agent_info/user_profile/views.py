from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse

#from user_profile.models import GPlusProfile
from user_profile import auth_handler

import logging
logger = logging.getLogger('custom')

def build_context(cdict=None, req=None):
    if cdict is None:
        cdict = {}
    cdict['G_CLIENT_ID'] = auth_handler.get_client_secrets()['web']['client_id']
    cdict['G_AUTH_URI'] = auth_handler.get_redirect_uri()
    cdict['G_SCOPE'] = auth_handler.SCOPE
    g_connected = False
    if req is not None and req.user.id is not None:
        d = cdict['G_CREDENTIALS'] = auth_handler.get_credentials(req)
        if d is not False:
            g_connected = True
            cdict['profile'] = d['user'].profile
        
    cdict['G_CONNECTED'] = g_connected
    return cdict
    
def render_template(template_name, req, cdict=None):
    cdict = build_context(cdict, req)
    return render_to_response(template_name, 
                              cdict, 
                              context_instance=RequestContext(req))
    

def index(req):
    if not req.user.is_authenticated():
        return redirect('/accounts/login')
    return render_template('index.html', req)

def login_page(req, next_page=None):
    if next_page is None:
        next_page = '/'
    user = authenticate(request=req)
    if user is not None:
        return redirect(next_page)
#    user = None
#    if req.user.id is not None:
#        try:
#            user = User.objects.get(id=req.user.id)
#        except User.DoesNotExist:
#            pass
#    if user is not None and user.is_active:
#        try:
#            profile = user.profile
#        except GPlusProfile.DoesNotExist:
#            profile = None
#        if profile is not None:
#            try:
#                credentials = user.gplus_credential
#            except GPlusCredential.DoesNotExist:
#                credentials = None
#        if profile is not None and credentials is not None:
#            auth_login(req, user)
#        logger.info('user: %s,  profile: %s, credentials: %s' % (user, profile, credentials))
    logger.info('req.user: %s' % (req.user))
    if req.user.is_authenticated():
        return redirect(next_page)
    try:
        state = req.session['state']
    except:
        state = auth_handler.generate_csrf_token()
        req.session['state'] = state
    return render_template('user_profile/login.html', req)
    
def login_post(req):
    username = req.POST['username']
    password = req.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(req, user)
            return redirect('/')
        else:
            return HttpResponse('Account Disabled')
    else:
        return HttpResponse('Login Failed')
    
@login_required
def logout(req):
    #auth_logout(req)
    return render_template('user_profile/logout.html', req)

@login_required
def logout_post(req):
    logger.info(req.REQUEST)
    value = req.REQUEST.get('confirm-value')
    if value == 'disconnect':
        ## TODO: disconnect from g+
        pass
    elif value == 'true':
        auth_logout(req)
        return redirect(reverse('user_profile.views.logout_success'))
    elif value == 'false':
        return redirect('/')
    else:
        return HttpResponseBadRequest()

def logout_success(req):
    return HttpResponse('Logout Successful')
    
def auth_return(req):
    credentials = auth_handler.validate_credentials(req)
    if credentials is False:
        return HttpResponseBadRequest()
    profile = auth_handler.add_user_from_credentials(req, credentials)
    logger.info(str(profile))
    if not profile:
        return HttpResponseBadRequest()
    user = profile.user
    logger.info('active=%s, auth=%s' % (user.is_active, user.is_authenticated()))
    if user.is_active:
        user = authenticate(credentials=user.gplus_credential)
        if user is not None:
            auth_login(req, user)
    return redirect('/')
    
    

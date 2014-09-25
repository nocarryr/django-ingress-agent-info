import os
import string
import httplib2
import json
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

import logging
logger = logging.getLogger('custom')

User = get_user_model()
GPlusProfile = None
GPlusCredential = None

SCOPE = 'https://www.googleapis.com/auth/plus.login'
REDIRECT_URI = None
CLIENT_SECRETS = None
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'oauth_client_secrets.json')
FLOW = None

def generate_csrf_token():
    chars = string.ascii_uppercase + string.digits
    return get_random_string(50, chars)
    
def get_client_secrets():
    global CLIENT_SECRETS
    if CLIENT_SECRETS is not None:
        return CLIENT_SECRETS
    filename = CLIENT_SECRETS_FILE
    need_save = False
    if not os.path.exists(filename):
        need_save = True
        secrets = {
            'web':{
                'redirect_uris':[], 
                'auth_uri':'https://accounts.google.com/o/oauth2/auth', 
                'token_uri':'https://accounts.google.com/o/oauth2/token', 
            }, 
        }
    else:
        with open(filename, 'r') as f:
            s = f.read()
        secrets = json.loads(s)
    if 'client_id' not in secrets['web']:
        secrets['web']['client_id'] = settings.GOOGLE_OAUTH_KEY
        need_save = True
    if 'client_secret' not in secrets['web']:
        secrets['web']['client_secret'] = settings.GOOGLE_OAUTH_SECRET
        need_save = True
    if need_save:
        s = json.dumps(secrets, indent=2)
        with open(filename, 'w') as f:
            f.write(s)
    CLIENT_SECRETS = secrets
    return secrets
    
def get_redirect_uri():
    global REDIRECT_URI
    if REDIRECT_URI is None:
        REDIRECT_URI = reverse('user_profile.views.auth_return')
    return REDIRECT_URI
    
def get_flow():
    get_client_secrets()
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, 
                                   scope='', 
                                   redirect_uri='postmessage')
    return flow

def get_auth_redirect(request):
    flow = get_flow()
    state = request.session['state']
    flow.params['state'] = state
    logger.info('session_key = %s' % (state))
    auth_url = flow.step1_get_authorize_url()
    return HttpResponseRedirect(auth_url)
    
def get_credentials(request=None, user_id=None):
    global GPlusCredential
    if GPlusCredential is None:
        GPlusCredential = ContentType.objects.get(app_label='user_profile', model='gpluscredential').model_class()
    if user_id is None:
        user_id = request.user.id
    storage = Storage(GPlusCredential, 'user', user_id, 'credential')
    credentials = storage.get()
    if credentials is None or credentials.invalid is True:
        return False
    return {'user': User.objects.get(id=user_id), 'credentials':credentials}
    
def validate_credentials(request):
    flow = get_flow()
    state = request.REQUEST.get('state')
    if state != request.session['state']:
        logger.info('state token mis-match')
        return False
    return flow.step2_exchange(request.REQUEST)
    
def add_user_from_credentials(request, credentials):
    global GPlusProfile, GPlusCredential
    if GPlusCredential is None:
        GPlusCredential = ContentType.objects.get(app_label='user_profile', model='gpluscredential').model_class()
    if GPlusProfile is None:
        GPlusProfile = ContentType.objects.get(app_label='user_profile', model='gplusprofile').model_class()
    user = request.user
    if user.id is None or user.profile is None:
        profile_data = get_profile_data(request, credentials)
        logger.info(str(profile_data))
        try:
            profile = GPlusProfile.objects.get(gplus_id=profile_data['id'])
            user = profile.user
            logger.info('PROFILE RETRIEVED')
        except GPlusProfile.DoesNotExist:
            profile, created = GPlusProfile.get_or_create(gplus_data=profile_data)
            user = profile.user
    try:
        storage = user.gplus_credential
    except GPlusCredential.DoesNotExist:
        storage = Storage(GPlusCredential, 'user', user, 'credential')
        storage.put(credentials)
    return profile
    
def build_service(request, credentials=None, user_id=None):
    if credentials is None:
        d = get_credentials(request, user_id)
        if d is False:
            return d
        credentials = d['credentials']
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('plus', 'v1', http=http)
    
def get_profile_data(request=None, credentials=None, user_id=None):
    service = build_service(request, credentials, user_id)
    return service.people().get(userId='me').execute()
    
class GPlusAuthBackend(object):
    def authenticate(self, **kwargs):
        request = kwargs.get('request')
        credentials = kwargs.get('credentials')
        if credentials is not None and not credentials.credential.invalid:
            return credentials.user
        if request is None:
            return None
        d = get_credentials(request)
        if d is False:
            return None
        return d['user']
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    

import json
from django.db import models
from django.contrib.auth import get_user_model
from oauth2client.django_orm import CredentialsField

User = get_user_model()

from auth_handler import get_profile_data

import logging
logger = logging.getLogger('custom')

class GPlusProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    gplus_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    profile_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    gplus_data_json = models.CharField(max_length=500)
    gplus_data_map = {
        'id':'gplus_id', 
        'displayName':'display_name', 
        'url':'profile_url', 
    }
    @classmethod
    def gplus_resource_to_model(cls, gplus_data):
        if isinstance(gplus_data, basestring):
            gplus_data = json.loads(gplus_data)
        model_data = {}
        for gplus_key, model_key in cls.gplus_data_map.iteritems():
            model_data[model_key] = gplus_data[gplus_key]
        model_data['user__first_name'] = gplus_data['name']['givenName']
        model_data['user__last_name'] = gplus_data['name']['familyName']
        model_data['image_url'] = gplus_data['image']['url']
        email = None
        if 'emails' in gplus_data:
            for email in gplus_data['emails']:
                if email['type'] == 'account':
                    model_data['user__email'] = email
                    break
        model_data['user__username'] = 'GPLUS_%s' % (gplus_data['id'])
        model_data['gplus_data_json'] = json.dumps(gplus_data)
        return model_data
    @classmethod
    def split_user_kwargs(cls, **kwargs):
        ukwargs = {}
        pkwargs = {}
        for key, val in kwargs.iteritems():
            if key.startswith('user__'):
                ukwargs[key.split('user__')[1]] = val
            else:
                pkwargs[key] = val
        return ukwargs, pkwargs
    @classmethod
    def get_or_create(cls, **kwargs):
        gplus_data = kwargs.get('gplus_data')
        if gplus_data is not None:
            mkwargs = cls.gplus_resource_to_model(gplus_data)
        else:
            mkwargs = kwargs.copy()
        ukwargs, pkwargs = cls.split_user_kwargs(**mkwargs)
        try:
            user = User.objects.get(username=ukwargs['username'])
        except User.DoesNotExist:
            user = User.objects.create_user(**ukwargs)
        pkwargs['user'] = user
        logger.info('ukwargs: \n%s\n\npkwargs: %s' % (ukwargs, pkwargs))
        profile, created = cls.objects.get_or_create(**pkwargs)
        return profile, created
    def get_profile_data(self):
        return get_profile_data(user_id=self.user.id)
    def __unicode__(self):
        return unicode(self.user)
    
    

class GPlusCredential(models.Model):
    user = models.OneToOneField(User, related_name='gplus_credential')
    credential = CredentialsField()
    def __unicode__(self):
        return u'%s credentials' % (self.user)


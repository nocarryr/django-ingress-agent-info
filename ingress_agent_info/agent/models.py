from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from user_profile.models import GPlusProfile

User = get_user_model()

def get_group(name):
    return Group.objects.get(name=name)
    
class AgentManager(models.GeoManager):
    def get_approved(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.filter(approval__is_approved=True)
    def get_pending(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.filter(approval__is_approved=False, 
                               approval__is_pending=True)
    def get_disabled(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.filter(approval__is_approved=False, 
                               approval__is_pending=False)


class Agent(models.Model):
    user = models.OneToOneField(User, related_name='agent')
    agent_name = models.CharField(max_length=100, 
                                  blank=True, 
                                  null=True)
    agent_level = models.PositiveIntegerField(default=1)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=True)
    objects = AgentManager()
    class Meta:
        permissions = (
            ('modify_others', "Modify other Agents' Info"), 
            ('view_others', "View other Agents' Info"), 
            ('view_unapproved', "View unapproved Agents"), 
            ('approve_agents', "Approve Agents"), 
            ('disable_agents', "Disable Agents"), 
            ('modify_own', "Modify your own info"), 
            ('view_own', "View your own info"), 
        )
    def __unicode__(self):
        if self.agent_name is None:
            return unicode(self.user.profile)
        return u'%s (%s)' % (self.agent_name, self.user.profile)

class Approval(models.Model):
    is_approved = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=True)
    agent = models.OneToOneField(Agent, related_name='approval')
    class Meta:
        permissions = (
            ('approve', 'Approve'), 
            ('disable', 'Disable'), 
        )
    def get_text_status(self):
        if self.is_approved:
            return 'approved'
        if self.is_pending:
            return 'pending'
        return 'disabled'
    def save(self, *args, **kwargs):
        if self.is_approved:
            self.is_pending = False
            user = self.agent.user
            user.groups.add(get_group('Approved Agent'))
        elif self.is_pending is False:
            user = self.agent.user
            user.groups.remove(get_group('Moderator'))
            user.groups.remove(get_group('Approved Agent'))
            user.groups.remove(get_group('Agent'))
        super(Approval, self).save(*args, **kwargs)
    def __unicode__(self):
        return u'%s - %s' % (self.agent, self.get_text_status())
        
@receiver(post_save, sender=GPlusProfile)
def on_profile_post_save(sender, **kwargs):
    if not kwargs.get('created'):
        return
    profile = kwargs.get('instance')
    user = profile.user
    user.groups.add(get_group('Agent'))
    try:
        agent = Agent.objects.get(user=user)
    except Agent.DoesNotExist:
        agent = Agent(user=user)
        agent.save()
        approval = Approval(agent=agent)
        approval.save()
    


class PlayArea(models.Model):
    agent = models.ForeignKey(Agent, related_name='play_areas')
    location = models.ForeignKey('locations.City')
    objects = models.GeoManager()
    def __unicode__(self):
        return unicode(self.location)

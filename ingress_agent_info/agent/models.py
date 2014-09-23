from django.contrib.gis.db import models
from user_profile.models import GPlusProfile

class Agent(models.Model):
    user = models.OneToOneField(GPlusProfile)
    agent_name = models.CharField(max_length=100, unique=True)
    agent_level = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True, auto_now_add=True)
    objects = models.GeoManager()
    def __unicode__(self):
        return self.agent_name
    
    
class PlayArea(models.Model):
    agent = models.ForeignKey(Agent, related_name='play_areas')
    location = models.ForeignKey('locations.City')
    objects = models.GeoManager()
    def __unicode__(self):
        return unicode(self.location)

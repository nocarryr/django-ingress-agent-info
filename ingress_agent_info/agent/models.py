from django.db import models

class Agent(models.Model):
    gPlusUserId = models.CharField(max_length=100, blank=True, null=True)
    display_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100, unique=True)
    agent_level = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True, auto_now_add=True)
    def __unicode__(self):
        return self.agent_name
    
    
class PlayArea(models.Model):
    agent = models.ForeignKey(Agent, related_name='play_areas')
    location = models.ForeignKey('locations.Location')
    def __unicode__(self):
        return unicode(self.location)

from django.contrib.gis import admin
from agent.models import Agent, PlayArea
    
admin.site.register(Agent, admin.GeoModelAdmin)
admin.site.register(PlayArea, admin.GeoModelAdmin)

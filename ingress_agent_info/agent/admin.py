from django.contrib import admin
from agent.models import Agent, PlayArea

class PlayAreaInline(admin.StackedInline):
    model = PlayArea
    
class AgentAdmin(admin.ModelAdmin):
    inlines = [PlayAreaInline]
    
admin.site.register(Agent, AgentAdmin)

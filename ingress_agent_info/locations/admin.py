from django.contrib import admin
from locations.models import Location, ViewPort, LatLong

admin.site.register(Location)
admin.site.register(ViewPort)
admin.site.register(LatLong)

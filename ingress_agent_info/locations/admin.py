from django.contrib.gis import admin
from locations.models import Country, State, City, GeoCodingConf

admin.site.register(Country, admin.GeoModelAdmin)
admin.site.register(State, admin.GeoModelAdmin)
admin.site.register(City, admin.GeoModelAdmin)
admin.site.register(GeoCodingConf)

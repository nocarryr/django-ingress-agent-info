from django.db import models

class LatLong(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    class Meta:
        unique_together = ('latitude', 'longitude')
    def __unicode__(self):
        return u'(%s, %s)' % (self.latitude, self.longitude)
        
class ViewPort(models.Model):
    northeast = models.ForeignKey(LatLong, related_name='viewports_northeast')
    southwest = models.ForeignKey(LatLong, related_name='viewports_southwest')
    @classmethod
    def get_or_create(cls, **kwargs):
        latlongs = {}
        for key in ['northeast', 'southwest']:
            val = kwargs.get(key)
            latlong, created = LatLong.objects.get_or_create(latitude=val['latitude'], longitude=val['longitude'])
            latlongs[key] = latlong
        try:
            vp = cls.objects.get(**latlongs)
        except cls.DoesNotExist:
            vp = cls(**latlongs)
            vp.save()
        return vp
    def set_points(self, point_data, do_save=True):
        for key, val in point_data.iteritems():
            latlong, created = LatLong.objects.get_or_create(latitude=val['latitude'], longitude=val['longitude'])
            setattr(self, key, latlong)
        if do_save:
            self.save()
    def __unicode__(self):
        return u'northeast: %s, southwest: %s' % (self.northeast, self.southwest)
        
class Location(models.Model):
    formatted_address = models.CharField(max_length=200)
    center = models.ForeignKey(LatLong, 
                               blank=True, 
                               null=True, 
                               related_name='location_centers')
    viewport = models.ForeignKey(ViewPort, 
                                 blank=True, 
                                 null=True, 
                                 related_name='locations')
    def set_center(self, latitude, longitude, do_save=True):
        latlong, created = LatLong.objects.get_or_create(latitude=latitude, longitude=longitude)
        self.center = latlong
        if do_save:
            self.save()
    def set_viewport(self, vp_data, do_save=True):
        vp = ViewPort.get_or_create(**vp_data)
        self.viewport = vp
        if do_save:
            self.save()
    def __unicode__(self):
        return self.formatted_address
    

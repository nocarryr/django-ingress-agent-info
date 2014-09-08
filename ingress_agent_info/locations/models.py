import urllib, urllib2
import json
from django.contrib.gis.db import models
from django.contrib.gis import geos
    
class Country(models.Model):
    name = models.CharField(max_length=30, unique=True)
    short_name = models.CharField(max_length=10, unique=True)
    objects = models.GeoManager()
    def __unicode____(self):
        return self.short_name
        
class State(models.Model):
    name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=2)
    country = models.ForeignKey(Country, related_name='states')
    objects = models.GeoManager()
    def __unicode__(self):
        return self.short_name
    
class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, 
                              blank=True, 
                              null=True, 
                              related_name='cities')
    country = models.ForeignKey(Country, related_name='cities')
    center = models.PointField()
    viewport = models.MultiPointField()
    objects = models.GeoManager()
    def __unicode__(self):
        names = [self.name]
        if self.state:
            names.append(unicode(self.state))
        else:
            names.append(unicode(self.country))
        return u', '.join(names)
    
GEOCODING_CONF_DEFAULTS = {'google_api_key':None, 'max_daily_requests':'2500'}
class GeoCodingConf(models.Model):
    name = models.CharField(max_length=30, 
                            choices=((key, key) for key in GEOCODING_CONF_DEFAULTS.keys()), 
                            unique=True)
    value = models.CharField(max_length=100, null=True)
    def save(self, *args, **kwargs):
        if self.value is None:
            default_value = GEOCODING_CONF_DEFAULTS.get(self.name)
            if default_value is not None:
                self.value = default_value
        super(GeoCodingConf, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.name
    
def get_geocode(address, **kwargs):
    address = urllib.quote_plus(address)
    show_debug = kwargs.get('show_debug', False)
    LOG = kwargs.get('log_fn')
    if LOG is None:
        def LOG(*args):
            if not show_debug:
                return
            print '\t'.join([str(arg) for arg in args])
    conf = {}
    for key in GEOCODING_CONF_DEFAULTS.keys():
        try:
            conf_item = GeoCodingConf.objects.get(name=key)
        except GeoCodingConf.DoesNotExist:
            conf_item = None
        if conf_item is None or conf_item.value is None:
            raise Exception('GeoCodingConf items not configured')
        conf[key] = conf_item.value
    conf['max_daily_requests'] = int(conf['max_daily_requests'])
    LOG('conf: %s' % (conf))
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    qs_fmt = 'address=%(address)s&key=%(api_key)s'
    qdict = {'address':address, 'api_key':conf['google_api_key']}
    url = '?'.join([base_url, qs_fmt % qdict])
    LOG(url)
    u = urllib2.urlopen(url)
    s = u.read()
    u.close()
    d = json.loads(s)
    if d['status'] != 'OK':
        LOG('request status: %s' % d['status'])
        if d['status'] == 'ZERO_RESULTS':
            return False
    def latlong_to_point(latlong):
        return geos.Point([latlong[key] for key in ['lat', 'lng']])
    def parse_address_type(addr_component):
        addr_types = addr_comp['types']
        if 'locality' in addr_types:
            return 'city'
        if 'administrative_area_level_1' in addr_types:
            return 'state'
        if 'country' in addr_types:
            return 'country'
    addr_types_needed = ['city', 'state', 'country']
    return_data = {}
    geometry = {}
    for result in d['results']:
        for addr_comp in result['address_components']:
            addr_type = parse_address_type(addr_comp)
            if not addr_type:
                continue
            if addr_type not in return_data:
                return_data[addr_type] = {}
            if 'name' not in return_data[addr_type]:
                return_data[addr_type]['name'] = addr_comp['long_name']
            if addr_type != 'city' and 'short_name' not in return_data[addr_type]:
                return_data[addr_type]['short_name'] = addr_comp['short_name']
        if 'center' not in geometry and 'location' in result['geometry']:
            loc = result['geometry']['location']
            geometry['center'] = latlong_to_point(loc)
        if 'viewport' not in geometry and 'viewport' in result['geometry']:
            vp = result['geometry']['viewport']
            geometry['viewport'] = geos.MultiPoint(*[latlong_to_point(vp[vpkey]) for vpkey in ['northeast', 'southwest']])
    if len(return_data) < len(addr_types_needed):
        return False
    return_data['city'].update(geometry)
    return return_data
    
def build_from_geocode(data):
    country, created = Country.objects.get_or_create(**data['country'])
    if data.get('state'):
        skwargs = data['state'].copy()
        skwargs['country'] = country
        state, created = State.objects.get_or_create(**skwargs)
    else:
        state = None
    ckwargs = data['city'].copy()
    ckwargs['country'] = country
    if state is not None:
        ckwargs['state'] = state
    city, created = City.objects.get_or_create(**ckwargs)

def get_and_build_from_address(address):
    geodata = get_geocode(address)
    if not geodata:
        return
    build_from_geocode(geodata)

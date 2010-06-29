from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.localflavor.uk.forms import UKPostcodeField
from django.contrib import messages
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.forms.models import inlineformset_factory

from userprofile.models import UserProfile
from things.models import Thing, ThingImage
import math

class UserProfileForm(forms.Form):
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    def clean(self):
        if not self.cleaned_data['latitude'] or not self.cleaned_data['longitude']:
            raise forms.ValidationError("Sorry, you need to enter your location on the map.")
        if self.cleaned_data['latitude'] < 0.865 or \
           self.cleaned_data['latitude'] > 1.1 or \
           self.cleaned_data['longitude'] > 0.04 or \
           self.cleaned_data['longitude'] < -0.187:
            raise forms.ValidationError("Sorry, the location you specified isn't in the British Isles. Please try again.")
        return self.cleaned_data


def lat_long_to_easting_northing(lat, lon):
    """ Ridiculously fussy function for converting longitude/latitude to UK
        OS national grid co-ordinates """
    # lat / lon need to be in radians
    
    a, b = 6377563.396, 6356256.910          # Airy 1830 major & minor semi-axes
    F0 = 0.9996012717                         # NatGrid scale factor on central meridian
    lat0, lon0= math.radians(49), math.radians(-2)  # NatGrid true origin
    N0, E0 = -100000, 400000;                 # northing & easting of true origin, metres
    e2 = 1 - (b*b)/(a*a)                     # eccentricity squared
    n = (a-b)/(a+b)
    n2=n*n
    n3=n*n*n
  
    cosLat, sinLat = math.cos(lat), math.sin(lat);
    nu = a*F0/math.sqrt(1-e2*sinLat*sinLat);              # transverse radius of curvature
    rho = a*F0*(1-e2)/math.pow(1-e2*sinLat*sinLat, 1.5);  # meridional radius of curvature
    eta2 = nu/rho-1;
  
    Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat-lat0);
    Mb = (3*n + 3*n*n + (21/8)*n3) * math.sin(lat-lat0) * math.cos(lat+lat0);
    Mc = ((15/8)*n2 + (15/8)*n3) * math.sin(2*(lat-lat0)) * math.cos(2*(lat+lat0));
    Md = (35/24)*n3 * math.sin(3*(lat-lat0)) * math.cos(3*(lat+lat0));
    M = b * F0 * (Ma - Mb + Mc - Md);              # meridional arc
  
    cos3lat = cosLat*cosLat*cosLat;
    cos5lat = cos3lat*cosLat*cosLat;
    tan2lat = math.tan(lat)*math.tan(lat);
    tan4lat = tan2lat*tan2lat;
  
    I = M + N0;
    II = (nu/2)*sinLat*cosLat;
    III = (nu/24)*sinLat*cos3lat*(5-tan2lat+9*eta2);
    IIIA = (nu/720)*sinLat*cos5lat*(61-58*tan2lat+tan4lat);
    IV = nu*cosLat;
    V = (nu/6)*cos3lat*(nu/rho-tan2lat);
    VI = (nu/120) * cos5lat * (5 - 18*tan2lat + tan4lat + 14*eta2 - 58*tan2lat*eta2);
  
    dLon = lon-lon0;
    dLon2 = dLon*dLon
    dLon3 = dLon2*dLon
    dLon4, dLon5, dLon6 = dLon3*dLon, dLon3*dLon*dLon, dLon3*dLon*dLon*dLon;
  
    N = I + II*dLon2 + III*dLon4 + IIIA*dLon6;
    E = E0 + IV*dLon + V*dLon3 + VI*dLon5;
  
    return E, N


@login_required
def home(request):
#    from django.db import connection
#    cursor = connection.cursor()
#    cursor.execute("select sqrt(((easting - %f) * (easting - %f)) + ((northing - %f) * (northing - %f))) as distance from userprofile_userprofile" % (2.5,2.5,3,4))
#    row = cursor.fetchone()
#    print row

    if request.method == 'POST':
        userprofile_form = UserProfileForm(request.POST)
        if userprofile_form.is_valid():
            userprofile = request.user.get_profile()
            latitude = userprofile_form.cleaned_data['latitude']
            longitude = userprofile_form.cleaned_data['longitude']
            userprofile.latitude, userprofile.longitude = latitude, longitude
            userprofile.easting, userprofile.northing = lat_long_to_easting_northing(latitude, longitude)
            userprofile.save()
    else:
        userprofile = request.user.get_profile()
        userprofile_form = UserProfileForm(initial={ 'longitude':userprofile.longitude,
                                                     'latitude':userprofile.latitude,
                                            })

    return render_to_response('userprofile/userprofile_home.html',
                             {'userprofile_form':userprofile_form,},
                             context_instance=RequestContext(request) )

@login_required
def my_stuff(request):
    return render_to_response('userprofile/my_stuff.html', context_instance=RequestContext(request))

class ThingForm(forms.ModelForm):
    class Meta:
        model = Thing
        exclude=('taken_status_other', 'regular', 'donor', 'date_time_added')


ThingImageFormSet = inlineformset_factory(Thing, 
    ThingImage, 
    can_delete=True,
    extra=1)


@login_required
def edit_thing(request, thing_id=None):
    if request.method == 'POST':
        if thing_id:
            thing = get_object_or_404(Thing, id=thing_id)
            action="edited"
        else:
            thing = None
            action="created"
        form = ThingForm(request.POST, request.FILES, instance=thing)
        if form.is_valid():
            thing = form.save(commit=False)
            thing.donor = request.user.get_profile()
            thingimage_formset = ThingImageFormSet(request.POST, request.FILES, instance=thing)
            if thingimage_formset.is_valid():
                thing.save()
                thingimage_formset.save()  
                messages.success(request, "An item was successfully %s." % action)

            return HttpResponseRedirect('/userprofile/my-stuff/')
    else:
        if thing_id:
            thing = get_object_or_404(Thing, id=thing_id)
            form = ThingForm(instance=thing)
            thingimage_formset = ThingImageFormSet(instance=thing)
        else:
            form = ThingForm()
            thingimage_formset = ThingImageFormSet(instance=Thing())

    return render_to_response('userprofile/edit_thing.html',
                              {'form': form,
                               'thingimage_formset':thingimage_formset},
                              context_instance=RequestContext(request))

@login_required
def delete_thing(request, thing_id):
    if request.GET.get('confirm')=='yes':
        thing = get_object_or_404(Thing, id=thing_id)
        thing.delete()
        messages.success(request, "An item of stuff was deleted.")
        return HttpResponseRedirect('/userprofile/my-stuff/')
    elif request.GET.get('confirm')=='no':
        messages.success(request, "Deletion of stuff cancelled.")
        return HttpResponseRedirect('/userprofile/my-stuff/')
    else:
        return render_to_response('userprofile/confirm_delete_thing.html',
                                  context_instance=RequestContext(request))

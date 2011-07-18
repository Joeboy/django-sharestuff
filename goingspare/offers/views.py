from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.gis.utils import GeoIP
from django.template.loader import get_template
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from offers.models import LocalOffer
from userprofile.models import UserProfile

from goingspare.utils import render_to_response_context
from goingspare.utils.http import JsonResponse
from goingspare.offers.decorators import user_offer
from notifications.models import Notification
from email_lists.models import EmailMessage
from .forms import (OfferForm, EmailOfferToListForm, OfferListForm,
                    OfferBrowseForm, OfferContactForm)


OFFERS_PER_PAGE = 10

@login_required
def my_offers(request):
    """
    Return a list of the user's offers
    """
    return render_to_response_context(request, 'offers/my_offers.html')


@user_offer
def edit_offer(request, offer=None):
    """
    Edit or create a user's offer
    """
    userprofile = request.user.get_profile()
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = OfferForm.save(form, commit=False)
            offer.donor = userprofile
            offer.save()
            form.save_m2m()
            for im in form.cleaned_data['image_list']:
                im.offer = offer
                im.save()
            action = offer and 'edited' or 'created'
            message = "A offer was successfully %s." % action
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        if offer is None:
            initial = {'location': userprofile.location}
            for action in 'list', 'show':
                for who in 'public', 'sharestuffers', 'watchers':
                    attr_name = 'offers_%s_%s' % (action, who)
                    initial['%s_%s' % (action, who)] = getattr(userprofile,
                                                               attr_name)

            form = OfferForm(initial=initial)
            initial['list_public'] = userprofile.offers_list_public
        else:
            form = OfferForm(instance=offer, initial={'image_list': ','.join([str(im.id) for im in offer.localofferimage_set.all()])})

    return render_to_response_context(request, 'offers/edit_offer.html', {'form': form,
                                                                          'offer': offer,
                                                                          'image_list': offer and offer.image_list or '[]'})


@user_offer
def delete_offer(request, offer):
    """
    Delete a user's offer
    """
    if request.GET.get('confirm') == 'yes':
        offer.delete()
        request.user.message_set.create(message="An offer was deleted.")
        return HttpResponseRedirect(reverse('my-offers'))
    elif request.GET.get('confirm') == 'no':
        request.user.message_set.create(message="Deletion of offer cancelled.")
        return HttpResponseRedirect(reverse('my-offers'))
    else:
        return render_to_response_context(request, 'offers/confirm_delete_offer.html')


@user_offer
def email_offer_to_list(request, offer):
    userprofile = request.user.get_profile()
    if request.POST:
        form = EmailOfferToListForm(request.POST, userprofile=userprofile)
        if form.is_valid():
            msg = EmailMessage(
                subscription=form.cleaned_data['subscription'],
                offer=offer,
                message_type=form.cleaned_data['message_type'],
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['message'],
            )
            msg.save()
            msg.send_mail()
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        initial = {}
        if userprofile.subscription_set.count() == 1:
            initial['subscription'] = userprofile.subscription_set.get()
        form = EmailOfferToListForm(userprofile=request.user.get_profile(),
                                    initial=initial)
    c = {'offer': offer,
         'form': form}
    return render_to_response_context(request, 'offers/email_offer_to_list.html', c)


def get_offers(input, extra=None):
    if extra is None:
        extra = {}
    form = OfferBrowseForm(input)
    if form.is_valid():
        params = form.cleaned_data
        params.update(extra)
        offers = LocalOffer.objects.filter_by(**params)
    else:
        offers = None
    return offers, form
    

def list_offers(request):
    """
    Sorta the same as browse_offers, but for direct linking rather than
    filtering via a form
    """
    if request.user.is_authenticated():
        userprofile = request.user.get_profile()
        lng, lat = userprofile.location.coords
    else:
        userprofile = None
        lng, lat = None, None

    form = OfferListForm(request.REQUEST)

    if form.is_valid():
        latitude = form.cleaned_data['latitude']
        longitude = form.cleaned_data['longitude']
        if None in (latitude, longitude):
            latitude, longitude = lat, lng
        offers = LocalOffer.objects.all().filter_by(
            donorprofile=form.cleaned_data['donorprofile'],
            watched_users=form.cleaned_data['watched_users'],
            latitude=latitude,
            longitude=longitude,
            asking_userprofile=userprofile,
            tags=form.cleaned_data['tags'],
            max_distance=form.cleaned_data['max_distance'])
        paginator = Paginator(list(offers), OFFERS_PER_PAGE)
        page = request.GET.get('page', 1)

        c = RequestContext(request, {'page': paginator.page(page)})
        if request.is_ajax():
            t = get_template('offers/list_offers_nochrome.html')
            return JsonResponse({'html': t.render(c)})
        else:
            t = get_template('offers/list_offers.html')
            return HttpResponse(t.render(c))
    else:
        # TODO
        print form.errors
        for e in form.errors:
            print e
        return HttpResponse("invalid")


def browse_offers(request):
    """
    """
    if request.user.is_authenticated():
        userprofile = request.user.get_profile()
    else:
        userprofile = None

    if request.method == 'POST' or request.GET.get('page'):
        if request.is_ajax():
            return list_offers(request)

        offers, form = get_offers(request.POST, {'asking_userprofile':userprofile})
        if form.errors:
            if request.is_ajax():
                return JsonResponse({'errors': form.errors})
            else:
                return render_to_response_context(
                    request,
                    'offers/browse_offers.html',
                    {'form': form,
                     'offers': []})
    else:
        if userprofile and userprofile.location:
            lng, lat = userprofile.location.coords
            location_source = 'userprofile'
        else:
            g = GeoIP()
            ip = request.META.get('REMOTE_ADDR')
            lat, lng = 52.63639666, 1.29432678223
            location_source = 'none'
            if ip:
                latlon = g.lat_lon(ip)
                if latlon:
                    lat, lng = latlon
                    location_source = 'ip'
        form = OfferBrowseForm(initial={'max_distance': 25,
                                        'latitude': lat,
                                        'longitude': lng,
                                        'location_source': location_source})
        offers = []

    paginator = Paginator(list(offers), OFFERS_PER_PAGE)
    page = paginator.page(request.GET.get('page', 1))
    return render_to_response_context(request,
                                      'offers/browse_offers.html',
                                      {'form': form,
                                       'page': page})


def user_offers(request, username):
    donor = get_object_or_404(UserProfile, user__username=username)
    userprofile = UserProfile.get_for_user(request.user)
    offers = LocalOffer.objects.filter(donor=donor).filter_by_user(userprofile)
    return render_to_response_context(request,
                                      'offers/user_offers.html',
                                      {'offers': offers,
                                       'donor': donor})


def view_offer(request, offer_hash):
    userprofile = UserProfile.get_for_user(request.user)

    if userprofile:
        if userprofile.location:
            qs = LocalOffer.objects.distance(userprofile.location)
        else:
            qs = LocalOffer.objects.all()
    else:
        qs = LocalOffer.objects.all()

    offer = get_object_or_404(qs, hash=offer_hash)
    permitted = offer.show_to_user(userprofile)
    return render_to_response_context(request,
                                      'offers/offer.html',
                                      {'offer': offer,
                                       permitted: permitted,})


text_tpl = get_template('offers/emailmessages/offer_contact.txt')
html_tpl = get_template('offers/emailmessages/offer_contact.html')

@transaction.commit_on_success
def offer_contact(request, offer_hash):
    offer = get_object_or_404(LocalOffer, hash=offer_hash)
    if request.POST:
        form = OfferContactForm(request.POST)
        if form.is_valid():
            sender = request.user.get_profile()
            c = RequestContext(request,
                               {'domain': settings.SITE_DOMAIN,
                                'sender': sender,
                                'offer': offer,
                                'message': form.cleaned_data['message']})
            html_message = html_tpl.render(c)
            text_message = text_tpl.render(c)
            Notification.objects.create(to_user=offer.donor,
                                        message=html_message)
            if offer.donor.email_contact:
                msg = EmailMultiAlternatives('Sharestuff: enquiry about "%s"' % offer.title,
                                             text_message,
                                             sender.user.email,
                                             [offer.donor.user.email])
                msg.attach_alternative(html_message, "text/html")
                msg.send()

            return HttpResponseRedirect(reverse('offer-contact-sent'))
    else:
        form = OfferContactForm()

    return render_to_response_context(request,
                                      'offers/contact_form.html',
                                      {'offer_contact_form': form})


def offer_contact_sent(request):
    return render_to_response_context(request,
                                      'offers/offer_contact_sent.html')

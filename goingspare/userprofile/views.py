from goingspare.utils import render_to_response_context
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.db import transaction
from userprofile.models import UserProfile
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as django_login, logout as django_logout
from utils.formfields import UKPhoneNumberField

from django.contrib.auth.decorators import user_passes_test
staffmember_required=user_passes_test(lambda u: not u.is_anonymous() and u.is_staff)

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model=UserProfile
        exclude=('user', 'watched_users', 'email_lists')

    class Media:
        js=("http://www.google.com/jsapi?key=ABQIAAAA0okLrKZhiNabzBlBE2rJHRQRB3d2m0eE07bem--pb7XcM7LibBS3sJZUsLLOaucwIRuf8Q4305bVSw","/media/js/location_widget.js")
        css = {'screen': (  "http://www.google.com/uds/css/gsearch.css",
                            "http://www.google.com/uds/solutions/localsearch/gmlocalsearch.css"
                          )
                }
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)


def view_profile(request, user_id):
    userprofile = UserProfile.get_for_user(request.user) 
    donor = get_object_or_404(UserProfile, id=user_id)
    offers = donor.localoffer_set.filter_by_user(userprofile)
    return render_to_response_context(request,
                                      'userprofile/userprofile.html',
                                      {'donor':donor, 'offers':offers})

@login_required
def index(request):
    userprofiles = UserProfile.objects.all()
    return render_to_response_context(request, 'userprofile/index.html', {'userprofiles':userprofiles})


@login_required
@transaction.commit_on_success
def edit(request):
    userprofile = request.user.get_profile()
    if request.method == 'POST':
        form = UserProfileForm(instance=userprofile, data=request.POST)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect("/user/updated/")
    else:
        form = UserProfileForm(instance=userprofile,
                               initial={'email':userprofile.user.email})

    return render_to_response_context(request, 'userprofile/edit.html', {'userprofile_form':form,})


@login_required
def updated(request):
    return render_to_response_context(request, 'userprofile/userprofile_updated.html')


def login(request):
    raise NotImplementedError
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            django_login(request, form.get_user())
            return HttpResponseRedirect('/')
    else:
        form = AuthenticationForm(request)

    return render_to_response_context(request, 'userprofile/login.html', {'form':form})


@login_required
def logout(request):
    raise NotImplementedError
    django_logout(request)
    return HttpResponseRedirect('/')


@login_required
@transaction.commit_on_success
def change_password(request):
    if request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/user/password-changed/')
    else:
        form = PasswordChangeForm(request.user)

    return render_to_response_context(request, 'userprofile/change_password.html', {'form':form})


@login_required
def password_changed(request):
    return render_to_response_context(request, 'userprofile/password_changed.html')

@login_required
def user_list(request):
    userprofiles = UserProfile.objects.all()
    return render_to_response_context(request,
                                      'userprofile/list_users.html',
                                      {'userprofiles':userprofiles})

@login_required
def watch_user(request, user_id, unwatch=False):
    watched_userp = get_object_or_404(UserProfile, id=user_id)
    if unwatch:
        request.user.get_profile().watched_users.remove(watched_userp)
    else:
        request.user.get_profile().watched_users.add(watched_userp)
    return HttpResponseRedirect(reverse('view-userprofile', kwargs={'user_id':user_id}))

@staffmember_required
def manage_users(request):
    userprofiles = UserProfile.objects.all()
    return render_to_response_context(request, 'userprofile/manage/index.html', {'userprofiles':userprofiles})


class UserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs.pop('instance')
        return super(UserForm, self).__init__(*args, **kwargs)

    username = forms.CharField(max_length=30)
    name = forms.CharField(max_length=100)
    email = forms.EmailField(required=False)
    phone_number = UKPhoneNumberField(required=False)
    info = forms.CharField(widget=forms.Textarea, required=False)
    is_staff = forms.BooleanField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean(self):
        if not self.instance and not self.cleaned_data.get('password'):
            self._errors['password'] = ErrorList(["You can't create a new user without giving them a password."])
        if 'confirm_password' in self.cleaned_data.keys() and 'password' not in self.cleaned_data.keys() or \
            'password' in self.cleaned_data.keys() and 'confirm_password' not in self.cleaned_data.keys():
                self._errors['password'] = ErrorList(["You need to enter the same password in both the 'password' and 'confirm password' boxes."])
        elif 'password' in self.cleaned_data and not self.cleaned_data['password'] == self.cleaned_data['confirm_password']:
            self._errors['password'] = ErrorList(["The passwords you entered do not match."])
        return self.cleaned_data

@staffmember_required
def edit_user(request, id=None):
    if id:
        action = "edit"
        userprofile = get_object_or_404(UserProfile, id=id)
        user = userprofile.user
        initial = { 'username':user.username,
                    'name':userprofile.name,
                    'password':"",
                    'email':user.email,
                    'phone_number':userprofile.phone_number,
                    'info':userprofile.info,
                    'is_staff':user.is_staff,
                  }
    else:
        action = "add"
        userprofile = None
        initial = None
    if request.POST:
        form = UserForm(request.POST, instance=userprofile)
        if form.is_valid():
            if userprofile:
                user = userprofile.user
            else:
                userprofile = UserProfile()
                user = User()
                userprofile.user = user
                
            userprofile.user.username = form.cleaned_data['username']
            userprofile.name = form.cleaned_data['name']
            userprofile.user.email = form.cleaned_data['email']
            userprofile.phone_number = form.cleaned_data['phone_number']
            userprofile.info = form.cleaned_data['info']
            userprofile.user.is_staff = form.cleaned_data['is_staff']
            if form.cleaned_data['password']:
                userprofile.user.set_password(form.cleaned_data['password'])
            user.save()
            userprofile.user = user
            userprofile.save()
            request.user.message_set.create(message="User '%s' was %sed." % (userprofile.name, action))
            return HttpResponseRedirect("/user/manage/")
    else:
        form = UserForm(initial=initial, instance=userprofile)
    return render_to_response_context(request, 'userprofile/manage/edit.html', {'form':form, 'action':action})

@staffmember_required
def delete_user(request, id):
    userprofile = get_object_or_404(UserProfile, id=id)
    name = userprofile.name
    if request.GET.get('confirm'):
        userprofile.skill_set.all().delete()
        userprofile.user.delete()
        userprofile.delete()
        request.user.message_set.create(message="User '%s' was deleted." % (name,))
        return HttpResponseRedirect("/user/manage/")
    return render_to_response_context(request, 'userprofile/manage/confirm_delete.html', {'userprofile':userprofile})

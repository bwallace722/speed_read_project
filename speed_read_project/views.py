# These are views that shouldn't actually be handled
# by the app--so we put them into the wrapper.

import json

from django.contrib.auth import (
    authenticate, login as auth_login, logout as auth_logout)
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect


def login(request, context={}):

    if request.method == "GET":
        return render(request, 'speed_read_project/login.html', context)

    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect(reverse('speed_read:initial'))
            else:
                return HttpResponse("Account is not active.")
        else:
            return HttpResponse("Account is not valid.")
    else:
        return HttpResponse("Something went wrong.")


def logout(request):
    auth_logout(request)
    return login(
        request, context={"error_message" : "You have been logged out."})
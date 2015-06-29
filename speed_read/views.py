import random

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import TrainingSession as TS, Exercise, Passage

@login_required
def initial_view(request):
    """
    This is the entry point view. It creates a SessionHandler 
    and attaches it to the User's session, then calls the 
    next_exercise method.
    """
    # check whether this is the appropriate session:
    template_name = 'speed_read/initial.html'
    if TS.find_training_session(request) is None:
        user = request.user
        session = TS(user=user)
        session.save()
        return render(request, template_name, {})
    else:
        return render(
            request, template_name,
            {"error_message" :
            "It looks like you're already in the middle of a session."})

@login_required
def session_landing(request):
    """This is the page we should redirect to when users enter a bad url."""
    # TODO move html into a template and make it look good
    session = TS.find_training_session(request)
    response = "<p>session landing</p>"
    if session is None:
        response += "you currently have no session"
    else:
        response += "you're in the middle of session: " + str(session.id)
        exercise = session.get_current_exercise()
        if exercise is not None:
            response += ("<br>you're currently working on exercise: " +
                        str(exercise.id))
    return HttpResponse(response)

@login_required
def generate_exercise_and_reroute(request):
    """
    This is the hub linked to by the initial page and the results
    page when the controller needs to generate a new exercise for the
    session and then send the user to that start that exercise.
    """
    return TS.generate_exercise_and_reroute(request)


@login_required
def section_view(request, session_id, exercise_id, section):
    """
    Displays any of the sections' views
    """
    return render(request, 'speed_read/section.html', 
                  {
                  'status_url' : reverse('speed_read:exercise_status',
                                         kwargs={'session_id' : session_id,
                                                 'exercise_id' : exercise_id,
                                                 'section' : section}),
                  'section' : section,
                  })

@login_required
def section_status(request, session_id, exercise_id, section):
    return TS.get_section_status(request, session_id, exercise_id, section)


@login_required
def exit_portal(request):
    return HttpResponse("this is the exit page")
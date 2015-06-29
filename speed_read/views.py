import random

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse

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
        exercise = session.active_exercise
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
def passage_time(request, session_id, exercise_id, start_or_stop):
    print('passage start')
    verify_results = TS.verify_request(request, session_id, 
                                       exercise_id, 'passage')
    if(verify_results['active']):
        if start_or_stop == 'start':
            print('started')
            verify_results['exercise'].start_passage()
        elif start_or_stop == 'stop':
            print('calling stop_passage()')
            verify_results['exercise'].stop_passage()
    return HttpResponse('success')

@login_required
def section_status(request, session_id, exercise_id, section):
    """
    Called from the passage_view's angular javascript session as
    soon as the page loads. 
    Returns the following json'd dictionary:
    {
    * is_visible : boolean <whether this is *this user's* current session>
    * is_active : boolean <whether this is the active portion of
                    the ongoing exercise>
    * content : dictionary of section-specific content
    * next_link : None or string <link to comprehension_questions>
                  --I think we can just use a string...
    }
    """
    # checks whether this is the active section
    verify_results = TS.verify_request(request, session_id,
                                       exercise_id, section)
    exercise = verify_results['exercise']
    visible = verify_results['visible']
    active = verify_results['active']
    session = verify_results['session']
    #assign the right content
    if section == 'passage':
        start_url = reverse('speed_read:passage_time',
                            kwargs={'session_id': session_id,
                                    'exercise_id': exercise_id,
                                    'start_or_stop': 'start'})
        stop_url = reverse('speed_read:passage_time',
                            kwargs={'session_id': session_id,
                                    'exercise_id': exercise_id,
                                    'start_or_stop': 'stop'})
        content = {'text': exercise.passage.passage_text,
                   'title': exercise.passage.passage_title,
                   'instructions': 'example instructions',
                   'start_url': start_url,
                   'stop_url': stop_url};
        next_link = reverse('speed_read:exercise',
                             kwargs={'session_id' : session_id,
                                     'exercise_id' : exercise_id,
                                     'section' : 'comprehension'}),
    elif section == 'comprehension':
        content = exercise.question_dictionary()
        next_link = reverse('speed_read:exercise',
                             kwargs={'session_id' : session_id,
                             'exercise_id' : exercise_id,
                             'section' : 'results'}),
    elif section == 'results':
        content = {'wpm' : exercise.words_per_minute,
                   'accuracy' : exercise.comprehension_accuracy,
                   'success' : (exercise.comprehension_accuracy
                                >= session.ACCURACY_THRESHOLD)}
        if session.get_continue_status:
            next_link = reverse('speed_read:generate',
                                kwargs={'session_id': session_id})
        else:
            next_link = reverse('speed_read:exit')

    response = {
    'visible' : visible,
    'active' : active,
    'content' : content,
    'next_link' : next_link,
    }
    return JsonResponse(response)


@login_required
def exit_portal(request):
    return HttpResponse("this is the exit page")
import random


from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from .models import TrainingSession as TS, Exercise, Passage, QuestionExercise


@never_cache
@login_required
def initial_view(request):
    """
    This is the entry point view. It creates a SessionHandler 
    and attaches it to the User's session, then calls the 
    next_exercise method.
    """
    # check whether this is the appropriate session:
    template_name = 'speed_read/initial.html'
    session = TS.find_training_session(request)
    if session is None or session.is_complete:
        context = {
            'next_link': reverse('speed_read:generate'),
        }
        return render(request, template_name, context)
    else:
        return render(
            request, template_name,
            {"error_message" :
            "It looks like you're already in the middle of a session."})

@never_cache
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
            response += ("<br>this section is active: " + session.get_active_section())
    return HttpResponse(response)


@never_cache
@login_required
def section_view(request, session_id, exercise_id, section):
    """
    Dispatcher between the three section views.
    """
    # checks whether this is the active section
    verify_results = TS.verify_request(request, session_id,
                                       exercise_id, section)
    if verify_results['visible']:
        if section == 'passage':
            return passage_view(request, verify_results)
        elif section == 'comprehension':
            return comprehension_view(request, verify_results)
        elif section == 'results':
            return results_view(request, verify_results)
    else:
        return redirect('speed_read:landing')


@never_cache
@login_required
def passage_view(request, verify_results):
    session = verify_results['session']
    exercise = verify_results['exercise']
    kwargs = {'session_id' : session.id,
              'exercise_id' : exercise.id,
              'section' : 'comprehension'}
    next_link = reverse('speed_read:exercise', 
                        kwargs = {'session_id' : session.id,
                                  'exercise_id' : exercise.id,
                                  'section' : 'comprehension'})
    start_url = reverse('speed_read:passage_time',
                        kwargs={'session_id' : session.id,
                                'exercise_id' : exercise.id,
                                'start_or_stop': 'start'})
    stop_url = reverse('speed_read:passage_time',
                        kwargs={'session_id' : session.id,
                                'exercise_id' : exercise.id,
                                'start_or_stop': 'stop'})
    context = {'exercise': exercise,
               'next_link' : next_link,
               'start_url': start_url,
               'stop_url': stop_url,
               'active': verify_results['active']};
    return render(request, 'speed_read/passage.html', context)

@never_cache
@login_required
def comprehension_view(request, verify_results):
    exercise = verify_results['exercise']
    next_link = reverse('speed_read:exercise',
                        kwargs={'session_id' : verify_results['session'].id,
                                'exercise_id' : exercise.id,
                                'section' : 'results'})
    status_link = reverse('speed_read:question_status',
                          kwargs={'session_id': verify_results['session'].id,
                                  'exercise_id': exercise.id,})
    questions = QuestionExercise.objects.filter(exercise=exercise)
    context = {'next_link': next_link,
               'status_link': status_link,
               'exercise': exercise,
               'questions': questions,
               'active': verify_results['active']}

    return render(request, 'speed_read/comprehension.html', context)

@login_required
def results_view(request, verify_results):
    session = verify_results['session']
    exercise = verify_results['exercise']
    if not session.is_complete:
        next_link = reverse('speed_read:generate')
    else:
        next_link = reverse('speed_read:exit', 
                            kwargs={'session_id': session.id})
    context = {'exercise': exercise,
               'session': session,
               'next_link': next_link,
               'active': verify_results['active']}
    return render(request, 'speed_read/results.html', context)


@never_cache
@login_required
def generate_exercise_and_reroute(request):
    """
    This is the hub linked to by the initial page and the results
    page when the controller needs to generate a new exercise for the
    session and then send the user to that start that exercise.
    """
    session = TS.find_training_session(request)
    if session is None:
        session = TS.objects.create(user=request.user, exercises_to_complete=1)
    #either they haven't started or they finished the last one
    if session.active_exercise is None or session.active_exercise.is_complete:
        session.generate_exercise()
        exercise = session.active_exercise
        return redirect('speed_read:exercise', session_id=session.id,
                        exercise_id=exercise.id, section='passage')
    else:
        return HttpResponse('404?')


@never_cache
@login_required
def passage_time(request, session_id, exercise_id, start_or_stop):
    verify_results = TS.verify_request(request, session_id, 
                                       exercise_id, 'passage')
    if(verify_results['active']):
        if start_or_stop == 'start':
            print('started')
            verify_results['exercise'].start_passage()
            return HttpResponse('success')
        elif start_or_stop == 'stop':
            verify_results['exercise'].stop_passage()
            return HttpResponse('success')


@never_cache
def question_status(request, session_id, exercise_id):
    if request.method == 'POST':
        id = int(request.POST['question_id'])
        correct = request.POST['correct'] == u'True'
        question_exercise = get_object_or_404(QuestionExercise, pk=id)
        exercise = question_exercise.exercise
        exercise.check_off(question_exercise, correct)
        return HttpResponse('received')

@never_cache
@login_required
def exit_portal(request, session_id):
    session = TS.find_training_session(request)
    if session is not None and str(session.id) == str(session_id) and session.is_complete:
        session.close()
        return HttpResponse("this is the exit page")
    else:
        print(session.id, session_id)
        return redirect('speed_read:landing')
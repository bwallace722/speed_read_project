import random

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from .models import TrainingSession, Exercise, Passage


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

@login_required
def initial_view(request):
    """
    This is the entry point view. It creates a SessionHandler 
    and attaches it to the User's session, then calls the 
    next_exercise method.
    """
    # check whether this is the appropriate session:
    template_name = 'speed_read/initial.html'
    if TrainingSession.get_current_session(request) is None:
        user = request.user
        session = TrainingSession(user=user)
        session.save()
        return render(request, template_name, {})
    else:
        return render(
            request, template_name,
            {"error_message" :
            "It looks like you're already in the middle of a session."})

@login_required
def generate_exercise_and_reroute(request):
    """
    This is the reroute hub linked to by the initial page and the results
    page when the controller needs to generate a new exercise for the
    session and then send the user to that start that exercise.
    """
    # 1. get the session
    session = TrainingSession.get_current_session(request)
    if session is not None:
        # 2. choose a passage
        # we only exclude passages that have been used in THIS training
        # session, otherwise we could potentially run out of passages
        # with an avid user 
        used_passages = [ex.passage for ex in
            Exercise.objects.filter(training_session=session)]
        passages = [p for p in Passage.objects.all() if p not in used_passages]
        #assert len(passages)
        if not len(passages):
            p = Passage(passage_title="example", passage_text="example text")
            p.save()
            passages = [p]
        passage = random.choice(passages)
        # 3. choose questions for the passage
        # TODO give it actual questions
        questions = []

        # 4. instantiate the exercise and attach it to the session,
        # attach the questions
        new_exercise = Exercise(passage=passage, training_session=session)
        new_exercise.save()
        session.active_exercise = new_exercise
        session.save()
        for q in questions:
            QuestionExercise(q, new_exercise).save()

        # 5. redirect to the appropriate page (passage view)
        return passage_view(request)




    else:
        template_name = 'speed_read/initial.html'
        # this should be a safe redirect:
        # TODO should this redirect to results or initial?
        # or nowhere?
        # should these URLs have ids???
        return render(
            request, template_name,
            {"error_message" :
            "You need to start a new session."})


@login_required
def passage_view(request):
    """
    Handles the reading exercise and timing.
    """
    template_name = 'speed_read/passage.html'
    context = {}
    # grab the training session
    session = TrainingSession.get_current_session(request)
    # get the next passage to read
    context["passage"] = session.get_next_passage()
    return render(request, template_name, context)


@login_required
def comprehension_view(request):
    """
    Asks the user comprehension questions about the passage.
    """
    template_name = 'speed_read/comprehension.html'
    context = {}
    session = TrainingSession.get_current_session(request)
    if session is not None:
        context["questions"] = session.get_next_questions()
        return render(request, template_name, context)
    else:
        template_name = 'speed_read/initial.html'
        # this should be a safe redirect:
        # TODO should this redirect to results or initial?
        # or nowhere?
        # should these URLs have ids???
        return render(
            request, template_name,
            {"error_message" :
            "You need to start a new session."})


def results_view(request):    
    """
    Handles the results page and redirects back to exercises
    or passes control back to the initial website (i.e. ends).
    The layout of the page is:
    * results
    * (start next exercise OR continue)
    So we need to get the results, but then decide whether the link
    is back to another exercise, or continue on to another section
    """
    template_name = 'speed_read/results.html'
    context = {}
    session = TrainingSession.get_current_session(request)
    #there IS a session, so we're in the right place:
    if session is not None:
        context["results"] = session.get_next_results
        to_continue = session.get_continue_status
        next_link = {}
        if to_continue:
            next_link["href"] = "continue_href"
            next_link["name"] = "next exercise"
        else:
            next_link["href"] = "done_href"
            next_link["name"] = "continue"
        context["next_link"] = next_link
        return render(request, template_name, context)

    else:
        template_name = 'speed_read/initial.html'
        # this should be a safe redirect:
        # TODO should this redirect to results or initial?
        # or nowhere?
        # should these URLs have ids???
        return render(
            request, template_name,
            {"error_message" :
            "You need to start a new session."})

def exit_portal(request):
    return HttpResponse("this is the exit page")
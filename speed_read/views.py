from django.shortcuts import render
from django.views import generic

class SessionHandler(object):
    """
    This class is stored by a user's session (see Django docs) and
    handles a user's progression through speed reading training.
    When the training session begins, a SessionHandler object
    is created and immediately generates and 
    assigns exercises (see models.py).
    As the user completes their readings and comprehension
    questions, their progress is tracked here.
    """
    exercises = []
    def __init__(self, user):
        self.user = user

class InitialView(generic.TemplateView):
    """
    This is the entry point view.  It needs to see whether the
    user has done exercises before, and show one of two pages. 
    """

class PassageView(generic.TemplateView):
    """
    Handles the reading exercise and timing.
    """

class ComprehensionView(generic.TemplateView):
    """
    Asks the user comprehension questions about the passage.
    """


class ResultsView(generic.TemplateView):
    """
    Handles the results page and redirects back to exercises
    or passes control back to the initial website (i.e. ends).
    """

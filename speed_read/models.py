import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext as _, ugettext_lazy as __



class TrainingSession(models.Model):
    """
    This class is stored in the back end and
    handles a user's progression through a single
    session of speed reading training.  While it is stored as a model,
    it's more appropriate to think of this class (along with the 
    functions in the view) as the Controller.
    When the training session begins, a TrainingSession object
    is created and immediately generates and 
    assigns the first Exercise.
    As the user completes their readings and comprehension
    questions, their progress is tracked here.
    """
    ACCURACY_THRESHOLD = 0.5

    creation_time = models.DateTimeField(auto_now_add=True)
    # this is used to tell the user the last time they were working
    # on this session:
    last_modified = models.DateTimeField(auto_now=True)
    completion_time = models.DateTimeField(null=True)
    user = models.ForeignKey(User)
    active_exercise = models.ForeignKey('Exercise', null=True, default=None)

    is_complete = models.BooleanField(default=False)


    @staticmethod
    def find_training_session(request):
        """
        Finds the request's user and gets the current TrainingSession.
        TODO: should make some verifications here
        """
        sessions = TrainingSession.objects.filter(
            user=request.user, is_complete=False)
        if len(sessions) == 0:
            return None
        else:
            return sessions[0]

    @staticmethod
    def verify_request(request, session_id, exercise_id, section):
        """
        Verifies the request by comparing the
        session_id and exercise_id from the url (the inputs to this
        function) against the ones that can be found by checking for
        the request's session's user's TrainingSession, and also confirms
        that this section (passage|comprehension|results) is the one underway.
        """
        # checks whether this is the active section
        session = TrainingSession.find_training_session(request)
        if session is not None:
            exercise = session.active_exercise

            section_indices = ['passage', 'comprehension', 'results']
            active_section = section_indices.index(session.get_active_section())
            request_section = section_indices.index(section)
            visible = (active_section >= request_section)
            active = (active_section == request_section)


        else:
            exercise = None
            visible = False
            active = False




        return {'session': session,
                'exercise': exercise,
                'visible': visible,
                'active': active}

    def get_active_section(self):
        if self.active_exercise.passage_stop_time is None:
            return 'passage'
        elif self.active_exercise.completion_time is None:
            return 'comprehension'
        else:
            return 'results'

    def get_continue_status(self):
        """ 
        Returns True if the session should continue, False if the
        session is over.
        """
        return True

    def __str__(self):
        return "session: " + str(self.id) + " for user: " + str(self.user)


@python_2_unicode_compatible
class Passage(models.Model):
    """
    Stores a reading passage.
    It shouldn't change after it's created.
    """
    passage_title = models.CharField(default="", max_length=200)
    passage_text = models.TextField()
    words_in_passage = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return "Passage " + str(self.id) + ": " + self.passage_title

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to set
        the words_in_passage field.
        """
        self.words_in_passage = self.count_words(self.passage_text)
        #passing **kwargs threw an error
        super(Passage, self, *args).save()

    def count_words(self, passage_string):
        """
        Utility method to count the number of words.  Splits on
        whitespace and counts.
        """
        return len(passage_string.split())


class Exercise(models.Model):
    """
    An Exercise encapsulates the process of reading a passage and
    answering the relevent comprehension questions.  The main outcome
    metrics are the words_per_minute 'property' and the accuracy_percentage
    'property'.
    """
    passage = models.ForeignKey(Passage)
    training_session = models.ForeignKey(TrainingSession)
    questions = models.ManyToManyField(
        'ComprehensionQuestion', through='QuestionExercise')

    # Note: This is not time of creation, but rather the time when
    # the user starts reading it.  Time of creation is unecessary
    # because that is stored in the TrainingSession.
    passage_start_time = models.DateTimeField(null=True, default=None)
    passage_stop_time = models.DateTimeField(null=True, default=None)

    creation_time = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null = True, default=None)

    def start_passage(self):
        self.passage_start_time = timezone.now()
        self.save()

    def stop_passage(self):
        self.passage_stop_time = timezone.now()
        self.save()

    def completed(self):
        # this is how django implements auto_now. worth noting that this
        # means it's server time, not client time, so may take some
        # translation on the other side
        self.completion_time = timezone.now()
        self.save()

    def question_dictionary(self):
        dictionary = []
        for question_exercise in QuestionExercise.objects.filter(exercise=self):
            dictionary.append(question_exercise.toDictionary())
        return dictionary



    @property
    def is_complete(self):
        return (completion_time is not None)

    @property
    def duration_seconds(self):
        """Returns a non-integer number of seconds."""
        delta = self.passage_stop_time - self.passage_start_time
        return delta.total_seconds()

    @property
    def words_per_minute(self):
        """
        Calculates reading speed of the attempt in words per minute.
        """
        return (self.passage.words_in_passage
                * 60 #seconds per minute
                / self.duration_seconds)

    @property
    def comprehension_accuracy(self):
        """
        Returns the student's accuracy on the
        associated comprehension questions over the range [0, 1].
        """
        return None

    def __str__(self):
        return ("exercise: " + str(self.id) +
                " for " + str(self.training_session))




class ComprehensionQuestion(models.Model):
    """
    Comprehension questions are intended to be extremely simple
    questions that the student should be able to answer
    immediately after reading the passage.  Each passage should
    have 5-10 questions, and as currently designed an exercise
    will have a randomly selected subset of 5 of them.
    """
    passage = models.ForeignKey(Passage)
    text = models.TextField()
    exercises = models.ManyToManyField(Exercise, through='QuestionExercise')

class ComprehensionChoice(models.Model):
    question = models.ForeignKey(ComprehensionQuestion)
    correct = models.BooleanField(default=False)
    text = models.TextField()

    def toDictionary(self):
        return {'text': self.text, 'correct': self.correct}


class QuestionExercise(models.Model):
    """
    This is (obviously) an association class between Comprehension
    Questions and Exercises.  Notably, the status of the question
    (correct/incorrect/unattempted) within the exercise is stored here.
    """
    INCORRECT = 0
    CORRECT = 1
    UNATTEMPTED = 2
    STATUSES = {
        (INCORRECT, __('incorrect')),
        (CORRECT, __('correct')),
        (UNATTEMPTED, __('unattempted')),
    }
    question = models.ForeignKey(ComprehensionQuestion)
    exercise = models.ForeignKey(Exercise)
    status = models.SmallIntegerField(choices=STATUSES, default=UNATTEMPTED)

    def toDictionary(self):
        return {'id': self.id,
                'question_text': self.question.text,
                'status': self.status,
                'choices': [choice.toDictionary() for choice in
                    ComprehensionChoice.objects.filter(question=self.question)]}
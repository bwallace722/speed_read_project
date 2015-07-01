import datetime
import random

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
    EXERCISES_TO_COMPLETE = 5

    creation_time = models.DateTimeField(auto_now_add=True)
    # this is used to tell the user the last time they were working
    # on this session:
    last_modified = models.DateTimeField(auto_now=True)
    completion_time = models.DateTimeField(null=True)
    user = models.ForeignKey(User)
    active_exercise = models.ForeignKey('Exercise', null=True, default=None)
    accuracy_threshold = models.FloatField(default=ACCURACY_THRESHOLD)
    exercises_to_complete = models.SmallIntegerField(
        default=EXERCISES_TO_COMPLETE)


    @staticmethod
    def find_training_session(request):
        """
        Finds the request's user and gets the current TrainingSession.
        TODO: should make some verifications here
        """
        sessions = TrainingSession.objects.filter(
            user=request.user, completion_time=None)
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
        if session is not None and session.active_exercise is not None:
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

    def generate_exercise(self):
        # 1. choose a passage
        # we only exclude passages that have been used in THIS training
        # session, otherwise we could potentially run out of passages
        # with an avid user 
        used_passages = [ex.passage for ex in
            Exercise.objects.filter(training_session=self)]
        passages = [p for p in Passage.objects.all()] # if p not in used_passages]
        assert len(passages)
        passage = random.choice(passages)
        # 2. choose questions for the passage
        # TODO give it actual questions
        questions = ComprehensionQuestion.objects.filter(passage=passage)

        # 3. instantiate the exercise and attach it to the session,
        # attach the questions
        new_exercise = Exercise(passage=passage, training_session=self)
        new_exercise.save()
        self.active_exercise = new_exercise
        self.save()
        for q in questions:
            QuestionExercise(question=q, exercise=new_exercise).save()


    def get_active_section(self):
        if self.active_exercise.passage_stop_time is None:
            return 'passage'
        elif self.active_exercise.completion_time is None:
            return 'comprehension'
        else:
            return 'results'

    def check_completion(self):
        if self.completed_exercises >= self.exercises_to_complete:
            self.completion_time = timezone.now()
            self.save()

    @property
    def is_complete(self):
        print("self.completion_time", self.completion_time)
        return self.completion_time is not None

    @property
    def completed_exercises(self):
        return sum([1 for e in Exercise.objects.filter(training_session=self)
                        if e.success])

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

    @property
    def passage_instructions(self):
        return 'example instructions'


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

    def check_off(self, question_exercise, correct):
        if correct:
            question_exercise.status = QuestionExercise.CORRECT
        else:
            question_exercise.status = QuestionExercise.INCORRECT
        question_exercise.save()
        unanswered = [q for q in QuestionExercise.objects.filter(exercise=self)
                        if q.status == QuestionExercise.UNATTEMPTED]
        if len(unanswered) == 0:
            self.completion_time = timezone.now()
            self.training_session.check_completion()
            self.save()


    @property
    def passage_complete(self):
        return (self.passage_stop_time is not None)

    @property
    def passage_started(self):
        return (self.passage_start_time is not None)

    @property
    def is_complete(self):
        return (self.completion_time is not None)

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
        question_exercises = QuestionExercise.objects.filter(exercise=self)
        score = 0
        for qe in question_exercises:
            if qe.status == QuestionExercise.CORRECT:
                score += 1.0
        if len(question_exercises) > 0:
            score = score / len(question_exercises)
        return score

    @property
    def success(self):
        return self.comprehension_accuracy >= TrainingSession.ACCURACY_THRESHOLD


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
    @property
    def choices(self):
        return ComprehensionChoice.objects.filter(question=self)

    def __str__(self):
        return str(self.id) + ': ' + self.text

class ComprehensionChoice(models.Model):
    question = models.ForeignKey(ComprehensionQuestion)
    correct = models.BooleanField(default=False)
    text = models.TextField()

    def __str__(self):
        return self.question.text + ': ' + self.text


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
import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _, ugettext_lazy as __


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
        We overrides the default save method to set
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


class TrainingSession(models.Model):
    """
    A Training Session is the process of completing (e.g.)
    five exercises.
    """
    creation_time = models.DateTimeField()
    completion_time = models.DateTimeField(null=True)
    user = models.ForeignKey(User)


class Exercise(models.Model):
    """
    An Exercise encapsulates the process of reading a passage and
    answering the relevent comprehension questions.  The main outcome
    metrics are the words_per_minute 'property' and the accuracy_percentage
    'property'.
    """
    passage = models.ForeignKey(Passage)
    training_session = models.ForeignKey(TrainingSession)

    # Note: This is not time of creation, but rather the time when
    # the user starts reading it.  Time of creation is unecessary
    # because that is stored in the TrainingSession.
    start_time = models.DateTimeField(null=True)
    stop_time = models.DateTimeField(null=True)


    def __str__(self):
        return str(self.user) + ": " + str(self.words_per_minute) + " wpm"

    @property
    def duration_seconds(self):
        """Returns a non-integer number of seconds."""
        delta = self.stop_time - self.start_time
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
        pass


class ComprehensionQuestion(models.Model):
    """
    Comprehension questions are intended to be extremely simple
    questions that the student should be able to answer
    immediately after reading the passage.  Each passage should
    have 5-10 questions, and as currently designed an exercise
    will have a randomly selected subset of 5 of them.
    """
    passage = models.ForeignKey(Passage)
    exercises = models.ManyToManyField(Exercise, through='QuestionExercise')


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
    status = models.SmallIntegerField(choices=STATUSES)
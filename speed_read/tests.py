import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from models import *

class PassageModelTests(TestCase):

    def setUp(self):
        Passage.objects.create(passage_title="hi", passage_text="hi")
        Passage.objects.create(
            passage_title="hi hello", passage_text="hi hello")
        Passage.objects.create(
            passage_title="3", passage_text=
                "test            two __three__&& \n four")

    def test_to_string_without_error(self):
        hi = Passage.objects.get(passage_title="hi")
        self.assertEqual(str(hi), str(hi))

    def test_to_string(self):
        hi = Passage.objects.get(passage_title="hi")
        hi_id = str(hi.id)
        self.assertEqual(str(hi), "Passage " + hi_id + ": " + "hi")

    def test_one_word_count(self):
        hi = Passage.objects.get(passage_title="hi")
        self.assertEqual(hi.words_in_passage, 1)

    def test_two_word_count(self):
        hi_hello = Passage.objects.get(passage_title="hi hello")
        self.assertEqual(hi_hello.words_in_passage, 2)

    def test_tabs_and_newline(self):
        three = Passage.objects.get(passage_title="3")
        self.assertEqual(three.words_in_passage, 4)


class WordsPerMinuteTests(TestCase):
    # timedelta([days[, seconds[, 
    #    microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])

    def test_one_minute(self):
        now = datetime.datetime.now(pytz.utc)
        one_min = now + datetime.timedelta(0, 60)
        p = Passage.objects.create(
            passage_title="1", passage_text="one two three")
        u = User.objects.create()
        s = TrainingSession.objects.create(
            user=u, 
            creation_time=datetime.datetime.now(pytz.utc))
        a = Exercise.objects.create(
            passage=p, training_session=s,
            passage_start_time=now,
            passage_stop_time=one_min)
        self.assertEqual(a.words_per_minute, 3)

    def test_half_minute(self):
        now = datetime.datetime.now(pytz.utc)
        half_min = now + datetime.timedelta(0, 30)
        p = Passage.objects.create(
            passage_title="1", passage_text="one two three")
        u = User.objects.create()
        s = TrainingSession.objects.create(
            user=u, 
            creation_time=datetime.datetime.now(pytz.utc))
        a = Exercise.objects.create(
            passage=p, training_session=s,
            passage_start_time=now,
            passage_stop_time=half_min)
        self.assertEqual(a.words_per_minute, 6)


class TestBasicExercise(TestCase):
    def setUp(self):
        self.u = User.objects.create()
        self.session = TrainingSession.objects.create(user=self.u)
        self.passage1 = Passage.objects.create(passage_title='', passage_text='one')
        self.ex1 = Exercise.objects.create(passage=self.passage1, training_session=self.session)
        self.q1 = ComprehensionQuestion.objects.create(passage=self.passage1, text='')
        self.qe1 = QuestionExercise.objects.create(question=self.q1, exercise=self.ex1)
        self.q2 = ComprehensionQuestion.objects.create(passage=self.passage1, text='')
        self.qe2 = QuestionExercise.objects.create(question=self.q2, exercise=self.ex1)

    def test_ex1_unstarted(self):
        self.assertEqual(self.qe1.status, QuestionExercise.UNATTEMPTED)
        self.assertEqual(self.ex1.passage_start_time, None)
        self.assertEqual(self.ex1.passage_stop_time, None)
        self.assertFalse(self.ex1.passage_started)
        self.assertFalse(self.ex1.passage_complete)
        self.assertFalse(self.ex1.is_complete)

    def test_ex1_walk_through(self):
        #start the passage
        self.ex1.start_passage()
        self.assertTrue(self.ex1.passage_started)
        self.assertFalse(self.ex1.passage_complete)
        self.assertFalse(self.ex1.is_complete)
        #stop the passage
        self.ex1.stop_passage()
        self.assertTrue(self.ex1.passage_started)
        self.assertTrue(self.ex1.passage_complete)
        self.assertTrue(self.ex1.duration_seconds is not None)
        self.assertTrue(self.ex1.words_per_minute is not None)
        self.assertFalse(self.ex1.is_complete)
        #answer the first question -- not complete
        self.ex1.check_off(self.qe1, True)
        self.assertFalse(self.ex1.is_complete)
        #answer the second question -- now it's complete
        self.ex1.check_off(self.qe2, True)
        self.assertTrue(self.ex1.is_complete)
        #check comprehension accuracy and success
        self.assertEqual(self.ex1.comprehension_accuracy, 1.0)
        self.assertTrue(self.ex1.success, True)


class BasicTrainingSession(TestCase):
    def setUp(self):
        pass

    def test_manual_exercise(self):
        user1 = User.objects.create()
        session1 = TrainingSession.objects.create(user=user1, exercises_to_complete=1)
        passage1 = Passage.objects.create(passage_title='', passage_text='one')
        ex1 = Exercise.objects.create(passage=passage1, training_session=session1)
        q1 = ComprehensionQuestion.objects.create(passage=passage1, text='')
        qe1 = QuestionExercise.objects.create(question=q1, exercise=ex1)
        q2 = ComprehensionQuestion.objects.create(passage=passage1, text='')
        qe2 = QuestionExercise.objects.create(question=q2, exercise=ex1)
        #assign the artificial exercise
        session1.active_exercise = ex1
        #check before we read the passage
        self.assertFalse(session1.is_complete)
        self.assertEqual(session1.completed_exercises, 0)
        self.assertEqual(session1.get_active_section(), 'passage')
        #read the passage and check again
        ex1.start_passage()
        ex1.stop_passage()
        self.assertFalse(session1.is_complete)
        self.assertEqual(session1.completed_exercises, 0)
        self.assertEqual(session1.get_active_section(), 'comprehension')
        #answer the questions and check again
        ex1.check_off(qe1, True)
        ex1.check_off(qe2, True)
        self.assertEqual(session1.completed_exercises, 1)
        self.assertEqual(session1.get_active_section(), 'results')
        #should be completed now:
        session1.check_completion()
        self.assertTrue(session1.is_complete)


class BasicAutomatedTrainingSession(TestCase):
    def setUp(self):
        self.u = User.objects.create()
        self.session = TrainingSession.objects.create(user=self.u)
        self.passage1 = Passage.objects.create(passage_title='', passage_text='one')
        self.q1 = ComprehensionQuestion.objects.create(passage=self.passage1, text='')
        self.q2 = ComprehensionQuestion.objects.create(passage=self.passage1, text='')

    def test_automatic_exercise(self):
        self.session.generate_exercise()

        
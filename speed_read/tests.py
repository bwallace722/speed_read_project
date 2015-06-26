import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from models import Exercise, Passage, TrainingSession

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
            start_time=now,
            stop_time=one_min)
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
            start_time=now,
            stop_time=half_min)
        self.assertEqual(a.words_per_minute, 6)
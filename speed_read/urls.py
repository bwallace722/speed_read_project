from django.conf.urls import patterns, include, url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^home/$', views.initial_view, name='initial'),
    # landing page, link to here from expired pages, etc
    url(r'^landing/$', views.session_landing, name='landing'),
    # within an exercise -- passage view
    url(r'^(?P<session_id>[0-9]+)/(?P<exercise_id>[0-9]+)/(?P<section>passage|comprehension|results)/$',
        views.section_view, name='exercise'),
    url(r'^(?P<session_id>[0-9]+)/generate_exercise/$',
        views.generate_exercise_and_reroute, name='generate'),
    url(r'^(?P<session_id>[0-9]+)/(?P<exercise_id>[0-9]+)/passage_(?P<start_or_stop>start|stop)/$', 
        views.passage_time, name='passage_time'),
    url(r'^(?P<session_id>[0-9]+)/(?P<exercise_id>[0-9]+)/question_status/$', 
        views.question_status, name='question_status'),
    url(r'^exit/$', views.exit_portal, name='exit'),
]

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




    """
    template_name = 'speed_read/passage.html'
    context = {}
    session = TrainingSession.get_current_session(request)
    if session is not None:
        print(session)
        exercise = session.get_current_exercise()
        print(exercise)
    else:
        exercise = None
    # get the next passage to read
    # TODO: do something if it can't find the passage
    passage = Passage.objects.filter(exercise=exercise_id).get()

    # validate that the /session_id/exercise_id/ from the url are the same
    # as the current ones from the session object
    is_historical = (session is None or str(session.id) != session_id or
                     exercise is None or str(exercise.id) != exercise_id)
    print(is_historical)
    context = {"exercise" : exercise,
               "passage" : passage,
               "is_historical" : is_historical}
    """

        # template_name = 'speed_read/comprehension.html'
    # context = {}
    # session = TrainingSession.get_current_session(request)
    # if session is not None:
    #     context["questions"] = session.get_next_questions()
    #     return render(request, template_name, context)
    # else:
    #     template_name = 'speed_read/initial.html'
    #     # this should be a safe redirect:
    #     # TODO should this redirect to results or initial?
    #     # or nowhere?
    #     # should these URLs have ids???
    #     return render(
    #         request, template_name,
    #         {"error_message" :
    #         "You need to start a new session."})

        # template_name = 'speed_read/results.html'
    # context = {}
    # session = TrainingSession.get_current_session(request)
    # #there IS a session, so we're in the right place:
    # if session is not None:
    #     context["results"] = session.get_next_results
    #     to_continue = session.get_continue_status
    #     next_link = {}
    #     if to_continue:
    #         next_link["href"] = "continue_href"
    #         next_link["name"] = "next exercise"
    #     else:
    #         next_link["href"] = "done_href"
    #         next_link["name"] = "continue"
    #     context["next_link"] = next_link
    #     return render(request, template_name, context)

    # else:
    #     template_name = 'speed_read/initial.html'
    #     # this should be a safe redirect:
    #     # TODO should this redirect to results or initial?
    #     # or nowhere?
    #     # should these URLs have ids???
    #     return render(
    #         request, template_name,
    #         {"error_message" :
    #         "You need to start a new session."})

from django.contrib import admin
from .models import (TrainingSession, Exercise, Passage,
                    ComprehensionQuestion, ComprehensionChoice, 
                    QuestionExercise)

admin.site.register(TrainingSession)
admin.site.register(Exercise)
admin.site.register(Passage)
admin.site.register(ComprehensionQuestion)
admin.site.register(ComprehensionChoice)
admin.site.register(QuestionExercise)
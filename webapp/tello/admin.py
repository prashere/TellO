from django.contrib import admin

from tello.models import Teacher, Student, VocabularyCategory, VocabularyWord, StudentVocabulary, StudentReport, StorySession


# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(VocabularyCategory)
admin.site.register(VocabularyWord)
admin.site.register(StudentVocabulary)
admin.site.register(StudentReport)
admin.site.register(StorySession)

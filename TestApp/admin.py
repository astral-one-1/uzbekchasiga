from django.contrib import admin

# Register your models here.
from .models import Person, TestResult, TestModule, Question, Answer
admin.site.register(Person)
admin.site.register(TestResult)
admin.site.register(TestModule)
admin.site.register(Question)
admin.site.register(Answer)
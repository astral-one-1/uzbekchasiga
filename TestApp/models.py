from django.db import models
from django.utils import timezone
class Person(models.Model):
    ROLE_CHOISES = (
        ('admin', 'admin'),
        ('user', 'User'),
    )

    name = models.CharField(max_length=150)
    login = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOISES, default='user')
    vaqt = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.login

class TestModule(models.Model):
    title = models.CharField(max_length=150)  # test nomi
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=10)
    max_score = models.FloatField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TestResult(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    module = models.ForeignKey(TestModule, on_delete=models.CASCADE)    
    date = models.DateTimeField(auto_now_add = True)
    score = models.FloatField()
    def __str__(self):
        return f"{self.user.login} - {self.module.title} - {self.score}%"

class Question(models.Model):
    module = models.ForeignKey(TestModule, on_delete = models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)  # Variant matni
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
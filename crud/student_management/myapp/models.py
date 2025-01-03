from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[('Student', 'Student'), ('Teacher', 'Teacher')])

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Teacher'})

class Marks(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

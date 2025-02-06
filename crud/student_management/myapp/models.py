from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[('Student', 'Student'), ('Teacher', 'Teacher')])

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Marks(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

    def __str__(self):
        return f'{self.student.name} - {self.subject.name}: {self.marks}'

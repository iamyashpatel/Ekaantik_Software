from rest_framework import serializers
from .models import User, Subject, Marks

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'role']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher']  

class MarksSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)  

    class Meta:
        model = Marks
        fields = ['id', 'student', 'subject_name', 'marks']

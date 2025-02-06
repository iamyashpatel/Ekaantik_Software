from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import transaction
import json
from .models import User, Marks, Subject


def home(request):
    return HttpResponse("Welcome to the Student Management System!")


@method_decorator(csrf_exempt, name='dispatch')
def user_api(request, pk=None):
    if request.method == 'GET':
        if pk:
            try:
                user = User.objects.get(pk=pk)
                return JsonResponse({
                    'id': user.id,
                    'name': user.name,
                    'role': user.role,
                })
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            users = list(User.objects.values('id', 'name', 'role'))
            return JsonResponse(users, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            role = data.get('role')
            if not name or not role:
                return JsonResponse({'error': 'Both name and role are required'}, status=400)

            user = User.objects.create(name=name, role=role)
            return JsonResponse({'message': 'User created successfully', 'id': user.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'PUT':
        if not pk:
            return JsonResponse({'error': 'User ID is required for update'}, status=400)
        try:
            user = User.objects.get(pk=pk)
            data = json.loads(request.body)
            user.name = data.get('name', user.name)
            user.role = data.get('role', user.role)
            user.save()
            return JsonResponse({'message': 'User updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    elif request.method == 'DELETE':  # Delete a user
        if not pk:
            return JsonResponse({'error': 'User ID is required for deletion'}, status=400)
        try:
            with transaction.atomic():
                user = User.objects.get(pk=pk)
                user.delete()
            return JsonResponse({'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
def subject_api(request, pk=None):
    if request.method == 'GET':
        if pk:
            try:
                subject = Subject.objects.select_related('teacher').get(pk=pk)
                return JsonResponse({
                    'id': subject.id,
                    'name': subject.name,
                    'teacher_name': subject.teacher.name if subject.teacher else None
                })
            except Subject.DoesNotExist:
                return JsonResponse({'error': 'Subject not found'}, status=404)
        else:
            subjects = list(
                Subject.objects.select_related('teacher').values(
                    'id', 'name', 'teacher__name'
                )
            )
            for subject in subjects:
                subject['teacher_name'] = subject.pop('teacher__name', None)  # Rename key for clarity
            return JsonResponse(subjects, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            teacher_id = data.get('teacher_id')  # Expecting teacher_id in request
            
            if not name:
                return JsonResponse({'error': 'Subject name is required'}, status=400)
            if not teacher_id:
                return JsonResponse({'error': 'Teacher ID is required'}, status=400)

            # Check if the teacher exists
            try:
                teacher = User.objects.get(pk=teacher_id, role='Teacher')
            except User.DoesNotExist:
                return JsonResponse({'error': 'Teacher not found'}, status=404)
            
            # Create the subject
            subject = Subject.objects.create(name=name, teacher=teacher)
            return JsonResponse({'message': 'Subject created successfully', 'id': subject.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'PUT':
        if not pk:
            return JsonResponse({'error': 'Subject ID is required for update'}, status=400)
        
        try:
            subject = Subject.objects.get(pk=pk)
            data = json.loads(request.body)
            subject.name = data.get('name', subject.name)
            subject.save()
            return JsonResponse({'message': 'Subject updated successfully'})

        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=404)

    elif request.method == 'DELETE':
        if not pk:
            return JsonResponse({'error': 'Subject ID is required for deletion'}, status=400)
        
        try:
            subject = Subject.objects.get(pk=pk)
            subject.delete()
            return JsonResponse({'message': 'Subject deleted successfully'})

        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=404)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
def marks_api(request, pk=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('user_id')
            subject_name = data.get('subject')
            marks = data.get('marks')

            if not student_id or not subject_name or marks is None:
                return JsonResponse({'error': 'user_id, subject, and marks are required'}, status=400)

            # Retrieve the subject
            try:
                subject = Subject.objects.get(name=subject_name)
            except Subject.DoesNotExist:
                return JsonResponse({'error': 'Subject not found'}, status=404)

            student = User.objects.get(pk=student_id)
            mark_entry, created = Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={'marks': marks}
            )
            message = 'Marks added successfully' if created else 'Marks updated successfully'
            return JsonResponse({'message': message, 'id': mark_entry.id}, status=201 if created else 200)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        if pk:
            try:
                student = User.objects.get(pk=pk)
                marks = list(Marks.objects.filter(student=student).values('id', 'student__id', 'student__name', 'subject__name', 'marks'))
                return JsonResponse({'student': student.name, 'marks': marks})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            all_marks = list(Marks.objects.select_related('student').values(
                'id', 'student__id', 'student__name', 'subject__name', 'marks'
            ))
            return JsonResponse(all_marks, safe=False)

    elif request.method == 'DELETE':
        if not pk:
            return JsonResponse({'error': 'User ID is required for deletion'}, status=400)
        try:
            Marks.objects.filter(student_id=pk).delete()
            return JsonResponse({'message': 'Marks deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

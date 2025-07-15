from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from .models import Discipline, Group, Student, Grade


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'grades/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'grades/login.html')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    disciplines = Discipline.objects.filter(professors=request.user)
    selected_discipline = request.GET.get('discipline')
    selected_group = request.GET.get('group')

    context = {
        'disciplines': disciplines,
        'selected_discipline': int(selected_discipline) if selected_discipline else None,
        'groups': Group.objects.filter(discipline__id=selected_discipline) if selected_discipline else [],
        'selected_group': int(selected_group) if selected_group else None,
    }

    if selected_group:
        try:
            group_name = Group.objects.get(id=selected_group).name
        except Group.DoesNotExist:
            pass

        context = {
            'disciplines': disciplines,
            'selected_discipline': int(selected_discipline) if selected_discipline else None,
            'groups': Group.objects.filter(discipline__id=selected_discipline) if selected_discipline else [],
            'selected_group': int(selected_group) if selected_group else None,
            'selected_group_name': group_name,  # Добавляем название группы
        }
        grades = Grade.objects.filter(student__group_id=selected_group).select_related('student')
        date_columns = sorted({grade.date for grade in grades}, key=lambda x: x)

        students_data = []
        students = Student.objects.filter(group_id=selected_group).order_by('full_name')

        for student in students:
            student_grades = {grade.date: grade for grade in grades.filter(student=student)}

            processed_grades = []
            for date in date_columns:
                if date in student_grades:
                    processed_grades.append({
                        'date': date,
                        'value': student_grades[date].value,
                        'id': student_grades[date].id
                    })
                else:
                    processed_grades.append({
                        'date': date,
                        'value': None,
                        'id': None
                    })

            valid_grades = [g['value'] for g in processed_grades if g['value'] is not None]
            average = sum(valid_grades) / len(valid_grades) if valid_grades else 0

            students_data.append({
                'id': student.id,
                'name': student.full_name,
                'grades': processed_grades,
                'average': average
            })

        context.update({
            'date_columns': date_columns,
            'students_data': students_data
        })

    return render(request, 'grades/dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def add_grade(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            date = data.get('date')
            value = data.get('value')

            student = Student.objects.get(id=student_id)

            # Проверка доступа преподавателя
            if not Discipline.objects.filter(
                    professors=request.user,
                    group__in=[student.group]
            ).exists():
                return JsonResponse({'status': 'error', 'message': 'Нет доступа'})

            grade = Grade.objects.create(
                student=student,
                date=date,
                value=value
            )

            return JsonResponse({
                'status': 'success',
                'id': grade.id,
                'value': grade.value
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Неверный метод'})


@login_required
def update_grade(request):
    if request.method == 'POST':
        try:
            # Проверяем, что Content-Type является application/json
            if request.content_type != 'application/json':
                return JsonResponse({'status': 'error', 'message': 'Неверный Content-Type'}, status=400)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Неверный JSON'}, status=400)

            grade_id = data.get('grade_id')
            value = data.get('value')

            if not grade_id or value is None:
                return JsonResponse({'status': 'error', 'message': 'Отсутствуют обязательные параметры'}, status=400)

            grade = Grade.objects.get(id=grade_id)

            # Проверка доступа преподавателя
            if not Discipline.objects.filter(
                    professors=request.user,
                    group__in=[grade.student.group]
            ).exists():
                return JsonResponse({'status': 'error', 'message': 'Нет доступа'}, status=403)

            grade.value = value
            grade.save()

            return JsonResponse({'status': 'success'})

        except Grade.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Оценка не найдена'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Неверный метод'}, status=405)


@login_required
def delete_grade(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            grade_id = data.get('grade_id')

            grade = Grade.objects.get(id=grade_id)

            # Проверка доступа преподавателя
            if not Discipline.objects.filter(
                    professors=request.user,
                    group__in=[grade.student.group]
            ).exists():
                return JsonResponse({'status': 'error', 'message': 'Нет доступа'})

            grade.delete()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Неверный метод'})
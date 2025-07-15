from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Discipline(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название дисциплины")
    professors = models.ManyToManyField(User, verbose_name="Преподаватели")  # Изменили на ManyToManyField

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название группы")
    discipline = models.ManyToManyField(Discipline, verbose_name="Дисциплина")

class Student(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="ФИО студента")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент")
    date = models.DateField(verbose_name="Дата оценки")
    value = models.PositiveSmallIntegerField(verbose_name="Оценка")  # 1-5
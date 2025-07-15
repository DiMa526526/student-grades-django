from django.contrib import admin
from .models import Discipline, Group, Student, Grade


class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_professors')  # Заменили professor на display_professors

    def display_professors(self, obj):
        return ", ".join([professor.username for professor in obj.professors.all()])

    display_professors.short_description = 'Преподаватели'


admin.site.register(Discipline, DisciplineAdmin)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Grade)
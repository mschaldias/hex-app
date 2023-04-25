from django.contrib import admin
from .models import ToDoList, Task

# Register your models here.

admin.site.register(ToDoList)
admin.site.register(Task)
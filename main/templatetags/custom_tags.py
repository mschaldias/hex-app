from django import template
from main.models import Board,ToDoList,Task
register = template.Library()

@register.filter
def queryset(value):
    if isinstance(value,Board):
        return value.todolist_set.all()
    elif isinstance(value,ToDoList):
        return value.task_set.all()
    
    return None
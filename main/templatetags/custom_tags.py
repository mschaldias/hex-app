from django import template
from main.models import Board,ToDoList,Task
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def queryset(value):
    if isinstance(value,Board):
        return value.todolist_set.all()
    elif isinstance(value,ToDoList):
        return value.task_set.all()
    
    return 

@register.filter
@stringfilter
def remove_last_char(value):
    return value[:-1]

@register.filter(name='dict_key')
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    return d.get(k)

@register.filter
def load_style(styles,item):
    style = styles.get('weekday',None)
    if isinstance(item,Task):
        if item.hex or item.prev_hex:
            style = styles.get('hexlog')
        elif item.todolist.name in styles:
            style = styles[item.todolist.name]
        else:
            styles.get('weekday')
        
    
    return style

@register.filter
def item_text_load_onclick(items,item):
    function = f"toggle_edit('{items}','{item.id}')"
    if isinstance(item,Task):
        if item.hex or item.prev_hex:
            return ''
        return function
    
    return function
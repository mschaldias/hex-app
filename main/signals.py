from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Board,ToDoList 
 
@receiver(post_save, sender=User)
def create_board(sender, instance, created, **kwargs):
    if created:
        board = Board.objects.create(owner=instance,category='week',name='week board')
        board.todolist_set.create(name="archive")
        board.todolist_set.create(name="backlog")
        board.todolist_set.create(name="futurelog")
        board.initialize_week()

  

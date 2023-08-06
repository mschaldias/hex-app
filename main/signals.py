from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Board, Profile,ToDoList 
from django.contrib.auth import get_user_model
User = get_user_model()
 
@receiver(post_save, sender=User)
def create_board(sender, instance, created, **kwargs):
    if created:
        board = Board.objects.create(owner=instance,category='week',name='week board')
        board.todolist_set.create(name="archive")
        board.todolist_set.create(name="backlog",position=0)
        board.todolist_set.create(name="futurelog",position=1)
        board.hexable = True
        board.initialize_week()

  
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(owner=instance)

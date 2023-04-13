from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

# class Board(models.Model):
#     name = models.CharField(max_length=200)
#     user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)


#     def __str__(self):
#         return self.name

class ToDoList(models.Model):
    # board = models.ForeignKey(Board, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,blank=True)
    date = models.DateTimeField(null=True)
    
    def __str__(self):
        return f"{self.name} {self.date}"

class Item(models.Model):                       
    todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE,null=True)
    text = models.CharField(max_length=300,blank=True)
    complete = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ('position',)


    def set_todolist(self,todolist):
        self.due_date = todolist.date
        self.todolist = todolist
        self.save()
        
    
    def __str__(self):
        return self.text
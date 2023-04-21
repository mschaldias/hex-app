from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Board(models.Model):                       
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.category

class ToDoList(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,blank=True)
    date = models.DateTimeField(null=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ('position',)
    
    def __str__(self):
        return f"{self.name} {self.date}"

class Item(models.Model):                       
    todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    text = models.CharField(max_length=300,blank=True)
    complete = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('position',)
        
    
    def __str__(self):
        return self.text
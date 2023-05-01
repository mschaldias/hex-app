from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

# Create your models here.

class Board(models.Model):                       
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=200,default="New Board",blank=True)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.category
    
    def initialize_week(self,next_week=False):
        today = timezone.localtime()
        tz = today.tzinfo
        year, week_num, day_of_week = today.isocalendar()
        if next_week:
            week_num+=1

        for day_of_week in range(1,8):
            day_datetime = tz.localize(datetime.fromisocalendar(year,week_num,day_of_week))
            day_datetime = tz.localize(datetime.combine(day_datetime, datetime.max.time())) #sets time to 23:59 local time
            name = f"{day_datetime.strftime('%A')} {day_datetime.date()}"
            self.todolist_set.create(name=name,date=day_datetime)
        
        self.due_date = day_datetime
        self.save()

    def migrate_week(self,next_week=False):
        week_todolists = self.todolist_set.exclude(date=None)
        backlog = self.todolist_set.get(name="backlog")
        futurelog = self.todolist_set.get(name="futurelog")
        archive = self.todolist_set.get(name="archive")

        #move complete tasks to archive, move incomplete tasks to backlog
        archive(week_todolists,archive,backlog)
        week_todolists.delete()
        self.migrate_week(next_week)
        #assign futurelog tasks due this week to weekdays
        for task in futurelog.task_set.all():
            for todolist in week_todolists:
                if todolist.date == task.due_date:
                    task.todolist = todolist
                    task.save()
    
    def archive(self,todolists,archive,backlog=None):
        for todolist in todolists:
            for task in todolist.task_set.all():
                if task.complete:
                    task.todolist = archive
                else:
                    if backlog:
                        task.todolist = backlog
                task.save()


class ToDoList(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default="New List",blank=True)
    date = models.DateTimeField(null=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ('position',)
    
    def __str__(self):
        return f"{self.name}"

class Task(models.Model):                       
    todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    text = models.CharField(max_length=300,blank=True)
    complete = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ('position',)
        
    
    def __str__(self):
        return self.text
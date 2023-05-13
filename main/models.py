from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from main.custom_exceptions import IncorrectBoardCategoryError

# Create your models here.

class Board(models.Model):                       
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=200,default="New Board",blank=True)
    due_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.category
    
    def initialize_week(self,given_datetime=False,next_week=False):
        if self.category != 'week': raise IncorrectBoardCategoryError
        if not given_datetime:        
            given_datetime = timezone.localtime()
        tz = timezone.get_current_timezone()
        year, week_num, day_of_week = given_datetime.isocalendar()
        if next_week:
            week_num+=1
        self.start_date = (datetime.fromisocalendar(year,week_num,1)).astimezone(tz)
        for day_of_week in range(1,8):
            dt = (datetime.fromisocalendar(year,week_num,day_of_week)).astimezone(tz)
            date = dt.date()
            name = f"{date.strftime('%A')} {date}"
            self.todolist_set.create(name=name,date=date)
        
        dt = (datetime.combine(dt, datetime.max.time())).replace(tzinfo=tz) #sets dt to 23:59 local time
        self.due_date = dt
        self.save()

    def migrate_week(self,next_week=False,dt=None):
        if self.category != 'week': raise IncorrectBoardCategoryError
        week_todolists = self.todolist_set.exclude(date=None)

        #all complete tasks in board are moved to archive, 
        #tasks with due date up to datetime are moved to backlog
        #if datetime=None then all incomplete tasks in board are moved to backlog
        self.archive(week_todolists,datetime=dt)

        #if not migrating to next week and if board is already current week
        if not (next_week or self.start_date > timezone.now()):
            return      
       
        given_datetime=False
        if next_week:
            given_datetime = datetime.combine(self.start_date, datetime.min.time())
        week_todolists.delete()
        self.initialize_week(given_datetime=given_datetime,next_week=next_week)      
        return
    
    def archive(self,todolists,datetime=None):
        if self.category != 'week': raise IncorrectBoardCategoryError
        archive = self.todolist_set.get(name="archive")
        backlog = self.todolist_set.get(name="backlog")
        for todolist in todolists:
            for task in todolist.task_set.all():
                if task.complete:
                    task.todolist = archive
                elif datetime:
                    if task.due_date and task.due_date.astimezone(tz=timezone.get_current_timezone()) < datetime.astimezone(tz=timezone.get_current_timezone()):
                        task.todolist = backlog
                task.save()


class ToDoList(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default="New List",blank=True)
    date = models.DateField(null=True)
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
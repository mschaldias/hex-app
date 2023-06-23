from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from main.custom_exceptions import IncorrectBoardCategoryError
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator
from dateutil.relativedelta import relativedelta

# Create your models here.

class Board(models.Model):                       
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default="new board")
    category = models.CharField(max_length=200,default="main")
    due_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
    
    def initialize_week(self,given_datetime=None,next_week=False):
        if self.category != 'week': raise IncorrectBoardCategoryError
        #if not given a datetime automatically sets it to start of current week
        if not given_datetime:       
            given_datetime = timezone.localtime()
            year, week_num, day_of_week = given_datetime.isocalendar()
             
        year, week_num, day_of_week = given_datetime.isocalendar()
        if next_week:week_num+=1            
        day_of_week=1

        tz = timezone.get_current_timezone()
        self.start_date = (datetime.fromisocalendar(year,week_num,day_of_week)).replace(tzinfo=tz)
        for day_of_week in range(1,8):
            dt = (datetime.fromisocalendar(year,week_num,day_of_week)).replace(tzinfo=tz)
            date = dt.date()
            name = f"{date.strftime('%A')} {date}"
            self.todolist_set.create(name=name,date=date)
        
        dt = (datetime.combine(dt, datetime.max.time())).replace(tzinfo=tz) #sets dt to 23:59 local time
        self.due_date = dt
        self.save()

    def migrate_week(self,next_week=False,dt=None):
        if self.category != 'week': raise IncorrectBoardCategoryError
        week_todolists = self.todolist_set.exclude(date=None)
        futurelog = self.todolist_set.get(name="futurelog")
        backlog = self.todolist_set.get(name="backlog")
        tz = timezone.get_current_timezone()
        
        #board is in a future week and and we are migrating back to current week
        if (not next_week) and self.start_date > timezone.now():
                for week_todolist in week_todolists:
                    week_todolist.task_set.update(todolist=futurelog)
                week_todolists.delete()
                self.initialize_week(given_datetime=False,next_week=next_week) 
                for task in backlog.task_set.all():
                    if task.due_date:
                        if dt <= task.due_date <= self.due_date.astimezone(tz) :
                            task.todolist = week_todolists.get(date=task.due_date)
                        elif task.due_date > self.due_date.astimezone(tz) :
                            task.todolist = futurelog
                        task.save()
                
        #board is in current week and and we are backlogging incomplete tasks up to today and archiving current tasks
        elif not next_week:
            self.archive(week_todolists,datetime=dt)

        #migrate to next week
        else:
            #all complete tasks in board are moved to archive, 
            #tasks with due date up to datetime are moved to backlog
            self.archive(week_todolists,datetime=dt)
            
            week_todolists.delete()                
            self.initialize_week(next_week=next_week) 

            for task in futurelog.task_set.all():
                board_start_date = self.start_date.astimezone(tz)
                board_due_date = self.due_date.astimezone(tz)
                if task.due_date:
                    task_due_date = task.due_date.astimezone(tz)
                    if board_start_date <= task_due_date <= board_due_date:
                        week_day_todolist = self.todolist_set.get(date=task_due_date)
                        task.todolist = week_day_todolist
                        task.save()     
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
    name = models.CharField(max_length=200,default="new todolist")
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
    prev_date = models.DateTimeField(null=True)
    interval_value = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(100)],null=True)
    valid_interval_types = RegexValidator(r'^(days|weeks|months|years)$', "Only 'days','weeks','months' or 'years' are allowed.")
    interval_type = models.CharField(validators=[valid_interval_types],max_length=6,blank=True)


    class Meta:
        ordering = ('position',)
        
    def set_recurring(self,datetime=timezone.localtime()):
        if self.interval_type and self.interval_value:
            interval_type_options = ['days','weeks','months','years']
            kwargs = {x:self.interval_value for x in interval_type_options if x == self.interval_type}
            if self.complete:
                self.due_date = datetime + relativedelta(**kwargs)
                self.prev_date = datetime
                self.complete = False
                self.todolist = self.todolist.board.todolist_set.get(name='futurelog')
                self.save()

    
    def __str__(self):
        return self.text
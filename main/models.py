from random import choice
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from main.custom_exceptions import IncorrectBoardCategoryError
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator
from dateutil.relativedelta import relativedelta

# Create your models here.

class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    hex_streak = models.IntegerField(default=0,validators=[MinValueValidator(0)])

    def __str__(self):
        return f"owner:{self.owner}, streak: {self.hex_streak}"

class Board(models.Model):                       
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default="new board")
    category = models.CharField(max_length=200,default="main")
    due_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(null=True)
    hexable = models.BooleanField(default=False)

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

    def migrate_week(self,next_week=False,dt=None,now=timezone.now(),tz=timezone.get_current_timezone()):
        if self.category != 'week': raise IncorrectBoardCategoryError
        week_todolists = self.todolist_set.exclude(date=None)
        futurelog = self.todolist_set.get(name="futurelog")
        backlog = self.todolist_set.get(name="backlog")
        hexlog = self.todolist_set.get(name="hexlog")
        
        #board is in a future week and and we are migrating back to current week
        if (not next_week) and self.start_date > now:
                for week_todolist in week_todolists:
                    week_todolist.task_set.update(todolist=futurelog)
                week_todolists.delete()
                self.initialize_week(given_datetime=False,next_week=next_week)
                board_start_date = self.start_date.astimezone(tz)
                board_due_date = self.due_date.astimezone(tz)
                for task in backlog.task_set.all():
                    if task.due_date:
                        task_due_date = task.due_date.astimezone(tz)
                        if board_start_date <= task_due_date <= board_due_date :
                            task.todolist = week_todolists.get(date=task.due_date)
                        elif task_due_date > board_due_date:
                            task.todolist = futurelog
                        task.save()
                self.hexable = True
                self.save()
                
        #board is in current week and and we are backlogging incomplete tasks up to today and archiving complete tasks
        elif not next_week:
            logs = self.todolist_set.filter(name__in=['backlog','futurelog','hexlog'])
            self.archive(logs)
            self.archive(week_todolists,datetime=dt)
            self.hexable = True
            self.save()

        #migrate to next week
        else:
            #all complete tasks in board are moved to archive, 
            #tasks with due date up to datetime are moved to backlog
            self.archive(week_todolists,datetime=dt)
            backlog.task_set.filter(hex=True).update(todolist=hexlog)
            week_todolists.delete()                
            self.initialize_week(next_week=next_week,given_datetime=self.start_date) 

            for task in futurelog.task_set.all():
                board_start_date = self.start_date.astimezone(tz)
                board_due_date = self.due_date.astimezone(tz)
                if task.due_date:
                    task_due_date = task.due_date.astimezone(tz)
                    if board_start_date <= task_due_date <= board_due_date:
                        week_day_todolist = self.todolist_set.get(date=task_due_date)
                        task.todolist = week_day_todolist
                        task.save() 

            if not(self.start_date <= now <= self.due_date):  
                self.hexable = False
            self.save()  

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
                    if task.due_date and task.due_date.astimezone(tz=timezone.get_current_timezone()) <= datetime.astimezone(tz=timezone.get_current_timezone()):
                        task.todolist = backlog
                task.save()

    def hex(self):
        if self.category != 'week': raise IncorrectBoardCategoryError
        backlog = self.todolist_set.get(name="backlog")
        hexlog = self.todolist_set.get(name="hexlog")
        if self.hexable:
            tasks = list(backlog.task_set.filter(complete=False))
            if tasks:
                random_task = choice(tasks)
                random_task.todolist = hexlog
                random_task.due_date = self.due_date
                random_task.hex = True
                random_task.save()
                return True
        return False

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
    hex = models.BooleanField(default=False)
    prev_hex = models.BooleanField(default=False)
    next_task = models.OneToOneField('self',default=None,null=True,on_delete=models.SET_DEFAULT)


    class Meta:
        ordering = ('position',)

    def set_hex(self):
        profile = self.todolist.board.owner.profile
        if self.hex:
            if self.complete and not self.prev_hex:
                profile.hex_streak += 1
                self.hex = False
                self.prev_hex = True
        elif not self.complete and self.prev_hex:
                profile.hex_streak -=1
                profile.full_clean() #call to validator
                self.hex = True
                self.prev_hex = False
        
        self.save()  
        profile.save()
        
    def set_recurring(self,datetime=timezone.localtime()):
        if self.interval_type and self.interval_value:
            interval_type_options = ['days','weeks','months','years']
            interval_kwargs = {x:self.interval_value for x in interval_type_options if x == self.interval_type}
            if self.complete:
                if hasattr(self,'task'):
                    #if this instance is a previous task's next_task, set that task's next_task to None and move it to archive 
                    prev_task = self.task
                    prev_task.next_task = None
                    prev_task.todolist = self.todolist.board.todolist_set.get(name='archive')
                    prev_task.save()  
                #create next recurring task
                prev_date = datetime
                due_date = datetime + relativedelta(**interval_kwargs)
                task_kwargs = {'text':self.text,
                               'interval_type':self.interval_type,
                               'interval_value':self.interval_value,
                               'prev_date':prev_date,
                               'due_date':due_date}
                board = self.todolist.board   
                futurelog = board.todolist_set.get(name='futurelog')
                next_task = futurelog.task_set.create(**task_kwargs) 
                self.next_task = next_task
                week_day_todolist = board.todolist_set.filter(date=due_date.astimezone(timezone.get_current_timezone()).date())
                if week_day_todolist: next_task.todolist = week_day_todolist.first()
                next_task.save()

            else:
                if self.next_task:
                    task = self.next_task
                    self.next_task = None
                    task.delete()

            self.save()

    
    def __str__(self):
        return self.text
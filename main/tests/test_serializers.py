from django.test import TestCase
from django.contrib.auth.models import User
from main.custom_exceptions import IncorrectBoardCategoryError
from main.models import Board,ToDoList,Task
from django.db.models import Q
from main.serializers import BoardSerializer, TaskSerializer, ToDoListSerializer
from django.utils import timezone
from datetime import datetime, timedelta

timezones = ['America/New_York','America/Vancouver','America/Sao_Paulo','UTC']

class TaskSerializerTest(TestCase):
        
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='test_password')
        cls.board = Board.objects.get(owner=cls.user,category='week')
        cls.backlog = cls.board.todolist_set.get(name='backlog')
        cls.futurelog = cls.board.todolist_set.get(name='futurelog')
        
    def test_task_update_assigns_futurelog_task_to_backlog(self):

        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                task = Task.objects.create(todolist=self.futurelog,text='test text')
                now = timezone.localtime()
                datetime = now - timedelta(days=1)
                data = {'due_date':datetime}        

                ts = TaskSerializer(task,data=data,partial=True)
                if ts.is_valid():
                    ts.save()
                
                self.assertEqual(task.due_date,datetime)
                self.assertEqual(task.todolist,self.backlog)
            timezone.deactivate()

    def test_task_update_assigns_futurelog_task_to_weekday(self):

        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                task = Task.objects.create(todolist=self.futurelog,text='test text')
                now = timezone.localtime()
                board_due_date = self.board.due_date.astimezone(timezone.get_current_timezone())
                datetime = board_due_date - timedelta(seconds = 600) #set datetime to 10 minutes before board_due_date
                week_day_todolist = self.board.todolist_set.get(date=datetime.date())
                data = {'due_date':datetime}        

                ts = TaskSerializer(task,data=data,partial=True)
                if ts.is_valid():
                    ts.save()
                
                self.assertEqual(task.due_date,datetime)
                self.assertEqual(task.todolist, week_day_todolist)
            timezone.deactivate()

    def test_task_update_assigns_backlog_task_to_futurelog(self):

        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                task = Task.objects.create(todolist=self.backlog,text='test text')
                now = timezone.localtime()
                datetime = now + timedelta(weeks=1)
                data = {'due_date':datetime}
                
                ts = TaskSerializer(task,data=data,partial=True)
                if ts.is_valid():
                    ts.save()
                
                self.assertEqual(task.due_date,datetime)
                self.assertEqual(task.todolist,self.futurelog)
            timezone.deactivate()
    
    #Tests that when backlog task due_date is set to None, prev_date field is also set to None
    def test_backlog_task_prev_date_update(self):
        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                now = timezone.localtime()
                task = Task.objects.create(todolist=self.backlog,text='test text',prev_date=now)
                data = {'due_date':None}
                
                ts = TaskSerializer(task,data=data,partial=True)
                if ts.is_valid():
                    ts.save()
                
                self.assertEqual(task.todolist,self.backlog)
                self.assertEqual(task.due_date,None)
                self.assertEqual(task.prev_date,None)
                
            timezone.deactivate()


class BoardSerializerTest(TestCase):
    def test_board_create_week_raises_exception(self):
        data = {'category':'week'}
        board_serializer = BoardSerializer(data=data)
        with self.assertRaises(IncorrectBoardCategoryError):
           if board_serializer.is_valid():
               board_serializer.save()
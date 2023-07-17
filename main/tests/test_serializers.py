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
            self.board.initialize_week()
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

    def test_interval_updates(self):
        futurelog = self.futurelog
        task = Task.objects.create(todolist=futurelog,text='test text')
        data = {'interval_type':'weeks','interval_value':'1'}
        task_serializer = TaskSerializer(task, data = data,partial=True)

        self.assertTrue(task_serializer.is_valid())
        task_serializer.save()
        self.assertEqual(task.interval_type,'weeks')
        self.assertEqual(task.interval_value,1)

    def test_interval_updates_none(self):
        futurelog = self.futurelog
        task = Task.objects.create(todolist=futurelog,text='test text')
        data = {'interval_type':'','interval_value':None}
        task_serializer = TaskSerializer(task, data = data,partial=True)

        self.assertTrue(task_serializer.is_valid())
        task_serializer.save()
                
        self.assertEquals(task.interval_type,'')
        self.assertIsNone(task.interval_value)

    def test_complete_recurring_task(self):

        test_assign_futurelog = {'interval_type':'months', 
                                 'interval_value':2, 
                                 'weekday':'Monday',
                                 'expected_todolist': 'futurelog',
                                 'msg': 'test_assign_futurelog'
                                }        
        test_assign_weekday = {'interval_type':'days', 
                                'interval_value':1, 
                                'weekday':'Wednesday',
                                'expected_todolist': 'Thursday',
                                'msg': 'test_assign_weekday'
                                }
        tests = [test_assign_futurelog,test_assign_weekday]
        
        for test in tests:
            with self.subTest(msg=f"{test['msg']}", test=test):
                expected_todolist = self.board.todolist_set.get(name__startswith=test['expected_todolist'])
                task_create_params={'interval_type':test['interval_type'],'interval_value':test['interval_value']}
                weekday_todolist = self.board.todolist_set.get(name__startswith=test['weekday'])
                task = weekday_todolist.task_set.create(text = f"{test['weekday']} Test", **task_create_params)
                data = {'complete':True}
                year,week_num,_ = timezone.localtime().isocalendar()
                #set current_datetime to current week's Wednesday
                current_datetime = (datetime.fromisocalendar(year,week_num,3)).replace(tzinfo=timezone.get_current_timezone())
                task_serializer = TaskSerializer(task, data = data,context={'current_datetime':current_datetime} ,partial=True)

                self.assertTrue(task_serializer.is_valid())
                task_serializer.save()
                self.assertEqual(task.next_task.todolist,expected_todolist)

class BoardSerializerTest(TestCase):
    def test_board_create_week_raises_exception(self):
        data = {'category':'week'}
        board_serializer = BoardSerializer(data=data)
        with self.assertRaises(IncorrectBoardCategoryError):
           if board_serializer.is_valid():
               board_serializer.save()
import random
from django.test import TestCase
from django.contrib.auth.models import User
from main.custom_exceptions import IncorrectBoardCategoryError
from main.models import Board,ToDoList,Task
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

timezones = ['America/New_York','America/Vancouver','America/Sao_Paulo','UTC']
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test_password')

    def test_new_user_has_week_board(self):
        board = self.user.board_set.get(category='week')
        
        #checks archive,backlog and futurelog todolists are created
        qs = board.todolist_set.filter(Q(name='archive') | Q(name='backlog') | Q(name='futurelog'),date=None)
        self.assertEqual(qs.count(),3)
        
        #board has 7 weekday todolists with dates
        self.assertEqual(board.todolist_set.exclude(date=None).count(),7)


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='test_password')
        cls.week_board = cls.user.board_set.get(category='week')
        cls.futurelog = cls.week_board.todolist_set.get(name = 'futurelog')

    def test_set_recurring(self):
        kwargs = {'months':2}
        task = self.futurelog.task_set.create(text='test',complete=True,interval_type='months',interval_value=2)
        datetime = timezone.localtime()
        task.set_recurring(datetime=datetime)

        self.assertEqual(task.prev_date,datetime)
        self.assertEqual(task.due_date,datetime + relativedelta(**kwargs))
        self.assertFalse(task.complete)

        
class BoardModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='test_password')
        cls.week_board = cls.user.board_set.get(category='week')     
        cls.board = Board.objects.create(owner=cls.user,category='main')
        
    def test_dates_are_none_before_initialize(self):
        self.assertIsNone(self.board.start_date)
        self.assertFalse(self.board.due_date)

    def test_initialize_non_week_raises_exception(self):
        with self.assertRaises(IncorrectBoardCategoryError):
            self.board.initialize_week()
    
    def test_initialize_week_succeeds(self):
        
        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                #creating a user sends a signal to call initialize_week()    
                # so week_board todolists are deleted to test initialize_week directly  
                self.week_board.todolist_set.exclude(date=None).delete() 
                tz = timezone.get_current_timezone()
                
                year, week_num, day_of_week = timezone.localtime().isocalendar()
                expected_start_date = (datetime.fromisocalendar(year,week_num,1)).replace(tzinfo=tz)
                expected_due_date = (datetime.fromisocalendar(year,week_num,7)).replace(tzinfo=tz)
                expected_due_date = (datetime.combine(expected_due_date, datetime.max.time())).replace(tzinfo=tz)
                self.week_board.initialize_week()

                self.assertEquals(self.week_board.start_date,expected_start_date)
                self.assertEquals(self.week_board.due_date,expected_due_date)
                self.assertGreater(self.week_board.due_date,self.week_board.start_date)
                self.assertEqual(self.week_board.todolist_set.exclude(date=None).count(),7)

        timezone.deactivate()
        
    def test_archive(self):
        todolists = self.week_board.todolist_set.exclude(name='archive')
        archive = self.week_board.todolist_set.get(name='archive')
        count = archive.task_set.count()
        self.assertEqual(count,0)
        for todolist in todolists:
            todolist.task_set.create(text=f"task in {todolist}",complete=True)
            count +=1
        self.assertEqual(todolists.count(),9)
        self.week_board.archive(todolists)
        self.assertEqual(archive.task_set.count(),count)

    def test_archive_datetime(self):

        for tz in timezones:
            timezone.activate(tz)
            with self.subTest(msg=f"Testing with timezone {tz}", tz=tz):
                todolists = self.week_board.todolist_set.exclude(name='archive')
                archive = self.week_board.todolist_set.get(name='archive')
                backlog = self.week_board.todolist_set.get(name='backlog')
                futurelog = self.week_board.todolist_set.get(name='futurelog')
                now = timezone.now()

                backlog.task_set.create(text = "test in backlog", due_date = now)
                futurelog.task_set.create(text  = "test in futurelog", due_date = now + timedelta(weeks=3))
                count = backlog.task_set.count()

                for todolist in todolists.exclude(date=None):
                    due_date = (datetime.combine(todolist.date, datetime.min.time())).replace(tzinfo=timezone.get_current_timezone())
                    todolist.task_set.create(text=f"task in {todolist}",due_date=due_date)
                    count+=1
                self.assertEqual(todolists.exclude(date=None).count(),7)
                self.week_board.archive(todolists,datetime=self.week_board.due_date)
                self.assertEqual(archive.task_set.count(),0)
                self.assertEqual(backlog.task_set.count(),count)
            timezone.deactivate()

    def test_migrate_next_week(self):
        futurelog = self.week_board.todolist_set.get(name='futurelog')
        backlog = self.week_board.todolist_set.get(name='backlog')
        weekday_todolists = self.week_board.todolist_set.exclude(date=None)

        tz = timezone.get_current_timezone()
        localtime = timezone.localtime()
        year, week_num, day_of_week = localtime.isocalendar()
    
        datetime_weeks_away = (datetime.fromisocalendar(year,week_num+2,random.randint(1, 7))).replace(tzinfo=tz)
        datetime_next_week = (datetime.fromisocalendar(year,week_num+1,random.randint(1, 7))).replace(tzinfo=tz)

        futurelog_task1 = futurelog.task_set.create(text=f"task in should remain in futurelog",due_date=datetime_weeks_away)
        futurelog_task2 = futurelog.task_set.create(text=f"task that should be assigned to migrated week day",due_date=datetime_next_week)
        backlog_task = backlog.task_set.create(text=f"old backlog task")

        incomplete_weekday_tasks = []
        for todolist in weekday_todolists:
            due_date = (datetime.combine(todolist.date, datetime.min.time())).replace(tzinfo=timezone.get_current_timezone())
            task = todolist.task_set.create(text=f"task in {todolist} should go to backlog",due_date=due_date)
            incomplete_weekday_tasks.append(task)
        
        self.week_board.migrate_week(next_week=True,dt=self.week_board.due_date)

        # task1 should be in futurelog
        self.assertIn(futurelog_task1, futurelog.task_set.all())

        # backlog_task should be in backlog
        self.assertIn(backlog_task, backlog.task_set.all())

        # all tasks in incomplete_week_day_tasks should be in backlog
        for task in incomplete_weekday_tasks:
            self.assertIn(task,backlog.task_set.all())

        # task2 should be in weekday with date datetime_next_week
        self.assertIn(futurelog_task2,weekday_todolists.get(date=datetime_next_week).task_set.all())
        


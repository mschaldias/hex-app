import random
from django.test import TestCase
from main.custom_exceptions import IncorrectBoardCategoryError
from main.models import Board,ToDoList,Task
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
User = get_user_model()

timezones = ['America/New_York','America/Vancouver','America/Sao_Paulo','UTC']
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test', password='test_password')

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
        cls.user = User.objects.create_user(email='test', password='test_password')
        cls.week_board = cls.user.board_set.get(category='week')
        cls.futurelog = cls.week_board.todolist_set.get(name = 'futurelog')
        cls.archive = cls.week_board.todolist_set.get(name = 'archive')

    def test_set_recurring(self):
        kwargs = {'months':2}
        task = self.futurelog.task_set.create(text='test',complete=True,interval_type='months',interval_value=2)
        datetime = timezone.localtime()
        task.set_recurring(datetime=datetime)
        next_task = task.next_task

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.prev_date,datetime)
        self.assertEqual(next_task.due_date,datetime + relativedelta(**kwargs))
        self.assertFalse(next_task.complete)

    def test_set_recurring_incomplete(self):
        task = self.futurelog.task_set.create(text='test',complete=True,interval_type='months',interval_value=2)
        datetime = timezone.localtime()
        task.set_recurring(datetime=datetime)
        task.complete = False
        task.set_recurring(datetime=datetime)

        self.assertIsNone(task.next_task)

    def test_set_recurring_archive(self):
        task = self.futurelog.task_set.create(text='test',complete=True,interval_type='months',interval_value=2)
        datetime = timezone.localtime()
        task.set_recurring(datetime=datetime)
        next_task = task.next_task
        next_task.complete = True
        next_task.set_recurring(datetime=datetime)

        self.assertIn(task,self.archive.task_set.all())
        self.assertTrue(next_task.complete)

    def test_set_hex_complete(self):

        task = self.futurelog.task_set.create(text='test',complete=True,hex=True)
        task.set_hex()

        self.assertFalse(task.hex)
        self.assertTrue(task.prev_hex)
        self.assertTrue(task.complete)
        self.assertEquals(self.user.profile.hex_streak,1)

    def test_set_hex_prev_hex_incomplete(self):

        task = self.futurelog.task_set.create(text='test',complete=False,hex=False,prev_hex=True)
        self.user.profile.hex_streak = 1
        self.user.profile.save()
        task.set_hex()

        self.assertTrue(task.hex)
        self.assertFalse(task.prev_hex)
        self.assertFalse(task.complete)
        self.assertEquals(self.user.profile.hex_streak,0)
        
class BoardModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='test', password='test_password')
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

    def test_migrate_forward(self):
        true_now = timezone.now()
        fake_now = true_now + timedelta(weeks=4)
        self.week_board.migrate_week(forward=True,dt=self.week_board.due_date,now=fake_now)

        _, this_week_num, _ = true_now.isocalendar()
        expected_week_num = this_week_num + 4
        _,board_week_num,_ = self.week_board.start_date.isocalendar()

        self.assertEqual(expected_week_num,board_week_num)

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
        
        self.week_board.migrate_week(forward=True,next_week=True,dt=self.week_board.due_date)

        # task1 should be in futurelog
        self.assertIn(futurelog_task1, futurelog.task_set.all())

        # backlog_task should be in backlog
        self.assertIn(backlog_task, backlog.task_set.all())

        # all tasks in incomplete_week_day_tasks should be in backlog
        for task in incomplete_weekday_tasks:
            self.assertIn(task,backlog.task_set.all())

        # task2 should be in weekday with date datetime_next_week
        self.assertIn(futurelog_task2,weekday_todolists.get(date=datetime_next_week).task_set.all())

    def test_hex(self):
        backlog = self.week_board.todolist_set.get(name='backlog')
        today_todolist = self.week_board.todolist_set.get(date=timezone.localdate())

        task1 = backlog.task_set.create(text='task1')
        task2 = backlog.task_set.create(text='task2')

        expected_backlog_count = backlog.task_set.count()-1
        expected_today_todolist_count = today_todolist.task_set.count()+1

        self.assertTrue(self.week_board.hex(timezone.localdate()))
        self.assertEquals(backlog.task_set.count(),expected_backlog_count)
        self.assertEquals(today_todolist.task_set.count(),expected_today_todolist_count)
        


from django.test import TestCase
from django.contrib.auth.models import User
from main.custom_exceptions import IncorrectBoardCategoryError
from main.models import Board,ToDoList,Task
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

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


class BoardModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='test_password')
        cls.week_board = cls.user.board_set.get(category='week')     
        cls.board = Board.objects.create(owner=cls.user,category='main')
        
    def test_dates_are_none_before_initialize(self):
        self.week_board.todolist_set.all().delete() 
        self.assertIsNone(self.board.start_date)
        self.assertFalse(self.board.due_date)

    def test_initialize_non_week_raises_exception(self):
        with self.assertRaises(IncorrectBoardCategoryError):
            self.board.initialize_week()
    
    def test_initialize_week_succeeds(self):
        #creating a user sends a signal to call initialize_week()    
        # so week_board todolists are deleted to test initialize_week directly  
        self.week_board.todolist_set.all().delete() 
        self.week_board.initialize_week()
        self.assertIsNotNone(self.week_board.start_date)
        self.assertIsNotNone(self.week_board.due_date)
        self.assertGreater(self.week_board.due_date,self.week_board.start_date)
        self.assertEqual(self.week_board.todolist_set.exclude(date=None).count(),7)
        
    def test_archive(self):
        todolists = self.week_board.todolist_set.exclude(name='archive')
        archive = self.week_board.todolist_set.get(name='archive')
        count = archive.task_set.count()
        self.assertEqual(count,0)
        for todolist in todolists:
            todolist.task_set.create(text=f"task in {todolist}",complete=True)
            count +=1
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
                    due_date = (datetime.combine(todolist.date, datetime.min.time())).astimezone(tz=timezone.get_current_timezone())
                    todolist.task_set.create(text=f"task in {todolist}",due_date=due_date)
                    count+=1
                
                self.week_board.archive(todolists,datetime=self.week_board.due_date)
                self.assertEqual(archive.task_set.count(),0)
                self.assertEqual(backlog.task_set.count(),count)
            timezone.deactivate()

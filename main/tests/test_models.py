from django.test import TestCase
from django.contrib.auth.models import User
from main.custom_exceptions import IncorrectBoardCategoryError
from main.models import Board,ToDoList,Task
from django.db.models import Q


class UserModelTest(TestCase):
    @classmethod
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
        user = User.objects.create_user(username='test', password='test_password')
        Board.objects.create(owner=user,category='main')

    def test_dates_are_none_before_initialize(self):
        board = Board.objects.get(category='main')
        self.assertIsNone(board.start_date)
        self.assertFalse(board.due_date)

    def test_initialize_non_week_raises_exception(self):
        board = Board.objects.get(category='main')
        with self.assertRaises(IncorrectBoardCategoryError):
            board.initialize_week()
    
    def test_initialize_week_succeeds(self):
        week_board = Board.objects.get(category='week')  
        #creating a user sends a signal to call initialize_week()    
        # so we week_board todolists are deleted to test initialize_week directly  
        week_board.todolist_set.all().delete()
        week_board.initialize_week()
        self.assertIsNotNone(week_board.start_date)
        self.assertIsNotNone(week_board.due_date)
        self.assertGreater(week_board.due_date,week_board.start_date)
        self.assertEqual(week_board.todolist_set.exclude(date=None).count(),7)

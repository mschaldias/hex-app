from datetime import timedelta
from django.test import Client
from django.test import TestCase
from main.models import Board,ToDoList,Task
from main.serializers import TaskSerializer
from http import HTTPStatus
from django.utils import timezone
from main.views import week_utils

from django.contrib.auth import get_user_model
User = get_user_model()


#TODO test that any can access home page
#TODO test that only authenticated user can access Boards and Week pages
#TODO test if templates are correct?

class WeekUtilsTest(TestCase):

    @classmethod
    def setUpTestData(cls):       
        cls.user = User.objects.create_user(email='test', password='test_password')
        cls.board = cls.user.board_set.get(category='week')

    def test_set_zero_streak(self):
        self.user.profile.hex_streak = 100
        self.user.profile.save()
        board = self.board
        backlog = board.todolist_set.get(name="backlog")
        task = backlog.task_set.create()
        board.hex()

        week_utils(board,timezone.now()+timedelta(weeks=1))

        self.assertEquals(self.user.profile.hex_streak,0)
        self.assertFalse(task.hex)
        self.assertFalse(task.prev_hex)
        self.assertFalse(task.complete)
        self.assertIn(task,backlog.task_set.all())

class TasksViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):       
        cls.user = User.objects.create_user(email='test', password='test_password')
        cls.user.board_set.create(category='main')
        
    def setUp(self):
        main_board = self.user.board_set.get(category='main')
        self.todolist = main_board.todolist_set.create(name='test_todolist')

    def tearDown(self):
        self.todolist.delete()

    def test_get_tasks(self):
        self.client.login(email='test', password='test_password')
        todolist_id = self.todolist.id
        task1 = self.todolist.task_set.create(text = 'test_task1')
        task2= self.todolist.task_set.create(text = 'test_task2')
        response = self.client.get('/api/tasks/')
        expected_data = [TaskSerializer(task1).data,TaskSerializer(task2).data]
                  
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data,expected_data)

    def test_post_task(self):
        self.client.login(email='test', password='test_password')
        todolist_id = self.todolist.id
        data = {'todolist': todolist_id} 
               
        response = self.client.post('/api/tasks/',data)
    
        task_id = response.data.get('id',None)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(self.todolist.task_set.filter(id=task_id))
        self.assertEqual(self.todolist.task_set.count(),1)

    def test_delete_task(self):
        self.client.login(email='test', password='test_password')
        task1 = self.todolist.task_set.create(text = 'test_task1')
        response = self.client.delete(f"/api/tasks/{task1.id}")
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(self.todolist.task_set.count(),0)

    def test_put_task(self):
        self.client.login(email='test', password='test_password')
        task1 = self.todolist.task_set.create(text = 'test_task1')
        datetime = timezone.now()
        data = {'id':task1.id,'text':'test text','due_date':datetime}
        response = self.client.put(f"/api/tasks/{task1.id}",data, content_type='application/json')          
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['id'],task1.id)



#TODO check api requests
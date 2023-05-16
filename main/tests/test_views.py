from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Board,ToDoList,Task
from main.serializers import TaskSerializer
from http import HTTPStatus
from django.utils import timezone


#TODO test that any can access home page
#TODO test that only authenticated user can access Boards and Week pages
#TODO test if templates are correct?

class TasksViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):       
        cls.user = User.objects.create_user(username='test', password='test_password')
        cls.user.board_set.create(category='main')
        
    def setUp(self):
        main_board = self.user.board_set.get(category='main')
        self.todolist = main_board.todolist_set.create(name='test_todolist')

    def tearDown(self):
        self.todolist.delete()

    def test_get_tasks(self):
        self.client.login(username='test', password='test_password')
        todolist_id = self.todolist.id
        task1 = self.todolist.task_set.create(text = 'test_task1')
        task2= self.todolist.task_set.create(text = 'test_task2')
        response = self.client.get('/api/tasks/')
        expected_data = [TaskSerializer(task1).data,TaskSerializer(task2).data]
                  
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data,expected_data)

    def test_post_task(self):
        self.client.login(username='test', password='test_password')
        todolist_id = self.todolist.id
        data = {'todolist': todolist_id} 
               
        response = self.client.post('/api/tasks/',data)
    
        task_id = response.data.get('id',None)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(self.todolist.task_set.filter(id=task_id))
        self.assertEqual(self.todolist.task_set.count(),1)

    def test_delete_task(self):
        self.client.login(username='test', password='test_password')
        task1 = self.todolist.task_set.create(text = 'test_task1')
        response = self.client.delete(f"/api/tasks/{task1.id}")
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(self.todolist.task_set.count(),0)

    def test_put_task(self):
        self.client.login(username='test', password='test_password')
        task1 = self.todolist.task_set.create(text = 'test_task1')
        datetime = timezone.now()
        data = {'id':task1.id,'text':'test text','due_date':datetime}
        response = self.client.put(f"/api/tasks/{task1.id}",data, content_type='application/json')          
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['id'],task1.id)



#TODO check api requests
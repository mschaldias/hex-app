from rest_framework import serializers
from main.custom_exceptions import IncorrectBoardCategoryError
from .models import Board,ToDoList,Task
from django.utils import timezone
from datetime import datetime

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'todolist', 'text', 'complete', 'due_date' ,'position','interval_type','interval_value')

    def update(self,instance,validated_data): 
        board = instance.todolist.board
        current_datetime = self.context.get('current_datetime')
        super().update(instance, validated_data)  
        if board.category == 'week':
            if not current_datetime: current_datetime = timezone.localtime()
            current_date = current_datetime.date()
            validated_data_keys = validated_data.keys()

            if 'complete' in validated_data_keys:
                instance.set_hex()
                if instance.interval_type and instance.interval_value:
                    instance.set_recurring(datetime=current_datetime)   

            if ('interval_type' in validated_data_keys and 'interval_value' in validated_data_keys):
                instance.set_recurring(datetime=current_datetime)

            todolist = instance.todolist
            due_date = instance.due_date
            #if due_date is in data but is None then task date is being cleared and prev_date is also set to None
            if 'due_date' in validated_data_keys:
                if todolist.name == 'backlog' and not due_date:
                    instance.prev_date=None
            if due_date and not instance.complete:                
                if todolist.name == 'backlog': 
                    #if backlog task due_date is changed to after board due_date, task is assigned to futurelog
                    if due_date.date() > board.due_date.date():
                        futurelog = board.todolist_set.get(name='futurelog')
                        instance.todolist = futurelog
                elif todolist.name == 'futurelog':
                    #if futurelog task due_date is changed to be in the past, task is assigned to backlog
                    if due_date.date() < current_date:
                        backlog = board.todolist_set.get(name='backlog')
                        instance.todolist = backlog

                #if futurelog/backlog task due_date is between now and board.due_date then assign to week day
                if todolist.name == 'backlog' or todolist.name == 'futurelog':
                    if current_date <= due_date.date() <= board.due_date.astimezone(timezone.get_current_timezone()).date():
                        week_day_todolist = board.todolist_set.get(date=due_date.astimezone(timezone.get_current_timezone()).date())
                        instance.todolist = week_day_todolist
   
        instance.save()    
        return instance



class ToDoListSerializer(serializers.ModelSerializer):

    # user = serializers.ReadOnlyField(source='user.username')
    task_set = serializers.PrimaryKeyRelatedField(queryset = Task.objects.all(),many=True,required=False)
    
    class Meta:
        model = ToDoList
        fields = ('id','board','name','task_set','date')

    def update(self,instance,validated_data):
        board = instance.board
        name = instance.name
        board_category = board.category

        position = 0
        for task in validated_data.get('task_set',[]):
            if task.todolist in board.todolist_set.all():
                #tasks moved into futurelog or backlog from another todolist have their due_dates set to None
                if task.todolist != instance and board_category == 'week' and (name == 'futurelog' or name == 'backlog'):
                    if name == 'backlog':
                        task.prev_date = task.due_date
                    else:
                        task.prev_date = None

                    task.due_date = None 
                task.position = position
                task.todolist = instance
                if instance.date:
                    if not (task.hex or task.prev_hex):
                        task.due_date = (datetime.combine(instance.date, datetime.min.time())).replace(tzinfo=timezone.get_current_timezone())
                position+=1
                task.save()

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    
class BoardSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='user.username')
    todolist_set = serializers.PrimaryKeyRelatedField(queryset = ToDoList.objects.all(),many=True,required=False)
    
    class Meta:
        model = Board
        fields = ('id','owner','category','todolist_set','name')

    def create(self, validated_data):
        category = validated_data.get('category')
        if category == 'week':
            raise IncorrectBoardCategoryError
        else:
            return super().create(validated_data)  

    def update(self,instance,validated_data):
        user = self.context['user']

        position = 0
        for todolist in validated_data.get('todolist_set',[]):
            if todolist.board in user.board_set.all():
                todolist.position = position
                todolist.board = instance
                position+=1
                todolist.save()

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
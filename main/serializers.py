from rest_framework import serializers
from main.custom_exceptions import IncorrectBoardCategoryError
from .models import Board,ToDoList,Task
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.validators import RegexValidator


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'todolist', 'text', 'complete', 'due_date' ,'position','interval_type','interval_value')

    def update(self,instance,validated_data): 
        board = instance.todolist.board
        super().update(instance, validated_data)  
        if board.category == 'week':
            current_timezone = self.context.get('current_timezone', timezone.get_current_timezone())
            current_datetime = self.context.get('current_datetime', timezone.localtime())
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
            if due_date: due_date = due_date.astimezone(current_timezone)
            board_due_date = board.due_date.astimezone(current_timezone)
            #if due_date is in data but is None then task date is being cleared and prev_date is also set to None
            if 'due_date' in validated_data_keys:
                if todolist.name == 'backlog' and not due_date:
                    instance.prev_date=None
            if due_date and not instance.complete:                

                if due_date > board_due_date:
                    futurelog = board.todolist_set.get(name='futurelog')
                    instance.todolist = futurelog

                elif due_date.date() < current_date:
                    backlog = board.todolist_set.get(name='backlog')
                    instance.todolist = backlog

                else:
                    week_day_todolist = board.todolist_set.get(date=due_date.date())
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
    valid_actions = RegexValidator(r'^(hex|current week|migrate)$', "Only 'hex','current week' or 'migrate' are allowed.")
    action = serializers.CharField(validators=[valid_actions],required=False)
       
    class Meta:
        model = Board
        fields = ('id','owner','category','todolist_set','name','action')

    def create(self, validated_data):
        category = validated_data.get('category')
        if category == 'week':
            raise IncorrectBoardCategoryError
        else:
            return super().create(validated_data)  

    def update(self,instance,validated_data):
        if instance.category == 'week':
            current_timezone = self.context.get('current_timezone', timezone.get_current_timezone())
            current_datetime = self.context.get('current_datetime', timezone.localtime())
            action = validated_data.get('action')
            if action:
                if action == 'migrate':
                    instance.migrate_week(forward=True,next_week=True,dt=instance.due_date,tz=current_timezone)

                elif action == 'current week':
                    dt = (datetime.combine(timezone.localtime()-timedelta(days=1), datetime.max.time())).replace(tzinfo=current_timezone)#datetime is 23:59 day before current day localtime
                    instance.migrate_week(dt=dt,tz=current_timezone) 
                elif action == 'hex':
                    instance.hex(current_datetime.date())

        else:
            position = 0
            for todolist in validated_data.get('todolist_set',[]):
                if todolist.board in instance.owner.board_set.all():
                    todolist.position = position
                    todolist.board = instance
                    position+=1
                    todolist.save()

            instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
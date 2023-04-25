from rest_framework import serializers
from .models import Board,ToDoList,Task

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'todolist', 'text', 'complete','position')

class ToDoListSerializer(serializers.ModelSerializer):

    # user = serializers.ReadOnlyField(source='user.username')
    task_set = serializers.PrimaryKeyRelatedField(queryset = Task.objects.all(),many=True,required=False)
    
    class Meta:
        model = ToDoList
        fields = ('id','board','name','task_set','date')

    def update(self,instance,validated_data):
        board = instance.board

        position = 0
        for task in validated_data.get('task_set',[]):
            if task.todolist in board.todolist_set.all():
                task.position = position
                task.todolist = instance
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
        fields = ('id','owner','category','todolist_set')

    def update(self,instance,validated_data):
        user = self.context['user']

        position = 0
        for todolist in validated_data.get('todolist_set',[]):
            if todolist.board in user.board_set.all():
                todolist.position = position
                todolist.board = instance
                position+=1
                todolist.save()

        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance
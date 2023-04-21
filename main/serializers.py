from rest_framework import serializers
from .models import Board,ToDoList, Item

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'todolist', 'text', 'complete','position')

class ToDoListSerializer(serializers.ModelSerializer):

    # user = serializers.ReadOnlyField(source='user.username')
    item_set = serializers.PrimaryKeyRelatedField(queryset = Item.objects.all(),many=True,required=False)
    
    class Meta:
        model = ToDoList
        fields = ('id','board','name','item_set','date')

    def update(self,instance,validated_data):
        board = instance.board

        position = 0
        for item in validated_data.get('item_set',[]):
            if item.todolist in board.todolist_set.all():
                item.position = position
                item.todolist = instance
                position+=1
                item.save()

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
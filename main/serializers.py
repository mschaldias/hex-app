from rest_framework import serializers
from .models import ToDoList, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'todolist', 'text', 'complete','position')

class ToDoListSerializer(serializers.ModelSerializer):
    item_set = ItemSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ToDoList
        fields = ('id', 'user', 'name','item_set')

    
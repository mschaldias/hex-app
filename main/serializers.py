from rest_framework import serializers
from .models import ToDoList, Item

class ItemSerializer(serializers.ModelSerializer):
    queryset = Item.objects.all()
    class Meta:
        model = Item
        fields = ('id', 'todolist', 'text', 'complete','position')

class ToDoListSerializer(serializers.ModelSerializer):
    queryset = ToDoList.objects.all()
    # item_list = ItemSerializer(many=True,)
    item_set = ItemSerializer(many=True,read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ToDoList
        fields = ('id', 'user', 'name','item_set','date')

    def update(self,instance,validated_data):
        item_list= validated_data.pop('item_list') #list of item ids
        todolist = instance
        action = validated_data.get('action')

        position = 0
        for id in item_list:
            item = Item.objects.get(id=id)
            item.position = position
            if action == "move":
                item.todolist = todolist
                if todolist.date:
                    item.due_date = todolist.date
            position+=1
            item.save()

        return instance

    
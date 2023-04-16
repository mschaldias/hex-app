from rest_framework import serializers
from .models import ToDoList, Item

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'todolist', 'text', 'complete','position')

class ToDoListSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')
    item_set = serializers.PrimaryKeyRelatedField(queryset = Item.objects.all(),many=True,required=False)
    
    class Meta:
        model = ToDoList
        fields = ('id', 'user', 'name','item_set','date')

    def update(self,instance,validated_data):
        user = self.context['user']

        position = 0
        for item in validated_data.get('item_set',[]):
            if item.todolist in user.todolist_set.all():
                item.position = position
                item.todolist = instance
                position+=1
                item.save()

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    
from django.shortcuts import render,redirect
from .models import ToDoList, Item
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET,require_POST
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ToDoListSerializer,ItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from http import HTTPStatus

# Create your views here.

# class ToDoListView(viewsets.ModelViewSet):
#     serializer_class = ToDoListSerializer
#     queryset = ToDoList.objects.all()

# class ItemView(viewsets.ModelViewSet):
#     serializer_class = ItemSerializer
#     queryset = Item.objects.all()

MAX_ITEMS = 10000

def home(request):
    return render(request,"main/home.html",{})

@login_required(login_url='/login/')
def view(request):

    todolists = request.user.todolist_set.filter(date__isnull=True)
    return render(request, "main/view.html",{"todolists":todolists})


@login_required(login_url='/login/')
def board(request):
    todolists = request.user.todolist_set.filter(date__isnull=True)
    return render(request, "main/viewgrid.html",{"lists": todolists,"title": "Board"})

@login_required(login_url='/login/')
def week(request):

    #backlog = incomplete items with due_date before this monday
    #futurelog = incomplete items with due_date after this sunday

    lists = request.user.todolist_set.filter(date__isnull=False)
    #find this week.monday
    #lists = this week's lists
    return render(request, "main/viewgrid.html",{"lists": lists, "title": "Week View"})

@login_required(login_url='/login/')
@api_view(['GET','POST','DELETE','PUT'])
def todolists(request,id=None):

    data = request.data

    if request.method == "GET":
        todolists = request.user.todolist_set.all()
        todolist_serializer = ToDoListSerializer(todolists,many=True)
        return Response(todolist_serializer.data,status=HTTPStatus.OK) 


    elif request.method == "POST":
        todolist_serializer = ToDoListSerializer(data = data)
        if todolist_serializer.is_valid():
            todolist_serializer.save(user=request.user,position=MAX_ITEMS,category="board")
            return Response(todolist_serializer.data,status=HTTPStatus.CREATED)
        return Response(todolist_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        todolist =request.user.todolist_set.get(id=id)
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        if request.method == "DELETE":
            todolist.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)   

        elif request.method == "PUT":
                todolist_serializer = ToDoListSerializer(todolist, data = data,context={'user':request.user}, partial=True)
                if todolist_serializer.is_valid():
                    todolist_serializer.save()
                    return Response(todolist_serializer.data,status=HTTPStatus.OK)  
                return Response(todolist_serializer.errors,status=HTTPStatus.BAD_REQUEST)   
    
    return Response()


@login_required(login_url='/login/')
@api_view(['GET','POST','DELETE','PUT'])
def items(request,id=None):

    data = request.data

    if request.method == "GET":
        items = Item.objects.filter(todolist__user=request.user)
        item_serializer = ItemSerializer(items,many=True)
        return Response(item_serializer.data,status=HTTPStatus.OK) 
    
    if request.method == "POST":
        item_serializer = ItemSerializer(data = data)
        todolist = request.user.todolist_set.filter(id=data.get('todolist'))
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        if item_serializer.is_valid():
            item_serializer.save(position=MAX_ITEMS)
            return Response(item_serializer.data,status=HTTPStatus.CREATED)
        return Response(item_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        item = Item.objects.get(id=id,todolist__user=request.user)
        if not item: return Response({}, status=HTTPStatus.NOT_FOUND)
    
        if request.method == "DELETE":
            item.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)        
        
        elif request.method == "PUT":
            item_serializer = ItemSerializer(item, data = data,partial=True)
            if item_serializer.is_valid():
                item_serializer.save()
                return Response(item_serializer.data,status=HTTPStatus.OK)  
            return Response(item_serializer.errors,status=HTTPStatus.BAD_REQUEST)             

@login_required(login_url='/login/')
@api_view(['PUT'])
def boards(request):   
    
    board = request.user.todolist_set.filter(date__isnull=True,category='board')
    
    if not (board):
        return Response({"msg":"board not found"},status=HTTPStatus.NOT_FOUND)

    data = request.data
    todolist_set = data.get("todolist_set")

    if not (todolist_set and type(todolist_set) is list):
         return Response({"msg":"todolist_set must be list"},status=HTTPStatus.BAD_REQUEST) 

    position = 0
    for id in todolist_set:
        todolist = board.get(id=id) 
        todolist.position = position
        todolist.save()
        position+=1
   
    todolist_serializer = ToDoListSerializer(board,many=True)
    return Response(todolist_serializer.data,status=HTTPStatus.OK)  
                
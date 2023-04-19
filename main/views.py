from django.shortcuts import render,redirect
from .models import Board,ToDoList, Item
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET,require_POST
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import BoardSerializer,ToDoListSerializer,ItemSerializer
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
    boards = request.user.board_set.all()
    return render(request, "main/test.html",{"lists":boards, "title":"View","set":"board_set"})


@login_required(login_url='/login/')
def board(request):
    todolists = ToDoList.objects.filter(board__owner=request.user,board__category="main")
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

    #There is only supposed to be one board with category "main" per user
    board = request.user.board_set.get(category="main",owner=request.user)

    if request.method == "GET":
        todolists = ToDoList.objects.filter(board__owner = request.user,board__category="main")
        todolist_serializer = ToDoListSerializer(todolists,many=True)
        return Response(todolist_serializer.data,status=HTTPStatus.OK) 

    elif request.method == "POST":
        todolist_serializer = ToDoListSerializer(data = data)
        if todolist_serializer.is_valid():
            todolist_serializer.save(position=MAX_ITEMS)
            return Response(todolist_serializer.data,status=HTTPStatus.CREATED)
        return Response(todolist_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        todolist = board.todolist_set.filter(id=id).first()
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        if request.method == "DELETE":
            todolist.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)   

        elif request.method == "PUT":
                todolist_serializer = ToDoListSerializer(todolist, data = data,context={'board':board}, partial=True)
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
        items = Item.objects.filter(todolist__board__owner=request.user)
        item_serializer = ItemSerializer(items,many=True)
        return Response(item_serializer.data,status=HTTPStatus.OK) 
    
    if request.method == "POST":
        todolist = ToDoList.objects.filter(board__owner=request.user,id=data.get('todolist'))
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        item_serializer = ItemSerializer(data = data)
        if item_serializer.is_valid():
            item_serializer.save(position=MAX_ITEMS)
            return Response(item_serializer.data,status=HTTPStatus.CREATED)
        return Response(item_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        item = Item.objects.filter(id=id,todolist__board__owner=request.user).first()
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
@api_view(['GET','POST','DELETE','PUT'])
def boards(request,id=None):   

    data = request.data

    if request.method == "GET":
        boards = request.user.board_set.all()
        board_serializer = BoardSerializer(boards,many=True)
        return Response(board_serializer.data,status=HTTPStatus.OK) 

    elif request.method == "POST":
        board_serializer = BoardSerializer(data = data)
        if board_serializer.is_valid():
            board_serializer.save()
            return Response(board_serializer.data,status=HTTPStatus.CREATED)
        return Response(board_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        board = request.user.board_set.get(id=id)
        if not board: return Response({}, status=HTTPStatus.NOT_FOUND)

        if request.method == "DELETE":
            board.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)   

        elif request.method == "PUT":
                board_serializer = BoardSerializer(board, data = data,context={'user':request.user}, partial=True)
                if board_serializer.is_valid():
                    board_serializer.save()
                    return Response(board_serializer.data,status=HTTPStatus.OK)  
                return Response(board_serializer.errors,status=HTTPStatus.BAD_REQUEST)   
    
    return Response()
    
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Board,ToDoList,Task,Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET,require_POST
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import BoardSerializer,ToDoListSerializer,TaskSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from http import HTTPStatus
from django.http import Http404
from django.utils import timezone
from datetime import datetime
from tzlocal import get_localzone
from django.db.models import Q


MAX_ITEMS = 10000

@require_GET
def home(request):
    return render(request,"main/home.html",{})

@require_GET
@login_required(login_url='/login/')
def todolists(request,id):
    board = request.user.board_set.filter(todolist=id).first()
    todolists = ToDoList.objects.filter(board__owner = request.user,id=id)
    if not todolists: raise Http404
    
    return render(request,"main/resource_view.html",{"lists": todolists,"resource":"todolists","parent":board,"items":"tasks","create_resources":False})  

@require_GET
@login_required(login_url='/login/')
def boards(request,id=None):
    if id:  
        board = request.user.board_set.filter(id=id).first()
        if not board: raise Http404
        todolists = ToDoList.objects.filter(board__owner = request.user,board__id=id)
        return render(request, "main/resource_view.html",{"lists": todolists,"parent": board,"resource":"todolists","items":"tasks","title":board.category,"create_resources":True})  

    boards = request.user.board_set.all()
    return render(request, "main/resource_view.html",{"lists":boards,"resource":"boards","items":"todolists","title":"Boards","create_resources":True})           

def migration(request):
    if request.method == "POST":
        board = request.user.board_set.get(category="week")        
        if request.POST.get("migrate"):
            # board.peek()
            board.migrate_week(next_week=True)
        elif request.POST.get("current_week"): 
            dt = (datetime.combine(timezone.localtime(), datetime.max.time())).astimezone(tz=timezone.get_default_timezone()) #datetime is 23:59 current day local time as UTC
            board.migrate_week(dt=dt) 
                 
    return redirect("/week/")

@login_required(login_url='/login/')
def week(request):

    #TODO
    #this board has to be created for each user using a fixture
    #this board can't be edited or deleted, and the category is  
    board = request.user.board_set.filter(category="week")
    if not board:
        board = request.user.board_set.create(category="week")
        board.initialize_week()
        archive = board.todolist_set.create(name="archive")
        backlog = board.todolist_set.create(name="backlog")
        futurelog = board.todolist_set.create(name="futurelog")
    else:
        board = board.first()

    #board always has this list which can't be edited or deleted
    archive = board.todolist_set.get(name="archive")
    
    #board always has these lists which can't be edited or deleted
    backlog = board.todolist_set.get(name="backlog")
    futurelog = board.todolist_set.get(name="futurelog")

    now = timezone.now()
    if now > board.due_date:
        board.migrate_week()

    for task in futurelog.task_set.filter(complete=False):
        if task.due_date and task.due_date < now:
            task.todolist = backlog
        elif task.due_date and board.start_date <= task.due_date <= board.due_date:
            date = task.due_date.astimezone(tz=timezone.get_current_timezone()).date()
            task.todolist = board.todolist_set.get(date=date)
        task.save()
    for task in backlog.task_set.filter(complete=False):
        if task.due_date and task.due_date > board.due_date:
            task.todolist = futurelog
            task.save()

    #archive complete tasks from backlog and futurelog
    board.archive(board.todolist_set.filter(name__in=['backlog','futurelog']))   
    week_todolists = board.todolist_set.exclude(date=None)
    return render(request, "main/resource_view.html",{"lists": week_todolists,
                                                        "week":True,
                                                        "parent": board,
                                                        "resource":"todolists",
                                                        "items":"tasks",
                                                        "title":board.category,
                                                        "create_resources":False,
                                                        "backlog":backlog,
                                                        "futurelog":futurelog
                                                        })  


#API Views:
@login_required(login_url='/login/')
@api_view(['GET','POST','DELETE','PUT'])
def todolists_api(request,id=None):

    data = request.data

    if request.method == "GET":
        todolists = ToDoList.objects.filter(board__owner = request.user)
        todolist_serializer = ToDoListSerializer(todolists,many=True)
        return Response(todolist_serializer.data,status=HTTPStatus.OK) 

    elif request.method == "POST":
        todolist_serializer = ToDoListSerializer(data = data)
        if todolist_serializer.is_valid():
            todolist_serializer.save(position=MAX_ITEMS)
            return Response(todolist_serializer.data,status=HTTPStatus.CREATED)
        return Response(todolist_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        todolist = ToDoList.objects.filter(board__owner = request.user,id=id).first()
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        if request.method == "DELETE":
            todolist.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)   

        elif request.method == "PUT":
                todolist_serializer = ToDoListSerializer(todolist, data = data, partial=True)
                if todolist_serializer.is_valid():
                    todolist_serializer.save()
                    return Response(todolist_serializer.data,status=HTTPStatus.OK)  
                return Response(todolist_serializer.errors,status=HTTPStatus.BAD_REQUEST)   
    
    return Response()


@login_required(login_url='/login/')
@api_view(['GET','POST','DELETE','PUT'])
def tasks_api(request,id=None):

    data = request.data

    if request.method == "GET":
        tasks = Task.objects.filter(todolist__board__owner=request.user)
        task_serializer = TaskSerializer(tasks,many=True)
        return Response(task_serializer.data,status=HTTPStatus.OK) 
    
    if request.method == "POST":
        todolist = ToDoList.objects.filter(board__owner=request.user,id=data.get('todolist')).first()
        if not todolist: return Response({}, status=HTTPStatus.NOT_FOUND)

        task_serializer = TaskSerializer(data = data)
        if task_serializer.is_valid():
            dt=None
            if todolist.date:
                dt = (datetime.combine(todolist.date, datetime.min.time())).astimezone(tz=timezone.get_current_timezone())
            task_serializer.save(position=MAX_ITEMS,due_date=dt)
            return Response(task_serializer.data,status=HTTPStatus.CREATED)
        return Response(task_serializer.errors,status=HTTPStatus.BAD_REQUEST) 
    
    else:
        task = Task.objects.filter(id=id,todolist__board__owner=request.user).first()
        if not task: return Response({}, status=HTTPStatus.NOT_FOUND)
    
        if request.method == "DELETE":
            task.delete()
            return Response({},status=HTTPStatus.NO_CONTENT)        
        
        elif request.method == "PUT":
            task_serializer = TaskSerializer(task, data = data,partial=True)
            if task_serializer.is_valid():
                if data.get("click",None):
                    complete= not(task.complete)
                    task_serializer.save(complete=complete)
                else:
                    task_serializer.save()
                return Response(task_serializer.data,status=HTTPStatus.OK)  
            return Response(task_serializer.errors,status=HTTPStatus.BAD_REQUEST)             

@login_required(login_url='/login/')
@api_view(['GET','POST','DELETE','PUT'])
def boards_api(request,id=None):   

    data = request.data

    if request.method == "GET":
        boards = request.user.board_set.all()
        board_serializer = BoardSerializer(boards,many=True)
        return Response(board_serializer.data,status=HTTPStatus.OK) 

    elif request.method == "POST":
        board_serializer = BoardSerializer(data = data)
        if board_serializer.is_valid():
            board_serializer.save(owner=request.user)
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
    
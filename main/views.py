from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Board, Profile,ToDoList,Task
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
from datetime import datetime, timedelta
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
    
    return render(request,"main/resource_view.html",{"resources": todolists,
                                                     "resource_name":"todolists",
                                                     "board":board,
                                                     "items":"tasks",
                                                     "create_resources":False,
                                                     "weekday":False
                                                     })  

@require_GET
@login_required(login_url='/login/')
def boards(request,id=None):
    boards = request.user.board_set.filter(category='main')
    if id:  
        board = boards.filter(id=id).first()
        if not board: raise Http404
        todolists = ToDoList.objects.filter(board__owner = request.user,board__id=id)
        return render(request, "main/resource_view.html",{"resources": todolists,
                                                          "parent": board,
                                                          "board": board,
                                                          "resource_name":"todolists",
                                                          "items":"tasks",
                                                          "title":board.name,
                                                          "create_resources":True,
                                                          })  

    return render(request, "main/resource_view.html",{"resources":boards,
                                                      "resource_name":"boards",
                                                      "items":"todolists",
                                                      "title":"Boards",
                                                      "create_resources":True,
                                                      })           

@login_required(login_url='/login/')
def action(request):
    if request.method == "POST":
        board = request.user.board_set.get(category="week")
        current_timezone = timezone.get_current_timezone()
        if request.POST.get("migrate"):
            board.migrate_week(forward=True,next_week=True,dt=board.due_date,tz=current_timezone)
        elif request.POST.get("current_week"): 
            dt = (datetime.combine(timezone.localtime()-timedelta(days=1), datetime.max.time())).replace(tzinfo=timezone.get_current_timezone())#datetime is 23:59 day before current day localtime
            board.migrate_week(dt=dt,tz=current_timezone) 
        elif request.POST.get("hex"):
            board.hex()
                 
    return redirect("/week/")


def week_utils(board,now):
    if now > board.due_date:
        board.migrate_week(forward=True,dt=board.due_date,now=now,tz=timezone.get_current_timezone())

    #board always has this list which can't be edited or deleted
    archive = board.todolist_set.get(name="archive")
    
    #board always has these lists which can't be edited or deleted
    backlog = board.todolist_set.get(name="backlog")
    futurelog = board.todolist_set.get(name="futurelog")
    hexlog = board.todolist_set.get(name="hexlog")

    # if there are any incomplete hexed tasks, hex streak goes to 0
    # hexed tasks are unhexed and moved to backlog
    overdue_hexed = Task.objects.filter(todolist__board=board,complete=False,hex=True,due_date__lt=now)    
    if overdue_hexed:
        overdue_hexed.update(hex=False,todolist=backlog)
        board.owner.profile.hex_streak = 0
        board.owner.profile.save()

login_required(login_url='/login/')
@require_GET
def hex_streak(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':                                
        profile = request.user.profile
        if not profile: raise Http404
        return render(request,"main/hex_streak.html", {
                                                 "hex_streak":profile.hex_streak,
                                                 "hex_streak_range":range(profile.hex_streak)
                                                })
    raise Http404

login_required(login_url='/login/')
@require_GET
def card(request,resource_name,id=None):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':                                
        resource = None
        if resource_name == "todolists":
            items = "tasks"
            resource = ToDoList.objects.filter(id=id,board__owner=request.user).first()
        elif resource_name == "boards":
            items = "todolists"
            resource = Board.objects.filter(id=id,owner=request.user).first()
        if not resource:  raise Http404

        return render(request,"main/card.html", {
                                                 "resource":resource,
                                                 "resource_name":resource_name,
                                                 "items":items,
                                                })
    raise Http404

@login_required(login_url='/login/')
@require_GET
def list(request,resource_name,id=None):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':                                
        items = li = board = None
        context = {}
        if resource_name == "todolists":
            items = "tasks"
            li = ToDoList.objects.filter(id=id,board__owner=request.user).first()
            if li: 
                board = li.board
                if board.category == 'week':
                    context['week'] = True
                    context['interval_type_options']=['days','weeks','months','years']
                    if li.date: context['weekday'] = True
        elif resource_name == "boards":
            items = "todolists"
            board = Board.objects.filter(id=id,owner=request.user).first()
            if board: li = board
        
        if not (li and board):    raise Http404

        params = {"resource_name":resource_name,"board":board,"list":li,"items":items}
        context['card_styles'] = {'backlog':'bg-danger','futurelog':'bg-primary','hexlog':'bg-dark'}
        context['item_styles'] = {'backlog':'list-group-item-hex-danger','futurelog':'list-group-item-hex-primary'}   
        context.update(params)

        return render(request,"main/list.html", context)
    raise Http404

@login_required(login_url='/login/')
def week(request):

    #this board is created for each new user using a signal
    board = request.user.board_set.get(category="week")
    week_utils(board,timezone.now())

    localdate = timezone.localdate()

    logs = board.todolist_set.filter(name__in=['backlog','futurelog','hexlog'])
    card_styles = {'backlog':'bg-danger','futurelog':'bg-primary','hexlog':'bg-dark'}
    item_styles = {'backlog':'list-group-item-hex-danger','futurelog':'list-group-item-hex-primary'}

    week_todolists = board.todolist_set.exclude(date=None)
    return render(request, "main/resource_view.html",{  "resources": week_todolists,
                                                        "resource_name":"todolists",
                                                        "logs":logs,
                                                        "week":True,
                                                        "board": board,
                                                        "items":"tasks",
                                                        "card_styles":card_styles,
                                                        "item_styles":item_styles,
                                                        "title":'week',
                                                        "create_resources":False,
                                                        "hex_streak":board.owner.profile.hex_streak,
                                                        "hex_streak_range":range(board.owner.profile.hex_streak),
                                                        "localdate":localdate,
                                                        "interval_type_options":['days','weeks','months','years'],
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
                dt = (datetime.combine(todolist.date, datetime.min.time())).replace(tzinfo=timezone.get_current_timezone())
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
    
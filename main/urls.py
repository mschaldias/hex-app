from django.urls import path,include
from rest_framework import routers
from . import views

urlpatterns = [
    path("",views.home, name = "home"),
    path("boards/",views.boards, name = "manage_boards"),
    path("week/",views.week, name = "week"),
    path("hex_streak/",views.hex_streak, name = "hex_streak"),
    path("list/<str:resource_name>/<int:id>/",views.list, name = "list"),
    path("card/<str:resource_name>/<int:id>/",views.card, name = "card"),
    path("action/",views.action, name = "action"), 
    path("todolists/<int:id>",views.todolists, name = "todolists"),
    path("boards/<int:id>",views.boards, name = "boards")   ,
    path("api/tasks/",views.tasks_api, name = "tasks"), 
    path("api/tasks/<int:id>",views.tasks_api, name = "tasks"),
    path("api/todolists/",views.todolists_api, name = "todolists"), 
    path("api/todolists/<int:id>",views.todolists_api, name = "todolists"),
    path("api/boards/",views.boards_api, name = "boards"), 
    path("api/boards/<int:id>",views.boards_api, name = "boards"), 
    
]
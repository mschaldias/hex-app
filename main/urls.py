from django.urls import path,include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'todolists', views.ToDoView, 'todolist')


urlpatterns = [
    path("",views.home, name = "home"),
    path("view/",views.view, name = "view"),
    path("week/",views.week, name = "week"), 
    path("todolist_view/<int:id>",views.todolist_view, name = "todolist_view"),
    path("board_view/<int:id>",views.board_view, name = "board_view")   ,
    path("tasks/",views.tasks, name = "tasks"), 
    path("tasks/<int:id>",views.tasks, name = "tasks"),
    path("todolists/",views.todolists, name = "todolists"), 
    path("todolists/<int:id>",views.todolists, name = "todolists"),
    path("boards/",views.boards, name = "boards"), 
    path("boards/<int:id>",views.boards, name = "boards"), 



    # path("api/", include(router.urls)), 
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
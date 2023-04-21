from django.urls import path,include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'todolists', views.ToDoListView, 'todolist')
# router.register(r'items', views.ItemView, 'item')


urlpatterns = [
    # path("<int:id>",views.index, name = "index"),
    path("",views.home, name = "home"),
    path("view/",views.view, name = "view"),
    # path("main/",views.main, name = "main"), 
    path("week/",views.week, name = "week"), 
    path("todolist_view/<int:id>",views.todolist_view, name = "todolist_view"),
    path("board_view/<int:id>",views.board_view, name = "board_view")   ,

    path("items/",views.items, name = "items"), 
    path("items/<int:id>",views.items, name = "items"),
    path("todolists/",views.todolists, name = "todolists"), 
    path("todolists/<int:id>",views.todolists, name = "todolists"),
    path("boards/",views.boards, name = "boards"), 
    path("boards/<int:id>",views.boards, name = "boards"), 



    # path("api/", include(router.urls)), 
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
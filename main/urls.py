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
    path("board/",views.board, name = "board"), 
    path("week/",views.week, name = "week"), 
    path("items/",views.items, name = "items"), 
    path("items/<int:id>",views.items, name = "items"),
    path("todolists/",views.todolists, name = "todolists"), 
    path("todolists/<int:id>",views.todolists, name = "todolists"),
    path("boards/",views.boards, name = "boards"), 



    # path("api/", include(router.urls)), 
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
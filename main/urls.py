from django.urls import path
from . import views

urlpatterns = [
    path("<int:id>",views.index, name = "index"),
    path("",views.home, name = "home"),
    path("view/",views.view, name = "view"),
    path("week/",views.week, name = "week"), 
]
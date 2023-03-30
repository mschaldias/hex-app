from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList

# Create your views here.

def index(request, id):

    ls = ToDoList.objects.get(id=id)
    # item = ls.item_set.get(id = 1) 
    # return HttpResponse("%s<br></br><p>%s</p>" %(ls.name, item.text))

    if ls in response.user.todolist.all():
        if request.method == "POST":
            print(request.POST)
            if request.POST.get("save"):
                for item in ls.item_set.all():
                    if request.POST.get("c" + str(item.id)) == "clicked":
                        item.complete = True
                    else:
                        item.complete = False
                    
                    item.save()
                
            elif request.POST.get("newItem"):
                text = request.POST.get("newText")

                if len(text) > 2:
                    ls.item_set.create(text = text, complete = False)
                else:
                    print("invalid input")

        return render(request,"main/list.html",{"ls": ls})
    else:
        return render(request,"main/view.html",{})

def home(request):
    return render(request,"main/home.html",{})


def create(request):
    #user = request.user 
    #can check user attributes here

    if request.method=="POST":
        form = CreateNewList(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            toDoList = ToDoList(name=name)
            toDoList.save()
            request.user.todolist.add(toDoList)
        
        return HttpResponseRedirect("/%i" %toDoList.id)

    else:
        form = CreateNewList()

    return render(request,"main/create.html",{"form": form})

def view(request):
    return render(request, "main/view.html",{})



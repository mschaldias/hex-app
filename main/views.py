from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import ToDoList, Item
from .forms import CreateNewList

# Create your views here.

def index(request, id):
    # item = ls.item_set.get(id = 1) 
    # return HttpResponse("%s<br></br><p>%s</p>" %(ls.name, item.text))

    ls = request.user.todolist_set.filter(id=id).first()

    if ls:

        for k in request.POST:
            if k.startswith("e") and any(str.isdigit(c) for c in k):
                id = ''.join([n for n in k if n.isdigit()])
                newText = request.POST.get(k)
                item = Item.objects.get(id=id)
                item.text = newText
                item.save()


        if request.method == "POST":
            print(request.POST)
            # if request.POST.get("save"):
            for item in ls.item_set.all():
                if request.POST.get("c" + str(item.id)) == "clicked":
                    item.complete = True
                else:
                    item.complete = False

                item.save()
                
            if request.POST.get("newItem"):
                text = request.POST.get("newText")
                ls.item_set.create(text = text, complete = False)


            elif request.POST.get("removeItem"):
                id = ''.join([n for n in request.POST.get("removeItem") if n.isdigit()])
                ls.item_set.filter(id=id).delete()       
 
        return render(request,"main/list.html",{"ls": ls})
    else:
        return redirect("/")

def home(request):
    return render(request,"main/home.html",{})


def create(request):

    if request.method=="POST":
        form = CreateNewList(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            toDoList = request.user.todolist_set.create(name=name)
        
        return redirect("/%i" %toDoList.id)

    else:
        form = CreateNewList()

    return render(request,"main/create.html",{"form": form})

def view(request):
    return render(request, "main/view.html",{})



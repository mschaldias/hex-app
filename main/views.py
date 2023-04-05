from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import ToDoList, Item
from .forms import CreateNewList

# Create your views here.

def index(request, id):

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


def view(request):
    if request.method=="POST":
        form = CreateNewList(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            request.user.todolist_set.create(name=name)

        elif request.POST.get("removeList"):
            id = ''.join([n for n in request.POST.get("removeList") if n.isdigit()])
            request.user.todolist_set.filter(id=id).delete() 
    
    form = CreateNewList()
    return render(request, "main/view.html",{"form":form})


def week(request):
    if request.method=="POST":
        print(request.POST)
    top = ["Monday","Tuesday","Wednesday","Thursday"]

    ls = request.user.todolist_set.filter(name="Monday").first()
    ls1 = request.user.todolist_set.filter(name="Tuesday").first()

    return render(request, "main/viewgrid.html",{"top": top,"ls":ls,"ls1":ls1})





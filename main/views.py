from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import ToDoList, Item
from .forms import CreateNewList
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET,require_POST
# Create your views here.

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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

@require_GET
@login_required(login_url='/login/')
def week(request):
    return render(request, "main/viewgrid.html",{})

@require_POST
@login_required(login_url='/login/')
def item_actions(request):
    if request.method == "POST":
        print(request.POST)
        if request.POST.get("sortable"):
                list_id = ''.join([n for n in request.POST.get("list-id") if n.isdigit()])
                item_ids = [''.join([n for n in i if n.isdigit()]) for i in request.POST.getlist("item-ids[]") if i]          
                ls = request.user.todolist_set.filter(id=list_id).first()
                
                if request.POST.get("action") == "move":
                    for id in item_ids:
                        item = Item.objects.all().filter(id=id).first()
                        item.todolist = ls
                        item.save()
                
                position = 0
                for id in item_ids:
                    item = Item.objects.all().filter(id=id,todolist__id=ls.id).first()
                    item.position = position
                    item.save()
                    position+=1

        elif request.POST.get("action"): 
            action = request.POST.get("action")
            id = ''.join([n for n in request.POST.get("id") if n.isdigit()])
            item = Item.objects.all().filter(id=id,todolist__user=request.user).first()
            if item:
                if action == "remove":
                    item.delete()
                elif action == "checkbox":
                    item.complete = not(item.complete)
                    item.save()
                
    return render(request, "main/viewgrid.html",{})




function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
}


function edit(resource,item_id,value){

    key = ""
    data={}
    if( resource == "tasks"){
        key = "text"
    }
    if (resource == "todolists"){
        key = "name"
        if (value===""){
            value = "List"
        }
    }
    else if (resource == "boards" ){
        key = "category"
        if (value===""){
            value = "Board"
        }
    }

    data = {"id":item_id,[key]:value}

    $.ajax(
        {
            type: 'PUT',
            url: `/api/${resource}/${item_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify(data),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)  
                if (resource == "boards"){
                    $(`#card${item_id} #header-text`).text(data.category);
                }   
                else if (resource == "todolists"){
                    $(`#card${item_id} #header-text`).text(data.name);
                }        
            },
            error: (data,msg,xhr) =>{
                console.log(data.responseText);
                $("#charFieldError .modal-title").text(JSON.parse(data.responseText)[key][0]);
                $('#charFieldError').modal("show")
            }
        }
    );
};

function set_task_date(item_id,value){
    const options = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      };
    $.ajax(
        {
            type: 'PUT',
            url: "/api/tasks/"+item_id,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify({
                id: item_id,
                due_date: value
            }),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)
                if (data.due_date != null){
                    date = new Date(data.due_date).toDateString()  
                    html = `<i class="fa-solid fa-calendar"></i>  ${date}`
                }else{
                    html = ''
                }                              
                $(`#item${item_id} .task-due-date-text`).html(html)
            },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}


function checkbox_click(item_id){

    $.ajax(
        {
            type: 'PUT',
            url: "/api/tasks/"+item_id,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify({
                id: item_id,
                click:true 
            }),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)
            },
            error: (error) =>{
                console.log(error);
            }
        }
    );
};

function delete_button(resource,item_id,card=false){
    item_id = item_id
    element = document.getElementById(`item${item_id}`);
    if (card){
        element = document.getElementById(`card${item_id}`);
    }
    element.remove();
    $.ajax(
        {
            type: 'DELETE',
            url: `/api/${resource}/${item_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify({
                id: item_id,
            }),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)
            },
            error: (error) =>{
                console.log(error);
            }
        }
    );
};

function append_new_item(list_id,element_id,card,log=false){ 
    $.ajax(
        {
            type: 'GET',
            url: document.URL,
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            success: (data) => {
                        parser = new DOMParser();
                        doc = parser.parseFromString(data, "text/html");
                        if (log){  
                            element = doc.getElementById(`${element_id}`)
                            $(`#${element_id}`).replaceWith(element)
                            initialize_sortable('todolists',`${element_id}`)   
                            let task_ids = document.querySelectorAll(`#${CSS.escape(element_id)}  li[id]`);
                            for (let i = 0; i < task_ids.length; i++) {
                                set_datepicker(task_ids[i].id.replace(/\D/g, ""));
                            }                                       
                        }                        
                        if (card) {
                            element = doc.getElementById(`card${element_id}`)
                            $(`#cards`).append(element);
                        }else{
                            element = doc.getElementById(`item${element_id}`)
                            $(`#${list_id}`).append(element);
                            initialize_sortable('todolists',list_id)
                        };
                        set_datepicker(element_id)      
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}

function create_button(resource,list_id,value="",card=false){
    key = ""
    data = {}
    if (resource  == "tasks"){
        key="todolist"
        data = {[key]:list_id}
    }
    if (resource == "todolists"){
        key = "board"
        data = {[key]:list_id}
        if (value !== ""){
            data["name"]=value
        }
    }
    
    if (resource == "boards"){
        if (value !== ""){
            key = "category"
            data = {"category":value};
        }
    }
    $.ajax(
        {
            type: 'POST',
            url: `/api/${resource}/`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify(data),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status);
                        append_new_item(list_id,data.id,card);
                    },
            error: (data,msg,xhr) =>{
                console.log(JSON.parse(data.responseText)[key][0])
                $("#charFieldError .modal-title").text(JSON.parse(data.responseText)[key][0]);
                $('#charFieldError').modal("show")
                console.log(error);
            }
        }
    );       
};

function sortable_event(resource,list_id){
    let ids = document.querySelectorAll(`#${CSS.escape(list_id)}  li[id]`);
    let ids_list = [];
    for (let i = 0; i < ids.length; i++) {
        ids_list.push(ids[i].id.replace(/\D/g, ""));
    }   
    data = {"task_set":ids_list,"id":list_id}
    if (resource == "boards"){
        data = {"todolist_set":ids_list,"id":list_id}
    }
    
    $.ajax(
        {
            type: 'PUT',
            url: `/api/${resource}/${list_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify(data),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status)                        
                        append_new_item(`${data.name}`,`${data.id}`,card=false,log=true)
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}
function set_datepicker(element_id){
    options = {
        todayHighlight:true,
        clearBtn:true,
        todayBtn:"linked", 
    }  
    $(`#datepicker${element_id}`).datepicker(options);
    
    $(`#datepicker${element_id}`).on('changeDate', function() {
        value = $(`#datepicker${element_id}`).datepicker('getDate');
        set_task_date(element_id,value);
        $(`#calendar-collapse${element_id}`).collapse("toggle")
        $(`#item-collapse${element_id}`).collapse("toggle")                
    });  
}

function initialize_sortable(resource,list_id){

    var list = document.getElementById(list_id);
    Sortable.create(list, {
        animation: 100,
        group: 'list-1',
        draggable: '.draggable',
        handle: '.handle',
        sort: true,
        filter: '.sortable-disabled',
        chosenClass: 'chosen',
        onAdd: function () {
            sortable_event(resource,list_id);
        },
        onUpdate: function () {
            sortable_event(resource,list_id)
        },
    });  

} 
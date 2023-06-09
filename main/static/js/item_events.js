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

function toggle_edit(items,item_id){

    item_text = $(`#item${item_id} #item-text`)
    if (item_text.attr('contenteditable') != 'true'){
        item_text.attr('contenteditable','true');
        item_text.focus();
        item_text.after(`<button id = "submit" class = "btn btn-success mx-auto"><i class="fa-solid fa-check"></i></button>`)
        $(`#item${item_id} #submit`).click(
            function(){
                item_text = $(`#item${item_id} #item-text`)
                edit(items,item_id,item_text.text())
                item_text.attr('contenteditable','false');
                $(`#item${item_id} #submit`).remove()
            });
    }
}

function set_task_repeat(item_id,clear=false){

    interval_value = $(`#interval_value${item_id}`).val()
    interval_type = $(`#interval_type${item_id}`).val()
    data = {}
    if (clear) {
        $(`#interval_value${item_id}`).val(null)   
        data = {"interval_value": null, "interval_type":''}
        $(`#repeat-collapse${item_id}`).collapse("hide")
        $(`#item-collapse${item_id}`).collapse("hide") 
    }    
    else if (interval_value && interval_type){
        data = {"interval_value": interval_value,"interval_type":interval_type}
    }
       
    $.ajax(
        {
            type: 'PUT',
            url: `/api/tasks/${item_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify(data),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)  
                if (data.interval_type && data.interval_value){ 
                    if (data.interval_value == 1){
                        data.interval_type = data.interval_type.replace(/.$/, '');
                    }
                        
                    text = `Every ${data.interval_value} ${data.interval_type}`
                }else{
                    text = ''
                }  
                $(`#item${item_id} .task-repeat-text`).text(text)
                       
            },
            error: (data,msg,xhr) =>{
                console.log(data.responseText);
                response = JSON.parse(data.responseText)["interval_value"]
                $("#charFieldError .modal-title").text(response);
                $('#charFieldError').modal("show")
            }
        }
    );

}

function edit(resource,item_id,value){

    key = ""
    data={}
    if( resource == "tasks"){
        key = "text"
    }
    if (resource == "todolists"){
        key = "name"
    }
    else if (resource == "boards" ){
        key = "name"
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
                    $(`#card${item_id} #header-text`).text(data.name);
                }   
                else if (resource == "todolists"){
                    $(`#card${item_id} #header-text`).text(data.name);
                }        
            },
            error: (data,msg,xhr) =>{
                console.log(data.responseText);
                response = JSON.parse(data.responseText)[key][0]
                $("#charFieldError .modal-title").text(response);
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
            key = "name"
            data = {[key]:value};
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
function set_datepicker(element_id,date){

    options = {
        todayHighlight:true,
        clearBtn:true,
        todayBtn:"linked", 
    }  
    $(`#datepicker${element_id}`).datepicker(options);
    if (date){
        $(`#datepicker${element_id}`).datepicker('update',new Date(date));
    }

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
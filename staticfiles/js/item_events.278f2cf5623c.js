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

function toggle(container_id,form_id,dragabble_id=null){
    $(`${container_id}`).toggleClass('hidden')
    $(`${form_id}`).toggleClass('hidden')
    if (dragabble_id){
        $(`${dragabble_id}`).toggleClass('dragabble handle')
    }
}

function set_task_repeat(item_id,clear=false){
    interval_value = $(`#interval_value`).val()
    interval_type = $(`#interval_type`).val()
    data = {}
    if (clear) {
        $(`#interval_value`).val(null)   
        data = {"interval_value": null, "interval_type":''}
    }    
    else if (interval_value && interval_type){
        data = {"interval_value": interval_value,"interval_type":interval_type}
    }  
    $.ajax({type: 'PUT',
            url: `/api/tasks/${item_id}`,
            contentType: 'application/json',
            headers: {"X-CSRFToken": getCookie("csrftoken")},
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
            }
    });
}

function edit(resource,item_id,value){
    key = ""
    data={}
    if(resource == "tasks"){
        key = "text"
    }
    if (resource == "todolists"){
        key = "name"
    }
    else if (resource == "boards" ){
        key = "name"
    }

    data = {"id":item_id,[key]:value}

    $.ajax({type: 'PUT',
            url: `/api/${resource}/${item_id}`,
            contentType: 'application/json',
            headers: {"X-CSRFToken": getCookie("csrftoken")},
            dataType: 'json',
            data: JSON.stringify(data),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)  
                if (resource == "boards"){
                    $(`#card${item_id} #header-text`).text(data.name);
                }   
                else if (resource == "todolists"){
                    $(`#card${item_id} #header-text`).text(data.name);
                    $(`#item${item_id} #item-text`).text(data.name) 
                }
                else if (resource == "tasks"){
                    $(`#item${item_id} #item-text`).text(data.text) 
                    $(`#item_modal${item_id} textarea`).val(data.text)
                }
                
            },
            error: (data,msg,xhr) =>{
                console.log(data.responseText);
            }
    });
}

function set_task_date(item_id,value){
    $.ajax({type: 'PUT',
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
                replace_element(document.URL,['board','logs'],scripts=true)
            },
            error: (error) =>{console.log(error);}
    });
}

function checkbox_click(item_id,item_hex,item_prev_hex){
    $.ajax({type: 'PUT',
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
                if (item_hex == "True"|| item_prev_hex == "True"){
                    replace_element('/hex_streak/',['streak-display'])
                }
                if (data.interval_type && data.interval_value){
                    replace_element(document.URL,['board','logs'],scripts=true)
                }                
            },
            error: (error) =>{console.log(error);}
})}

function delete_button(resource,item_id,card=false){
    item_id = item_id
    element = document.getElementById(`item${item_id}`);
    if (card){
        element = document.getElementById(`card${item_id}`);
    }
    
    $.ajax({type: 'DELETE',
            url: `/api/${resource}/${item_id}`,
            contentType: 'application/json',
            headers: {"X-CSRFToken": getCookie("csrftoken")},
            dataType: 'json',
            data: JSON.stringify({
                id: item_id,
            }),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)
                element.remove();
            },
            error: (error) =>{
                console.log(error);
            }
    });
};

function run_scripts(element) {
    Array.from(element.querySelectorAll("script"))
      .forEach( oldScriptEl => {
        const newScriptEl = document.createElement("script");
        Array.from(oldScriptEl.attributes).forEach( attr => {
          newScriptEl.setAttribute(attr.name, attr.value) 
        });
        const scriptText = document.createTextNode(oldScriptEl.innerHTML);
        newScriptEl.appendChild(scriptText);   
        oldScriptEl.parentNode.replaceChild(newScriptEl, oldScriptEl);
});}

function replace_element(url,element_ids,scripts=false){
    $.ajax({type: 'GET',
            url: url,
            headers: {"X-CSRFToken": getCookie("csrftoken")},
            success: (data) => {
                        parser = new DOMParser();
                        doc = parser.parseFromString(data, "text/html");
                        for (id of element_ids) {
                            element = doc.getElementById(id)
                            $(`#${id}`).replaceWith(element)
                            if (scripts){
                                run_scripts(element)   
                            }  
                        }                                                                                                    
                    },
            error: (error) => {console.log(error)}
    });
}

function append_new_item(parent_model,parent_id,item_id,card){
    if (card){
        url = `/card/${parent_model}/${item_id}/`      
    }
    else {
        url = `/list/${parent_model}/${parent_id}/`
    }
    $.ajax(
        {  type: 'GET',
            url: url,
            headers: {"X-CSRFToken": getCookie("csrftoken")},
            success: (data) => {
                        parser = new DOMParser();
                        doc = parser.parseFromString(data, "text/html");                                              
                        if (card) {
                            console.log(data)
                            element = doc.getElementById(`card${item_id}`)
                            $(`#cards`).append(element);
                            run_scripts(element)
                        }
                        else{
                            element = doc.getElementById(`item${item_id}`)
                            $(`#${parent_id}`).append(element);
                            run_scripts(element)                  
                        };                       
                    },
            error: (error) =>{console.log(error);}
    })
}

function create_button(items,parent_id,value="",card=false){
    key = ""
    data = {}
    resource_category = ""
    if (items  == "tasks"){
        key="todolist"
        data = {[key]:parent_id,text:value}
        resource_category = "todolists"
    }
    if (items == "todolists"){
        key = "board"
        data = {[key]:parent_id}
        if (value !== ""){
            data["name"]=value
        }
        resource_category = "boards"
        if (card){
            resource_category = "todolists"
        }
    }
    if (items == "boards"){
        resource_category = "boards"
        if (value !== ""){
            key = "name"
            data = {[key]:value};
        }
    }
    $.ajax({type: 'POST',
            url: `/api/${items}/`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify(data),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status);
                        append_new_item(resource_category,parent_id,data.id,card);
                    },
            error: (data,msg,xhr) =>{
                console.log(error);
            }
    });       
}

function sortable_event(resource_category,list_id,replace=false){
    let ids = document.querySelectorAll(`#${CSS.escape(list_id)}  li[id]`);
    let ids_list = [];
    for (let i = 0; i < ids.length; i++) {
        ids_list.push(ids[i].id.replace(/\D/g, ""));
    }   
    data = {"task_set":ids_list,"id":list_id}
    if (resource_category == "boards"){
        data = {"todolist_set":ids_list,"id":list_id}
        replace = false
    }
    $.ajax({type: 'PUT',
            url: `/api/${resource_category}/${list_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify(data),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status)
                        if (replace){
                            replace_element(`/list/${resource_category}/${data.id}/`,[data.id],scripts=true)
                        }
                    },
            error: (error) =>{
                console.log(error);
            }
    });
}
function set_datepicker(element_id,date){
    options = {
        todayHighlight:true,
        clearBtn:true,
        todayBtn:"linked", 
    }  
    $(`#datepicker`).datepicker(options);
    if (date){
        $(`#datepicker`).datepicker('update',new Date(date));
    }
    $(`#datepicker`).on('changeDate', function() {
        value = $(`#datepicker`).datepicker('getDate');
        set_task_date(element_id,value);
    });  
}

function initialize_sortable(resource_category,list_id, hexlog=false, weekday=false){
    list = document.getElementById(list_id);
    if (list) {
        Sortable.create(list, {
            delay: 100,
            delayOnTouchOnly: true, 
            animation: 100,
            group: {
                name:'weekday',
                pull: function(to,from){
                    return !Sortable.dragged.classList.contains('list-group-item-hex-dark')
                }      
            },
            draggable: '.draggable',
            handle: '.handle',
            sort: true,
            filter: '.sortable-disabled',
            chosenClass: 'chosen',
            onAdd: function () {
                sortable_event(resource_category,list_id,replace=true,hexlog=false,weekday=true);
            },
            onUpdate: function () {
                sortable_event(resource_category,list_id)
            },
        });            
    }
}

function autoresize(textarea){
    console.log('autoresize')
    textarea.style.height = '0px';     //Reset height, so that it not only grows but also shrinks
    textarea.style.height = (textarea.scrollHeight) + 'px';    //Set new height
    console.log(textarea.style.height)
}

function set_height(ta) {
    ta.style.height="0";
    ta.style.height = (ta.scrollHeight)+'px';
    ta.addEventListener('input',function(){autoresize(ta) })             
}
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


function edit_text(resource,item_id,value){

    key = "text"
    if (resource == "todolists"){
        key = "name"
    }

    data = {"id":item_id,[key]:value}
        
    $.ajax(
        {
            type: 'PUT',
            url: `/${resource}/${item_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify(data),
            success: (data,msg,xhr) => {
                console.log(msg,xhr.status)                
            },
            error: (data,msg,xhr) =>{
                console.log(data.responseText);
                $("#charFieldError .modal-title").text(JSON.parse(data.responseText)[key][0]);
                $('#charFieldError').modal("show")
            }
        }
    );
};


function checkbox_click(item_id,value){

    $.ajax(
        {
            type: 'PUT',
            url: "/items/"+item_id,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            dataType: 'json',
            data: JSON.stringify({
                id: item_id,
                complete: (value != 'true')
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

function delete_button(resource,item_id){
    item_id = item_id
    element = document.getElementById(`item${item_id}`);
    if (resource == 'boards'){
        element = document.getElementById(`card${item_id}`);
    }
    element.remove();
    $.ajax(
        {
            type: 'DELETE',
            url: `/${resource}/${item_id}`,
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

function append_new_item(list_id,element_id,card=false){
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
                        if (card) {
                            element = doc.getElementById(`card${element_id}`)
                        }else{
                           element = doc.getElementById(`item${element_id}`)
                        }
                        
                        $(`#${list_id}`).append(element);
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}

function create_button(resource,list_id){
    
    key = ""
    card = false
    data = {}
    if (resource  == "items"){
        key="todolist"
    }
    if (resource == "todolists"){
        key = "board"
    }
    data = {[key]:list_id}
    if (resource == "boards"){
        input = $("#boardName").val(),  
        data = {"category":input};
        card = true
    }
    $.ajax(
        {
            type: 'POST',
            url: `/${resource}/`,
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
            error: (error) =>{
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
    data = {"item_set":ids_list,"id":list_id}
    if (resource == "boards"){
        data = {"todolist_set":ids_list,"id":list_id}
    }
    
    $.ajax(
        {
            type: 'PUT',
            url: `/${resource}/${list_id}`,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify(data),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status)
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}
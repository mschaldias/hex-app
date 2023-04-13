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

function autosize_textarea(){
    $('textarea').each(function () {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
        }).on('input', function () {
        this.style.height = "0";
        this.style.height = (this.scrollHeight) + 'px';
      });
}

function edit_text(item_id,value){
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
                text: value
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

function delete_button(item_id){
    item_id = item_id
    element = document.getElementById("item"+item_id);
    element.remove();
    $.ajax(
        {
            type: 'DELETE',
            url: "/items/"+item_id,
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

function append_new_item(list_id,item_id){
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
                        item = doc.getElementById("item"+item_id)
                        $("#list"+list_id).append(item);
                        autosize_textarea();
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );
}

function create_button(list_id){

    $.ajax(
        {
            type: 'POST',
            url: "/items/",
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify({
                todolist: list_id,
            }),
            dataType: 'json',
            success: (data,msg,xhr) => {
                        console.log(msg,xhr.status)
                        append_new_item(list_id,data.id);
                    },
            error: (error) =>{
                console.log(error);
            }
        }
    );       
};

function sortable_event(action,list_id){

    let ids = document.querySelectorAll( "#list" + list_id + " li[id]");
    let ids_list = [];
    for (let i = 0; i < ids.length; i++) {
        ids_list.push(ids[i].id.replace(/\D/g, ""));
    }   
    
    // item_set = ids_list.map(x => {
    //     return({id: x,todolist:list_id});
    //   });
    $.ajax(
        {
            type: 'PUT',
            url: "/sortable_todolists/"+list_id,
            contentType: 'application/json',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            data: JSON.stringify({
                id: list_id,
                action: action,
                item_list: ids_list,
            }),
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
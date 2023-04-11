
function edit_text(item_id,value){
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            item_id: item_id,
            action: "edit",
            text: value
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
};


function checkbox_click(item_id){
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            item_id: item_id,
            action: "checkbox"
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
};

function remove_button(item_id){
    var item_id = "item" + item_id.replace(/\D/g, "");
    const element = document.getElementById(item_id);
    element.remove();
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            item_id: item_id,
            action: 'remove'
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
};

function append_new_item(list_id,item_id){
var list_item = 
    `<li class="list-group-item list-group-item-action list-group-item-hex text-white draggable" id = "item` + item_id + `}">
        <div class = "input-group mx-auto">
            <span class="handle btn border-0" style= "cursor:move"><i class="fa-solid fa-grip-lines-vertical fa" style="color:  var(--hex-body);"></i></span>
                <div class= "input-group-text bg-hex-sidenav border border-hex" >
                    <input class = "form-check-input bg-hex-topnav" type="checkbox", value = "clicked", name = "click` + item_id + `", onclick="checkbox_click(name)">
                </div> 
            <textarea id = "textarea" value = "" name = "edit` + item_id + `" class = "form-control bg-hex-topnav border border-hex text-white" onchange="edit_text(name,value)"></textarea>
            <button  id = "remove_button", name = "remove` + item_id + `", value = "` + item_id + `", class="btn btn-outline-hex-dark", onclick = "remove_button(name)"><i class="fa fa-minus"></i></button>
        </div>
    </li>`

    list_id="#" + list_id
    item_clone = $(list_id)

    $(list_id).append(list_item);
}

function add_button(list_id){
    
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            sortable: true,
            action: 'add',
            list_id: list_id,
            item_ids: []
        },
        success: (data) => {
            append_new_item(list_id,data)
        },
        error: (error) =>{
            console.log(error);
        }                        
    });

};

function sortable_event(action,list_id){

    let ids = document.querySelectorAll( "#" + list_id + " li[id]");
    let ids_list = [];
    for (let i = 0; i < ids.length; i++) {
        ids_list.push(ids[i].id);
    }       
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            sortable: true,
            action: action,
            list_id: list_id,
            item_ids: ids_list
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
}
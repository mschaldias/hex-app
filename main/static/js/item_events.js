
function edit_text(item_id,value){
    $.ajax({
        type:'POST',
        url: "/item_actions/",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            'id': item_id,
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
            'id': item_id,
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
            'id': item_id,
            action: 'remove'
        },
        // success:function(){
        //     alert('success');
        // }                        
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
            'sortable': true,
            'action': action,
            'list-id': list_id,
            'item-ids': ids_list
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
}

function sortable_event(action,list_id){

    let ids = document.querySelectorAll( "#" + list_id + " li[id");
    let ids_list = [];
    for (let i = 0; i < ids.length; i++) {
        ids_list.push(ids[i].id);
    }       
    $.ajax({
        type:'POST',
        url: "",
        data: {
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            'action': action,
            'list-id': list_id,
            'item-ids': ids_list
        },
        // success:function(){
        //     alert('success');
        // }                        
    });
}
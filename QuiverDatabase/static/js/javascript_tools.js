
function post_string_to_url(data, url, mode='same-origin')
{
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success:function(json) {
            //alert("Success!");
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}

function setup_ajax_csrf_token(csrf_token) { 
    // BUGFIX.  This took hours to get to work!  
    // And remember the csrf_token line at the top of template
    window.csrf_token = csrf_token
    
    $.ajaxSetup({          
        data: {csrfmiddlewaretoken: csrf_token },
    });				
}
        
function setup_edit_tag_setter_urls(tag_id_urls) 
{    
    $(document).ready(function() {
        for (const tag_url of tag_id_urls) {
            $(tag_url['tag_id']).editable(
            {	
                url: tag_url['setter'],
                pk: tag_url['pk'],
                
                error: function(response, newValue) {
                    return response.responseText;                    
                },
                
                success: function(response, newValue) {
                    var enable_ids = tag_url['enable_ids'];
                    
                    if(response.success) {
                        for (const tag_id of enable_ids)
                            $(tag_id).removeClass('invisible');
                    }
                    else {
                        for (const tag_id of enable_ids)
                            $(tag_id).addClass('invisible');
                        return response.error_msg;
                    }
                },
            });
            
            // BUGFIX: using .text() here causes a bug in which clicking on an editor's 
            // text item, the text is not shown in the edit field.  With the following, it *is* shown.
            $(tag_url['tag_id']).editable('setValue', tag_url['initial'], true);
        }
    });
}


function setup_ajax_csrf_token(csrf_token) { 
    // BUGFIX.  This took hours to get to work!  
    // And remember the csrf_token line at the top of template
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
                
                error: function(response, newValue) {
                    return response.responseText;                    
                },
                
                success: function(response, newValue) {
                    var enable_ids = tag_url['enable_ids'];
                    
                    if(response.success) 
                        for (const tag_id of enable_ids)
                            $(tag_id).removeClass('invisible');
                    else {
                        for (const tag_id of enable_ids)
                            $(tag_id).addClass('invisible');
                        return response.error_msg;
                    }
                },
            });
        }
    });
}
$(function() {
    $("#uploader").plupload({
	runtimes : 'html5',
	url : '.',
	max_file_size : '100mb',
	max_file_count: 20,
	chunk_size : '1mb',
	unique_names : true,
	multiple_queues : true,

	resize : {width : 320, height : 240, quality : 90},
	rename: true,
	sortable: true
    });
    $('form').submit(function(e) {
        var uploader = $('#uploader').plupload('getUploader');

        if (uploader.files.length > 0) {
            uploader.bind('StateChanged', function() {
                if (uploader.files.length === (uploader.total.uploaded + uploader.total.failed)) {
                    $('form')[0].submit();
                }
            });            
            uploader.start();
        } else {
            alert('You must at least upload one file.');
        }
        return false;
    });

    $('#resource_list .resource .delete').click(function(){
        var res = $(this).parents('.resource');
        $.ajax({url: res.data('name'),
                type: 'DELETE',
                success: function(text) {
                    res.fadeOut();
                }});
    })
});
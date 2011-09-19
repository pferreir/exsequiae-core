var oldContents;

$(window).load(function() {
    if (logged_in) {
        var term = $('#content').data('term');
        var edit_on = false;
        $('body').append($('<a id="edit_toggle" href="#">↩</a>'));

        $('#edit_toggle').bind('toggleState',
                               function() {
                                   (edit_on?hideEditor:showEditor).call(this, term);
                                   edit_on = !edit_on;
                               });

        $('#edit_toggle').click(function() {
            $(this).trigger('toggleState');
        });
    }
});

function resizeMarkedit() {
    $('.markedit').height($(window).height());
    $('.markedit textarea').height($(window).height() - 100);
}

function hideEditor(term) {
    $('#page').removeClass('inedit');
    $('#page').animate({width: '100%'}, 500);
    $('#editor').animate({right: '-=32%'}, 500, function() {
        $('body').append($('#edit_toggle').removeClass('expanded').html('↩'));
        $('#wrapper').replaceWith($('#page'));
        $('#content').html(oldContents);
    });

}

function loadContents(term) {
    $.ajax({url: '../' + term + '.json',
            success: function(text) {
                $('#edit_textarea').markeditSetState({
                    beforeSelect: text,
                    select: '',
                    afterSelect: '',
                    links: []});
            }});

}

function showEditor(term) {
    var old_page = $('#page')
    var bheight = $(window).height();

    oldContents = $('#content').html();

    $('#page').replaceWith($('<div id="wrapper"/>'))

    $('#wrapper').append($('<div id="editor"/>')).append(old_page)
    $('#editor').html('<textarea id="edit_textarea"/>');

    $('#editor').append($('#edit_toggle').addClass('expanded').html('↪'));
    $('#page').addClass('inedit')
    $('#page').animate({width: '67%'}, 500);

    $('#editor').show();
    $('#edit_textarea').markedit(
        {
            preview: false,
            postload: function() {
                $('#edit_textarea').markeditBindAutoPreview($('#content')); 
                loadContents(term);
            }
        });


    $('.markedit').append($('<div id="markedit_buttons"/>'));

    $('#markedit_buttons').append($('<button id="save_button">Save</button>'));
    $('#markedit_buttons').append($('<button id="cancel_button">Cancel</button>'));

    resizeMarkedit();

    $('#editor').animate({right: '+=32%'}, 500)

    $(window).resize(resizeMarkedit);

    $('#save_button').click(
        function() {
            var button = $(this);
            var state = $('#edit_textarea').markeditGetState();
            var text = state.beforeSelect + state.select + state.afterSelect;
            button.attr("disabled", true)
            $.ajax({'type': 'POST',
                    'url': '../' + term + '.json/',
                    'data': {content: text},
                    success: function(text) {
                        oldContents = $('#content').html();
                        button.attr("disabled", false);
                        var saved = $('<div class="saved">Saved!</div>').hide();
                        $(document.body).append(saved);
                        saved.fadeIn(100).delay(2000).fadeOut();
                    }});
            
        });

    $('#cancel_button').click(
        function() {
            $('#edit_toggle').trigger('toggleState');
        });
}
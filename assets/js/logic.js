function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function fireApiCall(url, successfn) {
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        type: "POST",
        url: url,
        data: {
        },
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: [
            function(msg) {
                console.log(msg);
            },
            successfn,
        ]
    });
}


function insertAtCaret(txtarea, text) {
    var strPos = 0;
    var br = ((txtarea[0].selectionStart || txtarea[0].selectionStart == '0') ?
        "ff" : (document.selection ? "ie" : false ) );
    if (br == "ie") {
        txtarea.focus();
        var range = document.selection.createRange();
        range.moveStart ('character', -txtarea.val().length);
        strPos = range.text.length;
    }
    else if (br == "ff") {
        strPos = txtarea[0].selectionStart;
    }

    var front = (txtarea.val()).substring(0,strPos);
    var back = (txtarea.val()).substring(strPos,txtarea.val().length);
    txtarea.val(front+text+back);
    strPos = strPos + text.length;
    if (br == "ie") {
        txtarea.focus();
        var range = document.selection.createRange();
        range.moveStart ('character', -txtarea.val().length);
        range.moveStart ('character', strPos);
        range.moveEnd ('character', 0);
        range.select();
    }
    else if (br == "ff") {
        txtarea[0].setSelectionRange(strPos, strPos);
        txtarea.focus();
    }
}

$('.ajax-call-reload').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), function(msg){location.reload();})
    return false;
});

$('button.subscribe-toggle').click(function() {
    var $a = $(this);
    if ($a.attr('id') == 'subscribe') {
        var antagonist = 'button#unsubscribe'
    }
    else {
        var antagonist = 'button#subscribe'
    }
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), function(msg){
        $(antagonist).prop("disabled",false).removeClass("disabled")
    })
    return false;
});

$('button.download-toggle').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'));
    return false;
});


$('.naming-scheme-segments > code').click(function() {
    var $input = $('#id_app-naming_scheme')
    insertAtCaret($input, $(this).text())
})


$('#id_opml_file').change(function() {
    var input = this.files[0];
    if (input) {
        $('#id_opml_file_inner').text(input.name);
    }
    else {
        $('#id_opml_file_inner').text('');
    };
})

var template = $.templates('#apsearch-template');
function searchReturn (data, textStatus, jqXHR) {
    $('#apsearch-attrib').show();
    if (data.resultCount == 0){
        $('#apsearch-results').hide()
        $('#apsearch-noresults').show();
    }
    else {
        var htmlOutput = template.render(data.results);
        $("#apsearch-results").html(htmlOutput);
        $('#apsearch-results').slideDown(200);
        $('.apsearch-addfeed').each(function(index) {
            $(this).on("click", function(e){
                e.preventDefault;
                $(this).attr('disabled', 'disabled');
                var feed_url = $(this).data('feed-url');
                var href = $(this).data('href');
                var id = $(this).data('id');
                var jqxhr = $.ajax({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    },
                    url: href,
                    type: 'POST',
                    data: {
                        feed_url: feed_url,
                    },
                    dataType: 'json',
                })
                .done(function () {
                    $('#apsearch-addfeed' + id).hide();
                    $('#apsearch-feedadded' + id).show();
                });
            });
        });
    };
    return false;
}

$('#apsearch button[type="submit"]').click(function(e){
    e.preventDefault;
    search_term = $('#apsearch input[name="search_term"]').val();
    if (search_term.length > 2) {
        var jqxhr = $.ajax({
            url: "https://itunes.apple.com/search",
            type: 'POST',
            data: {
                media: 'podcast',
                term: search_term,
                limit: 15,
            },
            dataType: 'json',
        })
        .done(searchReturn);
    };
    return false;
});


var episode_details = $.templates('#episode-details-template');
$('.episode-details-link').each(function(index) {
    $(this).on("click", function(e){
        e.preventDefault;
        var href = $(this).data('href');
        var jqxhr = $.ajax({
            url: href,
            type: 'GET',
            dataType: 'json',
        })
        .done(function (data, textStatus, jqXHR) {
            console.log(data);
            var htmlOutput = episode_details.render(data);
            $("#episodeDetailsModalContainer").html(htmlOutput);
            $('#episodeDetails').modal('show');
        });


    });
});

// function searchReturn (data, textStatus, jqXHR) {}

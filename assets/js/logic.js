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
        var successfn = function(msg){
            $('button#unsubscribe').prop("disabled",false).removeClass("disabled")
        }
    }
    else {
        var successfn = function(msg){
            $('button#subscribe').prop("disabled",false).removeClass("disabled")
        }
    }
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), successfn)
    return false;
});

$('.naming-scheme-segments > code').click(function() {
    var $input = $('#id_app-naming_scheme')
    insertAtCaret($input, $(this).text())
    // $input.focus()

})


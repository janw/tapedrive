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

$('.ajax-call-reload').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), function(msg){location.reload();})
    return false;
});

$('button#subscribe').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), function(msg){
        $('button#unsubscribe').prop("disabled",false).removeClass("disabled")
    })
    return false;
});

$('button#unsubscribe').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    fireApiCall($a.data('href'), function(msg){
        $('button#subscribe').prop("disabled",false).removeClass("disabled")
    })
    return false;
});

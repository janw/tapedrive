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

$('.api-caller').click(function() {
    var $a = $(this);
    $a.prop("disabled",true).addClass("disabled")
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        type: "POST",
        url: $a.data('href'),
        data: {
        },
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(msg) {
            console.log(msg);
            location.reload();
        }
    });
    return false;
});

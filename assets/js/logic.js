var search_results = [];
var topcharts_results = [];

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



////////////////////////////////////////////////////////////////////////////////
//
// PODCAST-RELATED FUNCTIONALITY
//


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



////////////////////////////////////////////////////////////////////////////////
//
// EPISODE-CENTRIC FUNCTIONALITY
//

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
            $('button.download-toggle').click(function() {
                var $a = $(this);
                $a.prop("disabled",true).addClass("disabled")
                fireApiCall($a.data('href'));
                return false;
            });
            replace_images();
        });
    });
});

function replace_images () {

    $('.has-src').hide().wrap(function() {
        return '<span class="img-has-src">' + $(this).text() + '</span>';
    });

    $('a').has('img.has-src').each(function(index) {
        $(this).data('href', $(this).attr('href'));
        $(this).attr('href', '#');
        $(this).on("click", function(e){
            e.preventDefault;
            console.log('Clicked img');
        });
     });

    $('.img-has-src').each(function(index) {
        var img = $($(this).find('img.has-src')[0]);
        $('<span class="img-alt">' + img.attr('alt') + '</span>').prependTo(this);

        $(this).on("click", function(event){
            event.preventDefault;
            var target = $(event.target);
            console.log('Target:', target);

            if (target.attr('class') == 'img-alt'){
                var wrapper = target.parent();
                console.log('clicked the alt')
            }
            else if (target.attr('class') == '.has-src') {
                var wrapper = target.parent();
                console.log('clicked img');
            }
            else {
                var wrapper = target;
            }

            $(wrapper.find('span.img-alt')[0]).empty().remove();
            var img = $(wrapper.find('img.has-src')[0]);
            img.attr('src', img.data('src')).unwrap().show();
        });
    })

}

////////////////////////////////////////////////////////////////////////////////
//
// SETTINGS VIEW FUNCTIONALITY
//


$('.naming-scheme-segments > code').click(function() {
    var $input = $('#id_app-naming_scheme')
    insertAtCaret($input, $(this).text())
})



////////////////////////////////////////////////////////////////////////////////
//
// APPLE PODCASTS SEARCH RELATED FUNCTIONALITY
//

var podcast_card = $.templates('#apsearch-template');

function searchReturn (data, textStatus, jqXHR) {
    $('#apsearch-results-spinner').hide();
    if (data.resultCount == 0){
        $('#apsearch-results').hide()
        $('#apsearch-noresults').show();
    }
    else {
        search_results = data.results;
        var htmlOutput = podcast_card.render(data.results);
        $('#apsearch-noresults').hide();
        $("#apsearch-results").html(htmlOutput).slideDown(400);
        $('#apsearch-attrib').slideDown(200);
    };
    return false;
}

function topchartsReturn (data) {
    topcharts_results = data.results;
    var htmlOutput = podcast_card.render(data.results);
    $("#apsearch-topcharts").html(htmlOutput).show();
    $('#apsearch-attrib').slideDown(200);
    return false;
}

$('#apsearch-addfeed').on("click", function(e){
    e.preventDefault;
    $(this).attr('disabled', 'disabled');
    var jqxhr = $.ajax({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        url: $(this).data('href'),
        type: 'POST',
        data: {
            feed_url: $(this).data('feed-url'),
            feed_id: $(this).data('id'),
        },
        dataType: 'json',
    })
    .done(function (data) {
        if (data.created == false) {
            console.log('Already there');
        }
        $('#apsearch-addfeed').hide();
        $('#apsearch-feedadded').show();
    });
});

$('#apsearch-details').on('show.bs.modal', function (e) {
    result_id = $(e.relatedTarget).data('id')
    result = search_results.find(x => x.id === result_id);
    if (typeof result === 'undefined') {
        result = topcharts_results.find(x => x.id === result_id);
    }
    if (typeof result === 'undefined') {
        return false;
    }
    console.log('Showing result details', result);

    $('#apsearch-artwork').prop('src', result.artworkUrl);
    $('#apsearch-title').text(result.name);
    $('#apsearch-artist').text(result.artistName);
    $('#apsearch-addfeed').show()
        .data('feed-url', result.feedUrl)
        .data('id', result.id)
        .removeAttr('disabled');
    $('#apsearch-feedadded').hide();

    var tmpl = $.templates('#apsearch-badge-template');
    var badges = tmpl.render(result.genres);
    $("#apsearch-badges").html(badges);

    return true;
})

$('#apsearch button[type="submit"]').click(function(e){
    e.preventDefault;
    search_term = $('#apsearch input[name="search_term"]').val();
    var url = $(this).data('href');
    console.log(url);
    if (search_term.length > 2) {
        var jqxhr = $.ajax({
            beforeSend: function(xhr, settings) {
                $('#apsearch-results-spinner').show();
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            },
            url: url,
            type: 'POST',
            data: {
                term: search_term,
            },
            dataType: 'json',
        })
        .done(searchReturn)
        .always(function() {
            $('#apsearch-results-spinner').hide();
        });
    };
    return false;
});

$('#apsearch-topcharts-refresh').click(function(e){
    e.preventDefault;
    var jqxhr = $.ajax({
        beforeSend: function(xhr, settings) {
            $('#apsearch-topcharts-spinner').show();
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        url: $(this).data('href'),
        type: 'GET',
        dataType: 'json',
    })
    .done(topchartsReturn)
    .always(function() {
        $('#apsearch-topcharts-spinner').hide();
    });
    return false;
});

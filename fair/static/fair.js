/**
 * Created by rasmusmunk on 08/09/2017.
 */
// The nbi_common.js file needs to be loaded before this

// error is the returned error object, expected to have a responseJSON dict
// that contains a "data" attribute with errors.
// The target is an html object that should support .append
function getMessages(dict) {
    var msg = "";
    for (var key in dict) {
        if (dict.hasOwnProperty(key)) {
            msg += dict[key];
        }
    }
    return msg;
}

function setupErdaImport() {
    //setup before functions
    var typingTimer;                //timer identifier
    var doneTypingInterval = 2000;  //time in ms, 2 seconds
    var $input = $('#erda_url');

    //on keyup, start the countdown
    $input.on('keyup mousedown', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });

    //on keydown, clear the countdown
    $input.on('keydown', function () {
        clearTimeout(typingTimer);
    });

    // Submit erda import link
    function doneTyping() {
        $('#form-erda span').remove();
        $('.loading-spinner').show();
        var _data = {
            'erda_url': $('#erda_url').val(),
            'csrf_token': $('#csrf_token').val()
        };
        $.ajax({
            url: '/erda_import',
            data: _data,
            type: 'POST',
            success: function (response) {
                $('.loading-spinner').hide();
                var json_response = response['data'];
                for (var key in json_response) {
                    if (json_response.hasOwnProperty(key)) {
                        $(".form-control#" + key).val(json_response[key]);
                    }
                }
            },
            error: function (error) {
                $('.loading-spinner').hide();
                var errors = error.responseJSON['data'];
                var msg = getMessages(errors);
                var span = document.createElement('span');
                span.className = "error help-inline";
                span.innerText = msg;
                var target = $('#form-erda .controls');
                target.append(span);
            }
        });
    }
}

// Projects page
if (location.pathname.match(/tag/)) {
    $(document).ready(function () {
        setupTagSearch(createProjectTile);
    });
}

if (location.pathname === '/create_project') {
    $(document).ready(function () {
        setupErdaImport();
    });
}

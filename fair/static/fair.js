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

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

// append a dropdown search result box to the sci_area form-control
function setupSciSearchBox() {
    var refElement = document.getElementById('sci_area');
    var target = refElement.parentNode.parentNode;
    var newList = document.createElement('ul');
    newList.className = "datalist form-control";
    newList.id = "sci_search_results";
    insertAfter(newList, target);
}

function setupSciSearch() {
    var $input = $('#sci_area');
    // populate search results on keyboard events and focus gained
    $input.on('keyup focus mousedown', function () {
        var _data = {
            'csrf_token': $('#csrf_token').val(),
            'sci_area': $input.val()
        };
        $.ajax({
            url: '/sci_area_search',
            data: _data,
            type: 'POST',
            success: function (response) {
                var jsonResponse = response['data'];
                var dataList = document.getElementById('sci_search_results');
                removeChildren(dataList);
                if (!isEmpty(jsonResponse)) {
                    for (var key in jsonResponse) {
                        if (jsonResponse.hasOwnProperty(key)) {
                            for (var value in jsonResponse[key]) {
                                if (jsonResponse[key].hasOwnProperty(value)) {
                                    var option = document.createElement('li');
                                    option.onmouseover = function () {
                                        this.style.background = "lightblue";
                                    };
                                    option.onmouseout = function () {
                                        this.style.background = "white";
                                    };
                                    option.onmousedown = function () {
                                        $('#sci_area').val(this.innerText);
                                    };
                                    option.innerText = jsonResponse[key][value];
                                    dataList.append(option);
                                }
                            }
                        }
                    }
                    $('#sci_search_results')
                        .attr('style', 'display: block; text-align: left;');
                }
            },
            error: function (error) {
                /* TODO -> a bit ugly */
                var errors = error.responseJSON['data'];
                var finalMsg = "";
                for (var error in errors) {
                    if (errors.hasOwnProperty(error)) {
                        for (var msg in errors[error]) {
                            if (errors[error].hasOwnProperty(msg)) {
                                finalMsg += errors[error][msg].join() + "\n";
                            }
                        }
                    }
                }
                var errorElement = $('#sci_error');
                if (errorElement.length) {
                    errorElement.innerText = finalMsg;
                } else {
                    var span = document.createElement('span');
                    span.id = "sci_error";
                    span.className = "error help-inline";
                    span.innerText = finalMsg;
                    var target = $('#sci_area');
                    target.after(span);
                }
            }
        })

    });

    // Clear search results on focus loss
    $input.on('focusout', function () {
        var dataList = document.getElementById('sci_search_results');
        removeChildren(dataList);
        $('#sci_search_results').attr('style', 'display: none');
    });
}

function createDatasetTile(dataset) {
    var newHeader = document.createElement('h3');
    newHeader.className = "card-title";
    newHeader.innerText = dataset.name;

    var newBody = document.createElement('p');
    newBody.className = "card-text";
    newBody.innerText = dataset.description;

    var newCaption = document.createElement('div');
    newCaption.className = "caption";
    newCaption.appendChild(newHeader);
    newCaption.appendChild(newBody);

    var newImage = document.createElement('img');
    newImage.src = "/images/" + dataset.image;
    newImage.alt = "Dataset";

    var newThumb = document.createElement('div');
    newThumb.className = "thumbnail mb-4";
    newThumb.appendChild(newImage);
    newThumb.appendChild(newCaption);

    var newLink = document.createElement('a');
    newLink.className = "d-block mb-4";
    newLink.href = "/show/" + dataset._id;
    newLink.appendChild(newThumb);

    var newDiv = document.createElement('div');
    newDiv.className = "col-sm-6 col-md-4 col-lg-3";
    newDiv.appendChild(newLink);
    return newDiv;
}

// Pages that support tag search
if (location.pathname.match(/\/search$/i) ||
    location.pathname === '/index' ||
    location.pathname === '/my_projects' ||
    location.pathname === '/') {

    $(document).ready(function () {
        setupTagSearch(createDatasetTile)
    });
}

if (location.pathname === '/create_project') {
    $(document).ready(function () {
        setupErdaImport();
        setupSciSearchBox();
        setupSciSearch();
    });
}

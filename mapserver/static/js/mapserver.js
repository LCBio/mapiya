// helper function used to insert csrf token into ajax post data
let getCookie = function (name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// helper function to check if jQuery returns undefined
$.fn.exists = function () {
    return this.length !== 0;
};


let fitHeight = function (viewport_id) {
    let offset = 200;
    $('#' + viewport_id).height($(window).innerHeight() - offset);
};

let initChart = function (map_pk, viewport_id) {
    fitHeight(viewport_id);

    $(window).resize(function () {
        fitHeight(viewport_id);
    });

    let $viewport = $('#' + viewport_id);

    $.getJSON('/map/' + map_pk + /data/, function (data) {
        // highcharts logic
    });

}

let initNGL = function (pdburl, viewport_id) {
    fitHeight(viewport_id);
    let $nglMenu = $('div.ngl-menu');
    let $icon = $('#nglMenuIcon');
    let $table = $nglMenu.find('table');
    let csrftoken = getCookie('csrftoken');
    let stage = new NGL.Stage(viewport_id, {backgroundColor: 'white'})
    representations = {};
    let struct;

    stage.loadFile(pdburl).then(function (o) {
        struct = o;

        $table.find('tbody').find('tr').each(function () {
            let key = $(this).attr('id');
            mkRepresentation(key);
        });

        o.autoView();
        $('.ngl-bottom-menu').css('visibility', 'visible');
    });

    $(window).resize(function () {
        fitHeight(viewport_id);
        stage.handleResize();
    });

    // onhover event handler for ngl menu on the right
    $nglMenu.hover(function () {
        $nglMenu.addClass('active');
        $icon.addClass('d-none');
        $table.removeClass('d-none');
    }, function () {
        $nglMenu.removeClass('active');
        $icon.removeClass('d-none');
        $table.addClass('d-none');
    });

    // "click on link within NGL table" event handler
    $table.on('click', 'a.ngl-cmd', function (event) {
        event.preventDefault();
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: $(this).attr('href'),
            method: 'POST',
            success: function (data) {
                if (data.error) {
                    alert(data.error);
                    // TODO: perhaps some nicer way to show errors
                } else if (data.addRep) {
                    let $newRow = $(data.addRep);
                    let key = $newRow.attr('id');
                    $table.find('tbody').append($newRow);
                    mkRepresentation(key);
                } else if (data.delRep) {
                    let key = data.delRep;
                    rmRepresentation(key);
                    $table.find('tr#' + key).remove();
                }
            }
        });
    });

    // "onchange" event handler for inputs and selects within NGL table
    $table.on('change', '.ngl-input', function () {
        let key = $(this).parents('tr').attr('id');
        let pk = key.split('_').pop();
        let dataobj = {
            'name': $(this).attr('name'),
            'value': $(this).val()
        };
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: '/ngl/' + pk + '/update/',
            method: 'POST',
            data: dataobj,
            success: function (data) {
                if (data.error) {
                    alert(data.error);
                } else if (data.updateRep) {
                    let key = data.updateRep;
                    rmRepresentation(key);
                    mkRepresentation(key);
                }
            }
        })
    });

    // toggle representation visibility event handler
    $table.on('click', 'a.ngl-eye', function () {
        let $icon = $(this).find('i');
        let key = $(this).parents('tr').attr('id');
        $icon.toggleClass(['fa-eye', 'fa-eye-slash']);
        representations[key].toggleVisibility();
    });

    // handler for on onclick event on the "cog" icon
    $table.on('click', 'a.ngl-options', function (event) {
        event.preventDefault();
        let url = $(this).attr('href');

        // current table row
        let $tr = $(this).parents('tr');
        let keyword = $(this).data('keyword');

        // next table row
        let $options = $tr.next();

        // if next row exists and has data-keyword attribute
        if ($options.exists() && $options.data('keyword')) {

            // if keywords match remove next row
            if ($options.data('keyword') === keyword) {
                $options.remove();
            }

        // create options panel as the next row in the table
        } else {
            $options = $('<tr><td colspan="5"><div></div></td></tr>');
            $options.insertAfter($tr);
        }

        // if panel options exists fill it with data fetched from the url and insert after current row
        if ($options.exists()) {
            $.ajax({
                url: url,
                method: 'GET',
                data: {keyword: keyword},
                success: function (data) {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        $options.data('keyword', keyword);
                        $options.find('div').html(data.html);
                    }
                }
            });
        }

    });

    // function which removes options panel when new type of representation is selected
    $table.on('change', 'select[name="representation"]', function () {
        let $options = $(this).parents('tr').next();
        if ($options.exists() && $options.data('keyword')) {
            if ($options.data('keyword') === 'representation') {
                $options.remove();
            }
        }
    });

    let fetchFromTable = function(key) {
        let $currentTr = $table.find('tr#' + key);
        return {
            'name': $currentTr.find('[name="name"]').val(),
            'color': $currentTr.find('[name="color"]').val(),
            'representation': $currentTr.find('[name="representation"]').val(),
            'selection': $currentTr.find('[name="selection"]').val()
        }
    };
    
    let rmRepresentation = function(key) {
        let rep = representations[key];
        struct.removeRepresentation(rep);
        delete representations[key];
    };

    let mkRepresentation = function(key) {
        let data = fetchFromTable(key);
        let pk = key.split('_').pop();
        let options = {};
        $.getJSON('/ngl/' + pk + '/options/', function (data) {
            options = data;
        });
        representations[key] = struct.addRepresentation(data.representation, Object.assign({}, {
            name: data.name,
            colorScheme: data.color,
            sele: data.selection,
        }, options));
    };

    $('#colorPicker').on('change', 'input', function () {
        stage.setParameters( { backgroundColor: $(this).val() } );
    });

    $('#fullScreen').on('click', function () {
        stage.toggleFullscreen();
    });

    $('#toggleSpin').on('click', function () {
        stage.toggleSpin();
    });

    $('#center').on('click', function () {
        stage.autoView();
    });

};

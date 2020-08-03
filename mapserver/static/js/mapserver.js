function getCookie(name) {
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
}

var initNGL = function (pdburl, viewport_id, map_pk) {
    var height_offset = 200;
    var fitHeight = function (viewport_id, offset) {
        $('#' + viewport_id).height($(window).innerHeight() - offset);
    };

    fitHeight(viewport_id, height_offset);
    let $nglMenu = $('div.ngl-menu');
    let $icon = $('#nglMenuIcon');
    let $table = $nglMenu.find('table');
    let csrftoken = getCookie('csrftoken');
    var stage = new NGL.Stage(viewport_id, {backgroundColor: 'white'})

    stage.loadFile(pdburl).then(function (o) {
        struct1 = o;
        o.addRepresentation("licorice", {colorScheme: "element"});

        $table.find('tbody').find('tr').each(function () {
            key = $(this).attr('id');
            mkRepresentation(key);
        });

        o.autoView();
        $('.ngl-bottom-menu').css('visibility', 'visible');
    });

    $(window).resize(function () {
        fitHeight(viewport_id, height_offset);
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
                    rmRepresentation(data.delRep);
                    $table.find('tr#' + data.delRep).remove();
                }
            }
        });
    });

    // "onchange" event handler for inputs and selects within NGL table
    $table.on('change', 'input, select', function () {
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
                    rmRepresentation(data.updateRep);
                    mkRepresentation(data.updateRep);
                }
            }
        })
    });

    $table.on('click', 'a.ngl-eye', function () {
        let $icon = $(this).find('i');
        let key = $(this).parents('tr').attr('id');
        $icon.toggleClass(['fa-eye', 'fa-eye-slash']);
        eval(key + '.toggleVisibility()')
    });

    var fetchFromTable = function(key) {
        let $currentTr = $table.find('tr#' + key);
        return {
            'name': $currentTr.find('[name="name"]').val(),
            'color': $currentTr.find('[name="color"]').val(),
            'representation': $currentTr.find('[name="representation"]').val(),
            'selection': $currentTr.find('[name="selection"]').val()
        }
    };
    
    var rmRepresentation = function(rep) {
        return struct1.removeRepresentation(eval(rep));
    };

    var mkRepresentation = function(rep) {
        return eval(rep +'=struct1.addRepresentation(fetchFromTable(rep).representation, {colorScheme: fetchFromTable(rep).color, sele: \'fetchFromTable(rep).selection\'})');
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

}







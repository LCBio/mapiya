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
    var stage = new NGL.Stage(viewport_id, {backgroundColor: 'white'})

    stage.loadFile(pdburl).then(function (o) {
        o.addRepresentation("cartoon", {colorScheme: "element"});
        o.autoView();
        $('.ngl-bottom-menu').css('visibility', 'visible');
    });

    $(window).resize(function () {
        fitHeight(viewport_id, height_offset);
        stage.handleResize();
    });

    let $nglMenu = $('div.ngl-menu');
    let $icon = $('#nglMenuIcon');
    let $table = $nglMenu.find('table');
    let csrftoken = getCookie('csrftoken');

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
                    // let costam = $newRow.find('[name="color"]');
                    // console.log(costam.val());
                    $table.find('tbody').append($newRow);
                    // TODO: here call to NGL function showRepresentation with arg = data.addRep
                } else if (data.delRep) {
                    $table.find('tr#' + data.delRep).remove();
                    // TODO: here call to NGL function deleteRepresentation with arg = data.delRep
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
                    // TODO: here call to NGL function modifyRepresentation with arg = data.updateRep
                    alert('Updated rep: ' + data.updateRep);
                }
            }
        })
    });

    $table.on('click', 'a.ngl-eye', function () {
        let $icon = $(this).find('i');
        let key = $(this).parents('tr').attr('id');
        $icon.toggleClass(['fa-eye', 'fa-eye-slash']);
        alert(key);
        // TODO: here call to NGL function toggleRepresentation with arg = key
    });
}

// var fun1 = function(representation_key, cmd) {
//     // ma odczytać wartości z tabeli html i przerobić na obiekt zrozumiały dla ngl.draw_rep
//     // cmd = {show, hide, delete}
// }

// $('#colorPicker').find('input').val();
// $('#colorPicker').on('change', 'input', function () {
//     alert($(this).val());
// });


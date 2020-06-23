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
        struct1 = o;
        basicRep = o.addRepresentation("cartoon", {colorScheme: "element"});
        o.autoView();
        $('.ngl-bottom-menu').css('visibility', 'visible');
    });

    $(window).resize(function () {
        fitHeight(viewport_id, height_offset);
        stage.handleResize();
    });

    var $nglMenu = $('.ngl-menu');
    var label_html = $nglMenu.html();
    var $table = $('<div></div>');
    var url = '/map/' + map_pk + '/table/';
    $.getJSON(url, function (data) {
        $table.html(data.html);
    });

    $(document).on('click', 'a.tablecmd', function (event) {
        event.preventDefault();
        $.ajax({
            url: $(this).attr('href'),
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'))
            },
            method: 'POST',
            data: {
                'cmd': $(this).data('cmd'),
                'pk': $(this).data('pk'),
            },
            success: function (data) {
                $table.html(data.html);
                $nglMenu.html($table.html());
            }
        })
    });

    $nglMenu.hover(function (event) {
        $nglMenu.html($table.html());
        $nglMenu.addClass('active');
    }, function (event) {
        $nglMenu.html(label_html);
        $nglMenu.removeClass('active');
    });

}
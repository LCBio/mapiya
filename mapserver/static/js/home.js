Dropzone.options.dropzone = {
    uploadMultiple: true,
    success: function (file, data) {
        let $table = $('table');
        if (! $table.exists()) {
            let $alert = $('.table-responsive .alert');
            $alert.replaceWith(data.table);
        }
        $table.html(data.table);
    }
};

// Options form
// TODO: this code should be optimized to check every dependency just once
let shouldShow = function ($input) {
    let requirements = $input.data('requirements');

    for (let requirement in requirements) {
        let values = requirements[requirement];
        let value = parseInt($('#id_' + requirement).val(), 10);
        if (!(values.includes(value))) return false;
    }
    return true;
};

let displayOptionsForm = function () {
    $('#optionsForm [data-requirements]').each(function () {
        let $row = $(this).parents('.form-group');
        if (shouldShow($(this))) {
            $row.removeClass('d-none').addClass('d-flex');
        } else {
            $row.removeClass('d-flex').addClass('d-none');
        }
    });
};

let initOptionsForm = function () {
    displayOptionsForm();
    $('#optionsForm input,select').on('change', function () {
        let $form = $(this).parents('form');
        $.ajax({
            url: $form.attr('action'),
            method: 'post',
            data: $form.serialize(),
            success: function (data) {
                displayOptionsForm();
            }
        });
    });
};

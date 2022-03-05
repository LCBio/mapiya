function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Options form
// TODO: this code should be optimized to check every dependency just once
let shouldShow = function ($input) {
    let requirements = $input.data('requirements');

    for (let requirement in requirements) {
        let values = requirements[requirement];
        let value = $('#id_' + requirement).val();
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
            success: async function (data) {
                displayOptionsForm();
                if (data.message) {
                    await sleep(250);
                    let $btn = $form.find('.btn-danger');
                    $btn.toggleClass('btn-danger btn-success');
                    let btnTxt = $btn.html();
                    $btn.html(data.message);
                    await sleep(500);
                    $btn.html(btnTxt);
                    $btn.toggleClass('btn-danger btn-success');
                }
            }
        });
    });
};

// Files table
let updateRow = function ($label) {
    let pk = $label.data('pk');
    let $link = $label.parents('tr').find('.temp-label');
    let $buttons = $label.parents('tr').find('.buttons');
    $.ajax({
        url: `/project/${pk}/status/`,
        success: function (data) {
            if (data.error) {
                $label.replaceWith(`<small class="text-danger font-weight-bold">$(data.error)</small>`);
            } else {
                let newLabel = $(data.msg);
                $label.replaceWith(newLabel);
                $link.replaceWith(data.link);
                $buttons.html(data.buttons)
                if (! data.completed) setTimeout(updateRow, 1000, newLabel);
            }
        }
    });
};

let initMapTable = function () {
    $('.progress-label').each(function () {
        updateRow($(this));
    });
};

// Dropzone
Dropzone.options.dropzone = {
    uploadMultiple: true,
    dictDefaultMessage: "4. Drop files here to download",
    success: function (file, data) {
        let $table = $('table');
        if (! $table.exists()) {
            let $alert = $('.help-wrapper');
            $alert.replaceWith(data.table);
        }
        $table.html(data.table);
        initMapTable();
    }
};


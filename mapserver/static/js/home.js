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

// Files table
let updateLabel = function ($label, complete, total) {
    console.log(complete, total);
    if (complete < total) {
        $label.find('span.complete-entry').html(`${complete}`);
    } else {
        let verbose = total > 1 ? 'models' : 'model';
        $label.replaceWith(`<small class="text-success">${total} ${verbose} ready!</small>`);
    }
};

let updateLink = function ($row, mapPk) {
    let $tempLabel = $row.find('.temp-label');
    if ($tempLabel.length > 0) {
        let link_txt = $tempLabel.html();
        let link_html = `<a href="/map/${mapPk}/">${link_txt}</a>`;
        $tempLabel.replaceWith(link_html);
    }
};

let updateRow = function ($label) {
    let mapPk = $label.data('map-pk');
    let $row = $label.parents('tr');
    $.ajax({
        url: `/map/${mapPk}/status/`,
        success: function (data) {
            let progress = JSON.parse(data.progress);
            if (progress[0] > 0) {
                updateLink($row, mapPk);
                updateLabel($label, progress[0], progress[1]);
                if (progress[0] < progress[1]) {
                    setTimeout(updateRow, 1000, $label);
                }
            } else {
                setTimeout(updateRow, 1000, $label);
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
    success: function (file, data) {
        let $table = $('table');
        if (! $table.exists()) {
            let $alert = $('.table-responsive .alert');
            $alert.replaceWith(data.table);
        }
        $table.html(data.table);
        initMapTable();
    }
};
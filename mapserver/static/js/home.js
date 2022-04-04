function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

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
                else handleRename($buttons.find('.rename-button'));
            }
        }
    });
};

const handleRename = function (renameButton) {
    renameButton.on('click', function (event) {
        event.preventDefault();
        const $td = renameButton.parents('tr').children(':nth-child(2)');
        const $link = $td.children('a');
        const oldName = $link.html();
        const $input = $(`<input class="rename-input" value="${oldName}"/>`);
        $td.html($input);
        $input.focus();

        $input.on('change', function (event) {
            $.ajax({
                url: renameButton.prop('href'),
                method: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                data: {
                    name: $input.val()
                },
                success: function (data) {
                    if (data.success) $link.html($input.val());
                }
            });
        });

        $input.on('focusout', function (event) {
            $td.html($link);
        });

        $input.on('keydown', event => {
            if (event.key === 'Escape') $input.focusout();
            else if(event.key === 'Enter') {
                if ($input.val() === oldName) $input.focusout();
                else {
                    $input.change();
                    $input.focusout();
                }
            }
        });

    });
};

let initMapTable = function () {
    $('.progress-label').each(function () {
        updateRow($(this));
    });
    $('.rename-button').each(function () {
        handleRename($(this));
    });
};

// Dropzone
Dropzone.options.dropzone = {
    uploadMultiple: true,
    dictDefaultMessage: "4. Drop files here",
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

let $modal = $('.modal');

$modal.on('show.bs.modal', function (event) {
    let $dialog = $(this).find('.modal-dialog');
    const modalSize = event.relatedTarget.getAttribute('data-size');
    const validSizes = ['xl', 'lg', 'sm'];
    if (validSizes.indexOf(modalSize) > -1) {
        $dialog.removeClass().addClass(`modal-dialog modal-${modalSize}`);
    } else {
        $dialog.removeClass().addClass('modal-dialog');
    }
    $(this).find('.modal-content').load(event.relatedTarget.href);
});

$modal.on('shown.bs.modal', function (event) {
    $(this).find('input').focus();
});

$modal.on('submit', 'form#rcsbForm', function (event) {
    event.preventDefault();
    let $form = $(this);
    $form.find('button').attr('disabled', true);

    $.ajax({
        url: $form.attr('action'),
        method: $form.attr('method'),
        data: $form.serialize(),
        success: function (data) {
            if (data.url) {
                window.location.replace(data.url);
            } else {
                $modal.find('.modal-content').html(data);
            }
        }
    });
});

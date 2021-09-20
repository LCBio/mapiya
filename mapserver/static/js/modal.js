let $modal = $('.modal');

$modal.on('show.bs.modal', function (event) {
    $(this).find('.modal-content').load(event.relatedTarget.href);
});

$modal.on('shown.bs.modal', function (event) {
    $(this).find('input').focus();
});

$modal.on('submit', 'form#rcsbForm', function (event) {
    event.preventDefault();
    let $form = $(this);
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

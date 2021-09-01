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

// helper function to check if jQuery returns undefined
$.fn.exists = function () {
    return this.length !== 0;
};

// enable all tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

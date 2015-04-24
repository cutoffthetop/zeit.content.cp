(function ($) {

var FIELDS = {
    'centerpage': 'referenced_cp',
    'channel': 'query',
    'query': 'raw_query'
};


var show_matching_field = function(container, current_type) {
    $(['referenced_cp', 'query', 'raw_query']).each(function(i, field) {
        var method = field == FIELDS[current_type] ? 'show' : 'hide';
        $('.fieldname-' + field, container)[method]();
    });
};


$(document).bind('fragment-ready', function(event) {
    var type_select = $('.fieldname-automatic_type select', event.__target);
    show_matching_field(event.__target, type_select.val());
    type_select.on(
        'change', function() {
            show_matching_field(event.__target, $(this).val());
    });
});

}(jQuery));

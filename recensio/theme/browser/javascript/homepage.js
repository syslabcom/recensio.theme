jq(document).ready(function ($) {
    $("#content_left .ellipsis_container").ThreeDots({max_rows: 3});
    $('#list_reviews_en').easyticker();
    $('#list_reviews_de').easyticker();
    $('#list_reviews_int').easyticker();
})(jq);
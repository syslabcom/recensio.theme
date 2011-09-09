jq(document).ready(function () {
    jq("#content_left .ellipsis_container").ThreeDots({max_rows: 3});
    jq('#list_reviews_en').easyticker();
    jq('#list_reviews_de').easyticker();
    jq('#list_reviews_int').easyticker();
});
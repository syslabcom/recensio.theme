jq(document).ready(function () {
    jq("#latest_reviewparts_box .ellipsis_container, \
        #latest_monographies_box .ellipsis_container, \
        #latest_internet_resources_box .ellipsis_container")
        .ThreeDots({max_rows: 4});
    jq("#latest_reviews_box .ellipsis_container").ThreeDots({max_rows: 4});
    /* The ticker items need to be displayed so that the size can be
       calculated by ThreeDots. They can then be hidden. Using
       visibility in css to avoid seeing an ugly flash of text before
       the page is loaded and the JavaScript kicks in. */
    jq('div#latest_reviews_box ul li.not_first').css('display', 'none')
    jq('div#latest_reviews_box ul li.not_first').css('visibility', 'visible')

    jq('#list_reviews_en').easyticker();
    jq('#list_reviews_de').easyticker();
    jq('#list_reviews_int').easyticker();

});
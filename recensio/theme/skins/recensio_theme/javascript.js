// hide_title is a style for the rich text editor.
// This logic will always hide/unhide the next element
jq(function(){
    jq('h4.hide_title').click(function(){
        jq(this).next().toggle();
    });
});

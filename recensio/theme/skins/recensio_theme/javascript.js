jq(document).ready(function() {
// hide_title is a style for the rich text editor.
// This logic will always hide/unhide the next element
    if (navigator.appName.search("Microsoft") !== -1) { // workaround for IE
        jq('p.hide_content').show();
    }
    jq('h4.hide_title').click(function() {
        jq(this).next().toggle();
    });
    

    jq('.easyticker').easyticker({
        speed: 'slow',
        dureeAffichage: 7000
        });
});

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

// This is a tiny bit hacky. BoolWidgets don't support 'required' property and 
// don't show errors. We add the basics via jquery.
    jq('#formfield-form-declaration_of_identity label').after('<span style="color: #f00;" title="Required" class="required"> ■ </span>')
    if (jq('dl.error').length > 0 && !jq('#formfield-form-declaration_of_identity input.checkboxType').attr('checked')) {
            jq('#formfield-form-declaration_of_identity').addClass('error');
    }
});

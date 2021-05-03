jq(document).ready(function () {
    jq(".fieldErrorBox").each(function () {
        if (this.textContent) {
            jq(this).addClass("highlighted");
        }
    });
    // hide_title is a style for the rich text editor.
    // This logic will always hide/unhide the next element
    if (navigator.appName.search("Microsoft") !== -1) {
        // workaround for IE
        jq("p.hide_content").show();
    }
    jq("h4.hide_title").click(function () {
        jq(this).next().toggle();
    });

    jq(".easyticker").easyticker({
        speed: "slow",
        dureeAffichage: 7000,
    });

    // This is a tiny bit hacky. BoolWidgets don't support 'required' property and
    // don't show errors. We add the basics via jquery.
    jq("#formfield-form-declaration_of_identity label").after(
        '<span style="color: #f00;" title="Required" class="required"> ■ </span>'
    );
    if (
        jq("dl.error").length > 0 &&
        !jq("#formfield-form-declaration_of_identity input.checkboxType").attr("checked")
    ) {
        jq("#formfield-form-declaration_of_identity").addClass("error");
    }

    if (jq("textarea#subject").length) {
        jq.getJSON(portal_url + "/subject_list_json", function (data) {
            jq("textarea#subject").typeahead({
                source: data,
                matcher: function (term) {
                    var entries = this.query.split("\n"),
                        searching_for = entries[entries.length - 1];
                    return term.search(searching_for) !== -1;
                },
                updater: function (term) {
                    var entries = this.query.split("\n");
                    return entries
                        .slice(0, entries.length - 1)
                        .concat([term])
                        .join("\n");
                },
            });
        });
    }
});

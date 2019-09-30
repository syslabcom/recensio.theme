oai_overlay=null;
function getDataFromOAI(isbn){
    var baseURL = portal_url + '/metadata_query?identifier=';
    jq.ajax({
        url: baseURL + isbn,
        dataType: 'json',
        success: function(data, textStatus, XMLHttpRequest){
            showResults(data);
        },
        error: function(data, textStatus, errorThrown){
            jq('#oaisuggestions .spinner').hide();
            alert("Error: " + textStatus);
        }
    })

}
function showResults(data){
    jq('#oaisuggestions .spinner').hide();
    jq('.missing_explanation_2:not(#missing_explanation_2_template)').remove();
    if(!data.length){
        var tmpl = jq('#oaisuggestiontemplateempty').clone();
        tmpl[0].id = "";
        jq('#oaisuggestiontemplate').after(tmpl).next().show();
        return
    }
    for (var result_id=data.length-1;result_id>=0;result_id--){
        var tmpl = jq('#oaisuggestiontemplate').clone();
        tmpl[0].id = "";
        var result = data[result_id];
        for (key in result){
            if (jq.inArray(key, ['keywords', 'authors', 'editors']) < 0) {
                tmpl.find('.oai_' + key + ' .value').text(result[key]);
            }
        }
        for(var i=0;i<result['keywords'].length;i++){
            tmpl.find('.oai_keywords .value ul').append('<li>'+result['keywords'][i]+'</li>')
        }
        var subtitle = tmpl.find('.oai_subtitle td.value');
        if (subtitle.text()) {
            subtitle.text(subtitle.text()[0].toUpperCase() + subtitle.text().substring(1));
        }
        for(var i=0;i<result['authors'].length;i++){
            var author = result['authors'][i];
            tmpl.find('.oai_authors .value').append('<div class="author"><span class="firstname">' +
                author['firstname'] + '</span> <span class="lastname">' +
                author['lastname'] + '</span></div>');
        }
        for(var i=0;i<result['editors'].length;i++){
            var editor = result['editors'][i];
            tmpl.find('.oai_editors .value').append('<div class="editor"><span class="firstname">' +
                editor['firstname'] + '</span> <span class="lastname">' +
                editor['lastname'] + '</span></div>');
        }
        var ddcs = ['ddcSubject', 'ddcTime', 'ddcPlace'];
        for(var i=0;i<ddcs.length;i++){
            var ddc = ddcs[i];
            jq(result[ddc]).each(function(i, data){
                var css_class = 'missing';
                var li_text = data;
                var source_id = ddc;
                if (ddc == 'ddcPlace') {
                    source_id = ddc + '_bsb';  // ddcPlace values differ in BSB
                }
                var matching_elems = jq('#' + source_id + ' option').filter(function(){return this.value == data;});
                if(matching_elems.length){
                    css_class = '';
                    li_text = matching_elems[0].text;
                }
                if (ddc == 'ddcPlace') {
                    var matching_elems = jq('#' + ddc + ' option').filter(function(){return this.text == li_text;});
                    if(matching_elems.length){
                        data = matching_elems[0].value;
                    } else {
                        css_class = 'missing';
                    }
                }
                tmpl.find('.oai_' + ddc + ' ul').append('<li ddc_id="' + data + '" class="' + css_class + '">' + li_text + '</li>');
            });
        }
        tmpl.find('.source_link').attr('href', result['source']['url']);
        tmpl.find('.source_link .source_name').text(result['source']['title']);
        jq('#oaisuggestiontemplate').after(tmpl).next().show();
    }
    jq('.useit').click(function(){takeOver(this);});
    oai_overlay = jq('#oaisuggestions').overlay();
}

function takeOver(elem){
    var j = jq(elem).parent().parent();
    var missing_flag = false;
    function takeSimpleInputOver(source, destination){
        if (destination === undefined){
            destination = source;
        }
        var new_val = j.find('.oai_' + source + ' .value').text().trim();
        if (new_val){
            jq('input#' + destination).val(new_val);
        }
    }
    takeSimpleInputOver('title');
    takeSimpleInputOver('subtitle');
    takeSimpleInputOver('location', 'placeOfPublication');
    takeSimpleInputOver('publisher');
    takeSimpleInputOver('series');
    takeSimpleInputOver('seriesVol');
    takeSimpleInputOver('pages');
    takeSimpleInputOver('bv');
    takeSimpleInputOver('ppn');
    takeSimpleInputOver('year', 'yearOfPublication');
    var new_lang = j.find('.oai_language .value').text().trim();
    jq('select#languageReviewedText').val(new_lang);
    j.find('.author').each(function(){
        var j = jq(this);
        var new_firstname = j.find('.firstname').text();
        var new_lastname = j.find('.lastname').text();
        var name_exists = false;
        jq('#archetypes-fieldname-authors tr#datagridwidget-row').each(function(){
            var existing_firstname = jq(this).find('input')[1].value
            var existing_lastname = jq(this).find('input')[0].value
            if (new_firstname == existing_firstname && new_lastname == existing_lastname){
                name_exists = true;
            }
        });
        if(!name_exists){
            jq('#archetypes-fieldname-authors #datagridwidget-add-button').click();
            jq('#archetypes-fieldname-authors #datagridwidget-row:last #firstname_authors_new').val(new_firstname);
            jq('#archetypes-fieldname-authors #datagridwidget-row:last #lastname_authors_new').val(new_lastname);
        }
    });
    var ddcs = ['ddcSubject', 'ddcTime', 'ddcPlace'];
    for(var i=0;i<ddcs.length;i++){
        var ddc = ddcs[i];
        j.find('.oai_' + ddc + ' li').each(function(){
            if(jq(this).attr('class') == 'missing'){
                if(! missing_flag){
                    jq('#missing_explanation').show();
                    jq('#' + ddc + '_help').append(jq('#missing_explanation_2_template').clone().show());
                    missing_flag = true;
                }
                jq('.missing_explanation_2 ul').append(this);
            }else{
                var set_elements = jq('#' + ddc).val() || [];
                set_elements[set_elements.length] = this.attributes['ddc_id'].value
                jq('#' + ddc).val(set_elements);
            }
        });
    }
    j.find('.oai_keywords li').each(function(){
        var new_val = this.textContent;
        var existing_option = jq('#archetypes-fieldname-subject textarea#subject');
        if (existing_option.val().match(new_val)) {
            /* do nothing, already in */
        }else{
            /* Append */
            newstr = existing_option.val()+'\n'+new_val;
            existing_option.val(newstr);
        }
        /*var existing_option = jq('#archetypes-fieldname-subject select[name=subject_existing_keywords:list] option[value=' + new_val + ']');
        if(existing_option.length){
            existing_option.attr('selected', 'selected');
        }else{
            var old_new_keywords = jq('#archetypes-fieldname-subject textarea#subject_keywords').val()
            old_new_keywords = old_new_keywords + new_val + '\n';
            jq('#archetypes-fieldname-subject textarea#subject_keywords').val(old_new_keywords);
        }*/
    });
    jq('#oaisuggestions .close').click();
}


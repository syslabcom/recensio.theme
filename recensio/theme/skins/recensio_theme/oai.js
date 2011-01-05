oai_overlay=null;
function getDataFromOAI(isbn){
    var baseURL = '/recensio/opac?identifier=';
    jq.getJSON(baseURL + isbn, function(data, textStatus, XMLHttpRequest){
        showResults(data);
     });

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
    for (result_id in data){
        var tmpl = jq('#oaisuggestiontemplate').clone();
        tmpl[0].id = "";
        var result = data[result_id];
        for (key in result){
            tmpl.find('.oai_' + key + ' .value').text(result[key]);
        }
        for(var i=0;i<result['authors'].length;i++){
            var author = result['authors'][i];
            tmpl.find('.oai_authors .value').append('<span class="author"><span class="firstname">' +
                author['firstname'] + '</span> <span class="lastname">' +
                author['lastname'] + '</span></span>');
        }
        var ddcs = ['ddcSubject', 'ddcTime', 'ddcPlace'];
        var i;
        for(i=0;i<=ddcs.length;i++){
            var ddc = ddcs[i];
            jq(result[ddc]).each(function(i, data){
                var css_class = 'missing';
                var li_text = data;
                var matching_elems = jq('#' + ddc + ' option').filter(function(){return this.value == data;});
                if(matching_elems.length){
                    css_class = '';
                    li_text = matching_elems[0].text;
                }
                tmpl.find('.oai_' + ddc + ' ul').append('<li ddc_id="' + data + '" class="' + css_class + '">' + li_text + '</li>');
            });
            jq('#oaisuggestiontemplate').after(tmpl).next().show();
        }
    }
    jq('.useit').click(function(){takeOver(this);});
    oai_overlay = jq('#oaisuggestions').overlay();
}

function takeOver(elem){
    var j = jq(elem).parent().parent();
    var missing_flag = false;
    jq('input#title').val(j.find('.oai_title .value').text().trim());
    jq('input#subtitle').val(j.find('.oai_subtitle .value').text().trim());
    jq('input#placeOfPublication').val(j.find('.oai_location .value').text().trim());
    jq('input#publisher').val(j.find('.oai_publisher .value').text().trim());
    jq('input#pages').val(j.find('.oai_pages .value').text().trim());
    jq('input#yearOfPublication').val(j.find('.oai_year .value').text().trim());
    jq('select#languageReviewedText').val(j.find('.oai_language .value').text().trim());
    j.find('.author').each(function(){
        var j = jq(this);
        jq('#archetypes-fieldname-authors #datagridwidget-add-button').click();
        jq('#archetypes-fieldname-authors #datagridwidget-row:last #firstname_authors_new').val(j.find('.firstname').text());
        jq('#archetypes-fieldname-authors #datagridwidget-row:last #lastname_authors_new').val(j.find('.lastname').text());
    });
    var ddcs = ['ddcSubject', 'ddcTime', 'ddcPlace'];
    for(var i in ddcs){
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
    jq('#oaisuggestions .close').click();
}


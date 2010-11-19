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
        jq(result['ddc']).each(function(i, data){
            var css_class = 'missing';
            if(jq('#ddcSubject option, #ddcTime option, #ddcPlace option').filter(function(){return this.text == data;}).length){
                css_class = '';
            }
            tmpl.find('.oai_ddc ul').append('<li class="' + css_class + '">' + data + '</li>');
        });
        jq('#oaisuggestiontemplate').after(tmpl).next().show();
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
    j.find('.oai_ddc li').each(function(){
        if(jq(this).attr('class') == 'missing'){
            if(! missing_flag){
                jq('#missing_explanation').show();
                jq('#ddcSubject_help, #ddcTime_help, #ddcPlace_help').append(jq('#missing_explanation_2_template').clone().show());
                missing_flag = true;
            }
            jq('.missing_explanation_2 ul').append(this);
        }else{}
            jq('#ddcSubject option, #ddcTime option, #ddcPlace option').filter(function(){return this.text == "Agrargeschichte";}).each(function(){
                var new_value = jq(this).val();
                var parent_ = jq(this).parent();
                var old_values = parent_.val();
                old_values.push(new_value);
                parent_.val(old_values);
            }); 
        //}
    });
    jq('#oaisuggestions .close').click();
}


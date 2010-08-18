
function getDataFromOAI(isbn, base_year){
    var baseURL = '/recensio/oai?identifier=';
    var identifiers = [isbn + (base_year - 1), isbn + base_year, isbn + (base_year + 1)];
    var identifiers = [isbn + base_year];
    for (i=0;i<identifiers.length;i++){
        jq.ajax({
            url : baseURL + identifiers[i],
            success : function(data, textStatus, XMLHttpRequest){
                var parser = DOMParser();
                var doc = parser.parseFromString(data, 'text/xml');
                var result = {};
                var dc_keys = ['title'
                              ,'creator'
                              ,'subject'
                              ,'description'
                              ,'publisher'
                              ,'contributor'
                              ,'date'
                              ,'type'
                              ,'format'
                              ,'identifier'
                              ,'source'
                              ,'language'
                              ,'relation'
                              ,'coverage'
                              ,'rights']
                for(var i=0;i<dc_keys.length;i++){
                    var dc_key = dc_keys[i];
                    result[dc_key] = jq('dc\\:' + dc_key, doc).map(function(){
                        return jq(this).text()
                    });
                };
                showResults(result);
            },
        });

    }
}
function showResults(data){
    var tmpl = jq('#oaisuggestion_template').clone();
    tmpl[0].id = "";
    var li_tmpl = jq('li.dc_definition', tmpl).clone();
    jq('li.dc_definition', tmpl).remove();
    var ul = jq('ul', tmpl);
    
    for (prop in data){
        var li = li_tmpl.clone();
        jq('def', li).text(prop);
        var inner_ul = jq('ul', li);
        var inner_li_tmpl = jq('li', inner_ul);
        jq('li', inner_ul).remove();
        for(var i=0;i<data[prop].length;i++){
            var inner_li = inner_li_tmpl.clone();
            inner_li.text(data[prop][i]);
            inner_ul.append(inner_li);
        }
        ul.append(li);
    }
    jq('#oaisuggestions').append(tmpl);
    tmpl.show();
}

getDataFromOAI('oai:nature.com:10.1038/scientificamerican0891-', 40);

//jQuery('#35e944af00da16d8f5a02b59a4ac7a06 ul').load('http://www.recensio.loc/rezensionen/zeitschriften/sehepunkte/index_html?expand:list=35e944af00da16d8f5a02b59a4ac7a06 #35e944af00da16d8f5a02b59a4ac7a06 ul > *')


jq(document).ready(function() {
    jq('.review_container a').removeAttr('href').css('cursor', 'pointer').click(function(e) {
        var targ;
        if (!e) var e = window.event;
        if (e.target) targ = e.target;
        else if (e.srcElement) targ = e.srcElement;
        if (targ.nodeType == 3) // defeat Safari bug
            targ = targ.parentNode;
        
        targ = jq(targ);
        if (targ.nodeName != 'div') {
            targ = targ.closest('div');
        }

        ul = targ.find('ul');
        if (targ.hasClass('expanded')) {
            ul.toggle('slow', function () {
                targ.removeClass('expanded');
            });
        } else {
            if (ul.find('> *').length == 0) {
                base_url = document.location.protocol + '//' + document.location.host + document.location.pathname;
                ul.load(base_url + '?expand:list=' + targ.attr('id') + ' #' + targ.attr('id') + ' ul > *', function() {
                    ul.toggle('slow'); 
                    targ.addClass('expanded');
                });
            } else {
                ul.toggle('slow');
                targ.addClass('expanded');
            }
        }
    })
});
        

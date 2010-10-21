/*
* jQuery easyTicker plugin
* Update on 24 september 2009
* Version 1.0
* Autor : Stéphane Litou (www.mushtitude.com)
*
* Licensed under GPL <http://en.wikipedia.org/wiki/GNU_General_Public_License>
* Copyright (c) 2008, Stéphane Litou <contact@mushtitude.com>
* All rights reserved.
*
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

(function(jQuery){
	jQuery.fn.easyticker = function(options) {
			var settings = {
				dureeAffichage: 5000,
				speed: 'slow'
			};
			if(options) {
				jQuery.extend(settings, options);
			}			
			return this.each(function () {
				var prochain;
				$(this).everyTime(settings.dureeAffichage, function(i) {
					if(i == 1) {
						current = $(this).children('li:first');		
					}else {			
						current = prochain;			
					}
					prochain = $(current).next('li');
					if(!$(prochain).html()) {
						prochain = $(this).children('li:first');
					}
					$(current).fadeOut(settings.speed);
					$(prochain).fadeIn(settings.speed);
				});
			});
			
			
			/*
			$(this).everyTime(settings.dureeAffichage, function(i) {
				if(i == 1) {
					current = $(this).children('li:first');		
				}else {			
					current = prochain;			
				}
				prochain = $(current).next('li');
				if(!$(prochain).html()) {
					prochain = $(this).children('li:first');
				}
				$(current).fadeOut(settings.speed);
				$(prochain).fadeIn(settings.speed);
			});
			*/
	};
})(jQuery);

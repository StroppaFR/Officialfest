/*
 * Copyright (c) 2005 Motion-Twin
 */

function replaceSelection(input, begin, end)
{
	if (input.setSelectionRange) {
		var selectionStart = input.selectionStart;
		var selectionEnd = input.selectionEnd;
		var replaceString = begin 
			+ input.value.substring(selectionStart, selectionEnd) 
			+ end;
		input.value = input.value.substring(0, selectionStart) 
			+ replaceString 
			+ input.value.substring(selectionEnd);
	}
	else if (document.selection) {
		var range = document.selection.createRange();
		if (range.parentElement() == input) {
			var isCollapsed = range.text == '';
			var replaceString = begin + range.text + end;
			range.text = replaceString;
			if (!isCollapsed){
				//it apears range.select() should select the newly
				//inserted text but that fails with IE
				range.moveStart('character', - replaceString.length);
				range.select();
			}
		}
	}
}

function insertText(txt)
{
	var area = document.form.content;
	area.focus();
	replaceSelection(area, txt, '');
}

function insertTag(begin, end)
{
	var area = document.form.content;
	area.focus();
	replaceSelection(area, begin, end);
}

function insertUrl()
{
	var url = prompt("Entrez l'adresse de la page :",'http://');
	if (url.length > 10) {
		var comment = prompt("Entrez le texte de votre lien :",url);
		if (comment.length == 0 || comment == url) {
			return insertText('[lien]'+url+'[/lien]');
		}
		else {
			return insertText('[lien='+url+']'+comment+'[/lien]');
		}
	}
	else {
		alert('Cette adresse semble non valide.');
	}
}


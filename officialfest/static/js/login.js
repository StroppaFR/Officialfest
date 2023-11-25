// Support for Enter key (13) in IE to submit login form
// (c) 2006 MotionTwin
//
// Full credits : Johan Känngård
// URL: http://dev.kanngard.net/Permalinks/ID_20050426091851.html

ie=(document.all)?true:false;

function keyDown(e) {
	if (!ie) {
		return;
	}
	var evt=(e)?e:(window.event)?window.event:null;
	if(evt){
		var key=(evt.charCode)?evt.charCode: ((evt.keyCode)?evt.keyCode:((evt.which)?evt.which:0));
		if( key=="13" ) {
			document.loginFormObject.submit()
		}
	}
}

document.onkeydown=keyDown;

boxee.browserWidth=1920;
boxee.browserHeight=1080;
boxee.enableLog(true);
boxee.renderBrowser=false;
boxee.autoChoosePlayer=true;
boxee.setDefaultCrop(0,0,0,18);

if(boxee.getVersion() > 1.8)
{
  boxee.setCanPause(true);
  boxee.setCanSkip(false);
  boxee.setCanSetVolume(false);
}

var count=1;

boxee.onPlay = function() {
	boxee.getActiveWidget().click(58,360);
}
 

boxee.onPause = function() {
	boxee.getActiveWidget().click(58,360);
}

function setActiveWidget()
{
	if(count != 10) {
player = "document.getElementById('ply')";
browser.execute(player+'.sendEvent("PLAY","true");');
setTimeout(setActiveWidget,3500);
	count = count + 1
	}
}
 
setTimeout(setActiveWidget,3500);



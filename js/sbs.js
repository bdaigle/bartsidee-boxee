boxee.enableLog(true);
boxee.renderBrowser = true;
boxee.autoChoosePlayer = false;
	
var current    = 0;
var active     = false;
var duration   = false;
var is_paused  = false;

boxee.onEnter = function()
{
    boxee.setMode(0);
    boxee.showNotification("[B]Schakelen naar volledig scherm...[/B]", ".", 2);
	playerTimer = setInterval(function(){
	if (!active) {
		   locatePlayer();
		   clearInterval(playerTimer);
	 }
	}, 1000)
}


function locatePlayer()
{
	   boxee.getWidgets().forEach(function(widget) {
		  if (widget.getAttribute("id") == 'myExperience1172254533001') {
			 active = true;
			 boxee.renderBrowser = false;
			 boxee.notifyConfigChange(widget.width, widget.height);
			 widget.setActive(true);
			 if(boxee.getVersion() > 7 ) {
				boxee.click(500,500)
			 } else {
				boxee.getActiveWidget().mouseMove(5,5)
			}
		  }
	   });

	   if (active)
	   {
		  if(boxee.getVersion() > 7 ) {
			  playerState.canPause = true;
		  } else {
			  boxee.setCanPause(true);
			  boxee.setCanSkip(false);
			  boxee.setCanSetVolume(false);
		  }
	   }

	   return active;
}
boxee.onDocumentLoading = function() {
	   boxee.setMode(1);
	   boxee.showNotification("[B]Druk NA de RECLAME op ENTER als de video begint te spelen [/B]", ".", 500);
}
	
if(boxee.getVersion() > 7 ) {
	boxee.apiMinVersion = 7.0;
	boxee.realFullScreen = false;
	boxee.showOSDOnStartup = false;
	boxee.autoChooseMouseLocation = false;

	boxee.onPause = function()
	{
	   playerState.isPaused = true;
	   boxee.getActiveWidget().mouseMove(400,400)
	   boxee.getActiveWidget().click(400,400)
	   boxee.getActiveWidget().click(100,600);
	}

	boxee.onPlay = function()
	{
	   playerState.isPaused = false;
	   boxee.getActiveWidget().mouseMove(400,400)
	   boxee.getActiveWidget().click(400,400)
	   boxee.getActiveWidget().click(100,600);
	}	
} else {	   
	boxee.onPause = function()
	{
	   is_paused = true;
	   boxee.getActiveWidget().mouseMove(10,10)
	   boxee.getActiveWidget().click(42,315);
	}

	boxee.onPlay = function()
	{
	   is_paused = false;
	   boxee.getActiveWidget().mouseMove(20,20)
	   boxee.getActiveWidget().click(42,315);
	}
}



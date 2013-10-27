boxee.enableLog(true);
boxee.autoChoosePlayer=false;
boxee.renderBrowser=true;

boxee.onInit = function() {
   browser.setCookie(".bbc.co.uk", "BBCPGstat", "0%3A-");
   browser.setCookie("empsize=large&ia=1");
}

var btn_y = 374;

var btn_x1 = 16;
var btn_x2 = 722;
var btn_x3 = 560;

var hasActive=false;
var Rescale=false;
var Subtitle=true;

if (boxee.getVersion() > 3.0)
{
	boxee.setCanPause(true);
	boxee.setCanSkip(false);
	boxee.setCanSetVolume(false);
}

function poll()
{
	if (!hasActive)
	{
		boxee.getWidgets().forEach(function(A)
		{
			if (A.getAttribute("src") != -1 && A.getAttribute('id') == 'bbc_emp_embed_emp')
			{
				A.setActive(true);
				if (A.width == 640 && !Rescale)
				{
					setTimeout(largeScale, 2000);
					Rescale=true;
					poll();
				}
				else if(A.width == 832)
				{
					hasActive=true;
					btn_y = 482;
					btn_x2 = 697;				
					boxee.renderBrowser=false;
					A.setActive(true);
					boxee.notifyConfigChange(A.width,A.height-40);
					setTimeout(startPlay, 2800);				
				}
				else
				{
					hasActive=true;
					btn_y = 374; 
					btn_x2 = 505;
					boxee.renderBrowser=false;
					A.setActive(true);
					boxee.notifyConfigChange(A.width,A.height-40);
					setTimeout(startPlay, 2800);
				}
			}
		});
	}
}
boxee.onDocumentLoaded = function() {
   boxee.setMode(1);
   boxee.showNotification("[B]Press Enter to view full screen when page is loaded[/B]", ".", 500);
}

boxee.onEnter = function()
{
    boxee.setMode(0);
	boxee.showNotification("[B]Switching to full screen...[/B]", ".", 2);
	setTimeout(poll,1000);
}


function startPlay()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
	setTimeout(function() {if(Subtitle)
		{
			boxee.getActiveWidget().click(btn_x2,btn_y);
		}
	}, 10000);
}

function largeScale()
{
	boxee.getActiveWidget().click(btn_x3,btn_y);
}

boxee.onPause = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}

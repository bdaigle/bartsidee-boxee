boxee.multiDoc = true;
boxee.enableLog(true);
boxee.autoChoosePlayer=false;
boxee.renderBrowser=true;
boxee.setCanSetVolume(false);

var btn_x = 16;
var btn_y = 374;
var bbc_x1 = 7;
var bbc_x2 = 633;
var bbc_y = 390;
var has_hd = true;
var has_active = false;
var play_started = false;
var hd_notified = false;
var hd_check = "(function(){if(document.getElementsByClassName('hd-available').length>0){return 1}})()";

var player_ref = 'iplayer.models.Emp.getInstance()';

bbc = {

   isInitialised: function()
   {
      if (this.execute('isInitialised()') == 'true') return true;
      else return false;
   },

   play: function()
   {
      if (!this.isPlaying())
      {
         width = boxee.getActiveWidget().width;
         height = boxee.getActiveWidget().height;
         this.click(width/2, height/2);
         //this.execute('play()');
      }
   },

   isPlaying: function()
   {
      if (this.execute('_isPlaying') == 'true') return true;
      else return false;
   },

   execute: function(str)
   {
      return browser.execute(player_ref+'.'+str);
   },

   isActive: function()
   {
      if (typeof boxee.getActiveWidget() == 'object') return true;
      else return false;
   },

   click: function(x, y)
   {
      boxee.getActiveWidget().click(x, y);
      boxee.getActiveWidget().mouseMove( - 1, -1);
   }

}

boxee.onInit = function() {
   browser.setCookie(".bbc.co.uk", "BBCPGstat", "0%3A-");
}

boxee.onDocumentLoaded = function()
{
   _findplayer = setInterval(function(){
      boxee.getWidgets().forEach(function(widget) {
         id = widget.getAttribute('id');
         src = widget.getAttribute('src');
         if (id.indexOf('bbc_') != -1 && src.indexOf('www.bbc.co.uk/emp') != -1) {
            boxee.renderBrowser = false;
            widget.setCrop(0, 0, 0, 35);
            boxee.notifyConfigChange(widget.width, widget.height-35);
            browser.invalidate();
            widget.setActive();
            startPlayer();
            clearInterval(_findplayer);
         }
      });
   },1000);
}

function startPlayer() {
   _waitForPlayer = setInterval(function() {
      if (bbc.isPlaying())
      {
         boxee.setCanPause(true);
         boxee.setCanSkip(true);
         clearInterval(_waitForPlayer);
      }
      if (bbc.isActive() && bbc.isInitialised())
         bbc.play()
   },4000);
}

boxee.onActivateExt = function(mode) {
   has_active = false;
   play_started = false;
   boxee.setCanSkip(false);
   boxee.setCanPause(false);
   //boxee.getActiveWidget().setActive(false);
   if (has_hd) {
      has_hd = false;
      boxee.showNotification("Switching to HD...", ".", 5);
      browser.execute('iplayer.episode.gotoHDUrl()');
   } else {
      has_hd = false;
      boxee.showNotification("Switching to default stream...", ".", 5);
      browser.navigate(boxee.getParam('src'));
   }
}

function bbcHdAvailable() {
   if (browser.execute(hd_check) == '1') {
      boxee.enableExt(0, "Toggle HD", "http://dir.boxee.tv/apps/common/icons/icons_hd.png");
      if (!hd_notified) {
         hd_notified = true;
         boxee.showNotification("This video is available in HD.", ".", 10);
      }
   }
}

function bbcGetLocation() {
   for (x = bbc_x1; x < bbc_x2; x += 1) {
      p = boxee.getActiveWidget().getPixelData(x, bbc_y);
      if ((p.r == 51) && (p.g == 51) && (p.b == 51)) return x;
   }
   return bbc_x2;
}

function bbcGetSeek(seek) {
   var x = bbcGetLocation() + (seek);
   if (seek > 0 && x > bbc_x2) x = bbc_x2;
   else if (seek < 0 && x < bbc_x1) x = bbc_x1;
   return x;
}

boxee.onPlay = function()
{
   //bbc.play();
   bbc.click(btn_x, btn_y);
}

boxee.onPause = function()
{
   bbc.click(btn_x, btn_y);
}

boxee.onSkip = function() {
   boxee.getActiveWidget().click(bbcGetSeek(30), bbc_y);
}

boxee.onBigSkip = function() {
   boxee.getActiveWidget().click(bbcGetSeek(60), bbc_y);
}

boxee.onBack = function() {
   boxee.getActiveWidget().click(bbcGetSeek( - 30), bbc_y);
}

boxee.onBigBack = function() {
   boxee.getActiveWidget().click(bbcGetSeek( - 60), bbc_y);
}
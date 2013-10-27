boxee.enableLog(true);
boxee.autoChoosePlayer = false;
boxee.renderBrowser = true;
boxee.browserWidth = 1280;
boxee.browserHeight = 720;

var playbackStarted = false;
var duration = 0;
var update;
var timer;

if (boxee.getVersion() < 7) {		
	update = function() {
		duration = parseInt(browser.execute('videoplayer.duration();'), 10);
		ctime = parseInt(browser.execute('videoplayer.currentTime();'), 10);
		progress = Math.round((ctime / duration)*100);
		boxee.setDuration(duration);
		boxee.notifyCurrentTime(ctime);
		boxee.notifyCurrentProgress(progress);
	};
} else {
	boxee.apiMinVersion = 7.0;
	boxee.setMode(boxee.LOCKED_PLAYER_MODE);
	boxee.showOSDOnStartup = false;
	boxee.onUpdateState = function() {
	   playerState.canPause = playerState.canSeek = playerState.canSeekTo = true;
	   playerState.time = parseInt(browser.execute('videoplayer.duration();'), 10);
	   playerState.duration = parseInt(browser.execute('videoplayer.currentTime();'), 10);
	};
	
	update = function(){
	   playerState.canPause = playerState.canSeek = playerState.canSeekTo = true;
	   playerState.time = parseInt(browser.execute('videoplayer.duration();'), 10);
	   playerState.duration = parseInt(browser.execute('videoplayer.currentTime();'), 10);
	};
}

waitforflow = setInterval(function() {
	 if (!playbackStarted) {
		boxee.log('Waiting for player to start...');
		if (browser.execute('started();') === 'true') {
			playbackStarted = true;
			boxee.log('Playback started');
			boxee.setCanPause(true);
            boxee.setCanSkip(true);
            boxee.setCanSetVolume(true);
			timer = setInterval(function() { update(); }, 500);
		}
		
	 }
	if (playbackStarted) {
			 if (browser.execute('completed();') === 'true') {
				setTimeout(function(){
					clearInterval(waitforflow);
					clearInterval(timer);
					boxee.notifyPlaybackEnded();
				},2000);
			 }
	}
}, 1000);

boxee.onPause = function() {
   browser.execute('videoplayer.pause();');
};

boxee.onPlay = function() {
   browser.execute('videoplayer.play();');
};

boxee.onSkip = function() {
	var seek = 10;
	browser.execute('videoplayer.onCurrentTimeUpdate(videoplayer.currentTime()+'+seek+');');
};

boxee.onBigSkip = function() {
	var seek = 60;
	browser.execute('videoplayer.onCurrentTimeUpdate(videoplayer.currentTime()+'+seek+');');
};

boxee.onBack = function() {
	var seek = 10;
	browser.execute('videoplayer.onCurrentTimeUpdate(videoplayer.currentTime()+'+seek+');');
};

boxee.onBigBack = function() {
	var seek = 60;
	browser.execute('videoplayer.onCurrentTimeUpdate(videoplayer.currentTime()+'+seek+');');
};

boxee.onSeekTo = function(milli) {
   browser.execute('videoplayer.onCurrentTimeUpdate(' + milli/1000 + ');');
};
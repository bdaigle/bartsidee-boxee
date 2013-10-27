boxee.enableLog(true);
boxee.autoChoosePlayer = true;
boxee.renderBrowser = false;

var playbackStarted = false;
var duration = 0;
var update;
var timer;

if (boxee.getVersion() < 7) {		
	update = function() {
		duration = parseInt(browser.execute('$f().getClip().fullDuration;'), 10);
		ctime = parseInt(browser.execute('$f().getTime()'), 10);
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
	   playerState.time = parseInt(browser.execute('$f().getTime();'), 10);
	   playerState.duration = parseInt(browser.execute('$f().getClip().fullDuration;'), 10);
	};
	
	update = function(){
	   playerState.canPause = playerState.canSeek = playerState.canSeekTo = true;
	   playerState.time = parseInt(browser.execute('$f().getTime();'), 10);
	   playerState.duration = parseInt(browser.execute('$f().getClip().fullDuration;'), 10);
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
   browser.execute('$f().pause();');
};

boxee.onPlay = function() {
   browser.execute('$f().play();');
};

boxee.onSkip = function() {
	var seek = 10;
	browser.execute('$f().seek($f().getTime()+'+seek+');');
};

boxee.onBigSkip = function() {
	var seek = 60;
	browser.execute('$f().seek($f().getTime()+'+seek+');');
};

boxee.onBack = function() {
	var seek = 10;
	browser.execute('$f().seek($f().getTime()-'+seek+');');
};

boxee.onBigBack = function() {
	var seek = 60;
	browser.execute('$f().seek($f().getTime()-'+seek+');');
};

boxee.onSeekTo = function(milli) {
   browser.execute('$f().seek(' + milli/1000 + ');');
};
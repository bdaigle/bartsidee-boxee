import mc
import os, sys
__cwd__ = os.getcwd().replace(";","")
sys.path.append(os.path.join(__cwd__, 'libs'))

import tracker
myTracker = tracker.Tracker('UA-19866820-2')

if ( __name__ == "__main__" ):
    mc.ActivateWindow(14000)
    myTracker.trackView('home')

    import app
    config = mc.GetApp().GetLocalConfig()
    window = mc.GetWindow(14000)

    control = window.GetControl(30)
    control.SetVisible(True)
    control = window.GetControl(31)
    control.SetVisible(True)

    if config.GetValue("play") != 'True':
        app.ShowNet()
        window.GetControl(52).SetVisible(False)
        window.GetControl(51).SetFocus()

    config.SetValue("play", 'False')



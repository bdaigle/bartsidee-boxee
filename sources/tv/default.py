import mc
import os
import sys
import re

VERSION = "2.03"
CWD     = os.getcwd().replace(";","")
APPID   = mc.GetApp().GetId()
sys.path.append(os.path.join(CWD, 'libs'))
sys.path.append(os.path.join(CWD, 'external'))

import tracker
GA = tracker.GA('UA-19866820-2')

if ( __name__ == "__main__" ):
    mc.ActivateWindow(14444)
    GA.setPageView('home')

    window = mc.GetWindow(14444)
    config = mc.GetApp().GetLocalConfig()
    mc.GetWindow(14446).ClearStateStack(False)

    import main
    main_obj = main.BARTSIDEE_MAIN()

    window.GetToggleButton(10101).SetSelected(True)

    if window.GetControl(1200).IsVisible():
        window.GetControl(1200).SetVisible(True)
        window.GetControl(1300).SetVisible(False)
        window.GetControl(1400).SetVisible(False)


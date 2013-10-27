import mc
import os
import sys
import re

VERSION = "0.1 beta"
CWD     = os.getcwd().replace(";","")
APPID   = mc.GetApp().GetId()
try: 
    IDENTIFIER = "boxee_" + mc.GetDeviceId() + mc.GetInfoString('System.ProfileName').replace(' ', '')
except:
    IDENTIFIER = "boxee_" + mc.GetInfoString('System.ProfileName').replace(' ', '')

sys.path.append(os.path.join(CWD, 'libs'))

import tracker
GA = tracker.GA('UA-19866820-2')

if ( __name__ == "__main__" ):
    mc.ActivateWindow(14000)
    GA.setPageView('home')

    import app
    main_obj = app.init()
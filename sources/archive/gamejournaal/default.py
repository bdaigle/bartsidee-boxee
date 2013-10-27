import mc

if ( __name__ == "__main__" ):
    mc.ActivateWindow(14000)

	from libs import app

	params = mc.GetApp().GetLaunchedWindowParameters()
	try:
		if params['noreload'] != "1":
			app.init()
	except:
		app.init()


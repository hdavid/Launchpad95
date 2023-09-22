
class Settings():
	# Add Stop buttons at the bottom of the Session. Experimental
	#SESSION__STOP_BUTTONS = True
	SESSION__STOP_BUTTONS = False

	# Link sessions between multiple launchpad95. Experimental
	#SESSION__LINK = True
	SESSION__LINK = False

	# Link stepseq to follow session. Experimental
	#STEPSEQ__LINK_WITH_SESSION = True
	STEPSEQ__LINK_WITH_SESSION = False

	# Should the step sequencer scroll automatically to the currently playing page
	STEP_SEQ_AUTO_SCROLL = False

	# configure what user modes buttons do.
	# the 3 first value configure the 3 sub modes of button user mode 1, 
	# and following ones are for user mode 2 button
	USER_MODES_1 = [
			"instrument" 
			,"device" 
			#,"user 1"
	]
	USER_MODES_2 = [
			 "drum stepseq"
			 ,"melodic stepseq" 
			 #,"user 2"
	]



	#device control stepless fader velocity thresholds
	#if velocity is above threshold, the parameter will be changed instantly
	VELOCITY_THRESHOLD_MAX = 100
	VELOCITY_THRESHOLD_MIN = 40
	#used for the gradient of the parameter change
	#the higher the value, the slower the parameter change
	VELOCITY_FACTOR = (127**2) * (127/2)
	USE_CUSTOM_DEVICE_CONTROL_COLORS = False


	#Logging feature for debugging (creates C:/Users/{USERNAME}/Documents/Ableton/User Library/Remote Scripts/log.txt)
	LOGGING = False

	# Map buttons to levels in volume slider. Exactly 7 values must be provided.
	# The lowest button is always set to -inf. Lowest supported value is -69 dB.
	# So far the values are not exact: -24 dB below equals -23.7 dB in Ableton.
	VOLUME_LEVELS = (6, 0, -6, -12, -18, -24, -42)

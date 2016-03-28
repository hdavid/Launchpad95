# Add Stop buttons at the bottom of the Session. Experimental
#SESSION__STOP_BUTTONS = True
SESSION__STOP_BUTTONS = False

# Link sessions between multiple launchpad95. Experimental
#SESSION__LINK = True
SESSION__LINK = False

# Link stepseq to follow session. Experimental
#STEPSEQ__LINK_WITH_SESSION = True
STEPSEQ__LINK_WITH_SESSION = False

# configure what user modes buttons do.
# the 3 first value configure the 3 sub modes of button user mode 1, 
# and following ones are for user mode 2 button
USER_MODES = [
		"instrument", "device", "user 1",
		 "drum stepseq", "melodic stepseq", "user 2"
]

# allow sep seq and instrument modes to save their scale settings.
# as live does not offer any api we are stuck with using the track or clip name...
# possible values : "clip" to save in clip, set, None,  (case matter)
# Experimental
#STEPSEQ__SAVE_SCALE = "clip"
#INSTRUMENT__SAVE_SCALE = "clip"
STEPSEQ__SAVE_SCALE = None
INSTRUMENT__SAVE_SCALE = None





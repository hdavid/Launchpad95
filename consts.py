
# LaunchPad Colours

LED_OFF = 4

RED_FULL = 7
RED_HALF = 6
RED_THIRD = 5
RED_BLINK = 11

GREEN_FULL = 52
GREEN_HALF = 36
GREEN_THIRD = 20
GREEN_BLINK = 56

AMBER_FULL = ((RED_FULL + GREEN_FULL) - 4)
AMBER_HALF = ((RED_HALF + GREEN_HALF) - 4)
AMBER_THIRD = ((RED_THIRD + GREEN_THIRD) - 4)
AMBER_BLINK = ((AMBER_FULL - 4) + 8)

def index_of(list, elt):
	for i in range(0,len(list)):
		if (list[i] == elt):
			return i
	return(-1)
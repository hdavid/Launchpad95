# flake8: noqa

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

# Scales
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CIRCLE_OF_FIFTHS = [7 * k % 12 for k in range(12)]
# KEY_CENTERS = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]

MUSICAL_MODES = [

	'Major',			[0, 2, 4, 5, 7, 9, 11],
	'Minor',			[0, 2, 3, 5, 7, 8, 10],
	'Dorian',			[0, 2, 3, 5, 7, 9, 10],
	'Mixolydian',		[0, 2, 4, 5, 7, 9, 10],
	'Lydian',			[0, 2, 4, 6, 7, 9, 11],
	'Phrygian',			[0, 1, 3, 5, 7, 8, 10],
	'Locrian',			[0, 1, 3, 5, 6, 8, 10],
	'Diminished',		[0, 1, 3, 4, 6, 7, 9, 10],

	'Whole-half',		[0, 2, 3, 5, 6, 8, 9, 11],
	'Whole Tone',		[0, 2, 4, 6, 8, 10],
	'Minor Blues',		[0, 3, 5, 6, 7, 10],
	'Minor Pentatonic', [0, 3, 5, 7, 10],
	'Major Pentatonic', [0, 2, 4, 7, 9],
	'Harmonic Minor',	[0, 2, 3, 5, 7, 8, 11],
	'Melodic Minor',	[0, 2, 3, 5, 7, 9, 11],
	'Super Locrian',	[0, 1, 3, 4, 6, 8, 10],

	'Bhairav',			[0, 1, 4, 5, 7, 8, 11],
	'Hungarian Minor',	[0, 2, 3, 6, 7, 8, 11],
	'Minor Gypsy',		[0, 1, 4, 5, 7, 8, 10],
	'Hirojoshi',		[0, 2, 3, 7, 8],
	'In-Sen',			[0, 1, 5, 7, 10],
	'Iwato',			[0, 1, 5, 6, 10],
	'Kumoi',			[0, 2, 3, 7, 9],
	'Pelog',			[0, 1, 3, 4, 7, 8],

	'Spanish',			[0, 1, 3, 4, 5, 6, 8, 10],
	'IonEol',			[0, 2, 3, 4, 5, 7, 8, 9, 10, 11]  # from aschneiderg@unal.edu.co
]


def index_of(list, elt):
	for i in range(0, len(list)):
		if (list[i] == elt):
			return i
	return(-1)

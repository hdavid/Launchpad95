from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from Launchpad import Launchpad

def create_instance(c_instance):
	""" Creates and returns the Launchpad script """
	return Launchpad(c_instance)

def get_capabilities():
	return {
		CONTROLLER_ID_KEY: controller_id(
			vendor_id = 4661, 
			product_ids = [14,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120], 
			model_name = 
			[
				'Launchpad', 
				'Launchpad S',
				'Launchpad Mini',  
				'Launchpad MK2', 
				'Launchpad MK2 2',
				'Launchpad MK2 3',
				'Launchpad MK2 4',
				'Launchpad MK2 5',
				'Launchpad MK2 6',
				'Launchpad MK2 7',
				'Launchpad MK2 8',
				'Launchpad MK2 9',
				'Launchpad MK2 10',
				'Launchpad MK2 11',
				'Launchpad MK2 12',
				'Launchpad MK2 13',
				'Launchpad MK2 14',
				'Launchpad MK2 15',
				'Launchpad MK2 16'
			]
		),
		PORTS_KEY: 
			[
				inport(props = [NOTES_CC, SCRIPT, REMOTE]), 
				outport(props = [NOTES_CC, SCRIPT, SYNC, REMOTE])
			]
	}

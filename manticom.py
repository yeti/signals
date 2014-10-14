# manticom
# Copyright (C) 2014, Collin Schupman at Yeti LLC

# Assumes JSON is in format : TODO->Write format

import manticom_ios

if __name__ == "__main__":

	print 'Hello, greetings and welcome!'
	print 'Today is a new beginning.\n'
	print 'Enter "E" at any time to exit\n'


	while True:
		print 'Please enter your JSON file!'
		json = raw_input('--> ')
		if json.endswith('.json') or json == 'E':
			break
		else:
			print 'Unrecognized JSON file, please try again!\n'

	if json != 'E':

		while True:
			print 'Please enter which stack you would like to generate code for (iOS) or "E" to exit the program'
			stack = raw_input('--> ')
			if stack == 'iOS' or stack == 'E':
				break
			else:
				print 'Unrecognized selection, please try again!\n'

		if stack == 'E':
			print 'Goodbye!'
		elif stack == 'iOS':
			manticom_ios.main(json)
	else:
		print "Goodbye!"
# manticom_ios
# Copyright (C) 2014, Collin Schupman at Yeti LLC

# This is a script to handle all the file generations for iOS stack

# Assumes JSON is in format : TODO->Write format
import json
from manticom_ios_coredata import write_xml_to_file
from manticom_ios_models import write_models_to_file


def main(incoming_json):
    print "iOS Script starting"
    print "Opening JSON"
    with open(incoming_json, "r") as f:
        objects = json.loads(f.read())["objects"]

        print "Writing out models......"

        write_models_to_file(objects)

        xml = None
        while True:
            print "Please enter CoreData contents file or 'skip' to skip this step\n"
            xml = raw_input('--> ')
            if xml == 'skip' or xml.endswith('contents'):
                break
            else:
                print 'Unrecognized contents file, please try again!\n'

        if xml.endswith('contents'):
            write_xml_to_file(xml, objects)

        print "Done"
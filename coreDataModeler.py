# Manticore
# Copyright (C) 2013, Collin Schupman at Yeti LLC

# This is a script to take as input a .json file and output
# an .xcdatamodeld file to represent the objects and their relations.

# input: python coreDataModeler.py filename.json

# the folder structure for the dataModeler looks something like this
# whatever.xcdatamodeld
#    whatever.xcdatamodel
#       contents (XML)
# ^ this is where we want to make our changes, should provide link her TODO 

# TODO:
#
# update contents
# add in xml metadata
# made correct dynamic cells

# Thinking: Work flow ->
# Create initial file using xcode
# Extra information and provide all that stuff to the program

import sys
import json
import StringIO
from lxml import etree
from xml.dom import minidom
import shutil


DATA_TYPES = {
    "date"       : "Date",
    "datetime"   : "Date",
    "int"        : "Integer 32",
    "integer"    : "Integer 32",
    "integer16"  : "Integer 16",
    "integer32"  : "Integer 32",
    "integer64"  : "Integer 64",
    "decimal"    : "Decimal",
    "double"     : "Double",
    "real"       : "Double",
    "float"      : "Float",
    "string"     : "String",
    "text"       : "String",
    "boolean"    : "Boolean",
    "array"      : "Transformable"
}

# inverseName?
# inverseEntity?
# howToChooseNames?
# TOO MANY?
def add_relationship(entity, name, destinationEntity):
    relationship = etree.SubElement(entity, "relationship", name = name)
    relationship.set("optional", "YES")
    relationship.set("deletionRule", "Nullify")
    relationship.set("destinationEntity", destinationEntity)
    relationship.set("syncable", "YES")
    return relationship
    

def add_attribute(entity, name, att_type):
    attribute = etree.SubElement(entity, "attribute", name = name)
    attribute.set("optional", "YES")
    attribute.set("attributeType", att_type)
    attribute.set("syncable", "YES")

def get_model(xml):
    xmldoc = minidom.parse(xml)
    itemlist = xmldoc.getElementsByTagName('model') 
    model = etree.Element("model")
    for att in itemlist[0].attributes.keys():
        model.set(att, itemlist[0].attributes[att].value)
    return model

def parse_objects(schema, model):
    for obj in schema:
        obj_name = obj.keys()[0]
        entity = etree.SubElement(model, "entity", name=obj_name[1:])
        obj_fields = obj[obj_name]

        for key, value in obj_fields.iteritems():
            values = value.split(",")

            if "optionals" in values:
                values.remove("optionals")
            if "primarykey" in values:
                values.remove("primarykey")

            if values[0] == "array":
                if "$" not in values[1]:
                    add_attribute(entity, key, DATA_TYPES[values[1]])
                else:
                    relationship = add_relationship(entity,"many"+value[1][1:], values[1][1:])
                    relationship.set("ordered", "YES")
                    relationship.set("toMany", "YES")
            else:
                if "$" in values[0]:
                    relationship = add_relationship(entity, "one"+values[0][1:], values[0][1:])
                    relationship.set("minCount", "1")
                    relationship.set("maxCount", "1")
                else:
                    add_attribute(entity, key, DATA_TYPES[values[0]])

    # TODO: come up with better way to compute height/position
    elements = etree.SubElement(model, "elements")
    for obj in schema:
        element = etree.SubElement(elements, "element", name = obj.keys()[0][1:])
        element.set("positionX", "0")
        element.set("positionY", "0")
        element.set("width", "128")
        element.set("height", "600")
    return model

def main_script(incoming_json, xml):
    f = open(incoming_json, "r")
    schema = json.loads(f.read())
    f.close()

    # should do a check here to ensure good json format
    model = get_model(xml)
    parse_objects(schema["objects"], model)
    #tree = etree.ElementTree(model)
    print etree.tostring(model, pretty_print = True)
    #tree.write("new.xml", pretty_print=True)

# check user input
if len(sys.argv) != 3:
    print "Error, usage: " + sys.argv[0] + " <file.json> <file.xml>" 
else:
    main_script(sys.argv[1], sys.argv[2])

# manticom_ios_coredata
# Copyright (C) 2014, Collin Schupman at Yeti LLC

# This is a script to update an existing CoreDataModel with a given JSON file

# Assumes JSON is in format : TODO->Write format

# Please pass in contents file from your xcode project, located here:
# project_name.xcdatamodeld
#    project_name.xcdatamodel
#       contents (XML)
# this script will make appropiate changes and update the file

# TODO:
# O2O case
# correctly resize elements, dynamically
import os
from lxml import etree
from xml.dom import minidom
import json

from manticom_ios_datamodels import create_mappings

# Conversions for use in CoreData
# TODO: images and videos on request objects don't even need to be saved?
# or possibly we shouldn't even be generating core data objects for requests?
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
    "array"      : "Transformable",
    "image"      : "String",
    "video"      : "String"
}

# Database Relationships
RELATIONSHIPS = {"O2O", "M2M", "O2M", "M2O"}


# A little logic to to make plural words more readable this won't cover everything,
# there's a few python libraries out there you could use: https://pypi.python.org/pypi/inflect
def get_word_plural(word):
    if word.endswith("y"):
        return word[:-1] + 'ies'
    elif word.endswith("ing"):
        return word
    else:
        return word + 's'


# Adds an elements branch and element leaf for each object in the JSON file
# TODO: come up with better way to compute height/position
def add_elements(model, objects):
    elements = etree.SubElement(model, "elements")
    for obj in objects:
        obj_name = get_proper_object_name(obj.keys()[0])
        element = etree.SubElement(elements, "element", name=obj_name)
        element.set("positionX", "0")
        element.set("positionY", "0")
        element.set("width", "128")
        element.set("height", "600")


# Sets up and returns a relationship between these two entities with all basic attributed filled in
def get_basic_relationship(entity, relationship_name, destination_entity, inverse_name, inverse_entity):
    relationship = etree.SubElement(entity, "relationship", name=relationship_name)
    relationship.set("optional", "YES")
    relationship.set("deletionRule", "Nullify")
    relationship.set("destinationEntity", destination_entity)
    relationship.set("syncable", "YES")
    relationship.set("inverseName", inverse_name)
    relationship.set("inverseEntity", inverse_entity)
    return relationship


# It seems redundant that we pass around the entities as well as their names
# then also get their names again from the entity in the following functions.

# Creates a one relationship between these two entities
def add_one_relationship(entity_one, entity_two, entity_one_name, entity_two_name):
    relationship = get_basic_relationship(entity_one,
                                          entity_two_name,
                                          entity_two.get('name'),
                                          entity_one_name,
                                          entity_two.get('name'))
    relationship.set("minCount", "1")
    relationship.set("maxCount", "1")


# Creates a many relationship between these two entities
def add_many_relationship(entity_one, entity_two, entity_one_name, entity_two_name):
    relationship = get_basic_relationship(entity_one,
                                          entity_two_name,
                                          entity_two.get('name'),
                                          entity_one_name,
                                          entity_two.get('name'))
    relationship.set("ordered", "YES")
    relationship.set("toMany", "YES")


# Doing stuff
def add_M2O_relationship(many_entity, one_entity, many_entities_relationship_name, one_entities_relationship_name):
    add_many_relationship(one_entity, many_entity, one_entities_relationship_name, many_entities_relationship_name)
    add_one_relationship(many_entity, one_entity, many_entities_relationship_name, one_entities_relationship_name)


# Adds O2M relationships between these two entities
def add_M2M_relationships(entity_one, entity_two, entity_one_relationship_name, entity_two_relationship_name):
    add_many_relationship(entity_one, entity_two, entity_two_relationship_name, entity_one_relationship_name)
    add_many_relationship(entity_two, entity_one, entity_one_relationship_name, entity_two_relationship_name)


# Adds O2M relationships between these two entities
def add_O2M_relationships(many_entity, one_entity, many_entities_relationship_name, one_entities_relationship_name):  
    add_many_relationship(many_entity, one_entity, many_entities_relationship_name, one_entities_relationship_name)
    add_one_relationship(one_entity, many_entity, one_entities_relationship_name, many_entities_relationship_name)


def get_proper_object_name(obj):
    return obj[1].upper() + obj[2:]


# Checks to see if this key and related model are duplicated in this set of fields
def conflicting_entity_name(fields, obj_key, obj_name, relationship_type):
    for key, value in fields.iteritems():
        if obj_key != key and obj_name in value and relationship_type in value:
            return True
    return False


# Adds relationships and inverse relationships for each required entity
# Currently only supports M2M, O2M. TODO: dd in others
def add_relationships(model, objects):
    for obj in objects:
        obj_name = obj.keys()[0]
        obj_fields = obj[obj_name]

        for key, value in obj_fields.iteritems():
            values = value.split(",")
            if "optional" in values:
                values.remove("optional")
            if "primarykey" in values:
                values.remove("primarykey")

            # TODO: This depends on the relationship mapping being the 1st value and the related object 2nd
            relationship_mapping = values[0]
            if relationship_mapping in ["O2M", "M2M", "M2O"]:
                related_obj_name = values[1]

                first_entity = second_entity = None
                for entity in model.iter("entity"):
                    if entity.get('name') == get_proper_object_name(obj_name):
                        first_entity = entity
                    elif entity.get('name') == get_proper_object_name(related_obj_name):
                        second_entity = entity

                first_entity_name = first_entity.get('name').lower().replace("response", "")
                if relationship_mapping == "O2M":
                    add_O2M_relationships(first_entity, second_entity, first_entity_name, key)
                elif relationship_mapping == "M2M":
                    add_M2M_relationships(first_entity, second_entity, key, get_word_plural(first_entity_name))
                elif relationship_mapping == "M2O":
                    """
                    If we have a entity which maps to another entity more than once, we can't use that entity's name
                    instead, let's use the key of the field.

                    For example, if we had a user who has followers and is also following other users, our user entity
                    would have two fields called "follow". This instead calls them followers and following.
                    """
                    conflicting = conflicting_entity_name(obj_fields, key, related_obj_name, relationship_mapping)
                    entity_label = key if conflicting else first_entity_name
                    add_M2O_relationship(first_entity, second_entity, get_word_plural(entity_label), key)

    
# Adds attributes to the given entity for its name and type
def add_entity_attribute(entity, name, att_type, optional):
    if name == "id":
        name = "theID"
    elif name == "description":
        name = "theDescription"
    elif '_' in name:
        words = name.split('_')
        name = words[0]
        for x in range(1, len(words)):
            next_word = words[x]
            next_word = next_word.capitalize()
            name += next_word

    attribute = etree.SubElement(entity, "attribute", name=name)
    attribute.set("optional", "YES" if optional else "NO")
    attribute.set("attributeType", att_type)
    attribute.set("syncable", "YES")


# Adds entities for each object in the JSON tree
def add_entities(model, objects):
    for obj in objects:
        obj_name = obj.keys()[0]
        if "Parameters" not in obj_name:
            entity = etree.SubElement(model, "entity", name=obj_name[1].upper() + obj_name[2:])
            obj_fields = obj[obj_name]
            for key, value in obj_fields.iteritems():
                values = value.split(",")
                if "primarykey" in values:
                    values.remove("primarykey")

                if values[0] not in RELATIONSHIPS and values[0]:
                    add_entity_attribute(entity, key, DATA_TYPES[values[0]], "optional" in values)


# Parses the given XML's model element and creates our initial root 
def get_model(xml):
    xmldoc = minidom.parse(xml)
    itemlist = xmldoc.getElementsByTagName('model') 
    new_model = etree.Element("model")
    current_xml_model = itemlist[0]
    for att in current_xml_model.attributes.keys():
        new_model.set(att, current_xml_model.attributes[att].value)
    return new_model


def write_xml_to_file(xml, objects):
    print "Reading XML"
    model = get_model(xml)

    print "Adding entities"
    add_entities(model, objects)

    print "Adding relationships"
    add_relationships(model, objects)

    print "Adding elements"
    add_elements(model, objects)
    
    # print tree (FOR DEBUGGING)
    # print "Printing XML"
    # print etree.tostring(model, pretty_print = True)

    # write tree
    print "Writing XML"
    tree = etree.ElementTree(model)
    tree.write(xml, pretty_print=True)
    #tree.write("new.xml", pretty_print=True)


if __name__ == "__main__":
    print "Loading XML and JSON"
    incoming_json = os.path.expanduser("~/projects/viddit/viddit/manticom-schema-1.0.json")
    xml_path = "~/ios_projects/viddit-ios/Viddit/Common/Models/VidditModel.xcdatamodeld/VidditModel.xcdatamodel/contents"
    # incoming_json = os.path.expanduser("~/projects/basicspace/api-schema-1.0.json")
    # xml_path = "~/ios_projects/basicspace-ios/BasicSpace/Common/BasicSpace.xcdatamodeld/BasicSpace.xcdatamodel/contents"
    xml = os.path.expanduser(xml_path)
    with open(incoming_json, "r") as f:
        print "Reading SML"
        read_json = json.loads(f.read())
        objects = read_json["objects"]
        urls = read_json["urls"] 
        print "Writing XML"
        # write_xml_to_file(xml, objects)

        print "Writing URLS"
        create_mappings(urls, objects)

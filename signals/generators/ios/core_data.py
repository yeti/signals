"""
Creates an Xcode Core Data file.
"""
import os
from xml.dom import minidom
from lxml import etree
from signals.parser.fields import Relationship, Field
from signals.generators.ios.conversion import get_proper_name

DATA_TYPES = {
    Field.DATE: "Date",
    Field.DATETIME: "Date",
    Field.INTEGER: "Integer 32",
    Field.DECIMAL: "Decimal",
    Field.FLOAT: "Float",
    Field.STRING: "String",
    Field.TEXT: "String",
    Field.BOOLEAN: "Boolean",
    Field.IMAGE: "String",
    Field.VIDEO: "String"
}


def get_data_type(field):
    if field.array:
        return "Transformable"
    else:
        return DATA_TYPES[field.field_type]


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
def add_elements(model, objects):
    elements = etree.SubElement(model, "elements")
    for object_name, data_object in objects.iteritems():
        element = etree.SubElement(elements, "element", name=get_proper_object_name(object_name))
        # TODO: come up with better way to compute height/position
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


def add_O2O_relationships(entity_one, entity_two, entity_one_relationship_name, entity_two_relationship_name):
    add_one_relationship(entity_one, entity_two, entity_two_relationship_name, entity_one_relationship_name)
    add_one_relationship(entity_two, entity_one, entity_one_relationship_name, entity_two_relationship_name)


def get_proper_object_name(obj):
    return obj[1].upper() + obj[2:]


# Checks to see if this key and related model are duplicated in this set of fields
def conflicting_entity_name(relationships, current_relationship):
    for relationship in relationships:
        is_equivalent = current_relationship.name != relationship.name
        is_equivalent = is_equivalent and current_relationship.related_object == relationship.related_object
        is_equivalent = is_equivalent and current_relationship.relationship_type == relationship.relationship_type
        return is_equivalent


# Adds relationships and inverse relationships for each required entity
# Currently only supports M2M, O2M. TODO: dd in others
def add_relationships(model, objects):
    for object_name, data_object in objects.iteritems():
        for relationship in data_object.relationships:
            first_entity = second_entity = None
            for entity in model.iter("entity"):
                if entity.get('name') == get_proper_object_name(object_name):
                    first_entity = entity
                elif entity.get('name') == get_proper_object_name(relationship.related_object.name):
                    second_entity = entity

            first_entity_name = first_entity.get('name').lower().replace("response", "")
            if relationship.relationship_type == Relationship.ONE_TO_MANY:
                add_O2M_relationships(first_entity, second_entity, first_entity_name, relationship.name)
            elif relationship.relationship_type == Relationship.MANY_TO_MANY:
                add_M2M_relationships(first_entity, second_entity, relationship.name,
                                      get_word_plural(first_entity_name))
            elif relationship.relationship_type == Relationship.ONE_TO_ONE:
                add_O2O_relationships(first_entity, second_entity, get_proper_name(relationship.name),
                                      first_entity_name)
            elif relationship.relationship_type == Relationship.MANY_TO_ONE:
                """
                If we have a entity which maps to another entity more than once, we can't use that entity's name
                instead, let's use the key of the field.

                For example, if we had a user who has followers and is also following other users, our user entity
                would have two fields called "follow". This instead calls them followers and following.
                """
                conflicting = conflicting_entity_name(data_object.relationships, relationship)
                entity_label = relationship.name if conflicting else first_entity_name
                add_M2O_relationship(first_entity, second_entity, get_word_plural(entity_label),
                                     get_proper_name(relationship.name))


# Adds attributes to the given entity for its name and type
def add_entity_attribute(entity, name, core_data_type, optional):
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
    attribute.set("attributeType", core_data_type)
    attribute.set("syncable", "YES")


# Adds entities for each object in the JSON tree
def add_entities(model, objects):
    for object_name, data_object in sorted(objects.iteritems()):
        # TODO: I don't think this is documented or used heavily as a standard
        if "Parameters" not in object_name:
            proper_object_name = get_proper_object_name(object_name)
            entity = etree.SubElement(model, "entity", name=proper_object_name)
            entity.set("representedClassName", proper_object_name)

            for field in data_object.fields:
                add_entity_attribute(entity, field.name, get_data_type(field), field.optional)


# Parses the given XML's model element and creates our initial root
def get_model(core_data_path):
    xml_dom = minidom.parse(core_data_path)
    item_list = xml_dom.getElementsByTagName('model')
    new_model = etree.Element("model")
    current_xml_model = item_list[0]
    for att in current_xml_model.attributes.keys():
        new_model.set(att, current_xml_model.attributes[att].value)
    return new_model


# parses the hidden .xccurrentversion for the name of the current version
# this information is stored inside its first and only <string> xml tag
def get_current_version(xcdatamodeld_path):
    xccurrentversion_path = '{}/.xccurrentversion'.format(xcdatamodeld_path)

    # .xccurrentversion might not exist if there is only one version
    if os.path.exists(xccurrentversion_path):
        try:
            xml_dom = minidom.parse(xccurrentversion_path)
            current_version_name = xml_dom.getElementsByTagName('string')[0].childNodes[0].data
            return current_version_name
        # Invalid .xccurrentversion format, passes in order to return first version name
        except (IndexError, AttributeError):
            pass

    return [filename for filename in os.listdir(xcdatamodeld_path)
            if filename.endswith('.xcdatamodel')][0]


def get_core_data_from_folder(xcdatamodeld_path):
    current_version_name = get_current_version(xcdatamodeld_path)
    return '{}/{}/contents'.format(xcdatamodeld_path, current_version_name)


def write_xml_to_file(xcdatamodeld_path, objects):
    core_data_path = get_core_data_from_folder(xcdatamodeld_path)

    model = get_model(core_data_path)
    add_entities(model, objects)
    add_relationships(model, objects)
    add_elements(model, objects)

    # write tree
    tree = etree.ElementTree(model)
    tree.write(core_data_path, pretty_print=True)

import json
import sys

__author__ = 'rudy'


class Schema(object):
    def __init__(self, schema_path):
        self.data_objects = {}
        self.schema_path = schema_path

        with open(schema_path, "r") as schema_file:
            read_json = json.loads(schema_file.read())
            self.create_objects(read_json["objects"])
            self.create_apis(read_json["urls"])

    def create_apis(self, api_json):
        pass

    def create_objects(self, object_json):
        for data_object_json in object_json:
            object_name = data_object_json.keys()[0]
            data_object = DataObject(object_name, data_object_json[object_name])
            self.data_objects[data_object.name] = data_object


class DataObject(object):
    def __init__(self, name, json_fields):
        self.fields = []
        self.relationships = []
        self.name = name
        for field_name, field_attributes in json_fields.iteritems():
            self.create_field(field_name, field_attributes)

    def create_field(self, field_name, field_attributes):
        field_attributes = field_attributes.split(",")
        is_relationship = reduce(lambda x, y: x or y in Relationship.TYPES, field_attributes, False)
        if is_relationship:
            self.relationships.append(Relationship(field_name, field_attributes))
        else:
            self.fields.append(Field(field_name, field_attributes))

    def __unicode__(self):
        print u"{}".format(self.name)


class Field(object):
    DATE = "date"
    DATETIME = "datetime"
    INTEGER = "int"
    DECIMAL = "decimal"
    FLOAT = "float"
    STRING = "string"
    TEXT = "text"
    BOOLEAN = "boolean"
    VIDEO = "video"
    IMAGE = "image"
    TYPES = [DATE, DATETIME, INTEGER, DECIMAL, FLOAT, STRING, TEXT, BOOLEAN, VIDEO, IMAGE]
    OPTIONAL = "optional"
    PRIMARY_KEY = "primarykey"
    ARRAY = "array"

    optional = False
    primary_key = False
    array = False
    field_type = None

    def __init__(self, field_name, field_attributes):
        self.name = field_name

        for attribute in field_attributes:
            self.process_attribute(attribute)

        self.validate_field()

    def process_attribute(self, attribute):
        if attribute == self.OPTIONAL:
            self.optional = True
        elif attribute == self.PRIMARY_KEY:
            self.primary_key = True
        elif attribute == self.ARRAY:
            self.array = True
        elif attribute in self.TYPES:
            self.field_type = attribute
        else:
            if attribute[0] == "$":
                print("Found an unexpected attribute: {} on {}. "
                      "Likely it's missing relationship type.".format(attribute, self.name))
            print("Found an unexpected attribute: {} on {}.".format(attribute, self.name))

    def validate_field(self):
        if self.field_type is None:
            print("Didn't find field type for {}, exiting.".format(self.name))
            sys.exit()

    def __unicode__(self):
        print u"{}".format(self.name)


class Relationship(Field):
    ONE_TO_ONE = "O2O"
    MANY_TO_MANY = "M2M"
    ONE_TO_MANY = "O2M"
    MANY_TO_ONE = "M2O"
    TYPES = [ONE_TO_ONE, MANY_TO_MANY, ONE_TO_MANY, MANY_TO_ONE]

    relationship_type = None
    related_object = None

    def process_attribute(self, attribute):
        if attribute in self.TYPES:
            self.relationship_type = attribute
        elif attribute[0] == "$":
            self.related_object = attribute
        else:
            super(Relationship, self).process_attribute(attribute)

    def validate_field(self):
        if self.related_object is None:
            print("Didn't find related object for {}, exiting.".format(self.name))
            sys.exit()


# abstract
class API(object):
    # url
    # doc
    # #meta
    # response
    pass


class GetAPI(API):
    pass


class PostAPI(API):
    pass


class PatchAPI(API):
    pass


class PutAPI(API):
    pass


class DeleteAPI(API):
    pass

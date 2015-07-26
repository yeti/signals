from signals.logging import SignalsError, warn


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
            if attribute.startswith("$"):
                raise SignalsError("Found an unexpected attribute: {} on {}. "
                                   "Likely it's missing relationship type.".format(attribute, self.name))
            warn("Found an unexpected attribute: {} on {}.".format(attribute, self.name))

    def validate_field(self):
        if self.field_type is None:
            raise SignalsError("Didn't find field type for {}, exiting.".format(self.name))


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
        elif attribute.startswith("$"):
            self.related_object = attribute
        else:
            super(Relationship, self).process_attribute(attribute)

    def validate_field(self):
        if self.related_object is None:
            raise SignalsError("Didn't find related object for {}, exiting.".format(self.name))

    @staticmethod
    def is_relationship(field_attributes):
        # If the relationship type is specified in any of the attributes, then it is a relationship
        return reduce(lambda x, y: x or y in Relationship.TYPES, field_attributes, False)

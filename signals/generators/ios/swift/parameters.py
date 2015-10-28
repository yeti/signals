from signals.generators.base.base_parameters import Parameter
from signals.parser.fields import Field, Relationship


class SwiftParameter(Parameter):
    SWIFT_DATA_TYPES = {
        Field.DATE: "NSDate",
        Field.DATETIME: "NSDate",
        Field.INTEGER: "Int",
        Field.DECIMAL: "Double",
        Field.FLOAT: "Float",
        Field.STRING: "String",
        Field.TEXT: "String",
        Field.BOOLEAN: "Bool",
        Field.IMAGE: "UIImage",
        Field.VIDEO: "NSURL"
    }

    def __init__(self, name, swift_type):
        super(SwiftParameter, self).__init__(name)
        self.swift_type = swift_type

    @staticmethod
    def get_swift_data_type(field):
        if field.array:
            return "Array"
        else:
            return SwiftParameter.SWIFT_DATA_TYPES[field.field_type]

    @staticmethod
    def generate_field_parameters(request_object):
        parameters = []
        for index, field in enumerate(request_object.fields):
            variable_type = SwiftParameter.get_swift_data_type(field)
            parameters.append(SwiftParameter(name=field.name, swift_type=variable_type))
        return parameters

    @staticmethod
    def generate_relationship_parameters(request_object):
        parameters = []
        for relationship in request_object.relationships:
            if relationship.relationship_type in [Relationship.MANY_TO_MANY, Relationship.ONE_TO_MANY]:
                variable_type = 'NSOrderedSet'
            else:
                from signals.generators.ios.ios_template_methods import iOSTemplateMethods
                variable_type = iOSTemplateMethods.get_object_name(relationship.related_object, upper_camel_case=True)
            parameters.append(SwiftParameter(name=relationship.name, swift_type=variable_type))
        return parameters

    @staticmethod
    def create_id_parameter(url_path, request_object):
        # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
        if ":id" in url_path and not Parameter.has_id_field(request_object):
            return SwiftParameter(name="theID", swift_type="Int")

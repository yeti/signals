"""
Creates list of Objective C specific method parameter names and types.
"""
from signals.generators.ios.conversion import get_objc_data_type
from signals.parser.fields import Relationship


class Parameter(object):
    def __init__(self, name, objc_type):
        self.name = name
        self.objc_type = objc_type


def has_id_field(request_object):
    return request_object and reduce(lambda x, y: x or y.name == 'id', request_object.fields, False)


def create_id_parameter(url_path, request_object):
    # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
    if ":id" in url_path and not has_id_field(request_object):
        return Parameter(name="theID", objc_type="NSNumber*")


def generate_relationship_parameters(request_object):
    parameters = []
    for relationship in request_object.relationships:
        if relationship.relationship_type in [Relationship.MANY_TO_MANY, Relationship.ONE_TO_MANY]:
            variable_type = 'NSOrderedSet*'
        else:
            from signals.generators.ios.template_methods import get_object_name
            variable_type = get_object_name(relationship.related_object, upper_camel_case=True)
        parameters.append(Parameter(name=relationship.name, objc_type=variable_type))
    return parameters


def generate_field_parameters(request_object):
    parameters = []
    for index, field in enumerate(request_object.fields):
        variable_type = get_objc_data_type(field)
        parameters.append(Parameter(name=field.name, objc_type=variable_type))
    return parameters

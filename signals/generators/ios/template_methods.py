"""
Methods to be used in the iOS generator's templates.
"""
import re
from urlparse import urlparse
from signals.generators.ios.parameters import create_id_parameter, generate_field_parameters, \
    generate_relationship_parameters, Parameter
from signals.generators.ios.conversion import get_proper_name
from signals.parser.api import API, GetAPI
from signals.parser.fields import Field


def method_name(api):
    # First create camel cased name from snake case
    method_name_string = ""
    for part in re.split(r'[/_]+', api.url_path):
        if part in [":id", "theID"]:
            continue
        else:
            method_name_string += part.capitalize()

    first_parameter_name = "Success"
    request_object = get_api_request_object(api)
    if request_object and len(request_object.properties()) > 0:
        first_field = request_object.properties()[0]
        first_parameter_name = get_proper_name(first_field.name, capitalize_first=True)
    elif create_id_parameter(api.url_path, request_object) is not None:
        first_parameter_name = "TheID"

    return "{}With{}".format(method_name_string, first_parameter_name)


def method_parameters(api):
    parameters = []

    # Create request object parameters
    request_object = get_api_request_object(api)
    if request_object:
        parameters.extend(generate_field_parameters(request_object))
        parameters.extend(generate_relationship_parameters(request_object))

    # Add id parameter if we need it
    id_parameter = create_id_parameter(api.url_path, request_object)
    if id_parameter:
        parameters.append(id_parameter)

    # Add required RestKit parameters
    parameters.extend([
        Parameter(name="success",
                  objc_type="void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult)"),
        Parameter(name="failure",
                  objc_type="void (^)(RKObjectRequestOperation *operation, NSError *error)")
    ])

    return create_parameter_signature(parameters)


def key_path(api):
    key_path_string = 'nil'
    if hasattr(api, 'resource_type'):
        key_path_string = 'nil' if api.resource_type == GetAPI.RESOURCE_DETAIL else '@"results"'
    elif isinstance(api, GetAPI) and ':id' not in api.url_path:
        # Get requests with an ID only return 1 object, not a list of results
        key_path_string = '@"results"'
    return key_path_string


def get_object_name(request_object, upper_camel_case=False):
    first_letter = request_object.name[1]
    if upper_camel_case:
        first_letter = first_letter.upper()
    return first_letter + request_object.name[2:]


def get_url_name(url_path):
    name = ""
    for index, part in enumerate(re.split(r'[/_]+', url_path)):
        if part in [":id", "theID"]:
            name += "WithId"
        elif index == 0:
            name += part
        else:
            name += part.capitalize()

    return name


def attribute_mappings(fields):
    attribute_mapping_string = ""
    for index, field in enumerate(fields):
        leading_comma = '' if index == 0 else ', '
        objc_variable_name = get_proper_name(field.name)
        attribute_mapping_string += '{}@"{}": @"{}"'.format(leading_comma, field.name, objc_variable_name)
    return attribute_mapping_string


def is_oauth(api):
    return api.authorization == API.OAUTH2 and not api.authorization_optional


def content_type(api):
    if api.content_type == API.CONTENT_TYPE_FORM:
        return "RKMIMETypeFormURLEncoded"
    else:
        return "RKMIMETypeJSON"


def get_media_fields(fields):
    return filter(lambda field: field.field_type in [Field.IMAGE, Field.VIDEO], fields)


def media_field_check(fields):
    statements = ["{} != nil".format(get_proper_name(field.name)) for field in fields]
    return " || ".join(statements)


def is_url(url):
    parse_result = urlparse(url)
    return parse_result.scheme in ['http', 'https']


# Helper methods for template tags

def create_parameter_signature(parameters):
    method_parts = []
    for index, method_field in enumerate(parameters):
        objc_variable_name = get_proper_name(method_field.name)
        parameter_signature = "({}){}".format(method_field.objc_type, objc_variable_name)
        # If this isn't the first parameter, also include the variable name before the type
        if index > 0:
            parameter_signature = "{}:{}".format(objc_variable_name, parameter_signature)

        method_parts.append(parameter_signature)

    return " ".join(method_parts)


def get_api_request_object(api):
    # We treat both request and parameter objects equally in method signatures
    return getattr(api, 'request_object', getattr(api, 'parameters_object', None))

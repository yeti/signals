"""
Methods to be used in the iOS generator's templates.
"""
import re
from urlparse import urlparse
from signals.generators.ios.parameters import ObjCParameter, SwiftParameter
from signals.generators.ios.conversion import get_proper_name
from signals.parser.api import API, GetAPI
from signals.parser.fields import Field


class iOSTemplateMethods(object):
    """
    Methods to translate the schema names and types to Objective-C or Swift variable names and types.
    """
    RESERVED_MAPPINGS = {
        "auto": "isAuto",
        "default": "isDefault",
        "description": "theDescription",
        "id": "theID",
        "register": "theRegister",
        "restrict": "shouldRestrict",
        "super": "isSuper",
        "volatile": "isVolatile"
    }

    # Some field names are reserved in Objective C
    @staticmethod
    def sanitize_field_name(field_name):
        if field_name in iOSTemplateMethods.RESERVED_MAPPINGS:
            return iOSTemplateMethods.RESERVED_MAPPINGS[field_name]
        else:
            return field_name

    @staticmethod
    def python_to_objc_variable(python_variable_name, capitalize_first=False):
        words = python_variable_name.split('_')

        def upper_camel_case(words_to_capitalize):
            return "".join(word.capitalize() for word in words_to_capitalize)

        if capitalize_first:
            return upper_camel_case(words)
        else:
            return words[0] + upper_camel_case(words[1:])

    @staticmethod
    def get_proper_name(name, capitalize_first=False):
        proper_name = iOSTemplateMethods.sanitize_field_name(name)
        return iOSTemplateMethods.python_to_objc_variable(proper_name, capitalize_first=capitalize_first)

    """
    Template Methods
    """

    @staticmethod
    def get_api_request_object(api):
        # We treat both request and parameter objects equally in method signatures
        return getattr(api, 'request_object', getattr(api, 'parameters_object', None))

    @staticmethod
    def get_object_name(request_object, upper_camel_case=False):
        first_letter = request_object.name[1]
        if upper_camel_case:
            first_letter = first_letter.upper()
        return first_letter + request_object.name[2:]

    @staticmethod
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

    @staticmethod
    def method_name(api):
        # First create camel cased name from snake case
        method_name_string = ""
        for part in re.split(r'[/_]+', api.url_path):
            if part in [":id", "theID"]:
                continue
            else:
                method_name_string += part.capitalize()

        first_parameter_name = "Success"
        request_object = iOSTemplateMethods.get_api_request_object(api)
        if request_object and len(request_object.properties()) > 0:
            first_field = request_object.properties()[0]
            first_parameter_name = get_proper_name(first_field.name, capitalize_first=True)
        elif ObjCParameter.create_id_parameter(api.url_path, request_object) is not None:
            first_parameter_name = "TheID"
        elif SwiftParameter.create_id_parameter(api.url_path, request_object) is not None:
            first_parameter_name = "TheID"

        return "{}With{}".format(method_name_string, first_parameter_name)

    @staticmethod
    def content_type(api):
        if api.content_type == API.CONTENT_TYPE_FORM:
            return "RKMIMETypeFormURLEncoded"
        else:
            return "RKMIMETypeJSON"

    @staticmethod
    def is_oauth(api):
        return api.authorization == API.OAUTH2 and not api.authorization_optional

    @staticmethod
    def get_media_fields(fields):
        return filter(lambda field: field.field_type in [Field.IMAGE, Field.VIDEO], fields)

    @staticmethod
    def media_field_check(fields):
        statements = ["{} != nil".format(get_proper_name(field.name)) for field in fields]
        return " || ".join(statements)

    @staticmethod
    def is_url(url):
        parse_result = urlparse(url)
        return parse_result.scheme in ['http', 'https']


def method_parameters(api):
    parameters = []

    # Create request object parameters
    request_object = get_api_request_object(api)
    if request_object:
        parameters.extend(ObjCParameter.generate_field_parameters(request_object))
        parameters.extend(ObjCParameter.generate_relationship_parameters(request_object))

    # Add id parameter if we need it
    id_parameter = ObjCParameter.create_id_parameter(api.url_path, request_object)
    if id_parameter:
        parameters.append(id_parameter)

    # Add required RestKit parameters
    parameters.extend([
        ObjCParameter(name="success",
                      objc_type="void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult)"),
        ObjCParameter(name="failure",
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


def attribute_mappings(fields):
    attribute_mapping_string = ""
    for index, field in enumerate(fields):
        leading_comma = '' if index == 0 else ', '
        objc_variable_name = get_proper_name(field.name)
        attribute_mapping_string += '{}@"{}": @"{}"'.format(leading_comma, field.name, objc_variable_name)
    return attribute_mapping_string

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

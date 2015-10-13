"""
Methods to be used in the iOS generator's templates.
"""
import re
from urlparse import urlparse
from signals.generators.ios.parameters import ObjCParameter, SwiftParameter
from signals.generators.ios.conversion import get_proper_name
from signals.parser.api import API
from signals.parser.fields import Field


class iOSTemplateMethods(object):
    """
    Methods used while generating iOS templates
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

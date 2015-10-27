"""
Methods to be used in the iOS generator's templates.
"""
import re
from signals.generators.base.base_template_methods import BaseTemplateMethods
from signals.generators.ios.conversion import get_proper_name
from signals.generators.ios.objc.parameters import ObjCParameter
from signals.generators.ios.swift.parameters import SwiftParameter
from signals.parser.api import API


class iOSTemplateMethods(BaseTemplateMethods):
    """
    Methods used while generating iOS templates
    """
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
    def media_field_check(fields):
        statements = ["{} != nil".format(get_proper_name(field.name)) for field in fields]
        return " || ".join(statements)

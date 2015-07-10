from datetime import datetime
import os
import subprocess
from urlparse import urlparse
from jinja2 import Environment, PackageLoader
import re
import shutil
from signals.logging import SignalsError, progress
from signals.generators.ios.utils import python_to_objc_variable, sanitize_field_name, get_object_name, \
    get_objc_data_type
from signals.parser.api import GetAPI, API
from signals.parser.fields import Relationship, Field
from signals.parser.schema import URL
from signals.generators.base.base_generator import BaseGenerator
from signals.generators.ios.core_data import write_xml_to_file

class iOSGenerator(BaseGenerator):
    def __init__(self, schema, data_models_path, core_data_path, project_name, api_url):
        super(iOSGenerator, self).__init__(schema)
        # Command flags
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name
        self.api_url = api_url

        # Setup
        if not os.path.exists(BaseGenerator.BUILD_DIR):
            os.makedirs(BaseGenerator.BUILD_DIR)
        self.header_file = "{}/{}DataModel.h".format(BaseGenerator.BUILD_DIR, self.project_name)
        self.implementation_file = "{}/{}DataModel.m".format(BaseGenerator.BUILD_DIR, self.project_name)
        self.jinja2_environment = Environment(loader=PackageLoader(__name__),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def process(self):
        if self.core_data_path is not None:
            if self.is_xcode_running():
                raise SignalsError("Must quit Xcode before writing to core data")
            progress("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)

        progress("Creating data model file")
        self.create_header_file()
        self.create_implementation_file()
        self.copy_data_models()

    def create_header_file(self):
        template = self.jinja2_environment.get_template('data_model.h.j2')
        context = {
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'urls': self.schema.urls,
            'method_name': self.method_name,
            'method_parameters': self.method_parameters
        }
        template_output = template.render(**context)
        with open(self.header_file, "w") as output_file:
            output_file.write(template_output)

    def create_implementation_file(self):
        template = self.jinja2_environment.get_template('data_model.m.j2')
        context = {
            'today': datetime.today(),
            'project_name': self.project_name,
            'request_objects': self.get_request_objects(),
            'request_object_name': get_object_name,
            'api_url': self.api_url,
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'urls': self.schema.urls,
            'data_objects': self.schema.data_objects,
            'key_path': self.key_path,
            'get_url_name': self.get_url_name,
            'get_object_name': self.get_object_name,
            'sanitize_field_name': sanitize_field_name,
            'attribute_mappings': self.attribute_mappings,
            'is_oauth': self.is_oauth,
            'content_type': self.content_type,
            'method_name': self.method_name,
            'method_parameters': self.method_parameters,
            'get_proper_name': self.get_proper_name,
            'get_media_fields': self.get_media_fields,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'media_field_check': self.media_field_check,
            'is_url': self.is_url
        }
        template_output = template.render(**context)
        with open(self.implementation_file, "w") as output_file:
            output_file.write(template_output)

    def copy_data_models(self):
        shutil.copyfile(self.header_file, "{}/DataModel.h".format(self.data_models_path))
        shutil.copyfile(self.implementation_file, "{}/DataModel.m".format(self.data_models_path))

    @staticmethod
    def is_xcode_running():
        return "Xcode.app" in subprocess.check_output(["ps", "-Ax"])

    # Template Methods #

    def get_request_objects(self):
        request_objects = []
        for name, data_object in self.schema.data_objects.iteritems():
            # TODO: Naming request objects as XRequest is not a standard we always keep true
            if 'Request' in name:
                request_objects.append(data_object)
        return request_objects

    def method_name(self, api):
        # First create camel cased name from snake case
        method_name = ""
        for part in re.split(r'[/_]+', api.url_path):
            if part in [":id", "theID"]:
                continue
            else:
                method_name += part.capitalize()

        first_parameter_name = "Success"
        request_object = self.get_api_request_object(api)
        if request_object and len(request_object.properties()) > 0:
            first_field = request_object.properties()[0]
            first_parameter_name = self.get_proper_name(first_field.name, capitalize_first=True)
        elif self.create_id_parameter(api.url_path, request_object) is not None:
            first_parameter_name = "TheID"

        return "{}With{}".format(method_name, first_parameter_name)

    def method_parameters(self, api):
        parameters = []

        # Create request object parameters
        request_object = self.get_api_request_object(api)
        if request_object:
            parameters.extend(self.generate_field_parameters(request_object))
            parameters.extend(self.generate_relationship_parameters(request_object))

        # Add id parameter if we need it
        id_parameter = self.create_id_parameter(api.url_path, request_object)
        if id_parameter:
            parameters.append(id_parameter)

        # Add required RestKit parameters
        parameters.extend([
            Parameter(name="success",
                      objc_type="void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult)"),
            Parameter(name="failure",
                      objc_type="void (^)(RKObjectRequestOperation *operation, NSError *error)")
        ])

        return self.create_parameter_signature(parameters)

    @staticmethod
    def key_path(api):
        key_path = 'nil'
        if hasattr(api, 'resource_type'):
            key_path = 'nil' if api.resource_type == GetAPI.RESOURCE_DETAIL else '@"results"'
        elif isinstance(api, GetAPI) and ':id' not in api.url_path:
            # Get requests with an ID only return 1 object, not a list of results
            key_path = '@"results"'
        return key_path

    @staticmethod
    def get_object_name(request_object, upper_camel_case=False):
        first_letter = request_object[1]
        if upper_camel_case:
            first_letter = first_letter.upper()
        return first_letter + request_object[2:]

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
    def attribute_mappings(fields):
        attribute_mapping_string = ""
        for index, field in enumerate(fields):
            leading_comma = '' if index == 0 else ', '
            objc_variable_name = iOSGenerator.get_proper_name(field.name)
            attribute_mapping_string += '{}@"{}": @"{}"'.format(leading_comma, field.name, objc_variable_name)
        return attribute_mapping_string

    @staticmethod
    def is_oauth(api):
        return api.authorization == API.OAUTH2 and not api.authorization_optional

    @staticmethod
    def content_type(api):
        if api.content_type == API.CONTENT_TYPE_FORM:
            return "RKMIMETypeFormURLEncoded"
        else:
            return "RKMIMETypeJSON"

    @staticmethod
    def get_media_fields(fields):
        return filter(lambda field: field.field_type in [Field.IMAGE, Field.VIDEO], fields)

    @staticmethod
    def media_field_check(fields):
        statements = ["{} != nil".format(iOSGenerator.get_proper_name(field.name)) for field in fields]
        return " || ".join(statements)

    @staticmethod
    def is_url(url):
        parse_result = urlparse(url)
        return parse_result.scheme in ['http', 'https']

    # Utility methods for template functions #

    def get_api_request_object(self, api):
        # We treat both request and parameter objects equally in method signatures
        request_object_name = getattr(api, 'request_object', getattr(api, 'parameters_object', None))
        if request_object_name:
            return self.schema.data_objects[request_object_name]

    @staticmethod
    def generate_relationship_parameters(request_object):
        parameters = []
        for relationship in request_object.relationships:
            if relationship.relationship_type in [Relationship.MANY_TO_MANY, Relationship.ONE_TO_MANY]:
                variable_type = 'NSOrderedSet*'
            else:
                variable_type = get_object_name(relationship.related_object)
            parameters.append(Parameter(name=relationship.name, objc_type=variable_type))
        return parameters

    @staticmethod
    def generate_field_parameters(request_object):
        parameters = []
        for index, field in enumerate(request_object.fields):
            variable_type = get_objc_data_type(field)
            parameters.append(Parameter(name=field.name, objc_type=variable_type))
        return parameters

    @staticmethod
    def has_id_field(request_object):
        return request_object and reduce(lambda x, y: x or y.name == 'id', request_object.fields, False)

    @staticmethod
    def create_id_parameter(url_path, request_object):
        # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
        if ":id" in url_path and not iOSGenerator.has_id_field(request_object):
            return Parameter(name="theID", objc_type="NSNumber*")

    @staticmethod
    def get_proper_name(name, capitalize_first=False):
        sanitized_field_name = sanitize_field_name(name)
        return python_to_objc_variable(sanitized_field_name, capitalize_first=capitalize_first)

    @staticmethod
    def create_parameter_signature(parameters):
        method_parts = []
        for index, method_field in enumerate(parameters):
            objc_variable_name = iOSGenerator.get_proper_name(method_field.name)
            parameter_signature = "({}){}".format(method_field.objc_type, objc_variable_name)
            # If this isn't the first parameter, also include the variable name before the type
            if index > 0:
                parameter_signature = "{}:{}".format(objc_variable_name, parameter_signature)

            method_parts.append(parameter_signature)

        return " ".join(method_parts)


class Parameter(object):
    def __init__(self, name, objc_type):
        self.name = name
        self.objc_type = objc_type

from collections import namedtuple
from datetime import datetime
from jinja2 import Environment, PackageLoader
import re
from signals.parser.fields import Field, Relationship
from signals.parser.schema import URL
from signals.generators.base.base_generator import BaseGenerator
from signals.generators.ios.core_data import write_xml_to_file
from signals.generators.ios.data_model import create_mappings

class iOSGenerator(BaseGenerator):
    OBJC_DATA_TYPES = {
        Field.DATE: "NSDate*",
        Field.DATETIME: "NSDate*",
        Field.INTEGER: "NSNumber*",
        Field.DECIMAL: "NSNumber*",
        Field.FLOAT: "NSNumber*",
        Field.STRING: "NSString*",
        Field.TEXT: "NSString*",
        Field.BOOLEAN: "NSNumber*",
        Field.IMAGE: "UIImage*",
        Field.VIDEO: "NSURL*"
    }

    def __init__(self, schema, data_models_path, core_data_path, project_name):
        super(iOSGenerator, self).__init__(schema)
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name
        self.jinja2_environment = Environment(loader=PackageLoader(__name__), extensions=['jinja2.ext.with_'])

    def process(self):
        print("Creating data model file")
        create_mappings(self.schema.urls, self.schema.data_objects, self.project_name)

        self.create_header_file()

        if self.core_data_path is not None:
            print("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)

    def create_header_file(self):
        header_template = self.jinja2_environment.get_template('data_model.h.j2')
        context = {
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'urls': self.schema.urls,
            'method_name': self.method_name,
            'method_parameters': self.method_parameters
        }
        template_output = header_template.render(**context)
        header_file_path = "{}/GeneratedDataModel.h".format(BaseGenerator.BUILD_DIR)
        with open(header_file_path, "w") as header_file:
            header_file.write(template_output)

    # Changes a python variable name to an objective c version
    @staticmethod
    def python_to_objc_variable(python_variable_name, capitalize_first=False):
        words = python_variable_name.split('_')

        def upper_camel_case(words):
            return "".join(word.capitalize() for word in words)

        if capitalize_first:
            return upper_camel_case(words)
        else:
            return words[0] + upper_camel_case(words[1:])

    # Some field names are reserved in Objective C
    @staticmethod
    def sanitize_field_name(field_name):
        if field_name == "id":
            return "theID"
        elif field_name == "description":
            return "theDescription"
        else:
            return field_name

    def get_api_request_object(self, api):
        # We treat both request and parameter objects equally in method signatures
        request_object_name = getattr(api, 'request_object', getattr(api, 'parameters_object', None))
        if request_object_name:
            return self.schema.data_objects[request_object_name]

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
            sanitized_field_name = self.sanitize_field_name(first_field.name)
            objc_variable_name = self.python_to_objc_variable(sanitized_field_name, capitalize_first=True)
            first_parameter_name = objc_variable_name

        return "{}With{}".format(method_name, first_parameter_name)

    def get_objc_data_type(self, field_type):
        if field_type == Field.ARRAY:
            return "NSArray*"
        else:
            return self.OBJC_DATA_TYPES[field_type]

    @staticmethod
    def get_object_name(obj):
        return obj[1].upper() + obj[2:]

    def method_parameters(self, api):
        has_id = False
        request_object = self.get_api_request_object(api)
        MethodField = namedtuple('MethodField', 'name objc_type')
        method_fields = []
        if request_object:
            # Create all of the parameters based on the request object's fields
            for index, field in enumerate(request_object.fields):
                if field.name == 'id':
                    has_id = True

                variable_type = self.get_objc_data_type(field.field_type)
                method_fields.append(MethodField(name=field.name, objc_type=variable_type))

            for relationship in request_object.relationships:
                if relationship.relationship_type in [Relationship.MANY_TO_MANY, Relationship.ONE_TO_MANY]:
                    variable_type = 'NSOrderedSet*'
                else:
                    variable_type = self.get_object_name(relationship.related_object)
                method_fields.append(MethodField(name=relationship.name, objc_type=variable_type))

        # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
        if "id" in api.url_path and not has_id:
            method_fields.append(MethodField(name="theID", objc_type="NSNumber*"))

        # Add required RestKit parameters
        restkit_method_fields = [
            MethodField(name="success", objc_type="void (^)(RKObjectRequestOperation *operation, "
                                                  "RKMappingResult *mappingResult)"),
            MethodField(name="failure", objc_type="void (^)(RKObjectRequestOperation *operation, NSError *error)")
        ]
        method_fields.extend(restkit_method_fields)

        method_parts = []
        for index, method_field in enumerate(method_fields):
            sanitized_field_name = self.sanitize_field_name(method_field.name)
            objc_variable_name = self.python_to_objc_variable(sanitized_field_name)

            parameter_signature = "({}){}".format(method_field.objc_type, objc_variable_name)
            # If this isn't the first parameter, also include the variable name before the type
            if index > 0:
                parameter_signature = "{}:{}".format(objc_variable_name, parameter_signature)

            method_parts.append(parameter_signature)

        return " ".join(method_parts)
